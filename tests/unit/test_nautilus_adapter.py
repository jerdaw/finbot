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
    adapter = NautilusAdapter(histories)
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
    adapter = NautilusAdapter({"SPY": _make_price_df(seed=1)})
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


def test_nautilus_adapter_rejects_non_rebalance_strategy() -> None:
    adapter = NautilusAdapter({"SPY": _make_price_df(seed=1)})
    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("SPY",),
        start=None,
        end=None,
        initial_cash=100_000.0,
        parameters={"equity_proportions": [1.0]},
    )

    with pytest.raises(ValueError, match="supports only strategy_name='rebalance'"):
        adapter.run(request)


def test_nautilus_adapter_requires_rebalance_parameters() -> None:
    adapter = NautilusAdapter({"SPY": _make_price_df(seed=1)})
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
