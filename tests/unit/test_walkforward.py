"""Unit tests for walk-forward testing functionality."""

from __future__ import annotations

import pandas as pd
import pytest

from finbot.core.contracts import BacktestRunRequest, WalkForwardConfig
from finbot.services.backtesting.adapters.backtrader_adapter import BacktraderAdapter
from finbot.services.backtesting.walkforward import generate_windows, run_walk_forward


def test_walkforward_config_validation():
    """Test WalkForwardConfig validation."""
    # Valid config
    config = WalkForwardConfig(train_window=100, test_window=20, step_size=10)
    assert config.train_window == 100
    assert config.test_window == 20
    assert config.step_size == 10
    assert config.anchored is False

    # Invalid train_window
    with pytest.raises(ValueError, match="train_window must be positive"):
        WalkForwardConfig(train_window=0, test_window=20, step_size=10)

    # Invalid test_window
    with pytest.raises(ValueError, match="test_window must be positive"):
        WalkForwardConfig(train_window=100, test_window=-5, step_size=10)

    # Invalid step_size
    with pytest.raises(ValueError, match="step_size must be positive"):
        WalkForwardConfig(train_window=100, test_window=20, step_size=0)


def test_generate_windows_rolling():
    """Test rolling window generation."""
    start = pd.Timestamp("2020-01-01")
    end = pd.Timestamp("2020-12-31")
    config = WalkForwardConfig(train_window=100, test_window=20, step_size=20, anchored=False)

    windows = generate_windows(start, end, config)

    # Should have multiple windows
    assert len(windows) > 0

    # Check first window
    assert windows[0].window_id == 0
    assert windows[0].train_end < windows[0].test_start

    # Check window IDs are sequential
    for i, window in enumerate(windows):
        assert window.window_id == i


def test_generate_windows_anchored():
    """Test anchored (expanding) window generation."""
    start = pd.Timestamp("2020-01-01")
    end = pd.Timestamp("2020-12-31")
    config = WalkForwardConfig(train_window=100, test_window=20, step_size=20, anchored=True)

    windows = generate_windows(start, end, config)

    # Should have multiple windows
    assert len(windows) > 0

    # All windows should have same train_start (anchored)
    first_train_start = windows[0].train_start
    for window in windows:
        assert window.train_start == first_train_start

    # Train windows should expand
    for i in range(1, len(windows)):
        assert windows[i].train_end > windows[i - 1].train_end


def test_generate_windows_insufficient_data():
    """Test error when insufficient data for windows."""
    start = pd.Timestamp("2020-01-01")
    end = pd.Timestamp("2020-01-31")  # Only ~23 business days
    config = WalkForwardConfig(train_window=100, test_window=20, step_size=10)

    with pytest.raises(ValueError, match="Insufficient data"):
        generate_windows(start, end, config)


def test_run_walk_forward_basic():
    """Test basic walk-forward execution."""
    # Create simple price data
    dates = pd.bdate_range("2020-01-01", periods=200)
    prices = pd.Series(range(100, 300), index=dates)

    df = pd.DataFrame(
        {
            "Open": prices * 0.99,
            "High": prices * 1.01,
            "Low": prices * 0.98,
            "Close": prices,
            "Adj Close": prices,
            "Volume": 1000000,
        }
    )

    # Create adapter
    adapter = BacktraderAdapter(price_histories={"STOCK": df})

    # Create walk-forward config
    config = WalkForwardConfig(train_window=50, test_window=20, step_size=20, anchored=False)

    # Create request
    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("STOCK",),
        start=dates[0],
        end=dates[-1],
        initial_cash=10000.0,
        parameters={"equity_proportions": [1.0]},
    )

    # Run walk-forward
    result = run_walk_forward(adapter, request, config, include_train=False)

    # Verify results
    assert len(result.windows) > 0
    assert len(result.test_results) == len(result.windows)
    assert len(result.train_results) == 0  # include_train=False
    assert "cagr_mean" in result.summary_metrics
    assert result.summary_metrics["window_count"] == len(result.windows)


