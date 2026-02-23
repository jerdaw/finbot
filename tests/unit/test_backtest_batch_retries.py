"""Unit tests for retry behavior in backtest_batch observability mode."""

from __future__ import annotations

import pandas as pd
import pytest

from finbot.core.contracts.batch import ErrorCategory
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


def test_backtest_batch_retry_requires_tracking_mode(tmp_path) -> None:
    registry = BatchRegistry(tmp_path / "batches")
    with pytest.raises(ValueError, match="requires track_batch"):
        backtest_batch(retry_failed=True, batch_registry=registry, **_batch_kwargs())


def test_backtest_batch_retries_transient_failures(monkeypatch, tmp_path) -> None:
    success_df = pd.DataFrame({"roi": [0.1], "cagr": [0.08]})
    call_count = {"value": 0}

    def _fake_process_map(*args, **kwargs):
        call_count["value"] += 1
        if call_count["value"] == 1:
            return [
                {
                    "item_id": 0,
                    "success": False,
                    "error_message": "network timeout",
                    "error_category": ErrorCategory.TIMEOUT,
                    "duration_seconds": 0.01,
                    "attempt_count": 1,
                }
            ]
        return [{"item_id": 0, "success": True, "result": success_df, "duration_seconds": 0.02, "attempt_count": 2}]

    monkeypatch.setattr("finbot.services.backtesting.backtest_batch.process_map", _fake_process_map)
    registry = BatchRegistry(tmp_path / "batches")

    result = backtest_batch(
        track_batch=True,
        retry_failed=True,
        max_retry_attempts=2,
        batch_registry=registry,
        **_batch_kwargs(),
    )

    assert len(result) == 1
    batch = registry.list_batches()[0]
    assert batch.succeeded_items == 1
    assert batch.failed_items == 0
    assert batch.item_results[0].attempt_count == 2
    assert batch.item_results[0].final_attempt_success is True


def test_backtest_batch_does_not_retry_non_transient_failures(monkeypatch, tmp_path) -> None:
    def _fake_process_map(*args, **kwargs):
        return [
            {
                "item_id": 0,
                "success": False,
                "error_message": "invalid parameter",
                "error_category": ErrorCategory.PARAMETER_ERROR,
                "duration_seconds": 0.01,
                "attempt_count": 1,
            }
        ]

    monkeypatch.setattr("finbot.services.backtesting.backtest_batch.process_map", _fake_process_map)
    registry = BatchRegistry(tmp_path / "batches")

    with pytest.raises(RuntimeError, match="All batch items failed"):
        backtest_batch(
            track_batch=True,
            retry_failed=True,
            max_retry_attempts=3,
            batch_registry=registry,
            **_batch_kwargs(),
        )

    batch = registry.list_batches()[0]
    assert batch.failed_items == 1
    assert batch.item_results[0].attempt_count == 1
    assert batch.item_results[0].final_attempt_success is False
