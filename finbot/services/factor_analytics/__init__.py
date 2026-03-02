"""Factor analytics services.

Standalone multi-factor model modules for factor regression, return
attribution, and risk decomposition.  All functions work on raw returns
arrays or DataFrames and are engine-agnostic.
"""

from finbot.services.factor_analytics.factor_attribution import compute_factor_attribution
from finbot.services.factor_analytics.factor_regression import (
    compute_factor_regression,
    compute_rolling_r_squared,
)
from finbot.services.factor_analytics.factor_risk import compute_factor_risk
from finbot.services.factor_analytics.viz import (
    plot_factor_attribution,
    plot_factor_correlation,
    plot_factor_loadings,
    plot_factor_risk_decomposition,
    plot_rolling_r_squared,
)

__all__ = [
    "compute_factor_attribution",
    "compute_factor_regression",
    "compute_factor_risk",
    "compute_rolling_r_squared",
    "plot_factor_attribution",
    "plot_factor_correlation",
    "plot_factor_loadings",
    "plot_factor_risk_decomposition",
    "plot_rolling_r_squared",
]
