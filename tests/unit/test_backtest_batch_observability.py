"""Unit tests for batch observability integration in backtest_batch."""

from __future__ import annotations

import pandas as pd
import pytest

from finbot.core.contracts.batch import BatchStatus, ErrorCategory
from finbot.services.backtesting.backtest_batch import backtest_batch
from finbot.services.backtesting.batch_registry import BatchRegistry


def _make_price_df() -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=5, freq="B")
    return pd.DataFrame(
        {
            "Open": [100.0, 101.0, 102.0, 103.0, 104.0],
            "High": [101.0, 102.0, 103.0, 104.0, 105.0],
            "Low": [99.0, 100.0, 101.0, 102.0, 103.0],
            "Close": [100.5, 101.5, 102.5, 103.5, 104.5],
            "Volume": [1_000_000, 1_100_000, 1_200_000, 1_300_000, 1_400_000],
        },
        index=dates,
    )


def _batch_kwargs() -> dict:
    return {
        "price_histories": [{"SPY": _make_price_df()}],
        "start": [pd.Timestamp("2020-01-01")],
        "end": [pd.Timestamp("2020-01-07")],
        "duration": [None],
        "start_step": [None],
        "init_cash": [100_000.0],
        "strat": ["NoRebalance"],
        "strat_kwargs": [{"equity_proportions": [1.0]}],
        "broker": ["BackBroker"],
        "broker_kwargs": [{}],
        "broker_commission": ["FixedCommissionScheme"],
        "sizer": ["AllInSizer"],
        "sizer_kwargs": [{}],
    }


def test_backtest_batch_track_batch_requires_registry() -> None:
    with pytest.raises(ValueError, match="requires batch_registry"):
        backtest_batch(track_batch=True, **_batch_kwargs())


def test_backtest_batch_track_batch_records_partial(monkeypatch, tmp_path) -> None:
    success_df = pd.DataFrame({"roi": [0.1], "cagr": [0.08]})
    mocked_results = [
        {"item_id": 0, "success": True, "result": success_df, "duration_seconds": 0.01},
        {
            "item_id": 1,
            "success": False,
            "error_message": "missing data",
            "error_category": ErrorCategory.DATA_ERROR,
            "duration_seconds": 0.02,
        },
    ]

    monkeypatch.setattr(
        "finbot.services.backtesting.backtest_batch.process_map", lambda *args, **kwargs: mocked_results
    )
    registry = BatchRegistry(tmp_path / "batches")

    result = backtest_batch(
        track_batch=True,
        batch_registry=registry,
        price_histories=[{"SPY": _make_price_df()}, {"SPY": _make_price_df()}],
        start=[pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-01")],
        end=[pd.Timestamp("2020-01-07"), pd.Timestamp("2020-01-07")],
        duration=[None],
        start_step=[None],
        init_cash=[100_000.0],
        strat=["NoRebalance"],
        strat_kwargs=[{"equity_proportions": [1.0]}],
        broker=["BackBroker"],
        broker_kwargs=[{}],
        broker_commission=["FixedCommissionScheme"],
        sizer=["AllInSizer"],
        sizer_kwargs=[{}],
    )

    assert len(result) == 1
    batches = registry.list_batches()
    assert len(batches) == 1
    batch = batches[0]
    assert batch.status == BatchStatus.PARTIAL
    assert batch.succeeded_items == 1
    assert batch.failed_items == 1
    assert batch.error_summary[ErrorCategory.DATA_ERROR.value] == 1


def test_backtest_batch_track_batch_raises_when_all_fail(monkeypatch, tmp_path) -> None:
    mocked_results = [
        {
            "item_id": 0,
            "success": False,
            "error_message": "invalid parameter",
            "error_category": ErrorCategory.PARAMETER_ERROR,
            "duration_seconds": 0.01,
        }
    ]
    monkeypatch.setattr(
        "finbot.services.backtesting.backtest_batch.process_map", lambda *args, **kwargs: mocked_results
    )

    registry = BatchRegistry(tmp_path / "batches")
    with pytest.raises(RuntimeError, match="All batch items failed"):
        backtest_batch(track_batch=True, batch_registry=registry, **_batch_kwargs())

    batches = registry.list_batches()
    assert len(batches) == 1
    assert batches[0].status == BatchStatus.FAILED
