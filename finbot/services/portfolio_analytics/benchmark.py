"""Benchmark comparison analytics for a portfolio returns series.

Computes standard relative-performance statistics against a reference
index using OLS regression and active-return analysis:

- Jensen's alpha (annualized)
- Systematic beta
- R-squared (goodness of fit)
- Tracking error (annualized active-return volatility)
- Information ratio
- Up-market and down-market capture ratios
"""

from __future__ import annotations

import math

import numpy as np
from scipy import stats

from finbot.core.contracts.portfolio_analytics import BenchmarkComparisonResult

_MIN_OBSERVATIONS = 30
_DEFAULT_ANNUALIZATION = 252


def _validate_inputs(
    portfolio_returns: np.ndarray,
    benchmark_returns: np.ndarray,
    annualization_factor: int,
) -> None:
    """Raise ValueError on invalid inputs."""
    if len(portfolio_returns) < _MIN_OBSERVATIONS:
        raise ValueError(
            f"portfolio_returns must have at least {_MIN_OBSERVATIONS} observations, got {len(portfolio_returns)}"
        )
    if len(portfolio_returns) != len(benchmark_returns):
        raise ValueError(
            f"portfolio_returns length ({len(portfolio_returns)}) must equal "
            f"benchmark_returns length ({len(benchmark_returns)})"
        )
    if annualization_factor < 1:
        raise ValueError(f"annualization_factor must be >= 1, got {annualization_factor}")


def compute_benchmark_comparison(
    portfolio_returns: np.ndarray,
    benchmark_returns: np.ndarray,
    risk_free_rate: float = 0.0,
    benchmark_name: str = "Benchmark",
    annualization_factor: int = _DEFAULT_ANNUALIZATION,
) -> BenchmarkComparisonResult:
    """Compute standard benchmark comparison statistics via OLS regression.

    The portfolio and benchmark excess returns (returns minus the per-bar
    risk-free rate) are regressed: ``excess_p = alpha + beta * excess_b``.

    Args:
        portfolio_returns: 1-D array of portfolio period returns.
        benchmark_returns: 1-D array of benchmark period returns.  Must be
            the same length as ``portfolio_returns``.
        risk_free_rate: Annual risk-free rate as a fraction (e.g. 0.04 = 4%).
            Converted to a per-bar rate internally.
        benchmark_name: Human-readable benchmark label stored in the result.
        annualization_factor: Trading periods per year.  Defaults to 252.

    Returns:
        BenchmarkComparisonResult with alpha, beta, R², tracking error,
        information ratio, and up/down capture ratios.

    Raises:
        ValueError: If fewer than 30 observations are supplied or the arrays
            have different lengths.
    """
    portfolio_returns = np.asarray(portfolio_returns, dtype=float)
    benchmark_returns = np.asarray(benchmark_returns, dtype=float)
    _validate_inputs(portfolio_returns, benchmark_returns, annualization_factor)

    rf_per_bar = risk_free_rate / annualization_factor
    excess_p = portfolio_returns - rf_per_bar
    excess_b = benchmark_returns - rf_per_bar

    slope, intercept, r_value, _p_value, _std_err = stats.linregress(excess_b, excess_p)
    beta = float(slope)
    alpha = float(intercept) * annualization_factor
    r_squared = float(r_value**2)

    sqrt_ann = math.sqrt(annualization_factor)
    active = portfolio_returns - benchmark_returns
    tracking_error = float(np.std(active, ddof=1)) * sqrt_ann

    mean_active_annual = float(np.mean(active)) * annualization_factor
    if tracking_error > 0:
        information_ratio = mean_active_annual / tracking_error
    elif mean_active_annual > 0:
        information_ratio = float("inf")
    elif mean_active_annual < 0:
        information_ratio = float("-inf")
    else:
        information_ratio = 0.0

    up_mask = benchmark_returns > 0
    down_mask = benchmark_returns < 0

    if np.any(up_mask):
        up_capture = float(np.mean(portfolio_returns[up_mask])) / float(np.mean(benchmark_returns[up_mask]))
    else:
        up_capture = float("nan")

    if np.any(down_mask):
        down_capture = float(np.mean(portfolio_returns[down_mask])) / float(np.mean(benchmark_returns[down_mask]))
    else:
        down_capture = float("nan")

    return BenchmarkComparisonResult(
        alpha=alpha,
        beta=beta,
        r_squared=r_squared,
        tracking_error=tracking_error,
        information_ratio=information_ratio,
        up_capture=up_capture,
        down_capture=down_capture,
        benchmark_name=benchmark_name,
        n_observations=len(portfolio_returns),
        annualization_factor=annualization_factor,
    )
