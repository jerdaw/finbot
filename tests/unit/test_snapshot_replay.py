"""Unit tests for snapshot replay mode in BacktraderAdapter."""

from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
import pandas as pd
import pytest

from finbot.core.contracts import BacktestRunRequest
from finbot.services.backtesting.adapters import BacktraderAdapter
from finbot.services.backtesting.snapshot_registry import DataSnapshotRegistry


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


def test_snapshot_replay_uses_requested_snapshot_id(tmp_path) -> None:
    histories = {"SPY": _make_price_df(seed=1)}
    snapshot_registry = DataSnapshotRegistry(tmp_path / "snapshots")
    snapshot = snapshot_registry.create_snapshot(
        symbols=["SPY"],
        data=histories,
        start=datetime(2019, 1, 1, tzinfo=UTC),
        end=datetime(2019, 12, 31, tzinfo=UTC),
    )

    adapter = BacktraderAdapter(
        {},
        snapshot_registry=snapshot_registry,
        enable_snapshot_replay=True,
    )
    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("SPY",),
        start=pd.Timestamp("2019-01-01"),
        end=pd.Timestamp("2019-12-31"),
        initial_cash=100_000.0,
        parameters={"equity_proportions": [1.0]},
        data_snapshot_id=snapshot.snapshot_id,
    )

    result = adapter.run(request)
    assert result.metadata.data_snapshot_id == snapshot.snapshot_id


def test_snapshot_replay_requires_registry() -> None:
    adapter = BacktraderAdapter(
        {"SPY": _make_price_df(seed=1)},
        enable_snapshot_replay=True,
    )
    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("SPY",),
        start=None,
        end=None,
        initial_cash=100_000.0,
        parameters={"equity_proportions": [1.0]},
        data_snapshot_id="snap-missing",
    )

    with pytest.raises(ValueError, match="requires snapshot_registry"):
        adapter.run(request)


def test_snapshot_replay_missing_snapshot_raises(tmp_path) -> None:
    snapshot_registry = DataSnapshotRegistry(tmp_path / "snapshots")
    adapter = BacktraderAdapter(
        {"SPY": _make_price_df(seed=1)},
        snapshot_registry=snapshot_registry,
        enable_snapshot_replay=True,
    )
    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("SPY",),
        start=None,
        end=None,
        initial_cash=100_000.0,
        parameters={"equity_proportions": [1.0]},
        data_snapshot_id="snap-does-not-exist",
    )

    with pytest.raises(FileNotFoundError, match="not found in registry"):
        adapter.run(request)


def test_snapshot_replay_is_deterministic_for_same_snapshot(tmp_path) -> None:
    histories = {"SPY": _make_price_df(seed=1)}
    snapshot_registry = DataSnapshotRegistry(tmp_path / "snapshots")
    snapshot = snapshot_registry.create_snapshot(
        symbols=["SPY"],
        data=histories,
        start=datetime(2019, 1, 1, tzinfo=UTC),
        end=datetime(2019, 12, 31, tzinfo=UTC),
    )
    adapter = BacktraderAdapter(
        {},
        snapshot_registry=snapshot_registry,
        enable_snapshot_replay=True,
    )
    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("SPY",),
        start=pd.Timestamp("2019-01-01"),
        end=pd.Timestamp("2019-12-31"),
        initial_cash=100_000.0,
        parameters={"equity_proportions": [1.0]},
        data_snapshot_id=snapshot.snapshot_id,
    )

    result_a = adapter.run(request)
    result_b = adapter.run(request)
    assert result_a.metrics == result_b.metrics
    assert result_a.metadata.data_snapshot_id == result_b.metadata.data_snapshot_id
