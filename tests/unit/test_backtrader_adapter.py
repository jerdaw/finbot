"""Unit tests for the Backtrader adapter contract implementation."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from finbot.core.contracts import BACKTEST_RESULT_SCHEMA_VERSION, BacktestRunRequest
from finbot.services.backtesting.adapters import BacktraderAdapter


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


@pytest.mark.parametrize(
    ("strategy_name", "symbols", "parameters"),
    [
        ("NoRebalance", ("SPY",), {"equity_proportions": [1.0]}),
        ("DualMomentum", ("SPY", "TLT"), {"lookback": 252, "rebal_interval": 21}),
        ("RiskParity", ("SPY", "QQQ", "TLT"), {"vol_window": 63, "rebal_interval": 21}),
    ],
)
def test_backtrader_adapter_runs_contract_output(
    strategy_name: str,
    symbols: tuple[str, ...],
    parameters: dict[str, object],
) -> None:
    histories = {
        "SPY": _make_price_df(seed=1),
        "TLT": _make_price_df(start_price=80.0, seed=2),
        "QQQ": _make_price_df(start_price=120.0, seed=3),
    }
    adapter = BacktraderAdapter(histories)
    request = BacktestRunRequest(
        strategy_name=strategy_name,
        symbols=symbols,
        start=pd.Timestamp("2019-01-01"),
        end=pd.Timestamp("2019-12-31"),
        initial_cash=100_000.0,
        parameters=parameters,
    )

    result = adapter.run(request)
    assert result.schema_version == BACKTEST_RESULT_SCHEMA_VERSION
    assert result.metadata.engine_name == "backtrader"
    assert result.metadata.strategy_name.lower() == strategy_name.lower()
    assert "roi" in result.metrics
    assert "cagr" in result.metrics
    assert "max_drawdown" in result.metrics


def test_backtrader_adapter_rejects_unknown_strategy() -> None:
    adapter = BacktraderAdapter({"SPY": _make_price_df()})
    request = BacktestRunRequest(
        strategy_name="UnknownStrategy",
        symbols=("SPY",),
        start=None,
        end=None,
        initial_cash=100_000.0,
        parameters={},
    )

    with pytest.raises(ValueError, match="Unknown strategy"):
        adapter.run(request)


def test_backtrader_adapter_rejects_missing_symbol_history() -> None:
    adapter = BacktraderAdapter({"SPY": _make_price_df()})
    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("SPY", "TLT"),
        start=None,
        end=None,
        initial_cash=100_000.0,
        parameters={"equity_proportions": [0.5, 0.5]},
    )

    with pytest.raises(ValueError, match="Missing price history"):
        adapter.run(request)
