"""Tests for new strategies (DualMomentum, RiskParity) and multi-asset Monte Carlo."""

import backtrader as bt
import numpy as np
import pandas as pd
import pytest

from finbot.services.backtesting.backtest_runner import BacktestRunner
from finbot.services.backtesting.brokers.commission_schemes import CommInfo_NoCommission
from finbot.services.backtesting.strategies.dual_momentum import DualMomentum
from finbot.services.backtesting.strategies.risk_parity import RiskParity
from finbot.services.simulation.monte_carlo.multi_asset_monte_carlo import multi_asset_monte_carlo


def _make_price_df(length: int = 500, seed: int = 42, trend: float = 0.0003) -> pd.DataFrame:
    """Create a synthetic price DataFrame for testing."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2015-01-01", periods=length)
    changes = rng.normal(trend, 0.01, length)
    changes[0] = 0
    prices = 100 * np.cumprod(1 + changes)
    return pd.DataFrame(
        {
            "Open": prices * 0.999,
            "High": prices * 1.005,
            "Low": prices * 0.995,
            "Close": prices,
            "Volume": rng.integers(1_000_000, 10_000_000, length),
        },
        index=dates,
    )


class TestDualMomentum:
    def test_runs_with_two_assets(self):
        ph1 = _make_price_df(seed=42, trend=0.0005)
        ph2 = _make_price_df(seed=99, trend=0.0001)
        runner = BacktestRunner(
            price_histories={"SPY": ph1, "TLT": ph2},
            start=None,
            end=None,
            duration=None,
            start_step=None,
            init_cash=10000.0,
            strat=DualMomentum,
            strat_kwargs={"lookback": 63, "rebal_interval": 21},
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=CommInfo_NoCommission,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )
        stats = runner.run_backtest()
        assert isinstance(stats, pd.DataFrame)
        assert "CAGR" in stats.columns

    def test_value_stays_positive(self):
        ph1 = _make_price_df(seed=42)
        ph2 = _make_price_df(seed=99)
        runner = BacktestRunner(
            price_histories={"A": ph1, "B": ph2},
            start=None,
            end=None,
            duration=None,
            start_step=None,
            init_cash=10000.0,
            strat=DualMomentum,
            strat_kwargs={"lookback": 63, "rebal_interval": 21},
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=CommInfo_NoCommission,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )
        runner.run_backtest()
        vh = runner.get_value_history()
        assert (vh["Value"] > 0).all()


class TestRiskParity:
    def test_runs_with_two_assets(self):
        ph1 = _make_price_df(seed=42)
        ph2 = _make_price_df(seed=99)
        runner = BacktestRunner(
            price_histories={"SPY": ph1, "TLT": ph2},
            start=None,
            end=None,
            duration=None,
            start_step=None,
            init_cash=10000.0,
            strat=RiskParity,
            strat_kwargs={"vol_window": 30, "rebal_interval": 21},
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=CommInfo_NoCommission,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )
        stats = runner.run_backtest()
        assert isinstance(stats, pd.DataFrame)
        assert "Sharpe" in stats.columns

    def test_value_stays_positive(self):
        ph1 = _make_price_df(seed=42)
        ph2 = _make_price_df(seed=99)
        runner = BacktestRunner(
            price_histories={"A": ph1, "B": ph2},
            start=None,
            end=None,
            duration=None,
            start_step=None,
            init_cash=10000.0,
            strat=RiskParity,
            strat_kwargs={"vol_window": 30, "rebal_interval": 21},
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=CommInfo_NoCommission,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )
        runner.run_backtest()
        vh = runner.get_value_history()
        assert (vh["Value"] > 0).all()


class TestMultiAssetMonteCarlo:
    def _make_asset_data(self, seed: int, length: int = 252) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        dates = pd.bdate_range("2020-01-01", periods=length)
        prices = 100 * np.cumprod(1 + rng.normal(0.0003, 0.01, length))
        return pd.DataFrame({"Close": prices}, index=dates)

    def test_returns_expected_keys(self):
        data = {
            "SPY": self._make_asset_data(42),
            "TLT": self._make_asset_data(99),
        }
        result = multi_asset_monte_carlo(data, sim_periods=50, n_sims=10)
        assert "portfolio_trials" in result
        assert "asset_trials" in result
        assert "correlation" in result
        assert "weights" in result

    def test_portfolio_trials_shape(self):
        data = {
            "SPY": self._make_asset_data(42),
            "TLT": self._make_asset_data(99),
        }
        result = multi_asset_monte_carlo(data, sim_periods=50, n_sims=20)
        assert result["portfolio_trials"].shape == (20, 50)

    def test_correlation_matrix_shape(self):
        data = {
            "A": self._make_asset_data(42),
            "B": self._make_asset_data(99),
            "C": self._make_asset_data(7),
        }
        result = multi_asset_monte_carlo(data, sim_periods=30, n_sims=5)
        assert result["correlation"].shape == (3, 3)

    def test_custom_weights(self):
        data = {
            "SPY": self._make_asset_data(42),
            "TLT": self._make_asset_data(99),
        }
        result = multi_asset_monte_carlo(data, sim_periods=30, n_sims=5, weights={"SPY": 0.6, "TLT": 0.4})
        weights = result["weights"]
        assert abs(weights["SPY"] - 0.6) < 1e-10
        assert abs(weights["TLT"] - 0.4) < 1e-10

    def test_requires_at_least_two_assets(self):
        data = {"SPY": self._make_asset_data(42)}
        with pytest.raises(ValueError, match="at least 2 assets"):
            multi_asset_monte_carlo(data, sim_periods=30, n_sims=5)

    def test_asset_trials_per_asset(self):
        data = {
            "SPY": self._make_asset_data(42),
            "TLT": self._make_asset_data(99),
        }
        result = multi_asset_monte_carlo(data, sim_periods=30, n_sims=10)
        assert "SPY" in result["asset_trials"]
        assert "TLT" in result["asset_trials"]
        assert result["asset_trials"]["SPY"].shape == (10, 30)
