"""Cost model contracts for backtesting fidelity improvements.

This module defines interfaces and base classes for modeling trading costs
in backtests. Cost models are pluggable components that can be configured
to match different execution scenarios.

Default cost models match current backtest behavior (minimal costs) to
maintain parity with legacy implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

import pandas as pd


class CostType(StrEnum):
    """Types of trading costs tracked in backtests."""

    COMMISSION = "commission"  # Brokerage commissions
    SPREAD = "spread"  # Bid-ask spread costs
    SLIPPAGE = "slippage"  # Market impact and execution slippage
    BORROW = "borrow"  # Margin/leverage borrow costs
    MARKET_IMPACT = "market_impact"  # Price impact from large orders


@dataclass(frozen=True, slots=True)
class CostEvent:
    """Single cost event during backtesting.

    Tracks when, where, and how much a cost was incurred.
    """

    timestamp: pd.Timestamp
    symbol: str
    cost_type: CostType
    amount: float  # Dollar amount (always positive)
    basis: str  # Human-readable description of calculation


class CostModel(Protocol):
    """Interface for cost calculation models.

    All cost models must implement this protocol to be used in backtests.
    """

    def calculate_cost(
        self,
        symbol: str,
        quantity: float,
        price: float,
        timestamp: pd.Timestamp,
        **kwargs: object,
    ) -> float:
        """Calculate cost for a trade.

        Args:
            symbol: Ticker symbol
            quantity: Number of shares (can be negative for sells)
            price: Execution price per share
            timestamp: Trade timestamp
            **kwargs: Additional context (e.g., portfolio value, volatility)

        Returns:
            Cost in dollars (always positive, even for sells)
        """
        ...

    def get_name(self) -> str:
        """Return human-readable name of this cost model."""
        ...


@dataclass(frozen=True, slots=True)
class CostSummary:
    """Summary of all costs incurred during a backtest."""

    total_commission: float
    total_spread: float
    total_slippage: float
    total_borrow: float
    total_market_impact: float
    cost_events: tuple[CostEvent, ...] = ()

    @property
    def total_costs(self) -> float:
        """Total of all costs."""
        return (
            self.total_commission
            + self.total_spread
            + self.total_slippage
            + self.total_borrow
            + self.total_market_impact
        )

    def costs_by_type(self) -> dict[CostType, float]:
        """Return costs broken down by type."""
        return {
            CostType.COMMISSION: self.total_commission,
            CostType.SPREAD: self.total_spread,
            CostType.SLIPPAGE: self.total_slippage,
            CostType.BORROW: self.total_borrow,
            CostType.MARKET_IMPACT: self.total_market_impact,
        }

    def costs_by_symbol(self) -> dict[str, float]:
        """Return costs broken down by symbol."""
        symbol_costs: dict[str, float] = {}
        for event in self.cost_events:
            symbol_costs[event.symbol] = symbol_costs.get(event.symbol, 0.0) + event.amount
        return symbol_costs
