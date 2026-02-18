"""Multi-objective Pareto-front optimizer for portfolio strategies.

Given a collection of ``BacktestRunResult`` objects (one per strategy/parameter
combination), this module identifies the Pareto-optimal subset — strategies
where no other strategy is simultaneously better on *all* chosen objectives.

Algorithm: O(n²) pairwise dominance checking. Suitable for strategy counts
encountered in typical grid-search sweeps (≤ 10 000 points).

Typical usage::

    from finbot.core.contracts import BacktestRunResult
    from finbot.services.optimization.pareto_optimizer import compute_pareto_front, plot_pareto_front

    results: list[BacktestRunResult] = [...]
    pareto = compute_pareto_front(results, objective_a="cagr", objective_b="max_drawdown")
    fig = plot_pareto_front(pareto)
    fig.show()
"""

from __future__ import annotations

import dataclasses
from collections.abc import Sequence
from typing import Any

import plotly.graph_objects as go

from finbot.core.contracts import BacktestRunResult
from finbot.core.contracts.optimization import ParetoPoint, ParetoResult


def compute_pareto_front(
    results: Sequence[BacktestRunResult],
    objective_a: str = "cagr",
    objective_b: str = "max_drawdown",
    *,
    maximize_a: bool = True,
    maximize_b: bool = False,
) -> ParetoResult:
    """Identify Pareto-optimal strategies from a set of backtest results.

    A point P *dominates* Q when:

    - P is at least as good as Q on **both** objectives, AND
    - P is strictly better than Q on **at least one** objective.

    "Better" depends on whether the objective is maximised or minimised:
    - Maximised: higher value is better.
    - Minimised: lower value is better.

    Parameters
    ----------
    results:
        Non-empty sequence of ``BacktestRunResult`` objects to evaluate.
    objective_a:
        Metric key for the primary objective (must exist in every
        ``result.metrics`` dict).
    objective_b:
        Metric key for the secondary objective.
    maximize_a:
        When ``True``, higher values of ``objective_a`` are preferred.
    maximize_b:
        When ``True``, higher values of ``objective_b`` are preferred.
        Defaults to ``False`` (e.g. ``max_drawdown`` — lower is better).

    Returns
    -------
    ParetoResult
        Full classification of all evaluated points.

    Raises
    ------
    ValueError
        If ``results`` is empty.
    KeyError
        If ``objective_a`` or ``objective_b`` is not present in a result's
        metrics dict.
    """
    if not results:
        raise ValueError("results must be non-empty")

    # Validate objectives exist in every result (raises KeyError on first miss).
    for result in results:
        if objective_a not in result.metrics:
            raise KeyError(f"Objective '{objective_a}' not found in metrics")
        if objective_b not in result.metrics:
            raise KeyError(f"Objective '{objective_b}' not found in metrics")

    # Build raw (a, b) tuples for the dominance check.
    raw_values: list[tuple[float, float]] = [
        (result.metrics[objective_a], result.metrics[objective_b]) for result in results
    ]

    maximize: tuple[bool, bool] = (maximize_a, maximize_b)

    # Determine dominance for each point.
    dominated_flags: list[bool] = [
        _is_dominated(raw_values[i], [raw_values[j] for j in range(len(raw_values)) if j != i], maximize=maximize)
        for i in range(len(results))
    ]

    # Build ParetoPoint objects.
    all_points: list[ParetoPoint] = []
    for result, (val_a, val_b), is_dominated in zip(results, raw_values, dominated_flags, strict=True):
        all_points.append(
            ParetoPoint(
                strategy_name=result.metadata.strategy_name,
                params=dataclasses.asdict(result.metadata),
                metrics=dict(result.metrics),
                objective_a=val_a,
                objective_b=val_b,
                is_pareto_optimal=not is_dominated,
            )
        )

    pareto_front = tuple(p for p in all_points if p.is_pareto_optimal)
    dominated_points = tuple(p for p in all_points if not p.is_pareto_optimal)

    return ParetoResult(
        objective_a_name=objective_a,
        objective_b_name=objective_b,
        all_points=tuple(all_points),
        pareto_front=pareto_front,
        dominated_points=dominated_points,
        n_evaluated=len(all_points),
    )


