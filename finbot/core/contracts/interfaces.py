"""Protocol interfaces for engine-agnostic platform integrations."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import pandas as pd

from finbot.core.contracts.models import (
    BacktestRunRequest,
    BacktestRunResult,
    BarEvent,
    FillEvent,
    OrderRequest,
    PortfolioSnapshot,
)


@runtime_checkable
class MarketDataProvider(Protocol):
    """Provides price/event data for backtests or live/paper execution."""

    def get_bars(
        self,
        symbol: str,
        start: pd.Timestamp | None = None,
        end: pd.Timestamp | None = None,
        timeframe: str = "1d",
    ) -> pd.DataFrame:
        """Return bars for a symbol and window."""


@runtime_checkable
class ExecutionSimulator(Protocol):
    """Converts order requests into fills given market context."""

    def simulate_fill(self, order: OrderRequest, bar: BarEvent) -> FillEvent:
        """Simulate a fill for an order on the given bar."""


@runtime_checkable
class PortfolioStateStore(Protocol):
    """Tracks and mutates portfolio state during a run."""

    def snapshot(self) -> PortfolioSnapshot:
        """Return the current portfolio snapshot."""

    def apply_fill(self, fill: FillEvent) -> PortfolioSnapshot:
        """Apply a fill and return the new snapshot."""


@runtime_checkable
class BacktestEngine(Protocol):
    """Engine interface for running contract-based backtests."""

    def run(self, request: BacktestRunRequest) -> BacktestRunResult:
        """Execute a backtest and return canonical run results."""
