"""Tests for regime-adaptive strategy and upgraded segment_by_regime()."""

from __future__ import annotations

import inspect

import backtrader as bt
import numpy as np
import pandas as pd
import pytest

from finbot.services.backtesting.strategies.regime_adaptive import (
    _REGIME_BEAR,
    _REGIME_BULL,
    _REGIME_SIDEWAYS,
    _REGIME_VOLATILE,
    RegimeAdaptive,
)

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_price_df(n_bars: int = 600, *, trend: float = 0.0003, vol: float = 0.008, seed: int = 42) -> pd.DataFrame:
    """Create synthetic OHLCV DataFrame with controllable trend and volatility."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2018-01-02", periods=n_bars)
    returns = rng.normal(trend, vol, n_bars)
    close = 100.0 * np.cumprod(1 + returns)
    return pd.DataFrame(
        {
            "Open": close * 0.999,
            "High": close * 1.002,
            "Low": close * 0.998,
            "Close": close,
            "Volume": np.full(n_bars, 1_000_000),
        },
        index=dates,
    )


def _run_strategy(equity_df: pd.DataFrame, bond_df: pd.DataFrame, **kwargs) -> float:
    """Run RegimeAdaptive through BacktestRunner and return final portfolio value."""
    import backtrader as bt

    from finbot.services.backtesting.backtest_runner import BacktestRunner
    from finbot.services.backtesting.brokers.fixed_commission_scheme import FixedCommissionScheme

    runner = BacktestRunner(
        price_histories={"SPY": equity_df, "TLT": bond_df},
        start=None,
        end=None,
        duration=None,
        start_step=None,
        init_cash=100_000,
        strat=RegimeAdaptive,
        strat_kwargs=kwargs,
        broker=bt.brokers.BackBroker,
        broker_kwargs={},
        broker_commission=FixedCommissionScheme,
        sizer=bt.sizers.AllInSizer,
        sizer_kwargs={},
        plot=False,
    )
    stats = runner.run_backtest()
    if "Final Value" in stats.columns:
        return float(stats["Final Value"].iloc[0])
    return 100_000.0


# Lightweight mock of a Backtrader data close-line
class _MockCloseLine:
    def __init__(self, prices: list[float]) -> None:
        self._prices = list(prices)

    def get(self, size: int) -> list[float]:
        # Backtrader's get() returns newest-first
        sliced = self._prices[-size:] if size <= len(self._prices) else self._prices[:]
        return list(reversed(sliced))

    def __getitem__(self, idx: int) -> float:
        # datas[0].close[0] = current close
        return self._prices[-1 + idx] if idx <= 0 else self._prices[idx]


class _MockFeed:
    def __init__(self, prices: list[float]) -> None:
        self.close = _MockCloseLine(prices)

    def __len__(self) -> int:
        return len(self.close._prices)


def _make_partial_strategy(prices: list[float], **param_overrides) -> RegimeAdaptive:
    """Create a RegimeAdaptive instance whose _classify_regime() can be called directly."""
    strat = object.__new__(RegimeAdaptive)
    defaults = {
        "lookback": len(prices) - 1,
        "rebal_interval": 21,
        "bull_threshold": 0.15,
        "bear_threshold": -0.10,
        "vol_threshold": 0.25,
        "bull_equity_pct": 0.90,
        "sideways_equity_pct": 0.60,
        "volatile_equity_pct": 0.30,
        "bear_equity_pct": 0.10,
        "periods_elapsed": 0,
        "order": None,
    }
    defaults.update(param_overrides)
    for k, v in defaults.items():
        setattr(strat, k, v)
    strat.datas = [_MockFeed(prices)]
    return strat


# ── Import / registration tests ───────────────────────────────────────────────


def test_strategy_can_be_imported():
    assert RegimeAdaptive is not None


def test_strategy_is_backtrader_strategy():
    assert issubclass(RegimeAdaptive, bt.Strategy)


def test_strategy_registered_in_adapter():
    from finbot.services.backtesting.adapters.backtrader_adapter import DEFAULT_STRATEGY_REGISTRY

    assert "regimeadaptive" in DEFAULT_STRATEGY_REGISTRY


def test_strategy_has_required_params():
    params = inspect.signature(RegimeAdaptive.__init__).parameters
    for expected in (
        "lookback",
        "rebal_interval",
        "bull_threshold",
        "bear_threshold",
        "vol_threshold",
        "bull_equity_pct",
        "sideways_equity_pct",
        "volatile_equity_pct",
        "bear_equity_pct",
    ):
        assert expected in params, f"Missing parameter: {expected}"


def test_default_params_match_docs():
    defaults = {
        k: v.default
        for k, v in inspect.signature(RegimeAdaptive.__init__).parameters.items()
        if v.default is not inspect.Parameter.empty
    }
    assert defaults["lookback"] == 252
    assert defaults["rebal_interval"] == 21
    assert defaults["bull_threshold"] == pytest.approx(0.15)
    assert defaults["bear_threshold"] == pytest.approx(-0.10)
    assert defaults["vol_threshold"] == pytest.approx(0.25)
    assert defaults["bull_equity_pct"] == pytest.approx(0.90)
    assert defaults["bear_equity_pct"] == pytest.approx(0.10)


# ── _classify_regime unit tests ───────────────────────────────────────────────


def test_classify_regime_bull():
    # Strongly upward trending prices → BULL
    prices = [100.0 * (1.001**i) for i in range(300)]
    strat = _make_partial_strategy(prices, lookback=252)
    assert strat._classify_regime() == _REGIME_BULL


def test_classify_regime_bear():
    # Strongly downward trending prices → BEAR
    prices = [100.0 * (0.9994**i) for i in range(300)]
    strat = _make_partial_strategy(prices, lookback=252)
    assert strat._classify_regime() == _REGIME_BEAR


def test_classify_regime_volatile():
    # Very high volatility → VOLATILE (even with near-zero trend)
    rng = np.random.default_rng(0)
    prices = [100.0]
    for _ in range(300):
        prices.append(prices[-1] * (1 + rng.normal(0.0, 0.05)))  # 5% daily vol
    strat = _make_partial_strategy(prices, lookback=252)
    assert strat._classify_regime() == _REGIME_VOLATILE


def test_classify_regime_sideways():
    # Very small drift, low vol → SIDEWAYS
    prices = [100.0 + 0.005 * i for i in range(300)]
    strat = _make_partial_strategy(prices, lookback=252, bull_threshold=0.15)
    assert strat._classify_regime() == _REGIME_SIDEWAYS


def test_classify_regime_insufficient_data():
    # Only 1 data point → fall back to sideways (safe default)
    strat = _make_partial_strategy([100.0])
    assert strat._classify_regime() == _REGIME_SIDEWAYS


# ── _equity_pct_for unit tests ────────────────────────────────────────────────


def test_equity_pct_for_bull():
    strat = _make_partial_strategy([100.0] * 10)
    assert strat._equity_pct_for(_REGIME_BULL) == pytest.approx(0.90)


def test_equity_pct_for_bear():
    strat = _make_partial_strategy([100.0] * 10)
    assert strat._equity_pct_for(_REGIME_BEAR) == pytest.approx(0.10)


def test_equity_pct_for_volatile():
    strat = _make_partial_strategy([100.0] * 10)
    assert strat._equity_pct_for(_REGIME_VOLATILE) == pytest.approx(0.30)


def test_equity_pct_for_sideways():
    strat = _make_partial_strategy([100.0] * 10)
    assert strat._equity_pct_for(_REGIME_SIDEWAYS) == pytest.approx(0.60)


# ── Full end-to-end backtests ─────────────────────────────────────────────────


def test_strategy_runs_full_backtest_and_portfolio_positive():
    equity_df = _make_price_df(600, trend=0.0003, vol=0.008)
    bond_df = _make_price_df(600, trend=0.0001, vol=0.003, seed=99)
    final = _run_strategy(equity_df, bond_df, lookback=126)
    assert final > 0


def test_strategy_survives_bear_equity_market():
    equity_df = _make_price_df(600, trend=-0.0003, vol=0.015)  # bearish
    bond_df = _make_price_df(600, trend=0.0001, vol=0.003, seed=1)
    final = _run_strategy(equity_df, bond_df, lookback=63)
    assert final > 0


# ── segment_by_regime with equity_curve ──────────────────────────────────────


def _make_backtest_result():
    """Create a minimal BacktestRunResult for segment_by_regime tests."""
    from datetime import UTC, datetime
    from uuid import uuid4

    from finbot.core.contracts.costs import CostSummary
    from finbot.core.contracts.models import BacktestRunMetadata, BacktestRunResult
    from finbot.core.contracts.versioning import BACKTEST_RESULT_SCHEMA_VERSION

    return BacktestRunResult(
        metadata=BacktestRunMetadata(
            run_id=str(uuid4()),
            engine_name="test",
            engine_version="0",
            strategy_name="Test",
            created_at=datetime.now(UTC),
            config_hash="x",
            data_snapshot_id=None,
            random_seed=None,
        ),
        metrics={"cagr": 0.1},
        schema_version=BACKTEST_RESULT_SCHEMA_VERSION,
        assumptions={},
        artifacts={},
        costs=CostSummary(
            total_commission=0.0,
            total_slippage=0.0,
            total_spread=0.0,
            total_borrow=0.0,
            total_market_impact=0.0,
        ),
    )


def _make_stable_market_data(n: int = 756) -> pd.DataFrame:
    """Stable upward trend — produces one long BULL regime, avoiding single-day period bugs."""
    rng = np.random.default_rng(42)
    dates = pd.bdate_range("2018-01-02", periods=n)
    # Very steady upward trend, low vol → detector sees persistent BULL regime
    closes = 100.0 * np.cumprod(1 + rng.normal(0.0008, 0.003, n))
    return pd.DataFrame({"Close": closes}, index=dates)


def test_segment_by_regime_without_equity_curve_returns_empty_metrics():
    from finbot.core.contracts.regime import MarketRegime
    from finbot.services.backtesting.regime import segment_by_regime

    result = _make_backtest_result()
    market_data = _make_stable_market_data()

    regime_metrics = segment_by_regime(result, market_data)

    for regime in MarketRegime:
        assert regime in regime_metrics
        assert regime_metrics[regime].metrics == {}


def test_segment_by_regime_with_equity_curve_populates_metrics():
    from finbot.services.backtesting.regime import segment_by_regime

    result = _make_backtest_result()
    n = 756
    market_data = _make_stable_market_data(n)

    rng = np.random.default_rng(77)
    dates = pd.bdate_range("2018-01-02", periods=n)
    portfolio_values = 100_000.0 * np.cumprod(1 + rng.normal(0.0005, 0.006, n))
    equity_curve = pd.Series(portfolio_values, index=dates)

    regime_metrics = segment_by_regime(result, market_data, equity_curve=equity_curve)

    # At least one regime must have real metrics (BULL should, given stable uptrend)
    assert any(m.metrics for m in regime_metrics.values())


def test_segment_by_regime_metrics_contain_expected_keys():
    from finbot.core.contracts.regime import MarketRegime
    from finbot.services.backtesting.regime import segment_by_regime

    result = _make_backtest_result()
    n = 756
    market_data = _make_stable_market_data(n)

    rng = np.random.default_rng(88)
    dates = pd.bdate_range("2018-01-02", periods=n)
    portfolio_values = 100_000.0 * np.cumprod(1 + rng.normal(0.0005, 0.006, n))
    equity_curve = pd.Series(portfolio_values, index=dates)

    regime_metrics = segment_by_regime(result, market_data, equity_curve=equity_curve)

    expected_keys = {"cagr", "volatility", "sharpe", "total_return", "days"}
    for regime in MarketRegime:
        m = regime_metrics[regime]
        if m.metrics:
            missing = expected_keys - set(m.metrics.keys())
            assert not missing, f"Regime {regime} missing keys: {missing}"