def _is_dominated(
    point: tuple[float, float],
    candidates: Sequence[tuple[float, float]],
    *,
    maximize: tuple[bool, bool],
) -> bool:
    """Return ``True`` if *point* is dominated by at least one candidate.

    Point P dominates Q when P is at least as good on both objectives AND
    strictly better on at least one.

    Parameters
    ----------
    point:
        ``(objective_a, objective_b)`` values for the point under test.
    candidates:
        All other points to check against.
    maximize:
        ``(maximize_a, maximize_b)`` — which objectives to maximise.
    """
    pa, pb = point
    max_a, max_b = maximize

    for ca, cb in candidates:
        # Check "at least as good on both objectives"
        if max_a:
            at_least_a = ca >= pa
            strictly_a = ca > pa
        else:
            at_least_a = ca <= pa
            strictly_a = ca < pa

        if max_b:
            at_least_b = cb >= pb
            strictly_b = cb > pb
        else:
            at_least_b = cb <= pb
            strictly_b = cb < pb

        if at_least_a and at_least_b and (strictly_a or strictly_b):
            return True

    return False


def plot_pareto_front(
    result: ParetoResult,
    *,
    title: str | None = None,
    show_dominated: bool = True,
) -> go.Figure:
    """Scatter plot of all evaluated strategies with the Pareto front highlighted.

    The Pareto-optimal points are rendered in blue; dominated points (when
    ``show_dominated=True``) in grey. The Pareto front points are connected by
    a line in order of ascending ``objective_a`` to make the frontier visible.

    Parameters
    ----------
    result:
        Output from :func:`compute_pareto_front`.
    title:
        Optional plot title. Defaults to ``"Pareto Front: <a> vs <b>"``.
    show_dominated:
        When ``False``, only the Pareto-optimal points are plotted.

    Returns
    -------
    go.Figure
        Plotly figure ready for ``.show()`` or ``.write_html()``.
    """
    traces: list[Any] = []

    if show_dominated and result.dominated_points:
        dom = result.dominated_points
        traces.append(
            go.Scatter(
                x=[p.objective_a for p in dom],
                y=[p.objective_b for p in dom],
                mode="markers",
                name="Dominated",
                marker={"color": "grey", "size": 8, "opacity": 0.5},
                text=[p.strategy_name for p in dom],
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    f"{result.objective_a_name}: %{{x:.4f}}<br>"
                    f"{result.objective_b_name}: %{{y:.4f}}<extra></extra>"
                ),
            )
        )

    # Sort Pareto front by objective_a for the connecting line.
    front_sorted = sorted(result.pareto_front, key=lambda p: p.objective_a)
    traces.append(
        go.Scatter(
            x=[p.objective_a for p in front_sorted],
            y=[p.objective_b for p in front_sorted],
            mode="lines+markers",
            name="Pareto Front",
            marker={"color": "blue", "size": 10},
            line={"color": "blue", "width": 2},
            text=[p.strategy_name for p in front_sorted],
            hovertemplate=(
                "<b>%{text}</b><br>"
                f"{result.objective_a_name}: %{{x:.4f}}<br>"
                f"{result.objective_b_name}: %{{y:.4f}}<extra></extra>"
            ),
        )
    )

    chart_title = title or f"Pareto Front: {result.objective_a_name} vs {result.objective_b_name}"

    fig = go.Figure(
        data=traces,
        layout=go.Layout(
            title=chart_title,
            xaxis_title=result.objective_a_name,
            yaxis_title=result.objective_b_name,
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        ),
    )
    return fig
