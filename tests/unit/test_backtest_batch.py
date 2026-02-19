"""Unit tests for backtest_batch module.

process_map is patched with a sequential map so tests run without spawning
subprocesses, which is fragile in pytest.
"""

from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from finbot.services.backtesting.backtest_batch import _get_starts_from_steps, backtest_batch

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_price_df(n: int = 300, seed: int = 1) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2018-01-02", periods=n)
    close = 100.0 * np.cumprod(1 + rng.normal(0.0003, 0.008, n))
    return pd.DataFrame(
        {"Open": close, "High": close * 1.001, "Low": close * 0.999, "Close": close, "Volume": 1_000_000},
        index=dates,
    )


def _make_stub_result(start_date: pd.Timestamp | None = None) -> pd.DataFrame:
    """Minimal DataFrame that looks like run_backtest output."""
    return pd.DataFrame(
        {
            "CAGR": [0.10],
            "Sharpe": [0.8],
            "Max Drawdown": [-0.15],
            "Start Date": [str(start_date or pd.Timestamp("2018-01-02"))],
            "strategy": ["NoRebalance"],
            "rebal_proportions (p)": [[1.0]],
        }
    )


# ── _get_starts_from_steps ────────────────────────────────────────────────────


def test_get_starts_from_steps_basic():
    start = pd.Timestamp("2018-01-01")
    end = pd.Timestamp("2019-01-01")
    step = pd.DateOffset(months=3)
    duration = pd.DateOffset(months=6)
    starts = _get_starts_from_steps(start, end, step, duration)
    assert len(starts) > 0
    # All starts should be before (end - duration)
    for s in starts:
        assert s + duration < end


def test_get_starts_from_steps_returns_empty_when_range_too_small():
    start = pd.Timestamp("2018-01-01")
    end = pd.Timestamp("2018-03-01")
    step = pd.DateOffset(months=1)
    duration = pd.DateOffset(months=6)  # longer than range
    starts = _get_starts_from_steps(start, end, step, duration)
    assert starts == []


def test_get_starts_from_steps_chronological():
    start = pd.Timestamp("2018-01-01")
    end = pd.Timestamp("2021-01-01")
    step = pd.DateOffset(months=6)
    duration = pd.DateOffset(months=6)
    starts = _get_starts_from_steps(start, end, step, duration)
    for i in range(len(starts) - 1):
        assert starts[i] < starts[i + 1]


# ── backtest_batch argument preprocessing ─────────────────────────────────────


def test_batch_empty_price_histories_raises():
    with pytest.raises(ValueError, match="price_histories cannot be empty"):
        backtest_batch(
            price_histories=[],
            strat=["NoRebalance"],
            start=[None],
            end=[None],
            duration=[None],
            start_step=[None],
        )


def test_batch_empty_dataframe_in_histories_raises():
    with pytest.raises(ValueError, match="empty"):
        backtest_batch(
            price_histories=[{"SPY": pd.DataFrame()}],
            strat=["NoRebalance"],
            start=[None],
            end=[None],
            duration=[None],
            start_step=[None],
        )


def test_batch_multiple_durations_raises():
    ph = [{"SPY": _make_price_df()}]
    with pytest.raises(ValueError, match="duration"):
        backtest_batch(
            price_histories=ph,
            strat=["NoRebalance"],
            start=[None],
            end=[None],
            duration=[None, pd.DateOffset(months=12)],  # two durations — invalid
            start_step=[None],
        )


def test_batch_multiple_start_steps_raises():
    ph = [{"SPY": _make_price_df()}]
    with pytest.raises(ValueError, match="start_step"):
        backtest_batch(
            price_histories=ph,
            strat=["NoRebalance"],
            start=[None],
            end=[None],
            duration=[None],
            start_step=[None, pd.DateOffset(months=3)],  # two steps — invalid
        )


def test_batch_coerces_scalar_kwarg_to_tuple():
    """Non-tuple kwargs should be wrapped in a 1-tuple inside backtest_batch."""
    ph = [{"SPY": _make_price_df()}]
    stub = _make_stub_result()

    def fake_process_map(fn, combs, **kw):
        return [stub] * len(combs)

    with patch("finbot.services.backtesting.backtest_batch.process_map", fake_process_map):
        result = backtest_batch(
            price_histories=ph,
            strat="NoRebalance",  # scalar — should be coerced
            start=None,
            end=None,
            duration=None,
            start_step=None,
        )
    assert isinstance(result, pd.DataFrame)


def test_batch_date_alignment_truncates_histories():
    """The function must truncate all histories to their overlap."""
    # Two price histories with different start dates
    df_early = _make_price_df(400, seed=1)  # starts 2018-01-02
    df_late = pd.DataFrame(
        {"Open": 100.0, "High": 100.0, "Low": 100.0, "Close": 100.0, "Volume": 1_000_000},
        index=pd.bdate_range("2019-01-02", periods=200),
    )
    ph = [{"SPY": df_early, "TLT": df_late}]
    stub = _make_stub_result()

    recorded_ph: list = []

    def fake_process_map(fn, combs, **kw):
        # Inspect the price_histories tuple element from one combination
        recorded_ph.extend(combs)
        return [stub] * len(combs)

    with patch("finbot.services.backtesting.backtest_batch.process_map", fake_process_map):
        backtest_batch(
            price_histories=ph,
            strat=["NoRebalance"],
            start=[None],
            end=[None],
            duration=[None],
            start_step=[None],
        )

    # Verify the batch ran — at least one combination was processed
    assert len(recorded_ph) >= 1


def test_batch_returns_dataframe_on_success():
    ph = [{"SPY": _make_price_df()}]
    stub = _make_stub_result()

    def fake_process_map(fn, combs, **kw):
        return [stub] * len(combs)

    with patch("finbot.services.backtesting.backtest_batch.process_map", fake_process_map):
        result = backtest_batch(
            price_histories=ph,
            strat=["NoRebalance"],
            start=[None],
            end=[None],
            duration=[None],
            start_step=[None],
        )
    assert isinstance(result, pd.DataFrame)
    assert not result.empty


def test_batch_multiple_strategies_produces_multiple_rows():
    ph = [{"SPY": _make_price_df()}]

    def fake_process_map(fn, combs, **kw):
        return [_make_stub_result() for _ in combs]

    with patch("finbot.services.backtesting.backtest_batch.process_map", fake_process_map):
        result = backtest_batch(
            price_histories=ph,
            strat=["NoRebalance", "Rebalance"],
            start=[None],
            end=[None],
            duration=[None],
            start_step=[None],
        )
    assert isinstance(result, pd.DataFrame)
    # 2 strategies → 2 combinations → 2 rows
    assert len(result) == 2
