"""Multi-factor regression analysis for portfolio returns.

Runs OLS regression of portfolio excess returns on a set of factor
returns (e.g. Mkt-RF, SMB, HML, RMW, CMA) and reports loadings, alpha,
R-squared, t-statistics, and p-values.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats

from finbot.core.contracts.factor_analytics import (
    FactorModelType,
    FactorRegressionResult,
)

_MIN_OBSERVATIONS = 30
_DEFAULT_ANNUALIZATION = 252

# Well-known Fama-French factor names for auto-detection
_FF3_FACTORS = {"Mkt-RF", "SMB", "HML"}
_FF5_FACTORS = _FF3_FACTORS | {"RMW", "CMA"}


def _validate_inputs(
    portfolio_returns: np.ndarray,
    factor_returns: pd.DataFrame,
    annualization_factor: int,
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
    if factor_returns.shape[1] < 1:
        raise ValueError("factor_returns must have at least 1 column")
    if annualization_factor < 1:
        raise ValueError(f"annualization_factor must be >= 1, got {annualization_factor}")
    if np.any(np.isnan(portfolio_returns)):
        raise ValueError("portfolio_returns must not contain NaN values")
    if factor_returns.isna().any().any():
        raise ValueError("factor_returns must not contain NaN values")


def _infer_model_type(factor_names: tuple[str, ...]) -> FactorModelType:
    """Infer model type from factor column names."""
    name_set = set(factor_names)
    if name_set == {"Mkt-RF"}:
        return FactorModelType.CAPM
    if name_set >= _FF3_FACTORS and not (_FF5_FACTORS - _FF3_FACTORS) & name_set:
        return FactorModelType.FF3
    if name_set >= _FF5_FACTORS:
        return FactorModelType.FF5
    return FactorModelType.CUSTOM


def compute_factor_regression(
    portfolio_returns: np.ndarray,
    factor_returns: pd.DataFrame,
    model_type: FactorModelType | None = None,
    annualization_factor: int = _DEFAULT_ANNUALIZATION,
) -> FactorRegressionResult:
    """Run OLS regression of portfolio returns on factor returns.

    The regression model is ``r_p = alpha + beta_1*f_1 + ... + beta_k*f_k + eps``
    where ``f_i`` are the factor return columns.

    Args:
        portfolio_returns: 1-D array of portfolio period returns.
        factor_returns: DataFrame with one column per factor.  Column
            names become the factor labels.
        model_type: Override for model type.  If ``None``, inferred from
            the column names (Mkt-RF/SMB/HML/RMW/CMA).
        annualization_factor: Trading periods per year.  Defaults to 252.

    Returns:
        ``FactorRegressionResult`` with loadings, alpha, R-squared,
        t-statistics, and p-values.

    Raises:
        ValueError: If fewer than 30 observations, length mismatch,
            no factor columns, or NaN values are present.
    """
    portfolio_returns = np.asarray(portfolio_returns, dtype=float)
    _validate_inputs(portfolio_returns, factor_returns, annualization_factor)

    factor_names = tuple(str(c) for c in factor_returns.columns)
    factor_matrix = factor_returns.to_numpy(dtype=float)

    n = len(portfolio_returns)
    k = len(factor_names)

    # Design matrix: [ones | factors]
    x_mat = np.column_stack([np.ones(n), factor_matrix])
    y = portfolio_returns

    # OLS via least-squares
    coeffs, _residuals_arr, _rank, _sv = np.linalg.lstsq(x_mat, y, rcond=None)

    intercept = float(coeffs[0])
    betas = coeffs[1:]

    # Predictions and residuals
    y_hat = x_mat @ coeffs
    residuals = y - y_hat

    # R-squared
    ss_res = float(np.sum(residuals**2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    r_squared = max(0.0, min(1.0, r_squared))

    # Adjusted R-squared
    adj_r_squared = 1.0 - (1.0 - r_squared) * (n - 1) / (n - k - 1) if n > k + 1 else r_squared

    # Residual standard deviation
    dof = n - k - 1
    residual_std = math.sqrt(ss_res / dof) if dof > 0 else 0.0

    # Standard errors via pinv for collinearity safety
    xtx_inv = np.linalg.pinv(x_mat.T @ x_mat)
    se = residual_std * np.sqrt(np.diag(xtx_inv))

    # T-statistics and p-values
    t_values = coeffs / np.where(se > 0, se, 1e-12)
    p_vals = 2.0 * (1.0 - stats.t.cdf(np.abs(t_values), df=max(dof, 1)))

    # Build output dicts
    loadings = {name: float(betas[i]) for i, name in enumerate(factor_names)}
    alpha_annualized = intercept * annualization_factor

    t_stats: dict[str, float] = {"alpha": float(t_values[0])}
    p_values: dict[str, float] = {"alpha": float(p_vals[0])}
    for i, name in enumerate(factor_names):
        t_stats[name] = float(t_values[i + 1])
        p_values[name] = float(p_vals[i + 1])

    resolved_model = model_type if model_type is not None else _infer_model_type(factor_names)

    return FactorRegressionResult(
        loadings=loadings,
        alpha=alpha_annualized,
        r_squared=r_squared,
        adj_r_squared=adj_r_squared,
        residual_std=residual_std,
        t_stats=t_stats,
        p_values=p_values,
        factor_names=factor_names,
        model_type=resolved_model,
        n_observations=n,
        annualization_factor=annualization_factor,
    )


def compute_rolling_r_squared(
    portfolio_returns: np.ndarray,
    factor_returns: pd.DataFrame,
    window: int = 63,
    annualization_factor: int = _DEFAULT_ANNUALIZATION,
) -> tuple[tuple[float, ...], tuple[str, ...]]:
    """Compute rolling-window R-squared for factor model fit over time.

    Args:
        portfolio_returns: 1-D array of portfolio period returns.
        factor_returns: DataFrame with one column per factor.
        window: Rolling window size in bars.  Defaults to 63 (~1 quarter).
        annualization_factor: Trading periods per year.

    Returns:
        A 2-tuple of:
        - ``values``: R-squared at each bar; ``float('nan')`` for the
          first ``window - 1`` positions.
        - ``dates``: String index labels (from ``factor_returns.index``)
          or ordinal indices if the index is not string-like.

    Raises:
        ValueError: If inputs are too short or have NaN.
    """
    portfolio_returns = np.asarray(portfolio_returns, dtype=float)
    if window < 2:
        raise ValueError(f"window must be >= 2, got {window}")
    if len(portfolio_returns) < window:
        raise ValueError(f"Need at least {window} observations for window={window}, got {len(portfolio_returns)}")
    if len(portfolio_returns) != len(factor_returns):
        raise ValueError(
            f"portfolio_returns length ({len(portfolio_returns)}) must equal "
            f"factor_returns length ({len(factor_returns)})"
        )

    factor_matrix = factor_returns.to_numpy(dtype=float)
    n = len(portfolio_returns)

    values: list[float] = []
    for i in range(n):
        if i < window - 1:
            values.append(float("nan"))
        else:
            start = i - window + 1
            y_win = portfolio_returns[start : i + 1]
            x_win = np.column_stack([np.ones(window), factor_matrix[start : i + 1]])
            coeffs, _res, _rank, _sv = np.linalg.lstsq(x_win, y_win, rcond=None)
            y_hat = x_win @ coeffs
            ss_res = float(np.sum((y_win - y_hat) ** 2))
            ss_tot = float(np.sum((y_win - np.mean(y_win)) ** 2))
            r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
            values.append(max(0.0, min(1.0, r2)))

    # Build date labels
    try:
        dates = tuple(str(d) for d in factor_returns.index)
    except Exception:
        dates = tuple(str(i) for i in range(n))

    return tuple(values), dates
