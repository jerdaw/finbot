"""Full drawdown period analysis for a returns series.

Detects individual peak-to-trough-to-recovery episodes, computes the
underwater curve, and returns aggregate statistics.

Unlike ``quantstats.max_drawdown()`` (a single scalar), this module
identifies every distinct drawdown period including its depth, duration,
and recovery time — giving a complete picture of tail-risk episodes.
"""

from __future__ import annotations

import numpy as np

from finbot.core.contracts.portfolio_analytics import DrawdownAnalysisResult, DrawdownPeriod

_RECOVERY_THRESHOLD = -1e-14  # treat uw >= this as "back to peak"


def compute_drawdown_analysis(
    returns: np.ndarray,
    top_n: int = 5,
) -> DrawdownAnalysisResult:
    """Detect and analyse all drawdown episodes in a returns series.

    For each contiguous period where the portfolio is below its prior
    peak, a ``DrawdownPeriod`` record is emitted.  If the series ends
    while still in a drawdown, that period is included with ``end_idx``
    and ``recovery_bars`` set to ``None``.

    Aggregate statistics (``max_depth``, ``avg_depth``, etc.) are
    computed over **all** detected periods, not just the top-N subset
    stored in ``periods``.

    Args:
        returns: 1-D array of period returns (e.g. 0.01 = 1% gain).
        top_n: Maximum number of drawdown periods to retain in the
            result, sorted by depth (deepest first).  Defaults to 5.

    Returns:
        DrawdownAnalysisResult with the underwater curve, top-N
        periods, and aggregate statistics.

    Raises:
        ValueError: If fewer than 2 observations are supplied or
            ``top_n < 1``.
    """
    returns = np.asarray(returns, dtype=float)
    n = len(returns)

    if n < 2:
        raise ValueError(f"returns must have at least 2 observations, got {n}")
    if top_n < 1:
        raise ValueError(f"top_n must be >= 1, got {top_n}")

    wealth = np.cumprod(1.0 + returns)
    peak = np.maximum.accumulate(wealth)
    uw = (wealth - peak) / peak  # underwater curve (non-positive)

    # ── State-machine scan ────────────────────────────────────────────
    all_periods: list[DrawdownPeriod] = []
    in_drawdown = False
    peak_idx = 0
    trough_idx = 0

    for i in range(n):
        if not in_drawdown:
            if uw[i] < _RECOVERY_THRESHOLD:
                in_drawdown = True
                trough_idx = i
            else:
                peak_idx = i
        else:
            if uw[i] < uw[trough_idx]:
                trough_idx = i
            if uw[i] >= _RECOVERY_THRESHOLD:
                depth = float(-uw[trough_idx])
                dur = trough_idx - peak_idx
                rec = i - trough_idx
                all_periods.append(
                    DrawdownPeriod(
                        start_idx=peak_idx,
                        trough_idx=trough_idx,
                        end_idx=i,
                        depth=depth,
                        duration_bars=dur,
                        recovery_bars=rec,
                    )
                )
                in_drawdown = False
                peak_idx = i

    if in_drawdown:
        depth = float(-uw[trough_idx])
        dur = trough_idx - peak_idx
        all_periods.append(
            DrawdownPeriod(
                start_idx=peak_idx,
                trough_idx=trough_idx,
                end_idx=None,
                depth=depth,
                duration_bars=dur,
                recovery_bars=None,
            )
        )

    # ── Aggregate stats from all detected periods ─────────────────────
    if all_periods:
        max_depth = max(p.depth for p in all_periods)
        avg_depth = sum(p.depth for p in all_periods) / len(all_periods)
        avg_duration = sum(p.duration_bars for p in all_periods) / len(all_periods)
        recovered = [p for p in all_periods if p.recovery_bars is not None]
        avg_recovery: float | None = (
            sum(p.recovery_bars for p in recovered) / len(recovered)  # type: ignore[misc]
            if recovered
            else None
        )
    else:
        max_depth = 0.0
        avg_depth = 0.0
        avg_duration = 0.0
        avg_recovery = None

    current_drawdown = float(max(-uw[-1], 0.0))

    # ── Top-N periods sorted by depth descending ──────────────────────
    top_periods = tuple(sorted(all_periods, key=lambda p: p.depth, reverse=True)[:top_n])

    return DrawdownAnalysisResult(
        periods=top_periods,
        underwater_curve=tuple(float(x) for x in uw),
        n_periods=len(top_periods),
        max_depth=max_depth,
        avg_depth=avg_depth,
        avg_duration_bars=avg_duration,
        avg_recovery_bars=avg_recovery,
        current_drawdown=current_drawdown,
        n_observations=n,
    )
