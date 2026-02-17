"""Serialization helpers for checkpoint persistence."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from finbot.core.contracts.checkpoint import ExecutionCheckpoint
from finbot.core.contracts.models import OrderSide, OrderType
from finbot.core.contracts.orders import Order, OrderExecution, OrderStatus, RejectionReason


def serialize_checkpoint(checkpoint: ExecutionCheckpoint) -> dict:
    """Convert checkpoint to JSON-compatible dict.

    Args:
        checkpoint: Checkpoint to serialize

    Returns:
        JSON-compatible dictionary
    """
    return {
        "version": checkpoint.version,
        "simulator_id": checkpoint.simulator_id,
        "checkpoint_timestamp": checkpoint.checkpoint_timestamp.isoformat(),
        "cash": str(checkpoint.cash),
        "initial_cash": str(checkpoint.initial_cash),
        "positions": {symbol: str(qty) for symbol, qty in checkpoint.positions.items()},
        "pending_orders": [_serialize_order(order) for order in checkpoint.pending_orders],
        "completed_orders": [_serialize_order(order) for order in checkpoint.completed_orders],
        "peak_value": str(checkpoint.peak_value) if checkpoint.peak_value is not None else None,
        "daily_start_value": str(checkpoint.daily_start_value) if checkpoint.daily_start_value is not None else None,
        "trading_enabled": checkpoint.trading_enabled,
        "slippage_bps": str(checkpoint.slippage_bps),
        "commission_per_share": str(checkpoint.commission_per_share),
        "latency_config_name": checkpoint.latency_config_name,
        "risk_config_data": checkpoint.risk_config_data,
    }


def deserialize_checkpoint(data: dict) -> ExecutionCheckpoint:
    """Convert dict to ExecutionCheckpoint.

    Args:
        data: Serialized checkpoint data

    Returns:
        ExecutionCheckpoint instance
    """
    return ExecutionCheckpoint(
        version=data["version"],
        simulator_id=data["simulator_id"],
        checkpoint_timestamp=datetime.fromisoformat(data["checkpoint_timestamp"]),
        cash=Decimal(data["cash"]),
        initial_cash=Decimal(data["initial_cash"]),
        positions={symbol: Decimal(qty) for symbol, qty in data["positions"].items()},
        pending_orders=[_deserialize_order(order_data) for order_data in data["pending_orders"]],
        completed_orders=[_deserialize_order(order_data) for order_data in data["completed_orders"]],
        peak_value=Decimal(data["peak_value"]) if data.get("peak_value") is not None else None,
        daily_start_value=Decimal(data["daily_start_value"]) if data.get("daily_start_value") is not None else None,
        trading_enabled=data.get("trading_enabled", True),
        slippage_bps=Decimal(data.get("slippage_bps", "5")),
        commission_per_share=Decimal(data.get("commission_per_share", "0")),
        latency_config_name=data.get("latency_config_name", "INSTANT"),
        risk_config_data=data.get("risk_config_data"),
    )


def _serialize_order(order: Order) -> dict:
    """Serialize Order to dict.

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
        "executions": [_serialize_execution(e) for e in order.executions],
        "rejected_at": order.rejected_at.isoformat() if order.rejected_at else None,
        "rejection_reason": order.rejection_reason.value if order.rejection_reason else None,
        "rejection_message": order.rejection_message,
        "cancelled_at": order.cancelled_at.isoformat() if order.cancelled_at else None,
    }


def _deserialize_order(data: dict) -> Order:
    """Deserialize Order from dict.

    Args:
        data: Serialized order data

    Returns:
        Order instance
    """
    order = Order(
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
        executions=[_deserialize_execution(e) for e in data["executions"]],
        rejected_at=datetime.fromisoformat(data["rejected_at"]) if data["rejected_at"] else None,
        rejection_reason=RejectionReason(data["rejection_reason"]) if data["rejection_reason"] else None,
        rejection_message=data["rejection_message"],
        cancelled_at=datetime.fromisoformat(data["cancelled_at"]) if data["cancelled_at"] else None,
    )
    return order


def _serialize_execution(execution: OrderExecution) -> dict:
    """Serialize OrderExecution to dict.

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


def _deserialize_execution(data: dict) -> OrderExecution:
    """Deserialize OrderExecution from dict.

    Args:
        data: Serialized execution data

    Returns:
        OrderExecution instance
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
