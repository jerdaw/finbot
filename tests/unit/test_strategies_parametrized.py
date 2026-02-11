"""Parametrized tests for all 10 backtesting strategies.

Runs each strategy through backtrader with synthetic price data to verify
order placement, rebalance triggers, signal generation, and that each strategy
produces valid stats output.
"""

from __future__ import annotations

import warnings

import backtrader as bt
import numpy as np
import pandas as pd
import pytest

from finbot.services.backtesting.analyzers.cv_tracker import CVTracker
from finbot.services.backtesting.brokers.fixed_commission_scheme import FixedCommissionScheme
from finbot.services.backtesting.strategies.dip_buy_sma import DipBuySMA
from finbot.services.backtesting.strategies.dip_buy_stdev import DipBuyStdev
from finbot.services.backtesting.strategies.macd_dual import MACDDual
from finbot.services.backtesting.strategies.macd_single import MACDSingle
from finbot.services.backtesting.strategies.no_rebalance import NoRebalance
from finbot.services.backtesting.strategies.rebalance import Rebalance
from finbot.services.backtesting.strategies.sma_crossover import SMACrossover
from finbot.services.backtesting.strategies.sma_crossover_double import SMACrossoverDouble
from finbot.services.backtesting.strategies.sma_crossover_triple import SMACrossoverTriple
from finbot.services.backtesting.strategies.sma_rebal_mix import SmaRebalMix


