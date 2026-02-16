"""Order validation before execution."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from finbot.core.contracts.models import OrderSide
from finbot.core.contracts.orders import Order, RejectionReason


@dataclass
class ValidationResult:
    """Result of order validation.

    Attributes:
        is_valid: Whether order is valid
        rejection_reason: Reason code if invalid
        message: Human-readable message if invalid
    """

    is_valid: bool
    rejection_reason: RejectionReason | None = None
    message: str | None = None


class OrderValidator:
    """Validates orders before execution.

    Performs pre-flight checks including:
    - Quantity validation
    - Buying power checks
    - Symbol validity
    - Position limits
    """

    def __init__(
        self,
        min_order_quantity: Decimal = Decimal("0.001"),
        max_order_quantity: Decimal = Decimal("1000000"),
    ):
        """Initialize validator.

        Args:
            min_order_quantity: Minimum allowed order quantity
            max_order_quantity: Maximum allowed order quantity
        """
        self.min_order_quantity = min_order_quantity
        self.max_order_quantity = max_order_quantity

    def validate(
        self,
        order: Order,
        account_balance: Decimal,
        positions: dict[str, Decimal],
        current_prices: dict[str, Decimal] | None = None,
    ) -> ValidationResult:
        """Validate order against account state.

        Args:
            order: Order to validate
            account_balance: Available cash balance
            positions: Current positions {symbol: quantity}
            current_prices: Current market prices {symbol: price}

        Returns:
            Validation result with pass/fail and reason
        """
        # Check quantity
        if order.quantity <= 0:
            return ValidationResult(
                is_valid=False,
                rejection_reason=RejectionReason.INVALID_QUANTITY,
                message=f"Order quantity must be positive, got {order.quantity}",
            )

        if order.quantity < self.min_order_quantity:
            return ValidationResult(
                is_valid=False,
                rejection_reason=RejectionReason.INVALID_QUANTITY,
                message=f"Order quantity {order.quantity} below minimum {self.min_order_quantity}",
            )

        if order.quantity > self.max_order_quantity:
            return ValidationResult(
                is_valid=False,
                rejection_reason=RejectionReason.INVALID_QUANTITY,
                message=f"Order quantity {order.quantity} exceeds maximum {self.max_order_quantity}",
            )

        # Check buying power for buy orders
        if order.side == OrderSide.BUY:
            required_cash = self._calculate_required_cash(order, current_prices)
            if required_cash is not None and required_cash > account_balance:
                return ValidationResult(
                    is_valid=False,
                    rejection_reason=RejectionReason.INSUFFICIENT_FUNDS,
                    message=f"Insufficient funds: need {required_cash}, have {account_balance}",
                )

        # Check sell orders against positions
        if order.side == OrderSide.SELL:
            current_position = positions.get(order.symbol, Decimal("0"))
            if current_position < order.quantity:
                return ValidationResult(
                    is_valid=False,
                    rejection_reason=RejectionReason.INVALID_QUANTITY,
                    message=f"Insufficient position: trying to sell {order.quantity}, have {current_position}",
                )

        # All checks passed
        return ValidationResult(is_valid=True)

    def _calculate_required_cash(
        self,
        order: Order,
        current_prices: dict[str, Decimal] | None,
    ) -> Decimal | None:
        """Calculate required cash for order.

        Args:
            order: Order to calculate for
            current_prices: Current market prices

        Returns:
            Required cash amount, or None if cannot calculate
        """
        # For limit orders, use limit price
        if order.limit_price is not None:
            return order.quantity * order.limit_price

        # For market orders, use current price if available
        if current_prices and order.symbol in current_prices:
            return order.quantity * current_prices[order.symbol]

        # Cannot calculate without price information
        return None
