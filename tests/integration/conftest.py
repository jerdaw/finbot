"""Shared fixtures for integration tests.

This module provides pytest fixtures and utilities for integration testing.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def integration_fixtures_dir() -> Path:
    """Return path to integration test fixtures directory."""
    return Path(__file__).parent.parent / "fixtures" / "integration"


@pytest.fixture
def sample_spy_data() -> pd.DataFrame:
    """Generate sample SPY price data for testing.

    Returns 1 year of daily data with realistic price movements.
    """
    # Generate 252 trading days (1 year)
    dates = pd.date_range(start="2023-01-03", periods=252, freq="B")

    # Start at $400, simulate random walk with drift
    import numpy as np

    np.random.seed(42)  # Reproducible

    returns = np.random.normal(0.0005, 0.01, 252)  # 0.05% daily drift, 1% volatility
    prices = 400 * (1 + returns).cumprod()

    # Create OHLCV data
    df = pd.DataFrame(
        {
            "Open": prices * (1 + np.random.normal(0, 0.002, 252)),
            "High": prices * (1 + np.abs(np.random.normal(0.005, 0.003, 252))),
            "Low": prices * (1 - np.abs(np.random.normal(0.005, 0.003, 252))),
            "Close": prices,
            "Adj Close": prices,  # No splits/dividends
            "Volume": np.random.randint(50_000_000, 150_000_000, 252),
        },
        index=dates,
    )

    return df


@pytest.fixture
def sample_tlt_data() -> pd.DataFrame:
    """Generate sample TLT (bond) price data for testing.

    Returns 1 year of daily data with lower volatility than stocks.
    """
    dates = pd.date_range(start="2023-01-03", periods=252, freq="B")

    import numpy as np

    np.random.seed(43)  # Different seed than SPY

    # Bonds have lower returns and volatility
    returns = np.random.normal(-0.0002, 0.005, 252)  # Slight negative drift, 0.5% vol
    prices = 100 * (1 + returns).cumprod()

    df = pd.DataFrame(
        {
            "Open": prices * (1 + np.random.normal(0, 0.001, 252)),
            "High": prices * (1 + np.abs(np.random.normal(0.002, 0.001, 252))),
            "Low": prices * (1 - np.abs(np.random.normal(0.002, 0.001, 252))),
            "Close": prices,
            "Adj Close": prices,
            "Volume": np.random.randint(5_000_000, 15_000_000, 252),
        },
        index=dates,
    )

    return df


@pytest.fixture
def sample_multi_asset_data(sample_spy_data, sample_tlt_data) -> dict[str, pd.DataFrame]:
    """Return dictionary of multiple asset price histories."""
    return {
        "SPY": sample_spy_data,
        "TLT": sample_tlt_data,
    }


@pytest.fixture
def sample_libor_data() -> pd.DataFrame:
    """Generate sample LIBOR rate data for testing."""
    dates = pd.date_range(start="2023-01-03", periods=252, freq="B")

    import numpy as np

    np.random.seed(44)

    # LIBOR rates around 4-5%
    rates = 4.5 + np.random.normal(0, 0.2, 252)
    rates = np.clip(rates, 0, 10)  # Keep reasonable

    df = pd.DataFrame({"Yield": rates / 100}, index=dates)  # Convert to decimal

    return df


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create temporary directory for test outputs."""
    output_dir = tmp_path / "test_outputs"
    output_dir.mkdir()
    return output_dir


def assert_valid_price_dataframe(df: pd.DataFrame, min_rows: int = 10):
    """Assert that a DataFrame is a valid price history.

    Args:
        df: DataFrame to validate
        min_rows: Minimum expected number of rows

    Raises:
        AssertionError: If DataFrame is invalid
    """
    assert isinstance(df, pd.DataFrame), "Result must be a DataFrame"
    assert not df.empty, "DataFrame should not be empty"
    assert len(df) >= min_rows, f"Expected at least {min_rows} rows, got {len(df)}"
    assert "Close" in df.columns, "Must have 'Close' column"
    assert df.index.name is None or "date" in df.index.name.lower() or isinstance(df.index, pd.DatetimeIndex), (
        "Index should be datetime"
    )


def assert_valid_backtest_stats(stats: pd.DataFrame):
    """Assert that backtest statistics are valid.

    Args:
        stats: Statistics DataFrame from backtest (stats are columns, not rows)

    Raises:
        AssertionError: If stats are invalid
    """
    assert isinstance(stats, pd.DataFrame), "Stats must be a DataFrame"
    assert not stats.empty, "Stats should not be empty"

    # Check for key metrics (stats are columns in the DataFrame)
    expected_metrics = [
        "CAGR",
        "Sharpe",
        "Max Drawdown",
    ]

    for metric in expected_metrics:
        assert metric in stats.columns, f"Missing expected metric: {metric}"

    # Validate metric ranges (access column values at row 0)
    cagr = stats["CAGR"].iloc[0]
    assert -1 <= cagr <= 10, f"CAGR {cagr} seems unreasonable"

    sharpe = stats["Sharpe"].iloc[0]
    assert -10 <= sharpe <= 10, f"Sharpe ratio {sharpe} seems unreasonable"

    max_dd = stats["Max Drawdown"].iloc[0]
    assert -1 <= max_dd <= 0, f"Max drawdown {max_dd} should be between -1 and 0"


def assert_valid_optimization_results(results: pd.DataFrame):
    """Assert that optimization results are valid.

    Args:
        results: Optimization results DataFrame

    Raises:
        AssertionError: If results are invalid
    """
    assert isinstance(results, pd.DataFrame), "Results must be a DataFrame"
    assert not results.empty, "Results should not be empty"
    assert len(results) > 1, "Should have multiple optimization trials"

    # Check for expected columns
    expected_cols = ["cagr", "sharpe", "max_drawdown"]
    for col in expected_cols:
        assert col in results.columns or any(col in c.lower() for c in results.columns), (
            f"Missing column related to: {col}"
        )
