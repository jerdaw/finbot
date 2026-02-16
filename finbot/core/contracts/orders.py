"""Order lifecycle contracts for execution tracking.

This module defines contracts for managing order lifecycle from creation
through execution, including state tracking, validation, and rejection handling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from finbot.core.contracts.models import OrderSide, OrderType


class OrderStatus(StrEnum):
    """Order lifecycle status."""

    NEW = "new"  # Created but not submitted
    SUBMITTED = "submitted"  # Sent to broker/simulator
    PARTIALLY_FILLED = "partially_filled"  # Partial execution
    FILLED = "filled"  # Fully executed
    REJECTED = "rejected"  # Rejected by broker/validator
    CANCELLED = "cancelled"  # Cancelled by user/system


class RejectionReason(StrEnum):
    """Reasons for order rejection."""

    INSUFFICIENT_FUNDS = "insufficient_funds"
    INVALID_QUANTITY = "invalid_quantity"
    INVALID_SYMBOL = "invalid_symbol"
    MARKET_CLOSED = "market_closed"
    DUPLICATE_ORDER = "duplicate_order"
    RISK_LIMIT_EXCEEDED = "risk_limit_exceeded"
    RISK_POSITION_LIMIT = "risk_position_limit"
    RISK_EXPOSURE_LIMIT = "risk_exposure_limit"
    RISK_DRAWDOWN_LIMIT = "risk_drawdown_limit"
    RISK_TRADING_DISABLED = "risk_trading_disabled"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class OrderExecution:
    """Record of an order execution (fill).

    Attributes:
        execution_id: Unique execution identifier
        order_id: Parent order identifier
        timestamp: Execution timestamp
        quantity: Quantity filled
        price: Fill price
        commission: Commission paid
        is_partial: Whether this is a partial fill
    """

    execution_id: str
    order_id: str
    timestamp: datetime
    quantity: Decimal
    price: Decimal
    commission: Decimal
    is_partial: bool


@dataclass
class Order:
    """Mutable order with lifecycle tracking.

    Attributes:
        order_id: Unique order identifier
        symbol: Trading symbol
        side: Order side (BUY/SELL)
        order_type: Order type (MARKET/LIMIT)
        quantity: Order quantity
        created_at: Creation timestamp
        status: Current order status
        limit_price: Limit price for limit orders
        submitted_at: Submission timestamp
        filled_quantity: Total quantity filled
        avg_fill_price: Average fill price
        total_commission: Total commission paid
        executions: List of individual fills
        rejected_at: Rejection timestamp
        rejection_reason: Rejection reason code
        rejection_message: Human-readable rejection message
        cancelled_at: Cancellation timestamp
    """

    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    created_at: datetime

    status: OrderStatus = OrderStatus.NEW

    # Optional: limit price for limit orders
    limit_price: Decimal | None = None

    # Execution tracking
    submitted_at: datetime | None = None
    filled_quantity: Decimal = Decimal("0")
    avg_fill_price: Decimal = Decimal("0")
    total_commission: Decimal = Decimal("0")
    executions: list[OrderExecution] = field(default_factory=list)

    # Rejection tracking
    rejected_at: datetime | None = None
    rejection_reason: RejectionReason | None = None
    rejection_message: str | None = None

    # Cancellation tracking
    cancelled_at: datetime | None = None

    def is_complete(self) -> bool:
        """Check if order is in a terminal state."""
        return self.status in {OrderStatus.FILLED, OrderStatus.REJECTED, OrderStatus.CANCELLED}

    def remaining_quantity(self) -> Decimal:
        """Calculate remaining unfilled quantity."""
        return self.quantity - self.filled_quantity

    def add_execution(self, execution: OrderExecution) -> None:
        """Add execution and update fill tracking.

        Args:
            execution: Order execution to add
        """
        self.executions.append(execution)
        self.filled_quantity += execution.quantity
        self.total_commission += execution.commission

        # Update average fill price
        if self.filled_quantity > 0:
            total_value = sum(e.quantity * e.price for e in self.executions)
            self.avg_fill_price = total_value / self.filled_quantity

        # Update status
        if self.filled_quantity >= self.quantity:
            self.status = OrderStatus.FILLED
        elif self.filled_quantity > 0:
            self.status = OrderStatus.PARTIALLY_FILLED
