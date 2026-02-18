"""Tests for statistical hypothesis testing module."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import numpy as np
import pytest

from finbot.core.contracts.costs import CostSummary
from finbot.core.contracts.models import BacktestRunMetadata, BacktestRunResult
from finbot.core.contracts.versioning import BACKTEST_RESULT_SCHEMA_VERSION
from finbot.services.backtesting.hypothesis_testing import (
    BootstrapCI,
    HypothesisTestResult,
    bootstrap_confidence_interval,
    compare_strategies,
    mannwhitney_test,
    paired_t_test,
    permutation_test,
    summarize_walk_forward_significance,
)

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_result(cagr: float, sharpe: float = 0.8) -> BacktestRunResult:
    return BacktestRunResult(
        metadata=BacktestRunMetadata(
            run_id=str(uuid4()),
            engine_name="test",
            engine_version="0",
            strategy_name="Test",
            created_at=datetime.now(UTC),
            config_hash="abc",
            data_snapshot_id=None,
            random_seed=None,
        ),
        metrics={"cagr": cagr, "sharpe": sharpe},
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


def _make_results(values: list[float], metric: str = "cagr") -> list[BacktestRunResult]:
    """Create a list of BacktestRunResult with the given metric values."""
    results = []
    for v in values:
        kwargs = {"cagr": v, "sharpe": 0.8}
        if metric != "cagr":
            kwargs[metric] = v
        r = _make_result(**kwargs)
        results.append(r)
    return results


# High-effect-size distributions: clearly different means
_HIGH_A = [0.12, 0.14, 0.13, 0.15, 0.11, 0.14, 0.13, 0.12]
_HIGH_B = [0.04, 0.03, 0.05, 0.04, 0.03, 0.05, 0.04, 0.03]

# Identical distributions: should not be significant
_SAME_A = [0.10, 0.10, 0.10, 0.10, 0.10, 0.10]
_SAME_B = [0.10, 0.10, 0.10, 0.10, 0.10, 0.10]


# ── paired_t_test ─────────────────────────────────────────────────────────────


def test_paired_t_test_significant():
    res = paired_t_test(_make_results(_HIGH_A), _make_results(_HIGH_B))
    assert res.significant is True


def test_paired_t_test_not_significant():
    res = paired_t_test(_make_results(_SAME_A), _make_results(_SAME_B))
    assert res.significant is False


def test_paired_t_test_insufficient_data_raises():
    single = _make_results([0.10])
    with pytest.raises(ValueError, match="at least 2"):
        paired_t_test(single, single)


def test_paired_t_test_mismatched_lengths_raises():
    a = _make_results([0.10, 0.12, 0.11])
    b = _make_results([0.09, 0.08])
    with pytest.raises(ValueError, match="equal-length"):
        paired_t_test(a, b)


def test_paired_t_test_result_structure():
    res = paired_t_test(_make_results(_HIGH_A), _make_results(_HIGH_B))
    assert isinstance(res, HypothesisTestResult)
    assert res.test_name == "paired_t_test"
    assert 0.0 <= res.p_value <= 1.0
    assert res.alpha == 0.05
    assert res.n_samples == len(_HIGH_A)
    assert len(res.notes) > 0


def test_paired_t_test_notes_contains_p_value():
    res = paired_t_test(_make_results(_HIGH_A), _make_results(_HIGH_B))
    assert "p=" in res.notes


def test_paired_t_test_missing_metric_raises():
    results = _make_results([0.10, 0.12])
    with pytest.raises(KeyError, match="nonexistent"):
        paired_t_test(results, results, metric="nonexistent")


def test_paired_t_test_custom_alpha():
    res = paired_t_test(_make_results(_HIGH_A), _make_results(_HIGH_B), alpha=0.01)
    assert res.alpha == 0.01


# ── mannwhitney_test ──────────────────────────────────────────────────────────


def test_mannwhitney_significant():
    res = mannwhitney_test(_make_results(_HIGH_A), _make_results(_HIGH_B))
    assert res.significant is True


def test_mannwhitney_not_significant():
    res = mannwhitney_test(_make_results(_SAME_A), _make_results(_SAME_B))
    assert res.significant is False


def test_mannwhitney_result_structure():
    res = mannwhitney_test(_make_results(_HIGH_A), _make_results(_HIGH_B))
    assert isinstance(res, HypothesisTestResult)
    assert res.test_name == "mannwhitney_test"
    assert 0.0 <= res.p_value <= 1.0


# ── permutation_test ──────────────────────────────────────────────────────────


def test_permutation_test_significant():
    res = permutation_test(_make_results(_HIGH_A), _make_results(_HIGH_B))
    assert res.significant is True


def test_permutation_test_deterministic():
    res1 = permutation_test(_make_results(_HIGH_A), _make_results(_HIGH_B), random_seed=42)
    res2 = permutation_test(_make_results(_HIGH_A), _make_results(_HIGH_B), random_seed=42)
    assert res1.p_value == res2.p_value


def test_permutation_test_different_seed_may_differ():
    res1 = permutation_test(_make_results([0.10, 0.11, 0.09]), _make_results([0.08, 0.09, 0.07]), random_seed=1)
    res2 = permutation_test(_make_results([0.10, 0.11, 0.09]), _make_results([0.08, 0.09, 0.07]), random_seed=999)
    # p-values may differ slightly with different seeds (not guaranteed to differ)
    assert 0.0 <= res1.p_value <= 1.0
    assert 0.0 <= res2.p_value <= 1.0


def test_permutation_test_structure():
    res = permutation_test(_make_results(_HIGH_A), _make_results(_HIGH_B))
    assert isinstance(res, HypothesisTestResult)
    assert res.test_name == "permutation_test"


# ── bootstrap_confidence_interval ─────────────────────────────────────────────


def test_bootstrap_ci_contains_true_mean():
    true_mean = 0.10
    values = [true_mean + np.random.default_rng(42 + i).normal(0, 0.005) for i in range(20)]
    results = _make_results(values)
    ci = bootstrap_confidence_interval(results, n_bootstrap=5_000, random_seed=42)
    assert ci.lower <= true_mean <= ci.upper


def test_bootstrap_ci_deterministic():
    results = _make_results([0.10, 0.12, 0.08, 0.11, 0.09])
    ci1 = bootstrap_confidence_interval(results, random_seed=42)
    ci2 = bootstrap_confidence_interval(results, random_seed=42)
    assert ci1.lower == ci2.lower
    assert ci1.upper == ci2.upper


def test_bootstrap_ci_structure():
    results = _make_results([0.10, 0.12, 0.08, 0.11, 0.09])
    ci = bootstrap_confidence_interval(results)
    assert isinstance(ci, BootstrapCI)
    assert ci.lower < ci.estimate < ci.upper
    assert ci.confidence_level == 0.95
    assert ci.n_bootstrap == 10_000


def test_bootstrap_ci_custom_confidence():
    results = _make_results([0.10, 0.12, 0.08, 0.11, 0.09])
    ci_95 = bootstrap_confidence_interval(results, confidence_level=0.95)
    ci_99 = bootstrap_confidence_interval(results, confidence_level=0.99)
    # 99% CI should be wider
    assert (ci_99.upper - ci_99.lower) >= (ci_95.upper - ci_95.lower)


# ── compare_strategies ────────────────────────────────────────────────────────


def test_compare_strategies_output_shape():
    strategies = {
        "A": _make_results(_HIGH_A),
        "B": _make_results(_HIGH_B),
        "C": _make_results([0.08, 0.07, 0.09, 0.08, 0.07, 0.09, 0.08, 0.07]),
    }
    df = compare_strategies(strategies)
    # 3 strategies → 3*(3-1)/2 = 3 pairs
    assert len(df) == 3
    assert "strategy_a" in df.columns
    assert "strategy_b" in df.columns
    assert "p_value" in df.columns
    assert "significant" in df.columns
    assert "winner" in df.columns


def test_compare_strategies_winner_column():
    strategies = {
        "Strong": _make_results(_HIGH_A),
        "Weak": _make_results(_HIGH_B),
    }
    df = compare_strategies(strategies)
    assert len(df) == 1
    row = df.iloc[0]
    # Strong should win (it has higher mean CAGR)
    assert row["winner"] == "Strong"


def test_compare_strategies_too_few_raises():
    with pytest.raises(ValueError, match="≥2 strategies"):
        compare_strategies({"OnlyOne": _make_results([0.10, 0.11])})


# ── summarize_walk_forward_significance ───────────────────────────────────────


def test_summarize_wf_significance_beats_benchmark():
    from datetime import timedelta

    import pandas as pd

    from finbot.core.contracts.walkforward import WalkForwardConfig, WalkForwardResult, WalkForwardWindow

    base = pd.Timestamp("2019-01-02")

    def _win(i: int) -> WalkForwardWindow:
        ts = base + timedelta(days=i * 90)
        te = ts + timedelta(days=60)
        tes = te + timedelta(days=1)
        tee = tes + timedelta(days=20)
        return WalkForwardWindow(window_id=i, train_start=ts, train_end=te, test_start=tes, test_end=tee)

    n = 6
    windows = tuple(_win(i) for i in range(n))
    # All CAGRs well above 7% benchmark
    test_results = tuple(_make_result(cagr=0.15 + i * 0.01) for i in range(n))
    wf = WalkForwardResult(
        config=WalkForwardConfig(train_window=60, test_window=21, step_size=21),
        windows=windows,
        test_results=test_results,
        summary_metrics={"cagr_mean": 0.18, "window_count": float(n)},
    )

    res = summarize_walk_forward_significance(wf, benchmark_metric_value=0.07)
    assert isinstance(res, HypothesisTestResult)
    assert res.significant is True
    assert res.test_name == "one_sample_t_test"


def test_summarize_wf_significance_notes_nonempty():
    from datetime import timedelta

    import pandas as pd

    from finbot.core.contracts.walkforward import WalkForwardConfig, WalkForwardResult, WalkForwardWindow

    base = pd.Timestamp("2019-01-02")

    def _win(i: int) -> WalkForwardWindow:
        ts = base + timedelta(days=i * 90)
        te = ts + timedelta(days=60)
        tes = te + timedelta(days=1)
        tee = tes + timedelta(days=20)
        return WalkForwardWindow(window_id=i, train_start=ts, train_end=te, test_start=tes, test_end=tee)

    n = 4
    windows = tuple(_win(i) for i in range(n))
    test_results = tuple(_make_result(cagr=0.10) for _ in range(n))
    wf = WalkForwardResult(
        config=WalkForwardConfig(train_window=60, test_window=21, step_size=21),
        windows=windows,
        test_results=test_results,
        summary_metrics={"window_count": float(n)},
    )

    res = summarize_walk_forward_significance(wf, benchmark_metric_value=0.05)
    assert len(res.notes) > 0
    assert "p=" in res.notes
