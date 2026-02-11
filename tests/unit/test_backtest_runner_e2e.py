"""End-to-end tests for BacktestRunner.

Tests BacktestRunner initialization, run_backtest execution with synthetic data,
compute_stats output columns, and run_backtest return type.
"""

from __future__ import annotations

import warnings

import backtrader as bt
import numpy as np
import pandas as pd
import pytest

from finbot.services.backtesting.backtest_runner import BacktestRunner
from finbot.services.backtesting.brokers.fixed_commission_scheme import FixedCommissionScheme
from finbot.services.backtesting.compute_stats import compute_stats
from finbot.services.backtesting.run_backtest import run_backtest
from finbot.services.backtesting.strategies.no_rebalance import NoRebalance
from finbot.services.backtesting.strategies.rebalance import Rebalance
from finbot.services.backtesting.strategies.sma_crossover import SMACrossover


def _make_price_df(n_days=500, start_price=100.0, seed=42):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2018-01-02", periods=n_days, freq="B")
    returns = rng.normal(0.0003, 0.012, n_days)
    close = start_price * np.cumprod(1 + returns)
    high = close * (1 + rng.uniform(0, 0.015, n_days))
    low = close * (1 - rng.uniform(0, 0.015, n_days))
    open_ = close * (1 + rng.uniform(-0.005, 0.005, n_days))
    volume = rng.integers(1_000_000, 10_000_000, n_days).astype(float)
    return pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=dates,
    )


class TestBacktestRunnerInit:
    """Tests for BacktestRunner initialization."""

    def test_initialization(self):
        df1 = _make_price_df()
        df2 = _make_price_df(seed=99)
        runner = BacktestRunner(
            price_histories={"SPY": df1, "TLT": df2},
            start=None,
            end=None,
            duration=None,
            start_step=None,
            init_cash=100_000,
            strat=Rebalance,
            strat_kwargs={"rebal_proportions": {0: 0.6, 1: 0.4}, "rebal_interval": 21},
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=FixedCommissionScheme,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )
        assert runner.init_cash == 100_000
        assert runner.stocks == ("SPY", "TLT")
        assert runner.strat is Rebalance

    def test_initialization_with_dates(self):
        df1 = _make_price_df()
        runner = BacktestRunner(
            price_histories={"SPY": df1},
            start=pd.Timestamp("2018-06-01"),
            end=pd.Timestamp("2019-06-01"),
            duration=None,
            start_step=None,
            init_cash=50_000,
            strat=SMACrossover,
            strat_kwargs={"fast_ma": 10, "slow_ma": 50},
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=FixedCommissionScheme,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )
        assert runner.start == pd.Timestamp("2018-06-01")
        assert runner.end == pd.Timestamp("2019-06-01")


class TestBacktestRunnerExecution:
    """Tests for running backtests end-to-end."""

    def test_run_backtest_returns_dataframe(self):
        df1 = _make_price_df()
        df2 = _make_price_df(seed=99, start_price=50.0)
        runner = BacktestRunner(
            price_histories={"SPY": df1, "TLT": df2},
            start=None,
            end=None,
            duration=None,
            start_step=None,
            init_cash=100_000,
            strat=Rebalance,
            strat_kwargs={"rebal_proportions": {0: 0.6, 1: 0.4}, "rebal_interval": 21},
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=FixedCommissionScheme,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            stats = runner.run_backtest()
        assert isinstance(stats, pd.DataFrame)

    def test_stats_has_required_columns(self):
        df1 = _make_price_df()
        df2 = _make_price_df(seed=99, start_price=50.0)
        runner = BacktestRunner(
            price_histories={"SPY": df1, "TLT": df2},
            start=None,
            end=None,
            duration=None,
            start_step=None,
            init_cash=100_000,
            strat=NoRebalance,
            strat_kwargs={"equity_proportions": {0: 0.6, 1: 0.4}},
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=FixedCommissionScheme,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            stats = runner.run_backtest()

        required_columns = [
            "Start Date",
            "End Date",
            "Duration",
            "Starting Value",
            "Ending Value",
            "ROI",
            "CAGR",
            "Sharpe",
            "Max Drawdown",
        ]
        for col in required_columns:
            assert col in stats.columns, f"Missing column: {col}"

    def test_stats_starting_value_matches_init_cash(self):
        df1 = _make_price_df()
        df2 = _make_price_df(seed=99, start_price=50.0)
        runner = BacktestRunner(
            price_histories={"SPY": df1, "TLT": df2},
            start=None,
            end=None,
            duration=None,
            start_step=None,
            init_cash=100_000,
            strat=Rebalance,
            strat_kwargs={"rebal_proportions": {0: 0.6, 1: 0.4}, "rebal_interval": 21},
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=FixedCommissionScheme,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            stats = runner.run_backtest()
        assert stats["Starting Value"].iloc[0] == pytest.approx(100_000, rel=0.01)


class TestRunBacktestFunction:
    """Tests for the run_backtest() wrapper function."""

    def test_run_backtest_with_tuple_args(self):
        """Test the process_map-compatible calling convention."""
        df1 = _make_price_df()
        df2 = _make_price_df(seed=99, start_price=50.0)
        args_tuple = (
            {"SPY": df1, "TLT": df2},  # price_histories
            None,  # start
            None,  # end
            None,  # duration
            None,  # start_step
            100_000,  # init_cash
            Rebalance,  # strat
            {"rebal_proportions": {0: 0.6, 1: 0.4}, "rebal_interval": 21},  # strat_kwargs
            bt.brokers.BackBroker,  # broker
            {},  # broker_kwargs
            FixedCommissionScheme,  # broker_commission
            bt.sizers.AllInSizer,  # sizer
            {},  # sizer_kwargs
            False,  # plot
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            stats = run_backtest(args_tuple)
        assert isinstance(stats, pd.DataFrame)


class TestComputeStats:
    """Tests for compute_stats function."""

    def test_compute_stats_returns_dataframe(self):
        dates = pd.date_range("2020-01-01", periods=252, freq="B")
        rng = np.random.default_rng(42)
        value_history = pd.Series(100_000 * np.cumprod(1 + rng.normal(0.0003, 0.01, 252)), index=dates)
        cash_history = pd.Series(np.full(252, 5000.0), index=dates)

        stats = compute_stats(
            value_history,
            cash_history,
            stocks=("SPY", "TLT"),
            strat=Rebalance,
            strat_kwargs={"rebal_proportions": {0: 0.6, 1: 0.4}, "rebal_interval": 21},
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=FixedCommissionScheme,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )
        assert isinstance(stats, pd.DataFrame)
        assert "ROI" in stats.columns
        assert "CAGR" in stats.columns
        assert "Sharpe" in stats.columns
        assert "Max Drawdown" in stats.columns

    def test_compute_stats_cash_utilization(self):
        dates = pd.date_range("2020-01-01", periods=100, freq="B")
        value_history = pd.Series(np.linspace(100_000, 110_000, 100), index=dates)
        cash_history = pd.Series(np.full(100, 10_000.0), index=dates)

        stats = compute_stats(
            value_history,
            cash_history,
            stocks=("SPY",),
            strat=None,
            strat_kwargs={},
            broker=None,
            broker_kwargs={},
            broker_commission=None,
            sizer=None,
            sizer_kwargs={},
            plot=False,
        )
        assert "Mean Cash Available" in stats.columns
        assert "Mean Cash Utilization" in stats.columns