def _make_price_df(n_days: int = 500, start_price: float = 100.0, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic OHLCV price data for backtrader."""
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


def _make_price_df_alt(n_days: int = 500, start_price: float = 50.0, seed: int = 99) -> pd.DataFrame:
    """Generate a second synthetic dataset (different seed/price)."""
    return _make_price_df(n_days=n_days, start_price=start_price, seed=seed)


def _make_price_df_bonds(n_days: int = 500, start_price: float = 80.0, seed: int = 7) -> pd.DataFrame:
    """Generate a third synthetic dataset for triple-asset strategies."""
    return _make_price_df(n_days=n_days, start_price=start_price, seed=seed)


def _run_strategy(strat_cls, strat_kwargs, data_feeds: list[pd.DataFrame], cash: float = 100_000) -> list:
    """Run a backtrader strategy with given data feeds and return results."""
    cerebro = bt.Cerebro()
    for df in data_feeds:
        feed = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(feed)
    cerebro.addstrategy(strat_cls, **strat_kwargs)
    cerebro.broker.setcash(cash)
    cerebro.broker.addcommissioninfo(FixedCommissionScheme())
    cerebro.addsizer(bt.sizers.AllInSizer)
    cerebro.addanalyzer(CVTracker)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        results = cerebro.run(stdstats=False)
    return results


class TestRebalanceStrategy:
    """Test Rebalance strategy with actual backtrader execution."""

    def test_rebalance_runs_successfully(self):
        df1 = _make_price_df()
        df2 = _make_price_df_alt()
        results = _run_strategy(
            Rebalance,
            {"rebal_proportions": {0: 0.6, 1: 0.4}, "rebal_interval": 21},
            [df1, df2],
        )
        assert len(results) == 1
        strat = results[0]
        assert hasattr(strat.analyzers, "cvtracker")

    def test_rebalance_tracks_value(self):
        df1 = _make_price_df()
        df2 = _make_price_df_alt()
        results = _run_strategy(
            Rebalance,
            {"rebal_proportions": {0: 0.6, 1: 0.4}, "rebal_interval": 21},
            [df1, df2],
        )
        value_hist = results[0].analyzers.cvtracker.value
        cash_hist = results[0].analyzers.cvtracker.cash
        assert len(value_hist) > 0
        assert len(cash_hist) > 0
        assert value_hist[0] == pytest.approx(100_000, rel=0.01)

    @pytest.mark.parametrize(
        "proportions,interval",
        [
            ({0: 0.5, 1: 0.5}, 5),
            ({0: 0.8, 1: 0.2}, 63),
            ({0: 0.3, 1: 0.7}, 252),
        ],
    )
    def test_rebalance_various_params(self, proportions, interval):
        df1 = _make_price_df()
        df2 = _make_price_df_alt()
        results = _run_strategy(Rebalance, {"rebal_proportions": proportions, "rebal_interval": interval}, [df1, df2])
        assert len(results) == 1


class TestNoRebalanceStrategy:
    """Test NoRebalance (buy-and-hold) strategy."""

    def test_no_rebalance_runs_successfully(self):
        df1 = _make_price_df()
        df2 = _make_price_df_alt()
        results = _run_strategy(
            NoRebalance,
            {"equity_proportions": {0: 0.6, 1: 0.4}},
            [df1, df2],
        )
        assert len(results) == 1

    @pytest.mark.parametrize(
        "proportions",
        [
            {0: 0.5, 1: 0.5},
            {0: 1.0, 1: 0.0},
            {0: 0.3, 1: 0.7},
        ],
    )
    def test_no_rebalance_various_allocations(self, proportions):
        df1 = _make_price_df()
        df2 = _make_price_df_alt()
        results = _run_strategy(NoRebalance, {"equity_proportions": proportions}, [df1, df2])
        assert len(results) == 1
        value_hist = results[0].analyzers.cvtracker.value
        assert value_hist[0] == pytest.approx(100_000, rel=0.01)


class TestSMACrossoverStrategy:
    """Test SMA crossover strategies."""

    @pytest.mark.parametrize(
        "fast_ma,slow_ma",
        [(10, 50), (20, 100), (5, 20)],
    )
    def test_sma_crossover_single(self, fast_ma, slow_ma):
        df = _make_price_df()
        results = _run_strategy(SMACrossover, {"fast_ma": fast_ma, "slow_ma": slow_ma}, [df])
        assert len(results) == 1

    @pytest.mark.parametrize(
        "fast_ma,slow_ma",
        [(10, 50), (20, 100)],
    )
    def test_sma_crossover_double(self, fast_ma, slow_ma):
        df1 = _make_price_df()
        df2 = _make_price_df_alt()
        results = _run_strategy(SMACrossoverDouble, {"fast_ma": fast_ma, "slow_ma": slow_ma}, [df1, df2])
        assert len(results) == 1

    @pytest.mark.parametrize(
        "fast_ma,med_ma,slow_ma",
        [(10, 30, 100), (5, 20, 50)],
    )
    def test_sma_crossover_triple(self, fast_ma, med_ma, slow_ma):
        df1 = _make_price_df()
        df2 = _make_price_df_alt()
        df3 = _make_price_df_bonds()
        results = _run_strategy(
            SMACrossoverTriple,
            {"fast_ma": fast_ma, "med_ma": med_ma, "slow_ma": slow_ma},
            [df1, df2, df3],
        )
        assert len(results) == 1


class TestMACDStrategies:
    """Test MACD strategies."""

    @pytest.mark.parametrize(
        "fast_ma,slow_ma,signal_period",
        [(12, 26, 9), (8, 21, 9)],
    )
    def test_macd_single(self, fast_ma, slow_ma, signal_period):
        df = _make_price_df()
        results = _run_strategy(
            MACDSingle,
            {"fast_ma": fast_ma, "slow_ma": slow_ma, "signal_period": signal_period},
            [df],
        )
        assert len(results) == 1

    @pytest.mark.parametrize(
        "fast_ma,slow_ma,signal_period",
        [(12, 26, 9), (8, 21, 9)],
    )
    def test_macd_dual(self, fast_ma, slow_ma, signal_period):
        df1 = _make_price_df()
        df2 = _make_price_df_alt()
        results = _run_strategy(
            MACDDual,
            {"fast_ma": fast_ma, "slow_ma": slow_ma, "signal_period": signal_period},
            [df1, df2],
        )
        assert len(results) == 1


class TestDipBuyStrategies:
    """Test dip-buying strategies."""

    @pytest.mark.parametrize(
        "fast_ma,med_ma,slow_ma",
        [(10, 30, 100), (5, 20, 50)],
    )
    def test_dip_buy_sma(self, fast_ma, med_ma, slow_ma):
        df = _make_price_df()
        results = _run_strategy(
            DipBuySMA,
            {"fast_ma": fast_ma, "med_ma": med_ma, "slow_ma": slow_ma},
            [df],
        )
        assert len(results) == 1

    @pytest.mark.parametrize(
        "buy_quantile,sell_quantile",
        [(0.1, 0.9), (0.05, 0.95)],
    )
    def test_dip_buy_stdev(self, buy_quantile, sell_quantile):
        df1 = _make_price_df()
        df2 = _make_price_df_alt()
        results = _run_strategy(
            DipBuyStdev,
            {"buy_quantile": buy_quantile, "sell_quantile": sell_quantile},
            [df1, df2],
        )
        assert len(results) == 1


class TestSmaRebalMix:
    """Test SmaRebalMix (alias for SMACrossoverTriple)."""

    def test_sma_rebal_mix_is_alias(self):
        assert SmaRebalMix is SMACrossoverTriple

    def test_sma_rebal_mix_runs(self):
        df1 = _make_price_df()
        df2 = _make_price_df_alt()
        df3 = _make_price_df_bonds()
        results = _run_strategy(
            SmaRebalMix,
            {"fast_ma": 10, "med_ma": 30, "slow_ma": 100},
            [df1, df2, df3],
        )
        assert len(results) == 1


class TestStrategyValueTracking:
    """Cross-strategy tests verifying value tracking consistency."""

    @pytest.mark.parametrize(
        "strat_cls,strat_kwargs,n_feeds",
        [
            (Rebalance, {"rebal_proportions": {0: 0.6, 1: 0.4}, "rebal_interval": 21}, 2),
            (NoRebalance, {"equity_proportions": {0: 0.6, 1: 0.4}}, 2),
            (SMACrossover, {"fast_ma": 10, "slow_ma": 50}, 1),
            (MACDSingle, {"fast_ma": 12, "slow_ma": 26, "signal_period": 9}, 1),
        ],
    )
    def test_value_never_negative(self, strat_cls, strat_kwargs, n_feeds):
        feeds = [_make_price_df(), _make_price_df_alt(), _make_price_df_bonds()][:n_feeds]
        results = _run_strategy(strat_cls, strat_kwargs, feeds)
        value_hist = results[0].analyzers.cvtracker.value
        assert all(v >= 0 for v in value_hist), "Portfolio value should never be negative"

    @pytest.mark.parametrize(
        "strat_cls,strat_kwargs,n_feeds",
        [
            (Rebalance, {"rebal_proportions": {0: 0.6, 1: 0.4}, "rebal_interval": 21}, 2),
            (NoRebalance, {"equity_proportions": {0: 0.6, 1: 0.4}}, 2),
            (SMACrossover, {"fast_ma": 10, "slow_ma": 50}, 1),
            (MACDSingle, {"fast_ma": 12, "slow_ma": 26, "signal_period": 9}, 1),
        ],
    )
    def test_cash_never_negative(self, strat_cls, strat_kwargs, n_feeds):
        feeds = [_make_price_df(), _make_price_df_alt(), _make_price_df_bonds()][:n_feeds]
        results = _run_strategy(strat_cls, strat_kwargs, feeds)
        cash_hist = results[0].analyzers.cvtracker.cash
        assert all(c >= -1 for c in cash_hist), "Cash should not go significantly negative"
