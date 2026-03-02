"""Factor-based risk decomposition for portfolio analysis.

Decomposes total portfolio variance into systematic (factor-driven) and
idiosyncratic components, and computes per-factor marginal contributions
to systematic risk.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from finbot.core.contracts.factor_analytics import FactorRegressionResult, FactorRiskResult
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


def compute_factor_risk(
    portfolio_returns: np.ndarray,
    factor_returns: pd.DataFrame,
    regression_result: FactorRegressionResult | None = None,
    annualization_factor: int = _DEFAULT_ANNUALIZATION,
) -> FactorRiskResult:
    """Decompose portfolio variance into systematic and idiosyncratic parts.

    Systematic variance = ``beta.T @ Sigma_f @ beta`` where ``Sigma_f`` is the
    factor covariance matrix.  Idiosyncratic variance is ``total - systematic``
    (clamped to zero).  Marginal contribution of factor *i* is
    ``beta_i * (Sigma_f @ beta)[i]``.

    Args:
        portfolio_returns: 1-D array of portfolio period returns.
        factor_returns: DataFrame with one column per factor.
        regression_result: Pre-computed regression result.  If ``None``,
            ``compute_factor_regression`` is called internally.
        annualization_factor: Trading periods per year.  Defaults to 252.

    Returns:
        ``FactorRiskResult`` with systematic, idiosyncratic, and marginal
        variance contributions.

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

    factor_names = regression_result.factor_names
    loadings = regression_result.loadings
    factor_matrix = factor_returns[list(factor_names)].to_numpy(dtype=float)

    beta = np.array([loadings[name] for name in factor_names], dtype=float)

    # Factor covariance matrix
    sigma_f = np.cov(factor_matrix, rowvar=False, ddof=1)
    # Handle single-factor case: np.cov returns scalar
    if sigma_f.ndim == 0:
        sigma_f = sigma_f.reshape(1, 1)

    # Systematic variance = beta.T @ Sigma_f @ beta
    systematic_variance = float(beta @ sigma_f @ beta)

    # Total portfolio variance
    total_variance = float(np.var(portfolio_returns, ddof=1))

    # Idiosyncratic = total - systematic, clamped to 0
    idiosyncratic_variance = max(0.0, total_variance - systematic_variance)

    # Percentage systematic
    pct_systematic = systematic_variance / total_variance if total_variance > 0 else 0.0
    pct_systematic = max(0.0, min(1.0, pct_systematic))

    # Marginal contributions: beta_i * (Sigma_f @ beta)[i]
    sigma_beta = sigma_f @ beta
    marginal_contributions = {name: float(beta[i] * sigma_beta[i]) for i, name in enumerate(factor_names)}

    return FactorRiskResult(
        systematic_variance=systematic_variance,
        idiosyncratic_variance=idiosyncratic_variance,
        total_variance=total_variance,
        pct_systematic=pct_systematic,
        marginal_contributions=marginal_contributions,
        factor_names=factor_names,
        n_observations=len(portfolio_returns),
    )
