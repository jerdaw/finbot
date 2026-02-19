"""Tests for the multi-objective Pareto-front optimizer."""

from __future__ import annotations

import dataclasses
from datetime import UTC, datetime
from uuid import uuid4

import plotly.graph_objects as go
import pytest

from finbot.core.contracts.costs import CostSummary
from finbot.core.contracts.models import BacktestRunMetadata, BacktestRunResult
from finbot.core.contracts.versioning import BACKTEST_RESULT_SCHEMA_VERSION
from finbot.services.optimization.pareto_optimizer import compute_pareto_front, plot_pareto_front

# ── Helpers ───────────────────────────────────────────────────────────────────

_ZERO_COSTS = CostSummary(
    total_commission=0.0,
    total_slippage=0.0,
    total_spread=0.0,
    total_borrow=0.0,
    total_market_impact=0.0,
)


def _make_result(
    cagr: float,
    max_drawdown: float,
    strategy_name: str = "Test",
    **extra_metrics: float,
) -> BacktestRunResult:
    """Build a BacktestRunResult from synthetic metric values.

    max_drawdown should be a positive number (e.g. 0.15 = 15% drawdown).
    Tests that minimize drawdown use maximize_b=False so that lower (smaller
    drawdown percentage) is preferred.
    """
    return BacktestRunResult(
        metadata=BacktestRunMetadata(
            run_id=str(uuid4()),
            engine_name="test",
            engine_version="0",
            strategy_name=strategy_name,
            created_at=datetime.now(UTC),
            config_hash="abc",
            data_snapshot_id=None,
            random_seed=None,
        ),
        metrics={"cagr": cagr, "max_drawdown": max_drawdown, **extra_metrics},
        schema_version=BACKTEST_RESULT_SCHEMA_VERSION,
        assumptions={},
        artifacts={},
        costs=_ZERO_COSTS,
    )


# ── Single-point tests ────────────────────────────────────────────────────────


def test_pareto_single_point():
    """One point is always Pareto-optimal (nothing else to dominate it)."""
    result = compute_pareto_front([_make_result(0.10, 0.15)])
    assert result.n_evaluated == 1
    assert len(result.pareto_front) == 1
    assert len(result.dominated_points) == 0
    assert result.pareto_front[0].is_pareto_optimal is True


# ── Two-point dominance tests ─────────────────────────────────────────────────


def test_pareto_two_points_one_dominates():
    """[cagr=0.15, dd=0.10] dominates [cagr=0.08, dd=0.20]: higher CAGR AND lower drawdown."""
    dominant = _make_result(0.15, 0.10, strategy_name="A")
    dominated = _make_result(0.08, 0.20, strategy_name="B")
    # maximize_a=True (higher CAGR better), maximize_b=False (lower drawdown % better)
    result = compute_pareto_front([dominant, dominated], maximize_b=False)
    assert len(result.pareto_front) == 1
    assert result.pareto_front[0].strategy_name == "A"
    assert len(result.dominated_points) == 1
    assert result.dominated_points[0].strategy_name == "B"


def test_pareto_two_points_tradeoff():
    """[cagr=0.15, dd=0.40] vs [cagr=0.08, dd=0.10]: each wins one objective → both optimal."""
    high_return = _make_result(0.15, 0.40, strategy_name="HighReturn")
    low_risk = _make_result(0.08, 0.10, strategy_name="LowRisk")
    result = compute_pareto_front([high_return, low_risk], maximize_b=False)
    assert len(result.pareto_front) == 2
    assert len(result.dominated_points) == 0


# ── Structural invariants ─────────────────────────────────────────────────────


def test_pareto_front_not_dominated():
    """No point in the Pareto front should be dominated by any other point in the full set."""
    results = [
        _make_result(0.05, 0.05, strategy_name="A"),
        _make_result(0.10, 0.12, strategy_name="B"),
        _make_result(0.15, 0.22, strategy_name="C"),
        _make_result(0.20, 0.35, strategy_name="D"),
    ]
    pareto = compute_pareto_front(results, maximize_a=True, maximize_b=False)
    # Each point wins on one objective → all should be Pareto-optimal
    for fp in pareto.pareto_front:
        for other in pareto.all_points:
            if other is fp:
                continue
            # 'other' dominates 'fp' iff: other.a >= fp.a AND other.b <= fp.b AND strictly better on one
            other_wins_a = other.objective_a >= fp.objective_a
            other_wins_b = other.objective_b <= fp.objective_b  # minimize: lower is better
            strictly_better = other.objective_a > fp.objective_a or other.objective_b < fp.objective_b
            assert not (other_wins_a and other_wins_b and strictly_better), (
                f"Front point {fp.strategy_name} is dominated by {other.strategy_name}"
            )


def test_dominated_points_excluded():
    """Every dominated point must appear in dominated_points, not in pareto_front."""
    results = [
        _make_result(0.20, 0.05, strategy_name="Best"),  # best CAGR, lowest drawdown
        _make_result(0.05, 0.30, strategy_name="Worst"),  # low CAGR, high drawdown
        _make_result(0.05, 0.35, strategy_name="AlsoWorst"),  # same CAGR, even higher drawdown
    ]
    pareto = compute_pareto_front(results, maximize_b=False)
    front_names = {p.strategy_name for p in pareto.pareto_front}
    dominated_names = {p.strategy_name for p in pareto.dominated_points}
    assert "Best" in front_names
    assert "Worst" in dominated_names
    assert "AlsoWorst" in dominated_names
    assert front_names.isdisjoint(dominated_names)


