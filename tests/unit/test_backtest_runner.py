"""Unit tests for BacktestRunner."""

from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def sample_price_histories():
    """Create sample price histories for backtesting."""
    dates = pd.date_range("2020-01-01", periods=252, freq="B")

    spy = pd.DataFrame(
        {
            "Open": range(100, 352),
            "High": range(101, 353),
            "Low": range(99, 351),
            "Close": range(100, 352),
            "Volume": [1000000] * 252,
        },
        index=dates,
    )
    spy.name = "SPY"

    tqqq = pd.DataFrame(
        {
            "Open": range(50, 302),
            "High": range(51, 303),
            "Low": range(49, 301),
            "Close": range(50, 302),
            "Volume": [500000] * 252,
        },
        index=dates,
    )
    tqqq.name = "TQQQ"

    return {"SPY": spy, "TQQQ": tqqq}


class TestBacktestRunner:
    """Tests for BacktestRunner class."""

    def test_backtest_runner_import(self):
        """Test that BacktestRunner can be imported."""
        from finbot.services.backtesting.backtest_runner import BacktestRunner

        assert BacktestRunner is not None

    def test_backtest_runner_is_class(self):
        """Test that BacktestRunner is a class."""
        from finbot.services.backtesting.backtest_runner import BacktestRunner

        assert isinstance(BacktestRunner, type)


class TestComputeStats:
    """Tests for compute_stats function."""

    def test_compute_stats_import(self):
        """Test that compute_stats can be imported."""
        from finbot.services.backtesting.compute_stats import compute_stats

        assert callable(compute_stats)


class TestBacktestBatch:
    """Tests for backtest_batch function."""

    def test_backtest_batch_import(self):
        """Test that backtest_batch can be imported."""
        from finbot.services.backtesting.backtest_batch import backtest_batch

        assert callable(backtest_batch)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
