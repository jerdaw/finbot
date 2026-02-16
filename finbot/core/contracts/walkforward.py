"""Walk-forward testing models and utilities for backtesting."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from finbot.core.contracts.models import BacktestRunResult


@dataclass(frozen=True, slots=True)
class WalkForwardConfig:
    """Configuration for walk-forward analysis.

    Attributes:
        train_window: Number of trading days in training period
        test_window: Number of trading days in test period
        step_size: Number of trading days to move forward each iteration
        anchored: If True, use expanding window (train start fixed);
                 if False, use rolling window (train start moves)
    """

    train_window: int
    test_window: int
    step_size: int
    anchored: bool = False

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.train_window <= 0:
            raise ValueError(f"train_window must be positive, got {self.train_window}")
        if self.test_window <= 0:
            raise ValueError(f"test_window must be positive, got {self.test_window}")
        if self.step_size <= 0:
            raise ValueError(f"step_size must be positive, got {self.step_size}")


@dataclass(frozen=True, slots=True)
class WalkForwardWindow:
    """A single walk-forward window with train and test periods.

    Attributes:
        window_id: Sequential identifier for this window (0-indexed)
        train_start: Start date of training period
        train_end: End date of training period (inclusive)
        test_start: Start date of test period
        test_end: End date of test period (inclusive)
    """

    window_id: int
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp

    def __post_init__(self) -> None:
        """Validate window dates."""
        if self.train_start >= self.train_end:
            raise ValueError(f"train_start must be before train_end: {self.train_start} >= {self.train_end}")
        if self.test_start >= self.test_end:
            raise ValueError(f"test_start must be before test_end: {self.test_start} >= {self.test_end}")
        # Test should start after train ends (but allow same day in case of gaps)
        if self.test_start < self.train_end:
            raise ValueError(f"test_start must be >= train_end: {self.test_start} < {self.train_end}")


@dataclass(frozen=True, slots=True)
class WalkForwardResult:
    """Results from walk-forward analysis.

    Attributes:
        config: Walk-forward configuration used
        windows: Tuple of windows tested
        train_results: Backtest results for training periods (optional)
        test_results: Backtest results for test (out-of-sample) periods
        summary_metrics: Aggregated metrics across all test windows
    """

    config: WalkForwardConfig
    windows: tuple[WalkForwardWindow, ...]
    test_results: tuple[BacktestRunResult, ...]
    summary_metrics: dict[str, float]
    train_results: tuple[BacktestRunResult, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Validate results."""
        if len(self.windows) != len(self.test_results):
            raise ValueError(
                f"Number of windows ({len(self.windows)}) must match number of test results ({len(self.test_results)})"
            )
        if self.train_results and len(self.windows) != len(self.train_results):
            raise ValueError(
                f"Number of windows ({len(self.windows)}) must match "
                f"number of train results ({len(self.train_results)})"
            )
