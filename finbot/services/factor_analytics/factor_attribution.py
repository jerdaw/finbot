"""Factor-based return attribution for portfolio analysis.

Decomposes total portfolio return into per-factor contributions, alpha
contribution, and residual return using the loadings from an OLS factor
regression.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from finbot.core.contracts.factor_analytics import FactorAttributionResult, FactorRegressionResult
from finbot.services.factor_analytics.factor_regression import (
    _DEFAULT_ANNUALIZATION,
    _MIN_OBSERVATIONS,
    compute_factor_regression,
)


def _validate_inputs(
    portfolio_returns: np.ndarray,
    factor_returns: pd.DataFrame,
) -> None:
    """Raise ValueError on invalid inputs."""
    if len(portfolio_returns) < _MIN_OBSERVATIONS:
        raise ValueError(
            f"portfolio_returns must have at least {_MIN_OBSERVATIONS} observations, got {len(portfolio_returns)}"
        )
    if len(portfolio_returns) != len(factor_returns):
        raise ValueError(
            f"portfolio_returns length ({len(portfolio_returns)}) must equal "
            f"factor_returns length ({len(factor_returns)})"
        )


def compute_factor_attribution(
    portfolio_returns: np.ndarray,
    factor_returns: pd.DataFrame,
    regression_result: FactorRegressionResult | None = None,
    annualization_factor: int = _DEFAULT_ANNUALIZATION,
) -> FactorAttributionResult:
    """Decompose portfolio return into factor contributions.

    Each factor's contribution equals ``loading_i * sum(factor_i_returns)``.
    The alpha contribution equals ``(alpha / ann_factor) * n_observations``.
    The residual is the gap between total return and explained return.

    Args:
        portfolio_returns: 1-D array of portfolio period returns.
        factor_returns: DataFrame with one column per factor.
        regression_result: Pre-computed regression result.  If ``None``,
            ``compute_factor_regression`` is called internally.
        annualization_factor: Trading periods per year.  Defaults to 252.

    Returns:
        ``FactorAttributionResult`` with per-factor and alpha contributions.

    Raises:
        ValueError: If fewer than 30 observations or length mismatch.
    """
    portfolio_returns = np.asarray(portfolio_returns, dtype=float)
    _validate_inputs(portfolio_returns, factor_returns)

    if regression_result is None:
        regression_result = compute_factor_regression(
            portfolio_returns,
            factor_returns,
            annualization_factor=annualization_factor,
        )

    n = len(portfolio_returns)
    factor_names = regression_result.factor_names
    loadings = regression_result.loadings

    # Per-factor contribution = loading * cumulative factor return
    factor_contributions: dict[str, float] = {}
    for name in factor_names:
        factor_sum = float(np.sum(factor_returns[name].to_numpy(dtype=float)))
        factor_contributions[name] = loadings[name] * factor_sum

    # Alpha contribution (daily alpha * number of days)
    daily_alpha = regression_result.alpha / annualization_factor
    alpha_contribution = daily_alpha * n

    # Total return = sum of period returns
    total_return = float(np.sum(portfolio_returns))

    # Explained = factor contributions + alpha contribution
    explained_return = sum(factor_contributions.values()) + alpha_contribution

    # Residual = total - explained
    residual_return = total_return - explained_return

    return FactorAttributionResult(
        factor_contributions=factor_contributions,
        alpha_contribution=alpha_contribution,
        total_return=total_return,
        explained_return=explained_return,
        residual_return=residual_return,
        factor_names=factor_names,
        n_observations=n,
    )
