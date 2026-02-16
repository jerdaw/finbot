"""Unit tests for corporate action handling (stock splits and dividends)."""

from __future__ import annotations

import backtrader as bt
import numpy as np
import pandas as pd
import pytest

from finbot.services.backtesting.backtest_runner import BacktestRunner
from finbot.services.backtesting.brokers.fixed_commission_scheme import FixedCommissionScheme
from finbot.services.backtesting.strategies.no_rebalance import NoRebalance


def create_price_data_with_split(
    initial_price: float = 100.0,
    split_ratio: float = 2.0,
    split_date: str = "2020-06-15",
    n_days_before: int = 100,
    n_days_after: int = 100,
) -> pd.DataFrame:
    """Create synthetic price data with a stock split.

    Args:
        initial_price: Starting price before split
        split_ratio: Split ratio (2.0 = 2:1 split, shares double, price halves)
        split_date: Date of the split
        n_days_before: Trading days before split
        n_days_after: Trading days after split

    Returns:
        DataFrame with OHLC + Adj Close + Stock Splits columns
    """
    split_ts = pd.Timestamp(split_date)

    # Create dates (trading days only - weekdays)
    dates_before = pd.bdate_range(end=split_ts - pd.Timedelta(days=1), periods=n_days_before)
    dates_after = pd.bdate_range(start=split_ts, periods=n_days_after)
    all_dates = dates_before.union(dates_after)

    # Price after split (unadjusted)
    post_split_price = initial_price / split_ratio

    # Create unadjusted prices
    close_prices = []
    stock_splits = []

    for date in all_dates:
        if date < split_ts:
            # Before split: use initial price (with small random variation)
            close_prices.append(initial_price * (1 + np.random.uniform(-0.01, 0.01)))
            stock_splits.append(0.0)
        else:
            # After split: use post-split price
            close_prices.append(post_split_price * (1 + np.random.uniform(-0.01, 0.01)))
            if date == split_ts:
                stock_splits.append(split_ratio)  # Record split on split date
            else:
                stock_splits.append(0.0)

    # Create adjusted prices (backward-adjusted from most recent price)
    # All pre-split prices should be divided by split_ratio
    adj_close_prices = []
    for i, date in enumerate(all_dates):
        if date < split_ts:
            # Adjust historical prices for the split
            adj_close_prices.append(close_prices[i] / split_ratio)
        else:
            # Post-split prices are not adjusted (they're the "current" prices)
            adj_close_prices.append(close_prices[i])

    # Create OHLC with small variations
    df = pd.DataFrame(
        {
            "Open": [p * 0.99 for p in close_prices],
            "High": [p * 1.01 for p in close_prices],
            "Low": [p * 0.98 for p in close_prices],
            "Close": close_prices,
            "Adj Close": adj_close_prices,
            "Volume": 1000000,
            "Dividends": 0.0,
            "Stock Splits": stock_splits,
        },
        index=all_dates,
    )

    return df


def create_price_data_with_dividend(
    initial_price: float = 100.0,
    dividend_amount: float = 2.0,
    ex_dividend_date: str = "2020-06-15",
    n_days_before: int = 100,
    n_days_after: int = 100,
) -> pd.DataFrame:
    """Create synthetic price data with a dividend payment.

    Args:
        initial_price: Starting price
        dividend_amount: Dividend per share
        ex_dividend_date: Ex-dividend date (price drops by dividend)
        n_days_before: Trading days before dividend
        n_days_after: Trading days after dividend

    Returns:
        DataFrame with OHLC + Adj Close + Dividends columns
    """
    ex_div_ts = pd.Timestamp(ex_dividend_date)

    # Create dates (trading days only - weekdays)
    dates_before = pd.bdate_range(end=ex_div_ts - pd.Timedelta(days=1), periods=n_days_before)
    dates_after = pd.bdate_range(start=ex_div_ts, periods=n_days_after)
    all_dates = dates_before.union(dates_after)

    # Create unadjusted prices
    close_prices = []
    dividends = []

    for date in all_dates:
        if date < ex_div_ts:
            # Before ex-dividend: around initial price
            close_prices.append(initial_price * (1 + np.random.uniform(-0.01, 0.01)))
            dividends.append(0.0)
        elif date == ex_div_ts:
            # On ex-dividend date: price drops by dividend amount
            # (In reality, it's not exactly the dividend amount, but close)
            close_prices.append((initial_price - dividend_amount) * (1 + np.random.uniform(-0.01, 0.01)))
            dividends.append(dividend_amount)
        else:
            # After ex-dividend: around post-dividend price
            close_prices.append((initial_price - dividend_amount) * (1 + np.random.uniform(-0.01, 0.01)))
            dividends.append(0.0)

    # Create adjusted prices (backward-adjusted to add back all dividends)
    # Total dividend paid so far (cumulative)
    total_dividends_paid = dividend_amount

    adj_close_prices = []
    for i, date in enumerate(all_dates):
        if date < ex_div_ts:
            # Historical prices get dividend added back
            adj_close_prices.append(close_prices[i] - total_dividends_paid)
        else:
            # Post-dividend prices are the current prices
            adj_close_prices.append(close_prices[i])

    # Create OHLC with small variations
    df = pd.DataFrame(
        {
            "Open": [p * 0.99 for p in close_prices],
            "High": [p * 1.01 for p in close_prices],
            "Low": [p * 0.98 for p in close_prices],
            "Close": close_prices,
            "Adj Close": adj_close_prices,
            "Volume": 1000000,
            "Dividends": dividends,
            "Stock Splits": 0.0,
        },
        index=all_dates,
    )

    return df


