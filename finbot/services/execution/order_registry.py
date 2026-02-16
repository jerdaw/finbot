"""Persistent storage for order history."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from finbot.core.contracts.models import OrderSide, OrderType
from finbot.core.contracts.orders import Order, OrderExecution, OrderStatus, RejectionReason


class OrderRegistry:
    """Persistent storage for order history.

    Orders are stored as JSON files organized by date:
    - storage_dir/YYYY/MM/DD/order-id.json

    Features:
    - Save and load individual orders
    - Query orders by symbol, status, date range
    - Retrieve execution history
    """

    def __init__(self, storage_dir: Path | str):
        """Initialize order registry.

        Args:
            storage_dir: Directory for storing order files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_order(self, order: Order) -> Path:
        """Save order to registry.

        Args:
            order: Order to save

        Returns:
            Path to saved order file
        """
        # Organize by date: YYYY/MM/DD/order-id.json
        year = order.created_at.year
        month = f"{order.created_at.month:02d}"
        day = f"{order.created_at.day:02d}"

        order_dir = self.storage_dir / str(year) / month / day
        order_dir.mkdir(parents=True, exist_ok=True)

        order_path = order_dir / f"{order.order_id}.json"

        # Serialize order
        order_data = self._serialize_order(order)

        with order_path.open("w") as f:
            json.dump(order_data, f, indent=2)

        return order_path

    def load_order(self, order_id: str) -> Order:
        """Load order by ID.

        Args:
            order_id: Order ID to load

        Returns:
            Loaded order

        Raises:
            FileNotFoundError: If order not found
        """
        # Search all date directories
        for order_path in self.storage_dir.rglob(f"{order_id}.json"):
            with order_path.open() as f:
                order_data = json.load(f)
            return self._deserialize_order(order_data)

        msg = f"Order {order_id} not found"
        raise FileNotFoundError(msg)

    def list_orders(
        self,
        symbol: str | None = None,
        status: OrderStatus | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int | None = None,
    ) -> list[Order]:
        """List orders matching criteria.

        Args:
            symbol: Filter by symbol
            status: Filter by status
            since: Filter orders created after this date
            until: Filter orders created before this date
            limit: Maximum number of orders to return

        Returns:
            List of matching orders, sorted by creation date (newest first)
        """
        orders: list[Order] = []

        # Iterate through all order files
        for order_path in sorted(self.storage_dir.rglob("*.json"), reverse=True):
            if limit and len(orders) >= limit:
                break

            try:
                with order_path.open() as f:
                    order_data = json.load(f)
                order = self._deserialize_order(order_data)

                # Apply filters
                if symbol and order.symbol != symbol:
                    continue
                if status and order.status != status:
                    continue
                if since and order.created_at < since:
                    continue
                if until and order.created_at > until:
                    continue

                orders.append(order)
            except (json.JSONDecodeError, KeyError):
                # Skip invalid files
                continue

        return orders

    def get_executions(self, order_id: str) -> list[OrderExecution]:
        """Get all executions for an order.

        Args:
            order_id: Order ID

        Returns:
            List of executions for this order
        """
        order = self.load_order(order_id)
        return order.executions

    def delete_order(self, order_id: str) -> bool:
        """Delete order from registry.

        Args:
            order_id: Order ID to delete

        Returns:
            True if deleted, False if not found
        """
        for order_path in self.storage_dir.rglob(f"{order_id}.json"):
            order_path.unlink()
            return True
        return False

    def _serialize_order(self, order: Order) -> dict:
        """Serialize order to JSON-compatible dict.

        Args:
            order: Order to serialize

        Returns:
            Serialized order data
        """
        return {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side.value,
            "order_type": order.order_type.value,
            "quantity": str(order.quantity),
            "created_at": order.created_at.isoformat(),
            "status": order.status.value,
            "limit_price": str(order.limit_price) if order.limit_price is not None else None,
            "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
            "filled_quantity": str(order.filled_quantity),
            "avg_fill_price": str(order.avg_fill_price),
            "total_commission": str(order.total_commission),
            "executions": [self._serialize_execution(e) for e in order.executions],
            "rejected_at": order.rejected_at.isoformat() if order.rejected_at else None,
            "rejection_reason": order.rejection_reason.value if order.rejection_reason else None,
            "rejection_message": order.rejection_message,
            "cancelled_at": order.cancelled_at.isoformat() if order.cancelled_at else None,
        }

    def _serialize_execution(self, execution: OrderExecution) -> dict:
        """Serialize execution to JSON-compatible dict.

        Args:
            execution: Execution to serialize

        Returns:
            Serialized execution data
        """
        return {
            "execution_id": execution.execution_id,
            "order_id": execution.order_id,
            "timestamp": execution.timestamp.isoformat(),
            "quantity": str(execution.quantity),
            "price": str(execution.price),
            "commission": str(execution.commission),
            "is_partial": execution.is_partial,
        }

    def _deserialize_order(self, data: dict) -> Order:
        """Deserialize order from JSON data.

        Args:
            data: Serialized order data

        Returns:
            Deserialized order
        """
        return Order(
            order_id=data["order_id"],
            symbol=data["symbol"],
            side=OrderSide(data["side"]),
            order_type=OrderType(data["order_type"]),
            quantity=Decimal(data["quantity"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            status=OrderStatus(data["status"]),
            limit_price=Decimal(data["limit_price"]) if data["limit_price"] is not None else None,
            submitted_at=datetime.fromisoformat(data["submitted_at"]) if data["submitted_at"] else None,
            filled_quantity=Decimal(data["filled_quantity"]),
            avg_fill_price=Decimal(data["avg_fill_price"]),
            total_commission=Decimal(data["total_commission"]),
            executions=[self._deserialize_execution(e) for e in data["executions"]],
            rejected_at=datetime.fromisoformat(data["rejected_at"]) if data["rejected_at"] else None,
            rejection_reason=RejectionReason(data["rejection_reason"]) if data["rejection_reason"] else None,
            rejection_message=data["rejection_message"],
            cancelled_at=datetime.fromisoformat(data["cancelled_at"]) if data["cancelled_at"] else None,
        )

    def _deserialize_execution(self, data: dict) -> OrderExecution:
        """Deserialize execution from JSON data.

        Args:
            data: Serialized execution data

        Returns:
            Deserialized execution
        """
        return OrderExecution(
            execution_id=data["execution_id"],
            order_id=data["order_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            quantity=Decimal(data["quantity"]),
            price=Decimal(data["price"]),
            commission=Decimal(data["commission"]),
            is_partial=data["is_partial"],
        )
