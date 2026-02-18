"""Unit tests for rebalance_optimizer module.

process_map is patched to avoid spawning subprocesses in CI.

The optimizer runs a gradient-descent loop (up to 1000 iterations) that
computes candidate proportion lists (cur_test_props) and then matches the
best result back by comparing str(cur_test_props[i]) == result["rebal_proportions (p)"].
Each fake_process_map therefore echoes back the actual proportions — extracted
from comb[6]["rebal_proportions"] — as their string representation so the
comparison always succeeds.

kwargs order inside rebalance_optimizer after coercion:
  0: price_histories, 1: strat, 2: start, 3: end,
  4: duration, 5: start_step, 6: strat_kwargs
"""

from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pandas as pd

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_price_df(n: int = 300, seed: int = 1) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2018-01-02", periods=n)
    close = 100.0 * np.cumprod(1 + rng.normal(0.0003, 0.008, n))
    return pd.DataFrame(
        {"Open": close, "High": close * 1.001, "Low": close * 0.999, "Close": close, "Volume": 1_000_000},
        index=dates,
    )


def _result_for_comb(comb: tuple) -> pd.DataFrame:
    """Build a minimal result DataFrame echoing the actual proportions from the combination.

    comb[6] is the strat_kwargs dict: {"rebal_proportions": [...], "rebal_interval": N}.
    Storing str(props) in "rebal_proportions (p)" makes the optimizer's line-51 comparison
    (str(cur_test_props[i]) == best) succeed correctly.
    """
    props = comb[6]["rebal_proportions"]
    return pd.DataFrame(
        {
            "CAGR": [0.10],
            "Sharpe": [0.8],
            "Max Drawdown": [-0.15],
            "Start Date": ["2018-01-02"],
            "rebal_proportions (p)": [str(props)],
            "rebal_interval": [21],
        }
    )


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_rebalance_optimizer_returns_best_ratios():
    from finbot.services.backtesting.rebalance_optimizer import rebalance_optimizer

    ph = [{"SPY": _make_price_df(), "TLT": _make_price_df(seed=2)}]

    def fake_process_map(fn, combs, **kw):
        return [_result_for_comb(c) for c in combs]

    with patch("finbot.services.backtesting.rebalance_optimizer.process_map", fake_process_map):
        result = rebalance_optimizer(
            price_histories=ph,
            strat=["Rebalance"],
            start=[None],
            end=[None],
            duration=[None],
            start_step=[None],
            strat_kwargs=[{"rebal_proportions": [0.5, 0.5], "rebal_interval": 21}],
        )

    assert result is not None


def test_rebalance_optimizer_returns_dataframe():
    from finbot.services.backtesting.rebalance_optimizer import rebalance_optimizer

    ph = [{"SPY": _make_price_df(), "TLT": _make_price_df(seed=3)}]

    def fake_process_map(fn, combs, **kw):
        return [_result_for_comb(c) for c in combs]

    with patch("finbot.services.backtesting.rebalance_optimizer.process_map", fake_process_map):
        result = rebalance_optimizer(
            price_histories=ph,
            strat=["Rebalance"],
            start=[None],
            end=[None],
            duration=[None],
            start_step=[None],
            strat_kwargs=[{"rebal_proportions": [0.5, 0.5], "rebal_interval": 21}],
        )

    assert isinstance(result, pd.DataFrame)


def test_rebalance_optimizer_uses_cagr_for_ranking():
    """Optimizer should not crash when using CAGR for selection."""
    from finbot.services.backtesting.rebalance_optimizer import rebalance_optimizer

    ph = [{"SPY": _make_price_df(), "TLT": _make_price_df(seed=4)}]

    def fake_process_map(fn, combs, **kw):
        return [_result_for_comb(c) for c in combs]

    with patch("finbot.services.backtesting.rebalance_optimizer.process_map", fake_process_map):
        # Should not raise
        rebalance_optimizer(
            price_histories=ph,
            strat=["Rebalance"],
            start=[None],
            end=[None],
            duration=[None],
            start_step=[None],
            strat_kwargs=[{"rebal_proportions": [0.5, 0.5], "rebal_interval": 21}],
        )


def test_rebalance_optimizer_date_alignment():
    """Optimizer should truncate histories to overlap period without crashing."""
    from finbot.services.backtesting.rebalance_optimizer import rebalance_optimizer

    spy = _make_price_df(400, seed=1)
    tlt = pd.DataFrame(
        {"Open": 100.0, "High": 100.0, "Low": 100.0, "Close": 100.0, "Volume": 1_000_000},
        index=pd.bdate_range("2019-06-01", periods=200),
    )
    ph = [{"SPY": spy, "TLT": tlt}]

    call_count = [0]

    def fake_process_map(fn, combs, **kw):
        call_count[0] += 1
        return [_result_for_comb(c) for c in combs]

    with patch("finbot.services.backtesting.rebalance_optimizer.process_map", fake_process_map):
        rebalance_optimizer(
            price_histories=ph,
            strat=["Rebalance"],
            start=[None],
            end=[None],
            duration=[None],
            start_step=[None],
            strat_kwargs=[{"rebal_proportions": [0.5, 0.5], "rebal_interval": 21}],
        )

    assert call_count[0] >= 1


def test_rebalance_optimizer_does_not_crash_single_asset():
    """Should work even with a single-asset price history."""
    from finbot.services.backtesting.rebalance_optimizer import rebalance_optimizer

    ph = [{"SPY": _make_price_df()}]

    def fake_process_map(fn, combs, **kw):
        return [_result_for_comb(c) for c in combs]

    with patch("finbot.services.backtesting.rebalance_optimizer.process_map", fake_process_map):
        # Should not raise
        rebalance_optimizer(
            price_histories=ph,
            strat=["Rebalance"],
            start=[None],
            end=[None],
            duration=[None],
            start_step=[None],
            strat_kwargs=[{"rebal_proportions": [1.0], "rebal_interval": 21}],
        )
