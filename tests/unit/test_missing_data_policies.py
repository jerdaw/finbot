"""Unit tests for missing data policy handling."""

from __future__ import annotations

import pandas as pd
import pytest

from finbot.core.contracts import (
    DEFAULT_MISSING_DATA_POLICY,
    BacktestRunRequest,
    MissingDataPolicy,
)
from finbot.services.backtesting.adapters.backtrader_adapter import BacktraderAdapter


def create_price_data_with_gaps(
    n_days: int = 100,
    gap_start: int = 40,
    gap_end: int = 45,
) -> pd.DataFrame:
    """Create price data with a gap (missing values) in the middle.

    Args:
        n_days: Total number of trading days
        gap_start: Index where gap starts (inclusive)
        gap_end: Index where gap ends (exclusive)

    Returns:
        DataFrame with OHLC + Adj Close with NaN values in specified range
    """
    dates = pd.bdate_range("2020-01-01", periods=n_days)

    # Create base prices
    close_prices = [100.0 + i * 0.5 for i in range(n_days)]

    # Create OHLC with small variations
    df = pd.DataFrame(
        {
            "Open": [p * 0.99 for p in close_prices],
            "High": [p * 1.01 for p in close_prices],
            "Low": [p * 0.98 for p in close_prices],
            "Close": close_prices,
            "Adj Close": close_prices,
            "Volume": 1000000,
        },
        index=dates,
    )

    # Introduce gap (NaN values)
    df.iloc[gap_start:gap_end, df.columns.get_indexer(["Open", "High", "Low", "Close", "Adj Close"])] = None

    return df


def test_default_policy_is_forward_fill():
    """Test that default missing data policy is FORWARD_FILL."""
    assert DEFAULT_MISSING_DATA_POLICY == MissingDataPolicy.FORWARD_FILL


def test_forward_fill_policy():
    """Test FORWARD_FILL policy fills gaps with last known value."""
    df_with_gaps = create_price_data_with_gaps(n_days=100, gap_start=40, gap_end=45)

    # Verify gaps exist
    assert df_with_gaps.isnull().any().any(), "Test data should contain missing values"

    adapter = BacktraderAdapter(
        price_histories={"STOCK": df_with_gaps},
        missing_data_policy=MissingDataPolicy.FORWARD_FILL,
    )

    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("STOCK",),
        start=None,
        end=None,
        initial_cash=10000.0,
        parameters={"equity_proportions": [1.0]},
    )

    result = adapter.run(request)

    # Should complete successfully without NaN errors
    assert result.metrics["ending_value"] > 0
    assert "missing_data_policy" in result.assumptions
    assert result.assumptions["missing_data_policy"] == "forward_fill"

    # Verify adapter actually filled the gaps
    processed_df = adapter._apply_missing_data_policy(df_with_gaps.copy(), "STOCK")
    assert not processed_df.isnull().any().any(), "Forward fill should eliminate all NaN values"

    # Verify forward fill behavior: gap values should match the value before gap
    pre_gap_value = df_with_gaps["Close"].iloc[39]  # Last value before gap
    filled_gap_values = processed_df["Close"].iloc[40:45]
    assert (filled_gap_values == pre_gap_value).all(), "Gap should be filled with last known value"


def test_drop_policy():
    """Test DROP policy removes rows with missing values."""
    df_with_gaps = create_price_data_with_gaps(n_days=100, gap_start=40, gap_end=45)

    adapter = BacktraderAdapter(
        price_histories={"STOCK": df_with_gaps},
        missing_data_policy=MissingDataPolicy.DROP,
    )

    # Verify adapter drops the gap rows
    processed_df = adapter._apply_missing_data_policy(df_with_gaps.copy(), "STOCK")
    assert not processed_df.isnull().any().any(), "Drop should eliminate all NaN values"
    assert len(processed_df) == 95, "Should have dropped 5 rows (40-44 inclusive)"

    request = BacktestRunRequest(
        start=None,
        end=None,
        strategy_name="NoRebalance",
        symbols=("STOCK",),
        parameters={"equity_proportions": [1.0]},
        initial_cash=10000.0,
    )

    result = adapter.run(request)

    # Should complete successfully with reduced dataset
    assert result.metrics["ending_value"] > 0
    assert result.assumptions["missing_data_policy"] == "drop"


