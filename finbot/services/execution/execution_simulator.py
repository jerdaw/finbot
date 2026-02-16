"""Execution simulator for paper trading."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from finbot.core.contracts.models import OrderSide, OrderType
from finbot.core.contracts.orders import Order, OrderExecution, OrderStatus, RejectionReason
from finbot.services.execution.order_validator import OrderValidator


class ExecutionSimulator:
    """Simulates order execution for paper trading.

    Features:
    - Realistic fill simulation with configurable slippage
    - Order validation before execution
    - Position and cash tracking
    - Support for market and limit orders
    """

    def __init__(
        self,
        initial_cash: Decimal,
        slippage_bps: Decimal = Decimal("5"),
        commission_per_share: Decimal = Decimal("0"),
    ):
        """Initialize execution simulator.

        Args:
            initial_cash: Starting cash balance
            slippage_bps: Slippage in basis points (default: 5 bps = 0.05%)
            commission_per_share: Commission per share traded
        """
        self.cash = initial_cash
        self.positions: dict[str, Decimal] = {}
        self.slippage_bps = slippage_bps
        self.commission_per_share = commission_per_share

        self.pending_orders: dict[str, Order] = {}
        self.completed_orders: dict[str, Order] = {}

        self.validator = OrderValidator()

    def submit_order(self, order: Order) -> Order:
        """Submit order for execution.

        Args:
            order: Order to submit

        Returns:
            Updated order with submission status
        """
        # Validate order
        current_prices: dict[str, Decimal] = {}
        validation = self.validator.validate(order, self.cash, self.positions, current_prices)

        if not validation.is_valid:
            order.status = OrderStatus.REJECTED
            order.rejected_at = datetime.now()
            order.rejection_reason = validation.rejection_reason
            order.rejection_message = validation.message
            self.completed_orders[order.order_id] = order
            return order

        # Update order status
        order.status = OrderStatus.SUBMITTED
        order.submitted_at = datetime.now()
        self.pending_orders[order.order_id] = order

        return order

    def process_market_data(
        self,
        symbol: str,
        price: Decimal,
        timestamp: datetime | None = None,
    ) -> list[OrderExecution]:
        """Process market data and execute pending orders.

        Args:
            symbol: Symbol for market data
            price: Current market price
            timestamp: Market data timestamp (defaults to now)

        Returns:
            List of executions generated
        """
        if timestamp is None:
            timestamp = datetime.now()

        executions: list[OrderExecution] = []

        # Find pending orders for this symbol
        orders_to_process = [
            order for order in self.pending_orders.values() if order.symbol == symbol and not order.is_complete()
        ]

        for order in orders_to_process:
            # Check if order can be filled
            if self._can_fill_order(order, price):
                execution = self._execute_order(order, price, timestamp)
                if execution:
                    executions.append(execution)

                # Move to completed if done
                if order.is_complete():
                    del self.pending_orders[order.order_id]
                    self.completed_orders[order.order_id] = order

        return executions

    def get_account_value(self, current_prices: dict[str, Decimal]) -> Decimal:
        """Calculate total account value.

        Args:
            current_prices: Current market prices for all positions

        Returns:
            Total account value (cash + positions)
        """
        position_value = sum(qty * current_prices.get(symbol, Decimal("0")) for symbol, qty in self.positions.items())

        return self.cash + position_value

    def _can_fill_order(self, order: Order, price: Decimal) -> bool:
        """Check if order can be filled at current price.

        Args:
            order: Order to check
            price: Current market price

        Returns:
            True if order can be filled
        """
        # Market orders always fill
        if order.order_type == OrderType.MARKET:
            return True

        # Limit buy: fill if price <= limit
        if order.order_type == OrderType.LIMIT and order.limit_price is not None:
            if order.side == OrderSide.BUY:
                return price <= order.limit_price
            # Limit sell: fill if price >= limit
            return price >= order.limit_price

        return False

    def _execute_order(
        self,
        order: Order,
        price: Decimal,
        timestamp: datetime,
    ) -> OrderExecution | None:
        """Execute order at given price.

        Args:
            order: Order to execute
            price: Execution price
            timestamp: Execution timestamp

        Returns:
            Order execution record, or None if execution failed
        """
        # Apply slippage
        slippage_multiplier = self.slippage_bps / Decimal("10000")
        if order.side == OrderSide.BUY:
            fill_price = price * (Decimal("1") + slippage_multiplier)
        else:
            fill_price = price * (Decimal("1") - slippage_multiplier)

        # Calculate quantity to fill (for now, fill entire order)
        fill_quantity = order.remaining_quantity()
        is_partial = False  # Full fills only for now

        # Calculate commission
        commission = fill_quantity * self.commission_per_share

        # Check if we have enough cash for buy
        if order.side == OrderSide.BUY:
            required_cash = fill_quantity * fill_price + commission
            if required_cash > self.cash:
                # Reject order due to insufficient funds
                order.status = OrderStatus.REJECTED
                order.rejected_at = timestamp
                order.rejection_reason = RejectionReason.INSUFFICIENT_FUNDS
                order.rejection_message = f"Insufficient cash: need {required_cash}, have {self.cash}"
                return None

        # Create execution
        execution = OrderExecution(
            execution_id=f"exec-{uuid.uuid4().hex[:16]}",
            order_id=order.order_id,
            timestamp=timestamp,
            quantity=fill_quantity,
            price=fill_price,
            commission=commission,
            is_partial=is_partial,
        )

        # Update order
        order.add_execution(execution)

        # Update positions and cash
        if order.side == OrderSide.BUY:
            self.positions[order.symbol] = self.positions.get(order.symbol, Decimal("0")) + fill_quantity
            self.cash -= fill_quantity * fill_price + commission
        else:
            self.positions[order.symbol] = self.positions.get(order.symbol, Decimal("0")) - fill_quantity
            self.cash += fill_quantity * fill_price - commission

        return execution

    def cancel_order(self, order_id: str) -> Order | None:
        """Cancel a pending order.

        Args:
            order_id: Order ID to cancel

        Returns:
            Cancelled order, or None if not found
        """
        order = self.pending_orders.get(order_id)
        if order is None:
            return None

        order.status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.now()

        del self.pending_orders[order_id]
        self.completed_orders[order_id] = order

        return order

    def get_order(self, order_id: str) -> Order | None:
        """Get order by ID.

        Args:
            order_id: Order ID

        Returns:
            Order if found, None otherwise
        """
        return self.pending_orders.get(order_id) or self.completed_orders.get(order_id)
