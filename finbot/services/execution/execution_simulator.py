"""Execution simulator for paper trading with latency simulation."""

from __future__ import annotations

import random
import uuid
from datetime import datetime
from decimal import Decimal

from finbot.core.contracts.latency import LATENCY_INSTANT, LatencyConfig
from finbot.core.contracts.models import OrderSide, OrderType
from finbot.core.contracts.orders import Order, OrderExecution, OrderStatus, RejectionReason
from finbot.services.execution.order_validator import OrderValidator
from finbot.services.execution.pending_actions import ActionType, PendingAction, PendingActionQueue


class ExecutionSimulator:
    """Simulates order execution for paper trading with latency.

    Features:
    - Realistic fill simulation with configurable slippage
    - Latency simulation (submission, fill, cancellation delays)
    - Order validation before execution
    - Position and cash tracking
    - Support for market and limit orders

    Example with latency:
        >>> from finbot.core.contracts.latency import LATENCY_NORMAL
        >>> simulator = ExecutionSimulator(
        ...     initial_cash=Decimal("100000"),
        ...     latency_config=LATENCY_NORMAL,
        ... )
        >>> # Orders will have realistic delays
    """

    def __init__(
        self,
        initial_cash: Decimal,
        slippage_bps: Decimal = Decimal("5"),
        commission_per_share: Decimal = Decimal("0"),
        latency_config: LatencyConfig = LATENCY_INSTANT,
    ):
        """Initialize execution simulator.

        Args:
            initial_cash: Starting cash balance
            slippage_bps: Slippage in basis points (default: 5 bps = 0.05%)
            commission_per_share: Commission per share traded
            latency_config: Latency configuration (default: instant execution)
        """
        self.cash = initial_cash
        self.positions: dict[str, Decimal] = {}
        self.slippage_bps = slippage_bps
        self.commission_per_share = commission_per_share
        self.latency_config = latency_config

        self.pending_orders: dict[str, Order] = {}
        self.completed_orders: dict[str, Order] = {}

        self.validator = OrderValidator()
        self.action_queue = PendingActionQueue()
        self.current_time = datetime.now()

    def submit_order(self, order: Order, timestamp: datetime | None = None) -> Order:
        """Submit order for execution with latency simulation.

        Args:
            order: Order to submit
            timestamp: Current time (defaults to now)

        Returns:
            Updated order (status depends on latency config)
        """
        if timestamp is None:
            timestamp = datetime.now()

        self.current_time = timestamp

        # Validate order immediately
        current_prices: dict[str, Decimal] = {}
        validation = self.validator.validate(order, self.cash, self.positions, current_prices)

        if not validation.is_valid:
            order.status = OrderStatus.REJECTED
            order.rejected_at = timestamp
            order.rejection_reason = validation.rejection_reason
            order.rejection_message = validation.message
            self.completed_orders[order.order_id] = order
            return order

        # Schedule submission with latency
        submission_time = timestamp + self.latency_config.submission_latency

        if self.latency_config.submission_latency.total_seconds() == 0:
            # Instant submission
            order.status = OrderStatus.SUBMITTED
            order.submitted_at = timestamp
            self.pending_orders[order.order_id] = order
        else:
            # Delayed submission
            order.status = OrderStatus.NEW
            self.action_queue.add_action(
                PendingAction(
                    action_type=ActionType.SUBMIT,
                    order_id=order.order_id,
                    scheduled_time=submission_time,
                    data={"order": order},
                )
            )

        return order

    def process_market_data(
        self,
        symbol: str,
        price: Decimal,
        timestamp: datetime | None = None,
    ) -> list[OrderExecution]:
        """Process market data and execute pending orders with latency.

        Args:
            symbol: Symbol for market data
            price: Current market price
            timestamp: Market data timestamp (defaults to now)

        Returns:
            List of executions generated
        """
        if timestamp is None:
            timestamp = datetime.now()

        self.current_time = timestamp

        # Process all due actions (submissions, fills, cancellations)
        self._process_due_actions(timestamp)

        executions: list[OrderExecution] = []

        # Find pending orders for this symbol that can be filled
        orders_to_process = [
            order for order in self.pending_orders.values() if order.symbol == symbol and not order.is_complete()
        ]

        for order in orders_to_process:
            # Check if order can be filled
            if self._can_fill_order(order, price):
                # Schedule fill action with latency
                fill_latency = self._get_fill_latency()
                fill_time = timestamp + fill_latency

                if fill_latency.total_seconds() == 0:
                    # Instant fill
                    execution = self._execute_order(order, price, timestamp)
                    if execution:
                        executions.append(execution)

                    # Move to completed if done
                    if order.is_complete():
                        del self.pending_orders[order.order_id]
                        self.completed_orders[order.order_id] = order
                else:
                    # Delayed fill
                    self.action_queue.add_action(
                        PendingAction(
                            action_type=ActionType.FILL,
                            order_id=order.order_id,
                            scheduled_time=fill_time,
                            data={"price": price, "symbol": symbol},
                        )
                    )

        return executions

    def cancel_order(self, order_id: str, timestamp: datetime | None = None) -> Order | None:
        """Cancel a pending order with latency simulation.

        Args:
            order_id: Order ID to cancel
            timestamp: Current time (defaults to now)

        Returns:
            Order being cancelled, or None if not found
        """
        if timestamp is None:
            timestamp = datetime.now()

        self.current_time = timestamp

        order = self.pending_orders.get(order_id)
        if order is None:
            return None

        # Cancel any pending fill actions for this order
        self.action_queue.cancel_order_actions(order_id)

        # Schedule cancellation with latency
        cancel_time = timestamp + self.latency_config.cancel_latency

        if self.latency_config.cancel_latency.total_seconds() == 0:
            # Instant cancellation
            order.status = OrderStatus.CANCELLED
            order.cancelled_at = timestamp
            del self.pending_orders[order_id]
            self.completed_orders[order_id] = order
        else:
            # Delayed cancellation
            self.action_queue.add_action(
                PendingAction(
                    action_type=ActionType.CANCEL,
                    order_id=order_id,
                    scheduled_time=cancel_time,
                    data={},
                )
            )

        return order

    def get_account_value(self, current_prices: dict[str, Decimal]) -> Decimal:
        """Calculate total account value.

        Args:
            current_prices: Current market prices for all positions

        Returns:
            Total account value (cash + positions)
        """
        position_value = sum(qty * current_prices.get(symbol, Decimal("0")) for symbol, qty in self.positions.items())

        return self.cash + position_value

    def get_order(self, order_id: str) -> Order | None:
        """Get order by ID.

        Args:
            order_id: Order ID

        Returns:
            Order if found, None otherwise
        """
        return self.pending_orders.get(order_id) or self.completed_orders.get(order_id)

    def _process_due_actions(self, current_time: datetime) -> None:
        """Process all actions due by current time.

        Args:
            current_time: Current simulation time
        """
        due_actions = self.action_queue.get_due_actions(current_time)

        for action in due_actions:
            if action.action_type == ActionType.SUBMIT:
                self._process_submit_action(action, current_time)
            elif action.action_type == ActionType.FILL:
                self._process_fill_action(action, current_time)
            elif action.action_type == ActionType.CANCEL:
                self._process_cancel_action(action, current_time)

    def _process_submit_action(self, action: PendingAction, timestamp: datetime) -> None:
        """Process delayed order submission.

        Args:
            action: Submit action
            timestamp: Action processing time (unused, use scheduled_time for accuracy)
        """
        order = action.data["order"]
        order.status = OrderStatus.SUBMITTED
        order.submitted_at = action.scheduled_time
        self.pending_orders[order.order_id] = order

    def _process_fill_action(self, action: PendingAction, timestamp: datetime) -> None:
        """Process delayed order fill.

        Args:
            action: Fill action
            timestamp: Action processing time
        """
        order = self.pending_orders.get(action.order_id)
        if order is None or order.is_complete():
            return

        price = action.data["price"]
        execution = self._execute_order(order, price, timestamp)

        # Move to completed if done
        if execution and order.is_complete():
            del self.pending_orders[action.order_id]
            self.completed_orders[action.order_id] = order

    def _process_cancel_action(self, action: PendingAction, timestamp: datetime) -> None:
        """Process delayed order cancellation.

        Args:
            action: Cancel action
            timestamp: Action processing time (unused, use scheduled_time for accuracy)
        """
        order = self.pending_orders.get(action.order_id)
        if order is None:
            return

        order.status = OrderStatus.CANCELLED
        order.cancelled_at = action.scheduled_time
        del self.pending_orders[action.order_id]
        self.completed_orders[action.order_id] = order

    def _get_fill_latency(self) -> datetime.timedelta:
        """Get fill latency (random between min and max).

        Returns:
            Fill latency timedelta
        """
        min_ms = self.latency_config.fill_latency_min.total_seconds() * 1000
        max_ms = self.latency_config.fill_latency_max.total_seconds() * 1000

        latency_ms = min_ms if min_ms == max_ms else random.uniform(min_ms, max_ms)

        from datetime import timedelta

        return timedelta(milliseconds=latency_ms)

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
