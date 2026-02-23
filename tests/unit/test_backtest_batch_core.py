"""Core behavior tests for backtest_batch execution/aggregation paths."""

from __future__ import annotations

import pandas as pd
import pytest

from finbot.services.backtesting.backtest_batch import _get_starts_from_steps, backtest_batch


def _make_price_df() -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=8, freq="B")
    return pd.DataFrame(
        {
            "Open": [100.0 + i for i in range(8)],
            "High": [101.0 + i for i in range(8)],
            "Low": [99.0 + i for i in range(8)],
            "Close": [100.5 + i for i in range(8)],
            "Volume": [1_000_000 + i * 10_000 for i in range(8)],
        },
        index=dates,
    )


def _batch_kwargs() -> dict:
    return {
        "price_histories": [{"SPY": _make_price_df()}],
        "start": [pd.Timestamp("2020-01-01")],
        "end": [pd.Timestamp("2020-01-10")],
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


def test_get_starts_from_steps_returns_expected_windows() -> None:
    starts = _get_starts_from_steps(
        latest_start_date=pd.Timestamp("2020-01-01"),
        earliest_end_date=pd.Timestamp("2020-01-10"),
        start_step=pd.Timedelta(days=2),
        duration=pd.Timedelta(days=3),
    )
    assert starts == [
        pd.Timestamp("2020-01-01"),
        pd.Timestamp("2020-01-03"),
        pd.Timestamp("2020-01-05"),
    ]


def test_backtest_batch_non_tracking_concats_results(monkeypatch) -> None:
    df1 = pd.DataFrame({"roi": [0.1], "cagr": [0.08]})
    df2 = pd.DataFrame({"roi": [0.2], "cagr": [0.15]})

    def _fake_process_map(*_args, **_kwargs):
        return [df1, df2]

    monkeypatch.setattr("finbot.services.backtesting.backtest_batch.process_map", _fake_process_map)

    result = backtest_batch(
        price_histories=[{"SPY": _make_price_df()}, {"SPY": _make_price_df()}],
        start=[pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-01")],
        end=[pd.Timestamp("2020-01-10"), pd.Timestamp("2020-01-10")],
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

    assert len(result) == 2
    assert list(result["roi"]) == [0.1, 0.2]


def test_backtest_batch_validates_empty_price_histories() -> None:
    with pytest.raises(ValueError, match="price_histories cannot be empty"):
        backtest_batch(**{**_batch_kwargs(), "price_histories": []})
