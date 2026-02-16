"""Market regime detection models for backtesting analysis."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

import pandas as pd


class MarketRegime(StrEnum):
    """Market regime classifications.

    Regimes help understand strategy performance in different market conditions.
    """

    BULL = "bull"
    """Strong upward trend - sustained positive returns."""

    BEAR = "bear"
    """Downward trend - sustained negative returns."""

    SIDEWAYS = "sideways"
    """Range-bound - low absolute returns, moderate volatility."""

    VOLATILE = "volatile"
    """High volatility - large price swings regardless of direction."""


@dataclass(frozen=True, slots=True)
class RegimeConfig:
    """Configuration for regime detection.

    Attributes:
        bull_threshold: Annual return threshold for bull regime (e.g., 0.15 = 15%)
        bear_threshold: Annual return threshold for bear regime (e.g., -0.10 = -10%)
        volatility_threshold: Annual volatility threshold for volatile regime (e.g., 0.25 = 25%)
        lookback_days: Rolling window for calculating returns/volatility
    """

    bull_threshold: float = 0.15
    bear_threshold: float = -0.10
    volatility_threshold: float = 0.25
    lookback_days: int = 252  # ~1 year of trading days

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.bull_threshold <= 0:
            raise ValueError(f"bull_threshold must be positive, got {self.bull_threshold}")
        if self.bear_threshold >= 0:
            raise ValueError(f"bear_threshold must be negative, got {self.bear_threshold}")
        if self.volatility_threshold <= 0:
            raise ValueError(f"volatility_threshold must be positive, got {self.volatility_threshold}")
        if self.lookback_days <= 0:
            raise ValueError(f"lookback_days must be positive, got {self.lookback_days}")


@dataclass(frozen=True, slots=True)
class RegimePeriod:
    """A detected market regime period.

    Attributes:
        regime: Classified regime
        start: Start date of regime period
        end: End date of regime period (inclusive)
        market_return: Annualized return during this period
        market_volatility: Annualized volatility during this period
    """

    regime: MarketRegime
    start: pd.Timestamp
    end: pd.Timestamp
    market_return: float
    market_volatility: float

    def __post_init__(self) -> None:
        """Validate period dates."""
        if self.start >= self.end:
            raise ValueError(f"start must be before end: {self.start} >= {self.end}")


@dataclass(frozen=True, slots=True)
class RegimeMetrics:
    """Performance metrics for a specific market regime.

    Attributes:
        regime: Market regime classification
        count_periods: Number of detected periods for this regime
        total_days: Total trading days in this regime
        metrics: Same metrics as BacktestRunResult (CAGR, Sharpe, etc.)
    """

    regime: MarketRegime
    count_periods: int
    total_days: int
    metrics: dict[str, float]

    def __post_init__(self) -> None:
        """Validate metrics."""
        if self.count_periods < 0:
            raise ValueError(f"count_periods must be non-negative, got {self.count_periods}")
        if self.total_days < 0:
            raise ValueError(f"total_days must be non-negative, got {self.total_days}")


class RegimeDetector(Protocol):
    """Protocol for regime detection implementations.

    Allows custom regime detection strategies while maintaining
    a consistent interface.
    """

    def detect(
        self,
        market_data: pd.DataFrame,
        config: RegimeConfig | None = None,
    ) -> list[RegimePeriod]:
        """Detect market regimes in historical data.

        Args:
            market_data: DataFrame with DatetimeIndex and 'Close' or 'Adj Close' column
            config: Optional regime detection configuration (uses defaults if None)

        Returns:
            List of detected regime periods in chronological order

        Raises:
            ValueError: If market_data is invalid or missing required columns
        """
        ...
