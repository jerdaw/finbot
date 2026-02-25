"""Kelly criterion computation for single and multi-asset portfolios.

Provides three entry points:

- ``compute_kelly_criterion``: Classic Kelly formula from win_rate + ratio.
- ``compute_kelly_from_returns``: Estimate Kelly from a raw returns series.
- ``compute_multi_asset_kelly``: Matrix Kelly optimisation for N assets.

All results are expressed as fractions of capital to allocate.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from finbot.core.contracts.risk_analytics import KellyResult, MultiAssetKellyResult

_MIN_OBSERVATIONS = 10


def compute_kelly_criterion(
    win_rate: float,
    win_loss_ratio: float,
) -> KellyResult:
    """Compute Kelly fraction from win rate and win/loss ratio.

    Uses the classic discrete Kelly formula:
        f* = win_rate - (1 - win_rate) / win_loss_ratio

    Args:
        win_rate: Fraction of periods with positive outcome, in [0, 1].
        win_loss_ratio: Average win / average loss (positive ratio).

    Returns:
        ``KellyResult`` with full, half, and quarter Kelly fractions.

    Raises:
        ValueError: If ``win_rate`` is outside [0, 1] or
            ``win_loss_ratio`` <= 0.
    """
    if not (0 <= win_rate <= 1):
        raise ValueError(f"win_rate must be in [0, 1], got {win_rate}")
    if win_loss_ratio <= 0:
        raise ValueError(f"win_loss_ratio must be > 0, got {win_loss_ratio}")

    full_kelly = win_rate - (1.0 - win_rate) / win_loss_ratio
    expected_value = win_rate * win_loss_ratio - (1.0 - win_rate)

    return KellyResult(
        full_kelly=full_kelly,
        half_kelly=full_kelly * 0.5,
        quarter_kelly=full_kelly * 0.25,
        win_rate=win_rate,
        win_loss_ratio=win_loss_ratio,
        expected_value=expected_value,
        is_positive_ev=expected_value > 0,
        n_observations=0,
    )


def compute_kelly_from_returns(
    returns: np.ndarray,
) -> KellyResult:
    """Estimate Kelly criterion from a raw daily returns series.

    Wins are defined as positive return days; losses as negative or zero.
    The win/loss ratio is the mean absolute win divided by the mean
    absolute loss.  Zero-loss returns are excluded from the loss mean to
    avoid division by zero.

    Args:
        returns: 1-D array of daily returns (e.g. 0.01 = 1% gain).

    Returns:
        ``KellyResult`` with all fractions and win-rate statistics.

    Raises:
        ValueError: If fewer than 10 observations are provided.
    """
    returns = np.asarray(returns, dtype=float)
    if len(returns) < _MIN_OBSERVATIONS:
        raise ValueError(f"Need at least {_MIN_OBSERVATIONS} observations, got {len(returns)}")

    wins = returns[returns > 0]
    losses = returns[returns < 0]

    n = len(returns)
    win_rate = len(wins) / n if n > 0 else 0.0

    avg_win = float(np.mean(wins)) if len(wins) > 0 else 0.0
    avg_loss = float(np.mean(np.abs(losses))) if len(losses) > 0 else 1e-9
    win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0.0

    full_kelly = win_rate - (1.0 - win_rate) / win_loss_ratio if win_loss_ratio > 0 else 0.0

    expected_value = win_rate * win_loss_ratio - (1.0 - win_rate)

    return KellyResult(
        full_kelly=full_kelly,
        half_kelly=full_kelly * 0.5,
        quarter_kelly=full_kelly * 0.25,
        win_rate=win_rate,
        win_loss_ratio=win_loss_ratio,
        expected_value=expected_value,
        is_positive_ev=expected_value > 0,
        n_observations=n,
    )


def compute_multi_asset_kelly(
    returns_df: pd.DataFrame,
) -> MultiAssetKellyResult:
    """Compute multi-asset Kelly weights via the matrix Kelly formula.

    Uses the continuous Kelly optimum: ``f* = Sigma^{-1} @ mu``, where
    ``Sigma`` is the sample covariance matrix and ``mu`` is the vector of
    mean returns.  Raw weights are clipped to ``[0, 1]`` and normalised to
    sum to 1 before being stored as ``weights``.

    Args:
        returns_df: DataFrame where each column is a daily returns series
            for one asset.  All columns must have the same length.

    Returns:
        ``MultiAssetKellyResult`` with per-asset and portfolio-level Kelly data.

    Raises:
        ValueError: If fewer than 2 assets are supplied.
    """
    if returns_df.shape[1] < 2:
        raise ValueError(f"compute_multi_asset_kelly requires at least 2 assets, got {returns_df.shape[1]}")

    assets = list(returns_df.columns)
    n_obs = len(returns_df)
    arr = returns_df.to_numpy(dtype=float)

    mu = np.mean(arr, axis=0)
    cov = np.cov(arr, rowvar=False, ddof=1)

    try:
        cov_inv = np.linalg.inv(cov)
    except np.linalg.LinAlgError:
        cov_inv = np.linalg.pinv(cov)

    raw_kelly = cov_inv @ mu

    # Clip to [0, 1] and normalise
    clipped = np.clip(raw_kelly, 0.0, None)
    total = float(np.sum(clipped))
    practical = clipped / total if total > 0 else np.ones(len(assets)) / len(assets)

    half_raw = raw_kelly * 0.5

    # Correlation matrix (JSON-safe nested dict)
    corr = np.corrcoef(arr, rowvar=False)
    correlation_matrix: dict[str, dict[str, float]] = {
        a: {b: float(corr[i, j]) for j, b in enumerate(assets)} for i, a in enumerate(assets)
    }

    # Per-asset single-asset Kelly results
    asset_kelly_results: dict[str, KellyResult] = {
        asset: compute_kelly_from_returns(returns_df[asset].to_numpy()) for asset in assets
    }

    return MultiAssetKellyResult(
        weights={a: float(practical[i]) for i, a in enumerate(assets)},
        full_kelly_weights={a: float(raw_kelly[i]) for i, a in enumerate(assets)},
        half_kelly_weights={a: float(half_raw[i]) for i, a in enumerate(assets)},
        correlation_matrix=correlation_matrix,
        asset_kelly_results=asset_kelly_results,
        n_assets=len(assets),
        n_observations=n_obs,
    )
