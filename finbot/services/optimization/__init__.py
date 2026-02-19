"""Portfolio optimization services.

Provides:
- DCA (Dollar Cost Averaging) optimizer: grid search over DCA parameters.
- Pareto-front optimizer: multi-objective Pareto analysis of backtest results.
"""

from __future__ import annotations

from finbot.services.optimization.pareto_optimizer import compute_pareto_front, plot_pareto_front

__all__ = [
    "compute_pareto_front",
    "plot_pareto_front",
]
