"""Value at Risk (VaR) and Conditional VaR (Expected Shortfall) computation.

Three methods are supported for each metric:

- ``historical``: empirical percentile of the return distribution.
- ``parametric``: closed-form normal-distribution formula.
- ``montecarlo``: simulated paths drawn from Normal(mu, sigma).

All VaR values are expressed as **positive loss magnitudes**
(e.g. ``0.02`` means a 2% loss at the given confidence level).

Square-root-of-time scaling is used for multi-day horizons, which
assumes i.i.d. returns and is standard for daily VaR calculations.
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from finbot.core.contracts.risk_analytics import CVaRResult, VaRBacktestResult, VaRMethod, VaRResult

_MIN_OBSERVATIONS = 30


def _validate_returns(returns: np.ndarray, label: str = "returns") -> None:
    """Raise ValueError if the returns array is too short."""
    if len(returns) < _MIN_OBSERVATIONS:
        raise ValueError(f"{label} must have at least {_MIN_OBSERVATIONS} observations, got {len(returns)}")


def compute_var(
    returns: np.ndarray,
    confidence: float = 0.95,
    method: str | VaRMethod = VaRMethod.HISTORICAL,
    horizon_days: int = 1,
    n_simulations: int = 10_000,
    portfolio_value: float | None = None,
) -> VaRResult:
    """Compute Value at Risk for a returns series.

    Args:
        returns: 1-D array of daily returns (e.g. 0.01 = 1% gain).
        confidence: Confidence level in (0, 1).  Defaults to 0.95.
        method: ``"historical"``, ``"parametric"``, or ``"montecarlo"``.
        horizon_days: Holding-period in trading days.  VaR is scaled by
            ``sqrt(horizon_days)`` (i.i.d. assumption).
        n_simulations: Monte Carlo paths.  Only used when ``method="montecarlo"``.
        portfolio_value: Optional dollar value; enables ``var_dollars`` output.

    Returns:
        VaRResult with ``var`` as a positive fraction.

    Raises:
        ValueError: If fewer than 30 observations are supplied.
    """
    returns = np.asarray(returns, dtype=float)
    _validate_returns(returns)
    method = VaRMethod(method)

    mu = float(np.mean(returns))
    sigma = float(np.std(returns, ddof=1))
    scale = float(np.sqrt(horizon_days))

    if method == VaRMethod.HISTORICAL:
        raw_var = float(-np.percentile(returns, (1 - confidence) * 100))
        var = raw_var * scale
    elif method == VaRMethod.PARAMETRIC:
        z = float(-stats.norm.ppf(1 - confidence))
        var = (z * sigma) * scale
    else:  # MONTECARLO
        rng = np.random.default_rng(seed=42)
        paths = rng.normal(mu, sigma, size=(n_simulations, horizon_days))
        cumulative = np.prod(1 + paths, axis=1) - 1
        var = float(-np.percentile(cumulative, (1 - confidence) * 100))

    var = max(var, 0.0)
    var_dollars = var * portfolio_value if portfolio_value is not None else None

    return VaRResult(
        var=var,
        confidence=confidence,
        method=method,
        horizon_days=horizon_days,
        n_observations=len(returns),
        portfolio_value=portfolio_value,
        var_dollars=var_dollars,
    )


def compute_cvar(
    returns: np.ndarray,
    confidence: float = 0.95,
    method: str | VaRMethod = VaRMethod.HISTORICAL,
) -> CVaRResult:
    """Compute Conditional VaR (Expected Shortfall) for a returns series.

    CVaR is the expected loss given that losses exceed the VaR threshold,
    so ``cvar >= var`` always holds.

    Args:
        returns: 1-D array of daily returns.
        confidence: Confidence level in (0, 1).  Defaults to 0.95.
        method: Computation method (same as ``compute_var``).

    Returns:
        CVaRResult containing both the CVaR and its underlying VaR.

    Raises:
        ValueError: If fewer than 30 observations are supplied.
    """
    returns = np.asarray(returns, dtype=float)
    _validate_returns(returns)
    method = VaRMethod(method)

    var_result = compute_var(returns, confidence=confidence, method=method, horizon_days=1)
    var_threshold = var_result.var

    tail_mask = returns <= -var_threshold
    tail_returns = returns[tail_mask]

    if len(tail_returns) == 0:
        cvar = var_threshold
        n_tail = 0
    else:
        cvar = float(-np.mean(tail_returns))
        n_tail = int(np.sum(tail_mask))

    cvar = max(cvar, var_threshold)

    return CVaRResult(
        cvar=cvar,
        var=var_threshold,
        confidence=confidence,
        method=method,
        n_tail_obs=n_tail,
        n_observations=len(returns),
    )


def var_backtest(
    returns: np.ndarray,
    confidence: float = 0.95,
    method: str | VaRMethod = VaRMethod.HISTORICAL,
    min_history: int = 252,
) -> VaRBacktestResult:
    """Backtest a VaR model via expanding-window violation analysis.

    For each day after the initial ``min_history`` training window, a
    1-day VaR is predicted from the preceding observations.  A violation
    occurs when the actual return falls below ``-var``.

    A model is considered **calibrated** when
    ``|violation_rate - (1 - confidence)| < 0.02``.

    Args:
        returns: 1-D array of daily returns.
        confidence: Confidence level in (0, 1).
        method: VaR computation method.
        min_history: Minimum training observations before the first forecast.

    Returns:
        VaRBacktestResult with violation statistics.

    Raises:
        ValueError: If the returns array is too short for any backtest.
    """
    returns = np.asarray(returns, dtype=float)
    _validate_returns(returns)
    method = VaRMethod(method)

    if len(returns) <= min_history:
        raise ValueError(f"Need more than {min_history} observations for backtest, got {len(returns)}")

    violations = 0
    test_count = 0

    for i in range(min_history, len(returns)):
        train = returns[:i]
        predicted_var = compute_var(train, confidence=confidence, method=method, horizon_days=1).var
        actual_return = returns[i]
        if actual_return < -predicted_var:
            violations += 1
        test_count += 1

    violation_rate = violations / test_count if test_count > 0 else 0.0
    expected_rate = 1.0 - confidence
    is_calibrated = abs(violation_rate - expected_rate) < 0.02

    return VaRBacktestResult(
        confidence=confidence,
        method=method,
        n_observations=test_count,
        n_violations=violations,
        violation_rate=violation_rate,
        expected_violation_rate=expected_rate,
        is_calibrated=is_calibrated,
    )