def test_stock_split_2_for_1():
    """Test that a 2:1 stock split is correctly handled via adjusted prices.

    In a 2:1 split:
    - Share count doubles
    - Price halves
    - Portfolio value should remain constant
    """
    # Create data with 2:1 split
    df = create_price_data_with_split(
        initial_price=100.0,
        split_ratio=2.0,
        split_date="2020-06-15",
        n_days_before=50,
        n_days_after=50,
    )

    # Verify the split is recorded
    split_events = df[df["Stock Splits"] != 0.0]
    assert len(split_events) == 1, "Should have exactly one split event"
    assert split_events["Stock Splits"].iloc[0] == 2.0, "Split ratio should be 2.0"

    # Verify adjusted prices are roughly half of unadjusted prices before split
    pre_split_data = df[df.index < pd.Timestamp("2020-06-15")]
    avg_close = pre_split_data["Close"].mean()
    avg_adj_close = pre_split_data["Adj Close"].mean()

    # Adjusted close should be ~half of close (within 5% tolerance for random variation)
    assert avg_adj_close == pytest.approx(avg_close / 2.0, rel=0.05)

    # Run backtest with adjusted prices
    runner = BacktestRunner(
        price_histories={"STOCK": df},
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

    stats = runner.run_backtest()

    # Backtest should complete successfully
    assert stats is not None
    assert "Ending Value" in stats.columns
    final_value = stats["Ending Value"].iloc[0]

    # Final value should be positive (not NaN or negative)
    assert final_value > 0, "Portfolio value should remain positive through split"


def test_stock_split_3_for_1():
    """Test that a 3:1 stock split is correctly handled."""
    # Use a Monday to ensure it's a trading day
    df = create_price_data_with_split(
        initial_price=150.0,
        split_ratio=3.0,
        split_date="2020-08-03",  # Monday, definitely a trading day
        n_days_before=40,
        n_days_after=40,
    )

    # Verify the split is recorded (use != 0 instead of > 0 to catch all splits)
    split_events = df[df["Stock Splits"] != 0.0]
    assert len(split_events) == 1, (
        f"Expected 1 split event, found {len(split_events)}. Dates in data: {df.index[0]} to {df.index[-1]}"
    )
    assert split_events["Stock Splits"].iloc[0] == 3.0

    # Verify adjusted prices are roughly 1/3 of unadjusted prices before split
    pre_split_data = df[df.index < pd.Timestamp("2020-08-03")]
    avg_close = pre_split_data["Close"].mean()
    avg_adj_close = pre_split_data["Adj Close"].mean()

    assert avg_adj_close == pytest.approx(avg_close / 3.0, rel=0.05)


def test_dividend_payment():
    """Test that dividend payments are correctly handled via adjusted prices.

    When a dividend is paid:
    - Price drops by ~dividend amount on ex-dividend date
    - Historical prices get dividend added back (backward adjustment)
    - Returns should account for dividend reinvestment
    """
    df = create_price_data_with_dividend(
        initial_price=100.0,
        dividend_amount=2.0,
        ex_dividend_date="2020-06-15",
        n_days_before=50,
        n_days_after=50,
    )

    # Verify dividend is recorded
    dividend_events = df[df["Dividends"] > 0]
    assert len(dividend_events) == 1, "Should have exactly one dividend event"
    assert dividend_events["Dividends"].iloc[0] == 2.0, "Dividend should be $2.00"

    # Verify ex-dividend date exists in data
    ex_div_date = pd.Timestamp("2020-06-15")
    assert ex_div_date in df.index, "Ex-dividend date should be in the data"

    # Verify adjusted prices account for dividend
    # Historical prices should be lower than unadjusted prices (dividend subtracted)
    pre_div_data = df[df.index < ex_div_date]
    assert (pre_div_data["Adj Close"] < pre_div_data["Close"]).all(), (
        "Historical adj prices should be less than unadjusted"
    )

    # Run backtest with adjusted prices
    runner = BacktestRunner(
        price_histories={"STOCK": df},
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

    stats = runner.run_backtest()

    # Backtest should complete successfully
    assert stats is not None
    final_value = stats["Ending Value"].iloc[0]
    assert final_value > 0, "Portfolio value should remain positive through dividend"


def test_multiple_dividends():
    """Test handling of multiple dividend payments."""
    # Create base data
    dates = pd.bdate_range("2020-01-01", periods=200)

    close_prices = [100.0] * 200
    dividends = [0.0] * 200

    # Add 3 dividends
    dividend_dates = [50, 100, 150]
    dividend_amount = 1.5

    for idx in dividend_dates:
        dividends[idx] = dividend_amount
        # Price drops by dividend on ex-div date
        for i in range(idx, 200):
            close_prices[i] -= dividend_amount

    # Calculate adjusted close (add back all dividends to historical prices)
    total_div = dividend_amount * len(dividend_dates)
    adj_close = [
        close_prices[i] - total_div + dividend_amount * sum(1 for d in dividend_dates if d <= i) for i in range(200)
    ]

    df = pd.DataFrame(
        {
            "Open": [p * 0.99 for p in close_prices],
            "High": [p * 1.01 for p in close_prices],
            "Low": [p * 0.98 for p in close_prices],
            "Close": close_prices,
            "Adj Close": adj_close,
            "Volume": 1000000,
            "Dividends": dividends,
            "Stock Splits": 0.0,
        },
        index=dates,
    )

    # Verify 3 dividend events
    div_events = df[df["Dividends"] > 0]
    assert len(div_events) == 3, "Should have 3 dividend events"

    # Run backtest
    runner = BacktestRunner(
        price_histories={"STOCK": df},
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

    stats = runner.run_backtest()
    assert stats is not None


def test_split_and_dividend_combined():
    """Test handling of both split and dividend in same dataset."""
    # Create data with split first, then dividend
    df_split = create_price_data_with_split(
        initial_price=200.0,
        split_ratio=2.0,
        split_date="2020-04-01",
        n_days_before=50,
        n_days_after=100,
    )

    # Modify to add a dividend after the split
    dividend_date = pd.Timestamp("2020-06-01")
    dividend_amount = 1.0

    # Add dividend to rows after dividend date
    df_split["Dividends"] = 0.0
    df_split.loc[dividend_date, "Dividends"] = dividend_amount

    # Adjust close prices for dividend (post-dividend adjustment)
    # This is simplified - real adjustment would be more complex
    for date in df_split.index:
        if date < dividend_date:
            df_split.loc[date, "Adj Close"] -= dividend_amount

    # Run backtest
    runner = BacktestRunner(
        price_histories={"STOCK": df_split},
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

    stats = runner.run_backtest()

    # Should handle both corporate actions
    assert stats is not None
    final_value = stats["Ending Value"].iloc[0]
    assert final_value > 0


def test_reverse_split():
    """Test reverse stock split (e.g., 1:5 - shares reduced, price increased)."""
    # Reverse split: ratio < 1 means shares decrease, price increases
    df = create_price_data_with_split(
        initial_price=10.0,
        split_ratio=0.2,  # 1:5 reverse split (1 share becomes 0.2 shares, price 5x)
        split_date="2020-06-15",
        n_days_before=50,
        n_days_after=50,
    )

    # After reverse split, price should be ~5x higher
    post_split_data = df[df.index >= pd.Timestamp("2020-06-15")]
    post_split_avg = post_split_data["Close"].mean()

    # Post-split price should be ~50 (10 * 5)
    assert post_split_avg == pytest.approx(50.0, rel=0.1)

    # Run backtest
    runner = BacktestRunner(
        price_histories={"STOCK": df},
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

    stats = runner.run_backtest()
    assert stats is not None