def test_run_walk_forward_with_train():
    """Test walk-forward with training results included."""
    # Create simple price data
    dates = pd.bdate_range("2020-01-01", periods=150)
    prices = pd.Series(range(100, 250), index=dates)

    df = pd.DataFrame(
        {
            "Open": prices * 0.99,
            "High": prices * 1.01,
            "Low": prices * 0.98,
            "Close": prices,
            "Adj Close": prices,
            "Volume": 1000000,
        }
    )

    # Create adapter
    adapter = BacktraderAdapter(price_histories={"STOCK": df})

    # Create walk-forward config
    config = WalkForwardConfig(train_window=50, test_window=20, step_size=30, anchored=False)

    # Create request
    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("STOCK",),
        start=dates[0],
        end=dates[-1],
        initial_cash=10000.0,
        parameters={"equity_proportions": [1.0]},
    )

    # Run walk-forward with training
    result = run_walk_forward(adapter, request, config, include_train=True)

    # Verify results
    assert len(result.windows) > 0
    assert len(result.test_results) == len(result.windows)
    assert len(result.train_results) == len(result.windows)  # include_train=True

    # Each train and test result should have metrics
    for train_result in result.train_results:
        assert "cagr" in train_result.metrics
    for test_result in result.test_results:
        assert "cagr" in test_result.metrics


def test_run_walk_forward_no_dates_error():
    """Test error when request doesn't have explicit dates."""
    df = pd.DataFrame(
        {
            "Open": [100],
            "High": [101],
            "Low": [99],
            "Close": [100],
            "Adj Close": [100],
            "Volume": 1000000,
        },
        index=pd.DatetimeIndex(["2020-01-01"]),
    )

    adapter = BacktraderAdapter(price_histories={"STOCK": df})
    config = WalkForwardConfig(train_window=50, test_window=20, step_size=10)

    # Request without dates
    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("STOCK",),
        start=None,  # Missing
        end=None,  # Missing
        initial_cash=10000.0,
        parameters={"equity_proportions": [1.0]},
    )

    with pytest.raises(ValueError, match="Walk-forward requires explicit start and end dates"):
        run_walk_forward(adapter, request, config)


def test_summary_metrics_calculation():
    """Test that summary metrics are calculated correctly."""
    dates = pd.bdate_range("2020-01-01", periods=200)
    prices = pd.Series(range(100, 300), index=dates)

    df = pd.DataFrame(
        {
            "Open": prices * 0.99,
            "High": prices * 1.01,
            "Low": prices * 0.98,
            "Close": prices,
            "Adj Close": prices,
            "Volume": 1000000,
        }
    )

    adapter = BacktraderAdapter(price_histories={"STOCK": df})
    config = WalkForwardConfig(train_window=50, test_window=20, step_size=20, anchored=False)

    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("STOCK",),
        start=dates[0],
        end=dates[-1],
        initial_cash=10000.0,
        parameters={"equity_proportions": [1.0]},
    )

    result = run_walk_forward(adapter, request, config)

    # Check summary metrics structure
    assert "cagr_mean" in result.summary_metrics
    assert "cagr_min" in result.summary_metrics
    assert "cagr_max" in result.summary_metrics
    assert "cagr_std" in result.summary_metrics
    assert "sharpe_mean" in result.summary_metrics
    assert "window_count" in result.summary_metrics

    # Verify values make sense
    assert result.summary_metrics["cagr_min"] <= result.summary_metrics["cagr_mean"]
    assert result.summary_metrics["cagr_mean"] <= result.summary_metrics["cagr_max"]
    assert result.summary_metrics["cagr_std"] >= 0


def test_window_dates_validation():
    """Test that generated windows have valid date ranges."""
    start = pd.Timestamp("2020-01-01")
    end = pd.Timestamp("2020-12-31")
    config = WalkForwardConfig(train_window=50, test_window=20, step_size=15)

    windows = generate_windows(start, end, config)

    for window in windows:
        # Train period valid
        assert window.train_start < window.train_end

        # Test period valid
        assert window.test_start < window.test_end

        # Test starts after train ends (or on same day)
        assert window.test_start >= window.train_end

        # All dates within overall range
        assert window.train_start >= start
        assert window.test_end <= end