def test_error_policy_raises_on_missing_data():
    """Test ERROR policy raises ValueError when missing data detected."""
    df_with_gaps = create_price_data_with_gaps(n_days=100, gap_start=40, gap_end=45)

    adapter = BacktraderAdapter(
        price_histories={"STOCK": df_with_gaps},
        missing_data_policy=MissingDataPolicy.ERROR,
    )

    request = BacktestRunRequest(
        start=None,
        end=None,
        strategy_name="NoRebalance",
        symbols=("STOCK",),
        parameters={"equity_proportions": [1.0]},
        initial_cash=10000.0,
    )

    # Should raise ValueError when trying to run with missing data
    with pytest.raises(ValueError, match="Missing data detected in STOCK with policy=ERROR"):
        adapter.run(request)


def test_error_policy_passes_with_clean_data():
    """Test ERROR policy succeeds when no missing data exists."""
    # Create data without gaps
    dates = pd.bdate_range("2020-01-01", periods=100)
    close_prices = [100.0 + i * 0.5 for i in range(100)]

    df_clean = pd.DataFrame(
        {
            "Open": [p * 0.99 for p in close_prices],
            "High": [p * 1.01 for p in close_prices],
            "Low": [p * 0.98 for p in close_prices],
            "Close": close_prices,
            "Adj Close": close_prices,
            "Volume": 1000000,
        },
        index=dates,
    )

    adapter = BacktraderAdapter(
        price_histories={"STOCK": df_clean},
        missing_data_policy=MissingDataPolicy.ERROR,
    )

    request = BacktestRunRequest(
        start=None,
        end=None,
        strategy_name="NoRebalance",
        symbols=("STOCK",),
        parameters={"equity_proportions": [1.0]},
        initial_cash=10000.0,
    )

    # Should complete successfully with clean data
    result = adapter.run(request)
    assert result.metrics["ending_value"] > 0
    assert result.assumptions["missing_data_policy"] == "error"


def test_interpolate_policy():
    """Test INTERPOLATE policy fills gaps with linear interpolation."""
    df_with_gaps = create_price_data_with_gaps(n_days=100, gap_start=40, gap_end=45)

    adapter = BacktraderAdapter(
        price_histories={"STOCK": df_with_gaps},
        missing_data_policy=MissingDataPolicy.INTERPOLATE,
    )

    # Verify interpolation behavior
    processed_df = adapter._apply_missing_data_policy(df_with_gaps.copy(), "STOCK")
    assert not processed_df.isnull().any().any(), "Interpolate should eliminate all NaN values"

    # Verify linear interpolation: values should be between before/after gap
    before_gap = df_with_gaps["Close"].iloc[39]  # 119.5
    after_gap = df_with_gaps["Close"].iloc[45]  # 122.5
    interpolated_values = processed_df["Close"].iloc[40:45]

    # All interpolated values should be between before and after
    assert (interpolated_values >= before_gap).all()
    assert (interpolated_values <= after_gap).all()

    # Should be roughly evenly spaced (linear)
    expected_step = (after_gap - before_gap) / 6  # 6 steps from 39 to 45
    for i, val in enumerate(interpolated_values, start=1):
        expected_val = before_gap + expected_step * i
        assert val == pytest.approx(expected_val, abs=0.1), f"Interpolation not linear at position {i}"

    request = BacktestRunRequest(
        start=None,
        end=None,
        strategy_name="NoRebalance",
        symbols=("STOCK",),
        parameters={"equity_proportions": [1.0]},
        initial_cash=10000.0,
    )

    result = adapter.run(request)
    assert result.metrics["ending_value"] > 0
    assert result.assumptions["missing_data_policy"] == "interpolate"


