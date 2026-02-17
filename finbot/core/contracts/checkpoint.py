"""Checkpoint contracts for ExecutionSimulator state persistence.

This module defines contracts for saving and restoring execution state,
enabling system restarts, disaster recovery, and state replay.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from finbot.core.contracts.orders import Order

# Checkpoint schema version
CHECKPOINT_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class ExecutionCheckpoint:
    """Snapshot of ExecutionSimulator state for persistence.

    Attributes:
        version: Checkpoint schema version
        simulator_id: Unique simulator identifier
        checkpoint_timestamp: When checkpoint was created
        cash: Current cash balance
        initial_cash: Initial cash balance (for reference)
        positions: Current positions {symbol: quantity}
        pending_orders: Orders not yet complete
        completed_orders: Order history
        peak_value: All-time peak portfolio value (for risk tracking)
        daily_start_value: Daily start value (for risk tracking)
        trading_enabled: Kill-switch state
        slippage_bps: Slippage configuration
        commission_per_share: Commission configuration
        latency_config_name: Latency profile name (INSTANT/FAST/NORMAL/SLOW)
        risk_config_data: Risk configuration as dict (optional)

    Example:
        >>> checkpoint = ExecutionCheckpoint(
        ...     version=CHECKPOINT_VERSION,
        ...     simulator_id="sim-12345",
        ...     checkpoint_timestamp=datetime.now(),
        ...     cash=Decimal("95000"),
        ...     initial_cash=Decimal("100000"),
        ...     positions={"SPY": Decimal("100")},
        ...     pending_orders=[],
        ...     completed_orders=[],
        ... )
    """

    # Metadata
    version: str
    simulator_id: str
    checkpoint_timestamp: datetime

    # Account state
    cash: Decimal
    initial_cash: Decimal
    positions: dict[str, Decimal]

    # Orders
    pending_orders: list[Order]
    completed_orders: list[Order]

    # Risk state (optional, only if risk controls enabled)
    peak_value: Decimal | None = None
    daily_start_value: Decimal | None = None
    trading_enabled: bool = True

    # Configuration
    slippage_bps: Decimal = Decimal("5")
    commission_per_share: Decimal = Decimal("0")
    latency_config_name: str = "INSTANT"
    risk_config_data: dict | None = None
