"""Canonical data contracts for backtesting and execution workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

import pandas as pd

from finbot.core.contracts.versioning import BACKTEST_RESULT_SCHEMA_VERSION


class OrderSide(StrEnum):
    """Supported order sides."""

    BUY = "buy"
    SELL = "sell"


class OrderType(StrEnum):
    """Supported order types."""

    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"


@dataclass(frozen=True, slots=True)
class BarEvent:
    """Single market data bar event."""

    symbol: str
    timestamp: pd.Timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float
    adj_close: float | None = None


@dataclass(frozen=True, slots=True)
class OrderRequest:
    """Engine-agnostic order request."""

    order_id: str
    timestamp: pd.Timestamp
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType = OrderType.MARKET
    limit_price: float | None = None
    stop_price: float | None = None
    tags: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class FillEvent:
    """Executed fill details."""

    order_id: str
    timestamp: pd.Timestamp
    symbol: str
    side: OrderSide
    quantity: float
    fill_price: float
    commission: float = 0.0
    slippage: float = 0.0


@dataclass(frozen=True, slots=True)
class PortfolioSnapshot:
    """Portfolio/account state at a point in time."""

    timestamp: pd.Timestamp
    cash: float
    equity: float
    gross_exposure: float
    net_exposure: float
    positions: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class BacktestRunRequest:
    """Canonical backtest run request payload."""

    strategy_name: str
    symbols: tuple[str, ...]
    start: pd.Timestamp | None
    end: pd.Timestamp | None
    initial_cash: float
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class BacktestRunMetadata:
    """Immutable metadata recorded for every run."""

    run_id: str
    engine_name: str
    engine_version: str
    strategy_name: str
    created_at: datetime
    config_hash: str
    data_snapshot_id: str
    random_seed: int | None = None


@dataclass(frozen=True, slots=True)
class BacktestRunResult:
    """Canonical run output contract shared across engines."""

    metadata: BacktestRunMetadata
    metrics: dict[str, float]
    schema_version: str = BACKTEST_RESULT_SCHEMA_VERSION
    assumptions: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
