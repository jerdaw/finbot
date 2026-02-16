"""Slippage and market impact cost models."""

from __future__ import annotations

import pandas as pd


class ZeroSlippage:
    """Zero slippage model (perfect execution at quoted price).

    This is the default for most backtests, assuming trades execute
    at exactly the expected price with no slippage.
    """

    def calculate_cost(
        self,
        symbol: str,
        quantity: float,
        price: float,
        timestamp: pd.Timestamp,
        **kwargs,
    ) -> float:
        """Calculate slippage cost (always zero)."""
        return 0.0

    def get_name(self) -> str:
        """Return name of this cost model."""
        return "ZeroSlippage"


class FixedSlippage:
    """Fixed slippage model.

    Applies a constant slippage cost as a percentage of trade value.
    Models execution slippage and small market impact.

    Args:
        bps: Slippage in basis points (e.g., 5 = 0.05% slippage)
    """

    def __init__(self, bps: float):
        if bps < 0:
            raise ValueError("bps must be non-negative")
        self.bps = bps
        self.slippage_fraction = bps / 10000.0  # Convert bps to fraction

    def calculate_cost(
        self,
        symbol: str,
        quantity: float,
        price: float,
        timestamp: pd.Timestamp,
        **kwargs,
    ) -> float:
        """Calculate slippage cost based on trade value."""
        trade_value = abs(quantity) * price
        return trade_value * self.slippage_fraction

    def get_name(self) -> str:
        """Return name of this cost model."""
        return f"FixedSlippage({self.bps:.1f} bps)"


class SqrtSlippage:
    """Square-root market impact model.

    Models market impact that scales with the square root of order size.
    This is based on empirical research showing non-linear price impact.

    Args:
        coefficient: Impact coefficient (higher = more impact)
        adv_fraction_threshold: Fraction of ADV above which impact applies

    The cost is calculated as:
        cost = coefficient * trade_value * sqrt(shares / daily_volume)

    References:
        Almgren, R., & Chriss, N. (2001). Optimal execution of portfolio transactions.
    """

    def __init__(self, coefficient: float = 0.1, adv_fraction_threshold: float = 0.01):
        if coefficient < 0:
            raise ValueError("coefficient must be non-negative")
        if adv_fraction_threshold < 0 or adv_fraction_threshold > 1:
            raise ValueError("adv_fraction_threshold must be between 0 and 1")

        self.coefficient = coefficient
        self.adv_fraction_threshold = adv_fraction_threshold

    def calculate_cost(
        self,
        symbol: str,
        quantity: float,
        price: float,
        timestamp: pd.Timestamp,
        **kwargs,
    ) -> float:
        """Calculate market impact using square-root model.

        Requires 'daily_volume' in kwargs to calculate impact.
        If not provided, falls back to zero cost.
        """
        daily_volume = kwargs.get("daily_volume")
        if daily_volume is None or daily_volume == 0:
            # No volume data available, assume zero impact
            return 0.0

        abs_quantity = abs(quantity)
        adv_fraction = abs_quantity / daily_volume

        # Only apply impact if order size exceeds threshold
        if adv_fraction < self.adv_fraction_threshold:
            return 0.0

        # Square-root impact model
        trade_value = abs_quantity * price
        impact_factor = (abs_quantity / daily_volume) ** 0.5
        return self.coefficient * trade_value * impact_factor

    def get_name(self) -> str:
        """Return name of this cost model."""
        return f"SqrtSlippage(coef={self.coefficient:.3f}, threshold={self.adv_fraction_threshold:.2%})"