def test_all_points_classified():
    """len(pareto_front) + len(dominated_points) must equal n_evaluated."""
    results = [_make_result(0.05 * i, 0.05 * i) for i in range(1, 8)]
    pareto = compute_pareto_front(results, maximize_b=False)
    assert len(pareto.pareto_front) + len(pareto.dominated_points) == pareto.n_evaluated
    assert pareto.n_evaluated == len(results)


# ── Objective direction tests ─────────────────────────────────────────────────


def test_pareto_maximize_both():
    """maximize_b=True: higher objective_b is better."""
    low_b = _make_result(0.10, 0.50, strategy_name="LowB")
    high_b = _make_result(0.10, 0.90, strategy_name="HighB")
    result = compute_pareto_front([low_b, high_b], maximize_a=True, maximize_b=True)
    # Same CAGR, but HighB has higher objective_b → HighB dominates LowB
    assert len(result.pareto_front) == 1
    assert result.pareto_front[0].strategy_name == "HighB"


def test_pareto_minimize_both():
    """maximize_a=False, maximize_b=False: lower values are better on both axes."""
    # B has lower CAGR (0.05 < 0.20) AND lower drawdown (0.10 < 0.30) → B dominates A
    results = [
        _make_result(0.20, 0.30, strategy_name="A"),
        _make_result(0.05, 0.10, strategy_name="B"),
    ]
    result = compute_pareto_front(results, maximize_a=False, maximize_b=False)
    assert len(result.pareto_front) == 1
    assert result.pareto_front[0].strategy_name == "B"


# ── Error cases ───────────────────────────────────────────────────────────────


def test_missing_metric_raises():
    """KeyError when an objective key is absent from any result's metrics."""
    result = _make_result(0.10, 0.15)
    with pytest.raises(KeyError):
        compute_pareto_front([result], objective_a="nonexistent_metric")


def test_empty_results_raises():
    """ValueError when results is empty."""
    with pytest.raises(ValueError, match="non-empty"):
        compute_pareto_front([])


# ── Edge cases ────────────────────────────────────────────────────────────────


def test_all_equal_points_all_optimal():
    """When all points have identical objective values, no one dominates another."""
    results = [_make_result(0.10, 0.15) for _ in range(5)]
    pareto = compute_pareto_front(results, maximize_b=False)
    assert len(pareto.pareto_front) == 5
    assert len(pareto.dominated_points) == 0


def test_large_set_returns_correct_front():
    """100 synthetic points: Pareto front verified via brute-force dominance check."""
    import random

    random.seed(0)
    # Use positive drawdown values; minimize drawdown (maximize_b=False)
    results = [_make_result(random.uniform(0.01, 0.30), random.uniform(0.01, 0.50)) for _ in range(100)]
    pareto = compute_pareto_front(results, objective_a="cagr", objective_b="max_drawdown", maximize_b=False)

    # Brute-force check: no front point should be dominated by any other point in the full set
    all_vals = [(p.objective_a, p.objective_b) for p in pareto.all_points]
    for fp in pareto.pareto_front:
        for a, b in all_vals:
            dominated = (
                a >= fp.objective_a
                and b <= fp.objective_b  # minimize: lower b is better
                and (a > fp.objective_a or b < fp.objective_b)
            )
            assert not dominated, (
                f"Front point cagr={fp.objective_a:.4f} dd={fp.objective_b:.4f} is dominated by ({a:.4f}, {b:.4f})"
            )

    assert len(pareto.pareto_front) + len(pareto.dominated_points) == 100


# ── Plot tests ────────────────────────────────────────────────────────────────


def test_plot_returns_figure():
    """plot_pareto_front() returns a plotly Figure."""
    results = [
        _make_result(0.15, 0.10, strategy_name="A"),
        _make_result(0.08, 0.40, strategy_name="B"),
    ]
    pareto = compute_pareto_front(results, maximize_b=False)
    fig = plot_pareto_front(pareto)
    assert isinstance(fig, go.Figure)


def test_plot_has_two_traces():
    """Figure has a dominated trace and a Pareto-front trace when dominated points exist."""
    results = [
        _make_result(0.20, 0.05, strategy_name="Best"),  # dominates Worst on both axes
        _make_result(0.05, 0.30, strategy_name="Worst"),
    ]
    pareto = compute_pareto_front(results, maximize_b=False)
    fig = plot_pareto_front(pareto, show_dominated=True)
    assert len(fig.data) == 2
    trace_names = {t.name for t in fig.data}
    assert "Pareto Front" in trace_names
    assert "Dominated" in trace_names


# ── Immutability test ─────────────────────────────────────────────────────────


def test_pareto_result_is_frozen():
    """ParetoResult and ParetoPoint are frozen dataclasses (immutable)."""
    results = [_make_result(0.10, 0.15)]
    pareto = compute_pareto_front(results, maximize_b=False)

    with pytest.raises((dataclasses.FrozenInstanceError, TypeError)):
        pareto.n_evaluated = 999  # type: ignore[misc]

    point = pareto.pareto_front[0]
    with pytest.raises((dataclasses.FrozenInstanceError, TypeError)):
        point.objective_a = 999.0  # type: ignore[misc]


# ── Objective name propagation ────────────────────────────────────────────────


def test_objective_names_stored_in_result():
    """ParetoResult stores the objective names passed to compute_pareto_front."""
    results = [_make_result(0.10, 0.15, sharpe=1.2)]
    pareto = compute_pareto_front(results, objective_a="cagr", objective_b="max_drawdown")
    assert pareto.objective_a_name == "cagr"
    assert pareto.objective_b_name == "max_drawdown"
