"""Correlation and diversification metrics for multi-asset portfolios.

Computes three complementary diversification measures:

- **Herfindahl-Hirschman Index (HHI)**: concentration of weights.
- **Effective N**: equivalent number of equally weighted assets (1 / HHI).
- **Diversification ratio**: weighted-average individual volatility divided
  by portfolio volatility; values above 1 indicate diversification benefit.

Also provides the full pairwise correlation matrix and per-asset volatilities.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from finbot.core.contracts.portfolio_analytics import DiversificationResult

_MIN_OBSERVATIONS = 30
_DEFAULT_ANNUALIZATION = 252


def _validate_inputs(
    returns_df: pd.DataFrame,
    weights: dict[str, float] | None,
    annualization_factor: int,
) -> None:
    """Raise ValueError on invalid inputs."""
    if returns_df.shape[1] < 2:
        raise ValueError(f"returns_df must have at least 2 columns (assets), got {returns_df.shape[1]}")
    if len(returns_df) < _MIN_OBSERVATIONS:
        raise ValueError(f"returns_df must have at least {_MIN_OBSERVATIONS} rows, got {len(returns_df)}")
    if annualization_factor < 1:
        raise ValueError(f"annualization_factor must be >= 1, got {annualization_factor}")
    if weights is not None:
        extra = set(weights.keys()) - set(returns_df.columns)
        missing = set(returns_df.columns) - set(weights.keys())
        if extra or missing:
            raise ValueError(f"weights keys must match returns_df columns. Extra: {extra}, missing: {missing}")
        if any(v < 0 for v in weights.values()):
            raise ValueError("all weights must be >= 0")
        weight_sum = sum(weights.values())
        if abs(weight_sum - 1.0) > 1e-9:
            raise ValueError(f"weights must sum to 1.0, got {weight_sum}")


def compute_diversification_metrics(
    returns_df: pd.DataFrame,
    weights: dict[str, float] | None = None,
    annualization_factor: int = _DEFAULT_ANNUALIZATION,
) -> DiversificationResult:
    """Compute diversification metrics for a multi-asset portfolio.

    Args:
        returns_df: DataFrame of period returns, one column per asset.
            All columns should be aligned to the same dates.
        weights: Optional mapping from column name to portfolio weight.
            Weights must be non-negative and sum to 1.0.  When ``None``,
            equal weights are applied (``1 / n_assets`` per asset).
        annualization_factor: Trading periods per year.  Defaults to 252.

    Returns:
        DiversificationResult containing HHI, effective N, diversification
        ratio, per-asset volatilities, portfolio volatility, and the full
        correlation matrix.

    Raises:
        ValueError: If fewer than 2 columns or 30 rows are present, or if
            supplied weights are invalid.
    """
    _validate_inputs(returns_df, weights, annualization_factor)

    assets = list(returns_df.columns)
    n = len(assets)
    arr = returns_df[assets].to_numpy(dtype=float)

    if weights is None:
        w = np.ones(n) / n
        weights_dict = dict.fromkeys(assets, 1.0 / n)
    else:
        w = np.array([weights[a] for a in assets], dtype=float)
        weights_dict = {a: float(weights[a]) for a in assets}

    sqrt_ann = math.sqrt(annualization_factor)

    # Per-asset annualized volatilities
    sigma_i = np.std(arr, axis=0, ddof=1) * sqrt_ann
    individual_vols = {a: float(sigma_i[i]) for i, a in enumerate(assets)}

    # Correlation matrix
    corr = np.corrcoef(arr, rowvar=False)
    correlation_matrix = {a: {b: float(corr[i, j]) for j, b in enumerate(assets)} for i, a in enumerate(assets)}

    # Average pairwise correlation (upper triangle, k=1 excludes diagonal)
    upper_mask = np.triu(np.ones((n, n), dtype=bool), k=1)
    avg_pairwise_correlation = float(np.mean(corr[upper_mask]))

    # Covariance for portfolio variance
    cov = np.cov(arr, rowvar=False, ddof=1)
    portfolio_variance = float(w @ cov @ w) * annualization_factor
    portfolio_vol = math.sqrt(max(portfolio_variance, 0.0))

    # Diversification ratio
    weighted_avg_vol = float(w @ sigma_i)
    diversification_ratio = (weighted_avg_vol / portfolio_vol) if portfolio_vol > 0 else 1.0

    # HHI and effective N
    herfindahl_index = float(np.sum(w**2))
    effective_n = 1.0 / herfindahl_index if herfindahl_index > 0 else float("inf")

    return DiversificationResult(
        n_assets=n,
        weights=weights_dict,
        herfindahl_index=herfindahl_index,
        effective_n=effective_n,
        diversification_ratio=diversification_ratio,
        avg_pairwise_correlation=avg_pairwise_correlation,
        correlation_matrix=correlation_matrix,
        individual_vols=individual_vols,
        portfolio_vol=portfolio_vol,
        n_observations=len(returns_df),
        annualization_factor=annualization_factor,
    )
