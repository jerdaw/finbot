"""Commission cost models."""

from __future__ import annotations

import pandas as pd


class ZeroCommission:
    """Zero commission model (free trading).

    Use this for testing or for brokers with zero-commission trading.
    """

    def calculate_cost(
        self,
        symbol: str,
        quantity: float,
        price: float,
        timestamp: pd.Timestamp,
        **kwargs: object,
    ) -> float:
        """Calculate commission cost (always zero)."""
        return 0.0

    def get_name(self) -> str:
        """Return name of this cost model."""
        return "ZeroCommission"


class FlatCommission:
    """Flat per-share commission model.

    This matches the current FixedCommissionScheme behavior in Backtrader.
    Default rate of $0.001 per share is typical for modern discount brokers.

    Args:
        per_share: Commission per share (default: $0.001)
        min_commission: Minimum commission per trade (default: $0)
    """

    def __init__(self, per_share: float = 0.001, min_commission: float = 0.0):
        if per_share < 0:
            raise ValueError("per_share must be non-negative")
        if min_commission < 0:
            raise ValueError("min_commission must be non-negative")

        self.per_share = per_share
        self.min_commission = min_commission

    def calculate_cost(
        self,
        symbol: str,
        quantity: float,
        price: float,
        timestamp: pd.Timestamp,
        **kwargs: object,
    ) -> float:
        """Calculate commission cost based on share quantity."""
        cost = abs(quantity) * self.per_share
        return max(cost, self.min_commission)

    def get_name(self) -> str:
        """Return name of this cost model."""
        return f"FlatCommission(${self.per_share:.4f}/share, min=${self.min_commission:.2f})"


class PercentageCommission:
    """Percentage-based commission model.

    Charges a percentage of trade value, subject to minimum commission.

    Args:
        rate: Commission as fraction of trade value (e.g., 0.001 = 0.1%)
        min_commission: Minimum commission per trade (default: $0)
        max_commission: Maximum commission per trade (default: no limit)
    """

    def __init__(
        self,
        rate: float,
        min_commission: float = 0.0,
        max_commission: float | None = None,
    ):
        if rate < 0:
            raise ValueError("rate must be non-negative")
        if min_commission < 0:
            raise ValueError("min_commission must be non-negative")
        if max_commission is not None and max_commission < min_commission:
            raise ValueError("max_commission must be >= min_commission")

        self.rate = rate
        self.min_commission = min_commission
        self.max_commission = max_commission

    def calculate_cost(
        self,
        symbol: str,
        quantity: float,
        price: float,
        timestamp: pd.Timestamp,
        **kwargs: object,
    ) -> float:
        """Calculate commission cost as percentage of trade value."""
        trade_value = abs(quantity) * price
        cost = trade_value * self.rate

        # Apply min/max bounds
        cost = max(cost, self.min_commission)
        if self.max_commission is not None:
            cost = min(cost, self.max_commission)

        return cost

    def get_name(self) -> str:
        """Return name of this cost model."""
        max_str = f", max=${self.max_commission:.2f}" if self.max_commission else ""
        return f"PercentageCommission({self.rate:.4%}, min=${self.min_commission:.2f}{max_str})"
