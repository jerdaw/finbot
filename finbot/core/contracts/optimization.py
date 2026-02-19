"""Typed contracts for multi-objective Pareto optimization.

Defines immutable result containers for Pareto-front analysis of
portfolio strategies. Engine-agnostic: works with any set of
``BacktestRunResult`` objects.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ParetoPoint:
    """A single evaluated strategy/parameter combination on the objective space.

    Attributes:
        strategy_name: Human-readable strategy identifier.
        params: Strategy hyperparameters used for this evaluation.
        metrics: Full backtest metrics dict (e.g., cagr, sharpe, max_drawdown).
        objective_a: Extracted value for the primary objective (e.g., CAGR).
        objective_b: Extracted value for the secondary objective (e.g., max_drawdown).
        is_pareto_optimal: True when no other evaluated point dominates this one.
    """

    strategy_name: str
    params: dict[str, object]
    metrics: dict[str, float]
    objective_a: float
    objective_b: float
    is_pareto_optimal: bool


@dataclass(frozen=True, slots=True)
class ParetoResult:
    """Full result of a Pareto-front computation.

    Attributes:
        objective_a_name: Metric key used as the primary objective (e.g., ``"cagr"``).
        objective_b_name: Metric key used as the secondary objective (e.g., ``"max_drawdown"``).
        all_points: Every evaluated strategy/parameter combination.
        pareto_front: Subset of ``all_points`` that are Pareto-optimal.
        dominated_points: Subset of ``all_points`` that are dominated.
        n_evaluated: Total number of points evaluated (== ``len(all_points)``).
    """

    objective_a_name: str
    objective_b_name: str
    all_points: tuple[ParetoPoint, ...]
    pareto_front: tuple[ParetoPoint, ...]
    dominated_points: tuple[ParetoPoint, ...]
    n_evaluated: int
