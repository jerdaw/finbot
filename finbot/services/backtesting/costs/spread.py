"""Bid-ask spread cost models."""

from __future__ import annotations

import pandas as pd


class ZeroSpread:
    """Zero spread model (assumes mid-price execution).

    This is the default for most backtests, assuming trades execute at
    the quoted price with no spread cost.
    """

    def calculate_cost(
        self,
        symbol: str,
        quantity: float,
        price: float,
        timestamp: pd.Timestamp,
        **kwargs,
    ) -> float:
        """Calculate spread cost (always zero)."""
        return 0.0

    def get_name(self) -> str:
        """Return name of this cost model."""
        return "ZeroSpread"


class FixedSpread:
    """Fixed bid-ask spread model.

    Applies a constant spread cost as a percentage of trade value.
    The spread is paid on both buys (pay the ask) and sells (receive the bid).

    Args:
        bps: Spread in basis points (e.g., 10 = 0.10% spread)

    Example:
        A 10 bps spread means:
        - Buy at ask: pay 0.05% above mid-price
        - Sell at bid: receive 0.05% below mid-price
        - Round-trip cost: 0.10% of trade value
    """

    def __init__(self, bps: float):
        if bps < 0:
            raise ValueError("bps must be non-negative")
        self.bps = bps
        self.spread_fraction = bps / 10000.0  # Convert bps to fraction

    def calculate_cost(
        self,
        symbol: str,
        quantity: float,
        price: float,
        timestamp: pd.Timestamp,
        **kwargs,
    ) -> float:
        """Calculate spread cost based on trade value.

        Spread cost is half the spread (one-way crossing cost).
        """
        trade_value = abs(quantity) * price
        # Pay half the spread (either buying at ask or selling at bid)
        return trade_value * (self.spread_fraction / 2.0)

    def get_name(self) -> str:
        """Return name of this cost model."""
        return f"FixedSpread({self.bps:.1f} bps)"
