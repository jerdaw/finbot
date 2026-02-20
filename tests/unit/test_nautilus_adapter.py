"""Unit tests for Nautilus pilot adapter contract behavior."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from finbot.adapters.nautilus import NautilusAdapter
from finbot.core.contracts import BacktestRunRequest


def _make_price_df(n_days: int = 320, start_price: float = 100.0, seed: int = 42) -> pd.DataFrame:
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


def test_nautilus_adapter_runs_pilot_fallback() -> None:
    histories = {
        "SPY": _make_price_df(seed=1),
        "TLT": _make_price_df(start_price=80.0, seed=2),
    }
    adapter = NautilusAdapter(histories, enable_native_execution=False)
    request = BacktestRunRequest(
        strategy_name="Rebalance",
        symbols=("SPY", "TLT"),
        start=pd.Timestamp("2019-01-01"),
        end=pd.Timestamp("2019-12-31"),
        initial_cash=100_000.0,
        parameters={"rebal_proportions": [0.6, 0.4], "rebal_interval": 21},
    )

    result = adapter.run(request)
    assert result.metadata.engine_name == "nautilus-pilot"
    assert result.metadata.run_id.startswith("nt-")
    assert "roi" in result.metrics
    assert result.assumptions["adapter_mode"] == "backtrader_fallback"
    assert result.artifacts["pilot_mode"] == "fallback"
    assert any("fallback" in warning for warning in result.warnings)


def test_nautilus_adapter_run_backtest_alias() -> None:
    adapter = NautilusAdapter({"SPY": _make_price_df(seed=1)}, enable_native_execution=False)
    request = BacktestRunRequest(
        strategy_name="Rebalance",
        symbols=("SPY",),
        start=None,
        end=None,
        initial_cash=100_000.0,
        parameters={"rebal_proportions": [1.0], "rebal_interval": 63},
    )
    result = adapter.run_backtest(request)
    assert result.metadata.engine_name == "nautilus-pilot"


def test_nautilus_adapter_rejects_unknown_strategy() -> None:
    adapter = NautilusAdapter({"SPY": _make_price_df(seed=1)}, enable_native_execution=False)
    request = BacktestRunRequest(
        strategy_name="SmaCrossover",
        symbols=("SPY",),
        start=None,
        end=None,
        initial_cash=100_000.0,
        parameters={"equity_proportions": [1.0]},
    )

    with pytest.raises(ValueError, match="supports strategy_name in"):
        adapter.run(request)


def test_nautilus_adapter_requires_rebalance_parameters() -> None:
    adapter = NautilusAdapter({"SPY": _make_price_df(seed=1)}, enable_native_execution=False)
    request = BacktestRunRequest(
        strategy_name="Rebalance",
        symbols=("SPY",),
        start=None,
        end=None,
        initial_cash=100_000.0,
        parameters={},
    )

    with pytest.raises(ValueError, match="requires 'rebal_proportions'"):
        adapter.run(request)


def test_nautilus_adapter_uses_native_path_when_available(monkeypatch: pytest.MonkeyPatch) -> None:
    adapter = NautilusAdapter({"SPY": _make_price_df(seed=1)}, enable_backtrader_fallback=False)
    request = BacktestRunRequest(
        strategy_name="Rebalance",
        symbols=("SPY",),
        start=pd.Timestamp("2019-01-01"),
        end=pd.Timestamp("2019-12-31"),
        initial_cash=100_000.0,
        parameters={"rebal_proportions": [1.0], "rebal_interval": 21},
    )

    monkeypatch.setattr(adapter, "_supports_native_nautilus", lambda: True)
    monkeypatch.setattr(
        adapter,
        "_run_via_nautilus",
        lambda _request: (
            {
                "starting_value": 100_000.0,
                "ending_value": 101_000.0,
                "roi": 0.01,
                "cagr": 0.01,
                "sharpe": 1.0,
                "max_drawdown": -0.02,
                "mean_cash_utilization": 0.9,
            },
            {"nautilus_strategy": "EMACross", "adapter_mode": "native_nautilus_proxy"},
            {"nautilus_venue": "XNAS"},
            ("native warning",),
        ),
    )

    result = adapter.run(request)
    assert result.metadata.engine_name == "nautilus-pilot"
    assert result.assumptions["adapter_mode"] == "native_nautilus_proxy"
    assert result.artifacts["pilot_mode"] == "native"
    assert result.metrics["roi"] == pytest.approx(0.01)
    assert "native warning" in result.warnings


def test_nautilus_adapter_accepts_norebalance_single_symbol_with_native(monkeypatch: pytest.MonkeyPatch) -> None:
    adapter = NautilusAdapter({"SPY": _make_price_df(seed=1)}, enable_backtrader_fallback=False)
    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("SPY",),
        start=pd.Timestamp("2019-01-01"),
        end=pd.Timestamp("2019-12-31"),
        initial_cash=100_000.0,
        parameters={"equity_proportions": [1.0]},
    )

    monkeypatch.setattr(adapter, "_supports_native_nautilus", lambda: True)
    monkeypatch.setattr(
        adapter,
        "_run_via_nautilus",
        lambda _request: (
            {
                "starting_value": 100_000.0,
                "ending_value": 110_000.0,
                "roi": 0.10,
                "cagr": 0.10,
                "sharpe": 1.2,
                "max_drawdown": -0.10,
                "mean_cash_utilization": 0.99,
            },
            {
                "nautilus_strategy": "BuyAndHoldStrategy",
                "strategy_equivalent": True,
                "equivalence_notes": "NoRebalance mapped to buy-and-hold",
                "confidence": "high",
            },
            {"nautilus_venue": "XNAS"},
            (),
        ),
    )

    result = adapter.run(request)
    assert result.assumptions["adapter_mode"] == "native_nautilus"
    assert result.assumptions["strategy_equivalent"] is True
    assert result.assumptions["confidence"] == "high"


def test_nautilus_adapter_rejects_norebalance_multi_symbol_request() -> None:
    adapter = NautilusAdapter(
        {"SPY": _make_price_df(seed=1), "TLT": _make_price_df(seed=2)},
        enable_native_execution=False,
    )
    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("SPY", "TLT"),
        start=pd.Timestamp("2019-01-01"),
        end=pd.Timestamp("2019-12-31"),
        initial_cash=100_000.0,
        parameters={"equity_proportions": [0.6, 0.4]},
    )

    with pytest.raises(ValueError, match="exactly one symbol"):
        adapter.run(request)


def test_nautilus_adapter_rejects_dualmomentum_single_symbol() -> None:
    adapter = NautilusAdapter({"SPY": _make_price_df(seed=1)}, enable_native_execution=False)
    request = BacktestRunRequest(
        strategy_name="DualMomentum",
        symbols=("SPY",),
        start=pd.Timestamp("2019-01-01"),
        end=pd.Timestamp("2019-12-31"),
        initial_cash=100_000.0,
        parameters={"lookback": 252, "rebal_interval": 21},
    )

    with pytest.raises(ValueError, match="exactly two symbols"):
        adapter.run(request)


def test_nautilus_adapter_rejects_riskparity_single_symbol() -> None:
    adapter = NautilusAdapter({"SPY": _make_price_df(seed=1)}, enable_native_execution=False)
    request = BacktestRunRequest(
        strategy_name="RiskParity",
        symbols=("SPY",),
        start=pd.Timestamp("2019-01-01"),
        end=pd.Timestamp("2019-12-31"),
        initial_cash=100_000.0,
        parameters={"vol_window": 63, "rebal_interval": 21},
    )

    with pytest.raises(ValueError, match="at least two symbols"):
        adapter.run(request)


def test_nautilus_adapter_runs_dualmomentum_proxy_native(monkeypatch: pytest.MonkeyPatch) -> None:
    adapter = NautilusAdapter(
        {"SPY": _make_price_df(seed=1), "TLT": _make_price_df(start_price=80.0, seed=2)},
        enable_backtrader_fallback=False,
    )
    request = BacktestRunRequest(
        strategy_name="DualMomentum",
        symbols=("SPY", "TLT"),
        start=pd.Timestamp("2019-01-01"),
        end=pd.Timestamp("2019-12-31"),
        initial_cash=100_000.0,
        parameters={"lookback": 63, "rebal_interval": 21},
    )

    monkeypatch.setattr(adapter, "_supports_native_nautilus", lambda: True)
    result = adapter.run(request)

    assert result.assumptions["adapter_mode"] == "native_nautilus_proxy"
    assert result.assumptions["execution_fidelity"] == "proxy_native"
    assert result.assumptions["strategy_equivalent"] is True
    assert result.assumptions["confidence"] == "medium"
    assert result.metrics["ending_value"] > 0


def test_nautilus_adapter_runs_riskparity_proxy_native(monkeypatch: pytest.MonkeyPatch) -> None:
    adapter = NautilusAdapter(
        {
            "SPY": _make_price_df(seed=1),
            "QQQ": _make_price_df(start_price=120.0, seed=3),
            "TLT": _make_price_df(start_price=80.0, seed=2),
        },
        enable_backtrader_fallback=False,
    )
    request = BacktestRunRequest(
        strategy_name="RiskParity",
        symbols=("SPY", "QQQ", "TLT"),
        start=pd.Timestamp("2019-01-01"),
        end=pd.Timestamp("2019-12-31"),
        initial_cash=100_000.0,
        parameters={"vol_window": 63, "rebal_interval": 21},
    )

    monkeypatch.setattr(adapter, "_supports_native_nautilus", lambda: True)
    result = adapter.run(request)

    assert result.assumptions["adapter_mode"] == "native_nautilus_proxy"
    assert result.assumptions["execution_fidelity"] == "proxy_native"
    assert result.assumptions["strategy_equivalent"] is True
    assert result.assumptions["confidence"] == "medium"
    assert result.metrics["ending_value"] > 0


def test_nautilus_adapter_dualmomentum_uses_full_native_when_available(monkeypatch: pytest.MonkeyPatch) -> None:
    adapter = NautilusAdapter(
        {"SPY": _make_price_df(seed=1), "TLT": _make_price_df(start_price=80.0, seed=2)},
        enable_backtrader_fallback=False,
    )
    request = BacktestRunRequest(
        strategy_name="DualMomentum",
        symbols=("SPY", "TLT"),
        start=pd.Timestamp("2019-01-01"),
        end=pd.Timestamp("2019-12-31"),
        initial_cash=100_000.0,
        parameters={"lookback": 63, "rebal_interval": 21},
    )

    monkeypatch.setattr(adapter, "_supports_native_nautilus", lambda: True)
    monkeypatch.setattr(
        adapter,
        "_run_via_nautilus_dual_momentum_native",
        lambda _request: (
            {
                "starting_value": 100_000.0,
                "ending_value": 120_000.0,
                "roi": 0.2,
                "cagr": 0.18,
                "sharpe": 1.1,
                "max_drawdown": -0.11,
                "mean_cash_utilization": 0.8,
            },
            {
                "nautilus_strategy": "DualMomentumNativeStrategy",
                "adapter_mode": "native_nautilus_full",
                "execution_fidelity": "full_native",
                "strategy_equivalent": False,
                "confidence": "low",
            },
            {"nautilus_strategy_impl": "full_native"},
            (),
        ),
    )

    result = adapter.run(request)

    assert result.assumptions["adapter_mode"] == "native_nautilus_full"
    assert result.assumptions["execution_fidelity"] == "full_native"
    assert result.assumptions["strategy_equivalent"] is False
    assert result.assumptions["confidence"] == "low"


def test_nautilus_adapter_dualmomentum_full_native_failure_falls_back_to_proxy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter = NautilusAdapter(
        {"SPY": _make_price_df(seed=1), "TLT": _make_price_df(start_price=80.0, seed=2)},
        enable_backtrader_fallback=False,
    )
    request = BacktestRunRequest(
        strategy_name="DualMomentum",
        symbols=("SPY", "TLT"),
        start=pd.Timestamp("2019-01-01"),
        end=pd.Timestamp("2019-12-31"),
        initial_cash=100_000.0,
        parameters={"lookback": 63, "rebal_interval": 21},
    )

    monkeypatch.setattr(adapter, "_supports_native_nautilus", lambda: True)
    monkeypatch.setattr(
        adapter,
        "_run_via_nautilus_dual_momentum_native",
        lambda _request: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    monkeypatch.setattr(
        adapter,
        "_run_via_nautilus_dual_momentum_proxy",
        lambda _request: (
            {
                "starting_value": 100_000.0,
                "ending_value": 101_000.0,
                "roi": 0.01,
                "cagr": 0.01,
                "sharpe": 0.4,
                "max_drawdown": -0.05,
                "mean_cash_utilization": 0.75,
            },
            {
                "nautilus_strategy": "DualMomentumProxy",
                "adapter_mode": "native_nautilus_proxy",
                "execution_fidelity": "proxy_native",
                "strategy_equivalent": True,
                "confidence": "medium",
            },
            {"nautilus_proxy_type": "dual_momentum"},
            (),
        ),
    )

    result = adapter.run(request)

    assert result.assumptions["adapter_mode"] == "native_nautilus_proxy"
    assert result.assumptions["execution_fidelity"] == "proxy_native"
    assert any("fell back to proxy-native mode" in warning for warning in result.warnings)


def test_build_metrics_from_equity_curve_tracks_mean_cash_utilization() -> None:
    adapter = NautilusAdapter({"SPY": _make_price_df(seed=1)}, enable_native_execution=False)
    index = pd.date_range("2024-01-01", periods=3, freq="D")
    equity_curve = pd.Series([100.0, 120.0, 110.0], index=index)
    cash_curve = pd.Series([100.0, 20.0, 10.0], index=index)

    metrics = adapter._build_metrics_from_equity_curve(
        equity_curve=equity_curve,
        cash_curve=cash_curve,
        initial_cash=100.0,
    )

    expected = (0.0 + (1.0 - (20.0 / 120.0)) + (1.0 - (10.0 / 110.0))) / 3.0
    assert metrics["mean_cash_utilization"] == pytest.approx(expected)


def test_simulate_dual_momentum_portfolio_returns_aligned_equity_and_cash() -> None:
    adapter = NautilusAdapter({"SPY": _make_price_df(seed=1)}, enable_native_execution=False)
    dates = pd.date_range("2024-01-01", periods=5, freq="D")
    prices = pd.DataFrame(
        {
            "SPY": [100.0, 101.0, 102.0, 103.0, 104.0],
            "TLT": [100.0, 99.0, 98.0, 97.0, 96.0],
        },
        index=dates,
    )

    equity_curve, cash_curve = adapter._simulate_dual_momentum_portfolio(
        prices=prices,
        symbols=("SPY", "TLT"),
        initial_cash=1_000.0,
        lookback=1,
        rebal_interval=1,
    )

    assert len(equity_curve) == len(prices.index)
    assert len(cash_curve) == len(prices.index)
    assert (equity_curve > 0).all()
    assert (cash_curve >= 0).all()


def test_simulate_risk_parity_portfolio_returns_aligned_equity_and_cash() -> None:
    adapter = NautilusAdapter({"SPY": _make_price_df(seed=1)}, enable_native_execution=False)
    dates = pd.date_range("2024-01-01", periods=6, freq="D")
    prices = pd.DataFrame(
        {
            "SPY": [100.0, 101.0, 102.0, 101.0, 103.0, 104.0],
            "QQQ": [100.0, 102.0, 101.0, 103.0, 104.0, 106.0],
            "TLT": [100.0, 99.5, 99.0, 99.2, 99.1, 99.0],
        },
        index=dates,
    )

    equity_curve, cash_curve = adapter._simulate_risk_parity_portfolio(
        prices=prices,
        symbols=("SPY", "QQQ", "TLT"),
        initial_cash=1_000.0,
        vol_window=2,
        rebal_interval=1,
    )

    assert len(equity_curve) == len(prices.index)
    assert len(cash_curve) == len(prices.index)
    assert (equity_curve > 0).all()
    assert (cash_curve >= 0).all()
