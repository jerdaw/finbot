"""Standalone risk analytics services: VaR/CVaR, stress testing, Kelly criterion."""

from finbot.services.risk_analytics.kelly import (
    compute_kelly_criterion,
    compute_kelly_from_returns,
    compute_multi_asset_kelly,
)
from finbot.services.risk_analytics.stress import SCENARIOS, run_all_scenarios, run_stress_test
from finbot.services.risk_analytics.var import compute_cvar, compute_var, var_backtest
from finbot.services.risk_analytics.viz import (
    plot_kelly_correlation_heatmap,
    plot_kelly_fractions,
    plot_stress_comparison,
    plot_stress_path,
    plot_var_comparison,
    plot_var_distribution,
)

__all__ = [
    "SCENARIOS",
    "compute_cvar",
    "compute_kelly_criterion",
    "compute_kelly_from_returns",
    "compute_multi_asset_kelly",
    "compute_var",
    "plot_kelly_correlation_heatmap",
    "plot_kelly_fractions",
    "plot_stress_comparison",
    "plot_stress_path",
    "plot_var_comparison",
    "plot_var_distribution",
    "run_all_scenarios",
    "run_stress_test",
    "var_backtest",
]
