"""Risk checker for order execution safety."""

from __future__ import annotations

from decimal import Decimal

from finbot.core.contracts.models import OrderSide
from finbot.core.contracts.orders import Order, RejectionReason
from finbot.core.contracts.risk import RiskConfig, RiskRuleType, RiskViolation


class RiskChecker:
    """Checks orders against risk rules.

    Features:
    - Position size limits (shares and value per symbol)
    - Portfolio exposure limits (gross and net)
    - Drawdown protection (daily and total from peak)
    - Kill-switch (emergency trading halt)

    Example:
        >>> from finbot.core.contracts.risk import RiskConfig, PositionLimitRule
        >>> config = RiskConfig(
        ...     position_limit=PositionLimitRule(max_shares=Decimal("1000")),
        ...     trading_enabled=True,
        ... )
        >>> checker = RiskChecker(config)
    """

    def __init__(self, risk_config: RiskConfig):
        """Initialize risk checker.

        Args:
            risk_config: Risk control configuration
        """
        self.risk_config = risk_config
        self.peak_value: Decimal = Decimal("0")
        self.daily_start_value: Decimal = Decimal("0")
        self.trading_enabled = risk_config.trading_enabled

    def check_order(
        self,
        order: Order,
        current_positions: dict[str, Decimal],
        current_prices: dict[str, Decimal],
        cash: Decimal,
    ) -> tuple[RejectionReason, str] | None:
        """Check order against all risk rules.

        Args:
            order: Order to check
            current_positions: Current positions {symbol: quantity}
            current_prices: Current market prices {symbol: price}
            cash: Current cash balance

        Returns:
            (rejection_reason, message) if violated, None if passed
        """
        # 1. Check kill-switch
        if not self.trading_enabled:
            return (
                RejectionReason.RISK_TRADING_DISABLED,
                "Trading is disabled (kill-switch active)",
            )

        # 2. Check position limits
        if self.risk_config.position_limit:
            violation = self._check_position_limits(order, current_positions, current_prices)
            if violation:
                return (RejectionReason.RISK_POSITION_LIMIT, violation.message)

        # 3. Check exposure limits
        if self.risk_config.exposure_limit:
            violation = self._check_exposure_limits(order, current_positions, current_prices, cash)
            if violation:
                return (RejectionReason.RISK_EXPOSURE_LIMIT, violation.message)

        # 4. Check drawdown limits
        if self.risk_config.drawdown_limit:
            portfolio_value = self._calculate_portfolio_value(current_positions, current_prices, cash)
            violation = self._check_drawdown_limits(portfolio_value)
            if violation:
                return (RejectionReason.RISK_DRAWDOWN_LIMIT, violation.message)

        return None

    def update_state(
        self,
        portfolio_value: Decimal,
        is_new_day: bool = False,
    ) -> None:
        """Update risk state after trades.

        Args:
            portfolio_value: Current total portfolio value
            is_new_day: Whether this is the start of a new trading day
        """
        # Update peak value
        if portfolio_value > self.peak_value:
            self.peak_value = portfolio_value

        # Reset daily tracking if new day
        if is_new_day:
            self.reset_daily_tracking(portfolio_value)

    def enable_trading(self) -> None:
        """Enable trading (clear kill-switch)."""
        self.trading_enabled = True

    def disable_trading(self) -> None:
        """Disable trading (activate kill-switch)."""
        self.trading_enabled = False

    def reset_daily_tracking(self, current_value: Decimal) -> None:
        """Reset daily drawdown tracking.

        Args:
            current_value: Current portfolio value (start of day)
        """
        self.daily_start_value = current_value

    def _check_position_limits(
        self,
        order: Order,
        current_positions: dict[str, Decimal],
        current_prices: dict[str, Decimal],
    ) -> RiskViolation | None:
        """Check position size limits.

        Args:
            order: Order to check
            current_positions: Current positions
            current_prices: Current prices

        Returns:
            RiskViolation if limit exceeded, None otherwise
        """
        rule = self.risk_config.position_limit
        if not rule:
            return None

        # Only check buy orders (sells reduce position)
        if order.side != OrderSide.BUY:
            return None

        # Calculate new position after order
        current_pos = current_positions.get(order.symbol, Decimal("0"))
        new_pos = current_pos + order.quantity

        # Check shares limit
        if rule.max_shares is not None and new_pos > rule.max_shares:
            return RiskViolation(
                rule_type=RiskRuleType.POSITION_LIMIT,
                message=f"Position would exceed max shares: {new_pos} > {rule.max_shares}",
                current_value=new_pos,
                limit_value=rule.max_shares,
            )

        # Check value limit
        if rule.max_value is not None:
            price = current_prices.get(order.symbol)
            if price is not None:
                new_value = new_pos * price
                if new_value > rule.max_value:
                    return RiskViolation(
                        rule_type=RiskRuleType.POSITION_LIMIT,
                        message=f"Position value would exceed limit: {new_value} > {rule.max_value}",
                        current_value=new_value,
                        limit_value=rule.max_value,
                    )

        return None

    def _check_exposure_limits(
        self,
        order: Order,
        current_positions: dict[str, Decimal],
        current_prices: dict[str, Decimal],
        cash: Decimal,
    ) -> RiskViolation | None:
        """Check portfolio exposure limits.

        Args:
            order: Order to check
            current_positions: Current positions
            current_prices: Current prices
            cash: Current cash

        Returns:
            RiskViolation if limit exceeded, None otherwise
        """
        rule = self.risk_config.exposure_limit
        if not rule:
            return None

        # Calculate current portfolio value
        portfolio_value = self._calculate_portfolio_value(current_positions, current_prices, cash)
        if portfolio_value == 0:
            return None

        # Simulate new positions after order
        new_positions = current_positions.copy()
        if order.side == OrderSide.BUY:
            new_positions[order.symbol] = new_positions.get(order.symbol, Decimal("0")) + order.quantity
        else:
            new_positions[order.symbol] = new_positions.get(order.symbol, Decimal("0")) - order.quantity

        # Calculate new exposure
        gross_exposure = Decimal("0")
        net_exposure = Decimal("0")

        for symbol, qty in new_positions.items():
            if qty == 0:
                continue
            price = current_prices.get(symbol, Decimal("0"))
            position_value = abs(qty) * price
            gross_exposure += position_value
            net_exposure += qty * price  # Signed for net

        # Convert to percentages
        gross_exposure_pct = (gross_exposure / portfolio_value) * Decimal("100")
        net_exposure_pct = (abs(net_exposure) / portfolio_value) * Decimal("100")

        # Check limits
        if gross_exposure_pct > rule.max_gross_exposure_pct:
            return RiskViolation(
                rule_type=RiskRuleType.EXPOSURE_LIMIT,
                message=f"Gross exposure would exceed limit: {gross_exposure_pct:.1f}% > {rule.max_gross_exposure_pct}%",
                current_value=gross_exposure_pct,
                limit_value=rule.max_gross_exposure_pct,
            )

        if net_exposure_pct > rule.max_net_exposure_pct:
            return RiskViolation(
                rule_type=RiskRuleType.EXPOSURE_LIMIT,
                message=f"Net exposure would exceed limit: {net_exposure_pct:.1f}% > {rule.max_net_exposure_pct}%",
                current_value=net_exposure_pct,
                limit_value=rule.max_net_exposure_pct,
            )

        return None

    def _check_drawdown_limits(
        self,
        portfolio_value: Decimal,
    ) -> RiskViolation | None:
        """Check drawdown protection limits.

        Args:
            portfolio_value: Current portfolio value

        Returns:
            RiskViolation if limit exceeded, None otherwise
        """
        rule = self.risk_config.drawdown_limit
        if not rule:
            return None

        # Check daily drawdown
        if rule.max_daily_drawdown_pct is not None and self.daily_start_value > 0:
            daily_return_pct = ((portfolio_value - self.daily_start_value) / self.daily_start_value) * Decimal("100")
            if daily_return_pct < -rule.max_daily_drawdown_pct:
                return RiskViolation(
                    rule_type=RiskRuleType.DRAWDOWN_LIMIT,
                    message=f"Daily drawdown exceeds limit: {-daily_return_pct:.1f}% > {rule.max_daily_drawdown_pct}%",
                    current_value=-daily_return_pct,
                    limit_value=rule.max_daily_drawdown_pct,
                )

        # Check total drawdown from peak
        if rule.max_total_drawdown_pct is not None and self.peak_value > 0:
            drawdown_pct = ((self.peak_value - portfolio_value) / self.peak_value) * Decimal("100")
            if drawdown_pct > rule.max_total_drawdown_pct:
                return RiskViolation(
                    rule_type=RiskRuleType.DRAWDOWN_LIMIT,
                    message=f"Total drawdown exceeds limit: {drawdown_pct:.1f}% > {rule.max_total_drawdown_pct}%",
                    current_value=drawdown_pct,
                    limit_value=rule.max_total_drawdown_pct,
                )

        return None

    def _calculate_portfolio_value(
        self,
        positions: dict[str, Decimal],
        prices: dict[str, Decimal],
        cash: Decimal,
    ) -> Decimal:
        """Calculate total portfolio value.

        Args:
            positions: Current positions
            prices: Current prices
            cash: Cash balance

        Returns:
            Total portfolio value
        """
        position_value = sum(qty * prices.get(symbol, Decimal("0")) for symbol, qty in positions.items())

        return cash + position_value
