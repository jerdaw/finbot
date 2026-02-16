"""Unit tests for adjusted price handling in backtests."""

from __future__ import annotations

import backtrader as bt
import pandas as pd
import pytest

from finbot.services.backtesting.backtest_runner import BacktestRunner
from finbot.services.backtesting.brokers.fixed_commission_scheme import FixedCommissionScheme
from finbot.services.backtesting.strategies.no_rebalance import NoRebalance


def test_adjusted_prices_used_when_available():
    """Test that BacktestRunner uses Adj Close when available."""
    # Create synthetic data with different Close and Adj Close
    dates = pd.date_range("2020-01-01", periods=100, freq="D")
    df = pd.DataFrame(
        {
            "Open": 100.0,
            "High": 101.0,
            "Low": 99.0,
            "Close": 100.0,  # Unadjusted
            "Adj Close": 90.0,  # Adjusted (10% lower due to dividends)
            "Volume": 1000000,
        },
        index=dates,
    )

    runner = BacktestRunner(
        price_histories={"TEST": df},
        start=None,
        end=None,
        duration=None,
        start_step=None,
        init_cash=10000.0,
        strat=NoRebalance,
        strat_kwargs={"equity_proportions": [1.0]},
        broker=bt.brokers.BackBroker,
        broker_kwargs={},
        broker_commission=FixedCommissionScheme,
        sizer=bt.sizers.AllInSizer,
        sizer_kwargs={},
        plot=False,
    )

    # Run backtest to trigger price adjustment
    runner.run_backtest()

    # After backtest, check that the price history was adjusted
    adjusted_df = runner.price_histories["TEST"]

    # Close should now equal Adj Close (90.0)
    assert adjusted_df["Close"].iloc[0] == 90.0, "Close should be replaced with Adj Close"

    # Original close should be preserved as Close_Unadjusted
    assert "Close_Unadjusted" in adjusted_df.columns, "Original close should be preserved"
    assert adjusted_df["Close_Unadjusted"].iloc[0] == 100.0, "Unadjusted close should be 100.0"

    # OHLC should be adjusted proportionally
    expected_adj_factor = 90.0 / 100.0  # 0.9
    assert adjusted_df["Open"].iloc[0] == pytest.approx(100.0 * expected_adj_factor)
    assert adjusted_df["High"].iloc[0] == pytest.approx(101.0 * expected_adj_factor)
    assert adjusted_df["Low"].iloc[0] == pytest.approx(99.0 * expected_adj_factor)


def test_no_adjustment_when_adj_close_missing():
    """Test that data without Adj Close is used as-is."""
    dates = pd.date_range("2020-01-01", periods=100, freq="D")
    df = pd.DataFrame(
        {
            "Open": 100.0,
            "High": 101.0,
            "Low": 99.0,
            "Close": 100.0,
            "Volume": 1000000,
        },
        index=dates,
    )

    runner = BacktestRunner(
        price_histories={"TEST": df},
        start=None,
        end=None,
        duration=None,
        start_step=None,
        init_cash=10000.0,
        strat=NoRebalance,
        strat_kwargs={"equity_proportions": [1.0]},
        broker=bt.brokers.BackBroker,
        broker_kwargs={},
        broker_commission=FixedCommissionScheme,
        sizer=bt.sizers.AllInSizer,
        sizer_kwargs={},
        plot=False,
    )

    # Run backtest to trigger price adjustment
    runner.run_backtest()

    adjusted_df = runner.price_histories["TEST"]

    # Close should remain unchanged
    assert adjusted_df["Close"].iloc[0] == 100.0

    # No Close_Unadjusted should be created
    assert "Close_Unadjusted" not in adjusted_df.columns


def test_adjustment_maintains_ohlc_relationships():
    """Test that OHLC adjustment maintains proper relationships (High >= Low, etc.)."""
    dates = pd.date_range("2020-01-01", periods=10, freq="D")
    df = pd.DataFrame(
        {
            "Open": [100.0, 102.0, 101.0, 99.0, 98.0, 100.0, 103.0, 105.0, 104.0, 102.0],
            "High": [102.0, 104.0, 103.0, 101.0, 100.0, 102.0, 105.0, 107.0, 106.0, 104.0],
            "Low": [99.0, 101.0, 100.0, 98.0, 97.0, 99.0, 102.0, 104.0, 103.0, 101.0],
            "Close": [101.0, 103.0, 102.0, 100.0, 99.0, 101.0, 104.0, 106.0, 105.0, 103.0],
            "Adj Close": [90.0, 92.0, 91.0, 89.0, 88.0, 90.0, 93.0, 95.0, 94.0, 92.0],  # ~10% adjustment
            "Volume": 1000000,
        },
        index=dates,
    )

    runner = BacktestRunner(
        price_histories={"TEST": df},
        start=None,
        end=None,
        duration=None,
        start_step=None,
        init_cash=10000.0,
        strat=NoRebalance,
        strat_kwargs={"equity_proportions": [1.0]},
        broker=bt.brokers.BackBroker,
        broker_kwargs={},
        broker_commission=FixedCommissionScheme,
        sizer=bt.sizers.AllInSizer,
        sizer_kwargs={},
        plot=False,
    )

    # Run backtest to trigger price adjustment
    runner.run_backtest()

    adjusted_df = runner.price_histories["TEST"]

    # Check OHLC relationships hold after adjustment
    for idx in range(len(adjusted_df)):
        row = adjusted_df.iloc[idx]
        assert row["High"] >= row["Low"], f"High must be >= Low at index {idx}"
        assert row["High"] >= row["Open"], f"High must be >= Open at index {idx}"
        assert row["High"] >= row["Close"], f"High must be >= Close at index {idx}"
        assert row["Low"] <= row["Open"], f"Low must be <= Open at index {idx}"
        assert row["Low"] <= row["Close"], f"Low must be <= Close at index {idx}"
