"""Rolling performance metrics for a returns series.

Computes rolling Sharpe ratio, annualized volatility, and (optionally)
rolling beta relative to a benchmark — all as full-length time-series
using a sliding window.

The first ``window - 1`` positions contain ``NaN`` (insufficient history).
"""

from __future__ import annotations

import math

import numpy as np

from finbot.core.contracts.portfolio_analytics import RollingMetricsResult

_MIN_OBSERVATIONS = 30
_DEFAULT_WINDOW = 63  # ~1 quarter of trading days
_DEFAULT_ANNUALIZATION = 252


def _validate_returns(returns: np.ndarray, label: str = "returns") -> None:
    """Raise ValueError if the returns array is too short."""
    if len(returns) < _MIN_OBSERVATIONS:
        raise ValueError(f"{label} must have at least {_MIN_OBSERVATIONS} observations, got {len(returns)}")


def compute_rolling_metrics(
    returns: np.ndarray,
    window: int = _DEFAULT_WINDOW,
    benchmark_returns: np.ndarray | None = None,
    risk_free_rate: float = 0.0,
    annualization_factor: int = _DEFAULT_ANNUALIZATION,
) -> RollingMetricsResult:
    """Compute rolling Sharpe ratio, volatility, and beta.

    For each bar ``i >= window - 1`` the metrics are calculated over the
    window ``returns[i - window + 1 : i + 1]``.  Earlier positions hold
    ``float('nan')``.

    Args:
        returns: 1-D array of period returns (e.g. 0.01 = 1% gain).
        window: Rolling window size in bars.  Defaults to 63 (~1 quarter).
        benchmark_returns: Optional 1-D benchmark returns array of the same
            length as ``returns``.  When supplied, rolling beta is computed.
        risk_free_rate: Annual risk-free rate as a fraction (e.g. 0.04 = 4%).
            Converted to a per-bar rate internally.
        annualization_factor: Trading periods per year.  Defaults to 252.

    Returns:
        RollingMetricsResult with ``sharpe``, ``volatility``, and optionally
        ``beta`` series, each of length ``n``.

    Raises:
        ValueError: If fewer than 30 observations are supplied, ``window < 2``,
            or ``benchmark_returns`` has a different length from ``returns``.
    """
    returns = np.asarray(returns, dtype=float)
    _validate_returns(returns)

    if window < 2:
        raise ValueError(f"window must be >= 2, got {window}")
    if annualization_factor < 1:
        raise ValueError(f"annualization_factor must be >= 1, got {annualization_factor}")

    n = len(returns)

    if benchmark_returns is not None:
        benchmark_returns = np.asarray(benchmark_returns, dtype=float)
        if len(benchmark_returns) != n:
            raise ValueError(f"benchmark_returns length ({len(benchmark_returns)}) must equal returns length ({n})")

    rf_per_bar = risk_free_rate / annualization_factor
    excess = returns - rf_per_bar
    sqrt_ann = math.sqrt(annualization_factor)

    sharpe_arr = np.full(n, float("nan"))
    vol_arr = np.full(n, float("nan"))
    beta_arr: np.ndarray | None = np.full(n, float("nan")) if benchmark_returns is not None else None

    for i in range(window - 1, n):
        start = i - window + 1
        window_excess = excess[start : i + 1]
        mu = float(np.mean(window_excess))
        sigma = float(np.std(window_excess, ddof=1))

        sharpe_arr[i] = (mu / sigma * sqrt_ann) if sigma > 0 else 0.0
        vol_arr[i] = sigma * sqrt_ann

        if benchmark_returns is not None and beta_arr is not None:
            window_bench = benchmark_returns[start : i + 1]
            bench_var = float(np.var(window_bench, ddof=1))
            if bench_var > 0:
                cov_val = float(np.cov(window_excess, window_bench, ddof=1)[0, 1])
                beta_arr[i] = cov_val / bench_var
            else:
                beta_arr[i] = 0.0

    dates = tuple(str(i) for i in range(n))
    beta_tuple: tuple[float, ...] | None = tuple(float(x) for x in beta_arr) if beta_arr is not None else None

    return RollingMetricsResult(
        window=window,
        n_obs=n,
        sharpe=tuple(float(x) for x in sharpe_arr),
        volatility=tuple(float(x) for x in vol_arr),
        beta=beta_tuple,
        dates=dates,
        annualization_factor=annualization_factor,
    )
