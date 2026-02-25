"""Portfolio analytics services.

Standalone analytics modules for rolling metrics, benchmark comparison,
drawdown analysis, and correlation / diversification metrics.  All
functions work on raw returns arrays or DataFrames and are engine-agnostic.
"""

from finbot.services.portfolio_analytics.benchmark import compute_benchmark_comparison
from finbot.services.portfolio_analytics.correlation import compute_diversification_metrics
from finbot.services.portfolio_analytics.drawdown import compute_drawdown_analysis
from finbot.services.portfolio_analytics.rolling import compute_rolling_metrics
from finbot.services.portfolio_analytics.viz import (
    plot_benchmark_scatter,
    plot_correlation_heatmap,
    plot_diversification_weights,
    plot_drawdown_periods,
    plot_rolling_metrics,
    plot_underwater_curve,
)

__all__ = [
    "compute_benchmark_comparison",
    "compute_diversification_metrics",
    "compute_drawdown_analysis",
    "compute_rolling_metrics",
    "plot_benchmark_scatter",
    "plot_correlation_heatmap",
    "plot_diversification_weights",
    "plot_drawdown_periods",
    "plot_rolling_metrics",
    "plot_underwater_curve",
]