def test_backfill_policy():
    """Test BACKFILL policy fills gaps with next known value (look-ahead bias)."""
    df_with_gaps = create_price_data_with_gaps(n_days=100, gap_start=40, gap_end=45)

    adapter = BacktraderAdapter(
        price_histories={"STOCK": df_with_gaps},
        missing_data_policy=MissingDataPolicy.BACKFILL,
    )

    # Verify backfill behavior
    processed_df = adapter._apply_missing_data_policy(df_with_gaps.copy(), "STOCK")
    assert not processed_df.isnull().any().any(), "Backfill should eliminate all NaN values"

    # Verify backfill behavior: gap values should match the value after gap
    post_gap_value = df_with_gaps["Close"].iloc[45]  # First value after gap
    filled_gap_values = processed_df["Close"].iloc[40:45]
    assert (filled_gap_values == post_gap_value).all(), "Gap should be filled with next known value"

    request = BacktestRunRequest(
        start=None,
        end=None,
        strategy_name="NoRebalance",
        symbols=("STOCK",),
        parameters={"equity_proportions": [1.0]},
        initial_cash=10000.0,
    )

    result = adapter.run(request)
    assert result.metrics["ending_value"] > 0
    assert result.assumptions["missing_data_policy"] == "backfill"


def test_multiple_symbols_with_different_gaps():
    """Test that policy is applied consistently across multiple symbols."""
    df1 = create_price_data_with_gaps(n_days=100, gap_start=20, gap_end=25)
    df2 = create_price_data_with_gaps(n_days=100, gap_start=60, gap_end=65)

    adapter = BacktraderAdapter(
        price_histories={"STOCK1": df1, "STOCK2": df2},
        missing_data_policy=MissingDataPolicy.FORWARD_FILL,
    )

    request = BacktestRunRequest(
        start=None,
        end=None,
        strategy_name="Rebalance",
        symbols=("STOCK1", "STOCK2"),
        parameters={"rebal_proportions": [0.5, 0.5], "rebal_interval": 20},
        initial_cash=10000.0,
    )

    result = adapter.run(request)

    # Should handle both symbols' gaps successfully
    assert result.metrics["ending_value"] > 0
    assert result.assumptions["missing_data_policy"] == "forward_fill"


def test_policy_applied_before_validation():
    """Test that policy is applied before dataframe validation.

    This ensures gaps are handled before the validation step that might
    reject dataframes with missing values.
    """
    df_with_gaps = create_price_data_with_gaps(n_days=100, gap_start=40, gap_end=45)

    # DROP policy should work even though original data has gaps
    adapter = BacktraderAdapter(
        price_histories={"STOCK": df_with_gaps},
        missing_data_policy=MissingDataPolicy.DROP,
    )

    # Should not raise during _select_price_histories because policy is applied first
    histories = adapter._select_price_histories(("STOCK",))
    assert "STOCK" in histories
    assert not histories["STOCK"].isnull().any().any()


def test_edge_case_gap_at_start():
    """Test handling of gap at the very beginning of data."""
    df = create_price_data_with_gaps(n_days=100, gap_start=0, gap_end=5)

    # Forward fill won't work at start (nothing to fill from)
    # But should not crash - will leave NaN or drop rows
    adapter_drop = BacktraderAdapter(
        price_histories={"STOCK": df},
        missing_data_policy=MissingDataPolicy.DROP,
    )

    processed = adapter_drop._apply_missing_data_policy(df.copy(), "STOCK")
    assert len(processed) == 95  # Should drop first 5 rows

    # Backfill should work for gap at start
    adapter_backfill = BacktraderAdapter(
        price_histories={"STOCK": df},
        missing_data_policy=MissingDataPolicy.BACKFILL,
    )

    processed_backfill = adapter_backfill._apply_missing_data_policy(df.copy(), "STOCK")
    assert not processed_backfill.isnull().any().any()


def test_edge_case_gap_at_end():
    """Test handling of gap at the very end of data."""
    df = create_price_data_with_gaps(n_days=100, gap_start=95, gap_end=100)

    # Forward fill should work at end
    adapter_ffill = BacktraderAdapter(
        price_histories={"STOCK": df},
        missing_data_policy=MissingDataPolicy.FORWARD_FILL,
    )

    processed = adapter_ffill._apply_missing_data_policy(df.copy(), "STOCK")
    assert not processed.isnull().any().any()

    # Backfill won't work at end (nothing to fill from)
    # But should not crash
    adapter_drop = BacktraderAdapter(
        price_histories={"STOCK": df},
        missing_data_policy=MissingDataPolicy.DROP,
    )

    processed_drop = adapter_drop._apply_missing_data_policy(df.copy(), "STOCK")
    assert len(processed_drop) == 95  # Should drop last 5 rows
