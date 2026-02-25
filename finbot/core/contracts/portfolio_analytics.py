"""Typed contracts for standalone portfolio analytics.

Defines immutable result containers for rolling metrics, benchmark
comparison, drawdown analysis, and correlation / diversification
metrics.  Engine-agnostic; works with any returns or price series.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RollingMetricsResult:
    """Container for rolling-window time-series performance metrics.

    Attributes:
        window: Rolling window size in bars.
        n_obs: Total number of observations in the input series.
        sharpe: Rolling annualized Sharpe ratio; NaN for the first
            ``window - 1`` positions.
        volatility: Rolling annualized volatility; same length as ``sharpe``.
        beta: Rolling beta vs benchmark; ``None`` when no benchmark was
            supplied.  Same length as ``sharpe`` when present.
        dates: Date labels for each bar (ISO strings or ordinal indices
            as strings).  Same length as ``sharpe``.
        annualization_factor: Trading periods per year used for scaling
            (e.g. 252 for daily data).
    """

    window: int
    n_obs: int
    sharpe: tuple[float, ...]
    volatility: tuple[float, ...]
    beta: tuple[float, ...] | None
    dates: tuple[str, ...]
    annualization_factor: int

    def __post_init__(self) -> None:
        """Validate rolling metrics result fields."""
        if self.window < 2:
            raise ValueError(f"window must be >= 2, got {self.window}")
        if self.n_obs < self.window:
            raise ValueError(f"n_obs ({self.n_obs}) must be >= window ({self.window})")
        if len(self.sharpe) != len(self.volatility):
            raise ValueError(
                f"sharpe length ({len(self.sharpe)}) must equal volatility length ({len(self.volatility)})"
            )
        if len(self.dates) != len(self.sharpe):
            raise ValueError(f"dates length ({len(self.dates)}) must equal sharpe length ({len(self.sharpe)})")
        if self.beta is not None and len(self.beta) != len(self.sharpe):
            raise ValueError(f"beta length ({len(self.beta)}) must equal sharpe length ({len(self.sharpe)})")
        if self.annualization_factor < 1:
            raise ValueError(f"annualization_factor must be >= 1, got {self.annualization_factor}")


@dataclass(frozen=True, slots=True)
class BenchmarkComparisonResult:
    """OLS-based benchmark statistics for a portfolio vs a reference index.

    Attributes:
        alpha: Jensen's alpha, annualized (OLS intercept x annualization factor).
        beta: Systematic beta (OLS slope of portfolio excess returns on
            benchmark excess returns).
        r_squared: Coefficient of determination in [0, 1].
        tracking_error: Annualized standard deviation of active returns
            (portfolio - benchmark).
        information_ratio: Active return divided by tracking error.  May be
            ``±inf`` when tracking error is zero.
        up_capture: Ratio of mean portfolio return to mean benchmark return
            on days when the benchmark is positive.  ``nan`` if no such days.
        down_capture: Same ratio on days when the benchmark is negative.
            ``nan`` if no such days.
        benchmark_name: Human-readable label for the benchmark.
        n_observations: Number of aligned return observations used.
        annualization_factor: Trading periods per year.
    """

    alpha: float
    beta: float
    r_squared: float
    tracking_error: float
    information_ratio: float
    up_capture: float
    down_capture: float
    benchmark_name: str
    n_observations: int
    annualization_factor: int

    def __post_init__(self) -> None:
        """Validate benchmark comparison result fields."""
        if not (0.0 <= self.r_squared <= 1.0):
            raise ValueError(f"r_squared must be in [0, 1], got {self.r_squared}")
        if self.tracking_error < 0:
            raise ValueError(f"tracking_error must be >= 0, got {self.tracking_error}")
        if self.n_observations < 2:
            raise ValueError(f"n_observations must be >= 2, got {self.n_observations}")
        if self.annualization_factor < 1:
            raise ValueError(f"annualization_factor must be >= 1, got {self.annualization_factor}")


@dataclass(frozen=True, slots=True)
class DrawdownPeriod:
    """A single peak-to-trough-to-recovery drawdown episode.

    Attributes:
        start_idx: Bar index where the drawdown begins (the last peak).
        trough_idx: Bar index of the maximum loss within the episode.
        end_idx: Bar index of full recovery; ``None`` if the series ends
            while still in drawdown.
        depth: Drawdown magnitude as a positive fraction
            (e.g. 0.20 = 20% loss from peak).
        duration_bars: Number of bars from peak to trough.
        recovery_bars: Bars from trough to recovery; ``None`` when
            ``end_idx`` is ``None``.
    """

    start_idx: int
    trough_idx: int
    end_idx: int | None
    depth: float
    duration_bars: int
    recovery_bars: int | None

    def __post_init__(self) -> None:
        """Validate drawdown period fields."""
        if self.start_idx < 0:
            raise ValueError(f"start_idx must be >= 0, got {self.start_idx}")
        if self.trough_idx < self.start_idx:
            raise ValueError(f"trough_idx ({self.trough_idx}) must be >= start_idx ({self.start_idx})")
        if self.end_idx is not None and self.end_idx < self.trough_idx:
            raise ValueError(f"end_idx ({self.end_idx}) must be >= trough_idx ({self.trough_idx})")
        if self.depth < 0:
            raise ValueError(f"depth must be >= 0, got {self.depth}")
        if self.duration_bars < 0:
            raise ValueError(f"duration_bars must be >= 0, got {self.duration_bars}")
        if self.recovery_bars is not None and self.recovery_bars < 0:
            raise ValueError(f"recovery_bars must be >= 0, got {self.recovery_bars}")


@dataclass(frozen=True, slots=True)
class DrawdownAnalysisResult:
    """Aggregate drawdown analysis over a full returns series.

    Attributes:
        periods: Detected drawdown episodes sorted by depth (deepest first),
            up to ``top_n`` entries.
        underwater_curve: Signed underwater fraction at each bar
            (e.g. -0.20 means 20% below the running peak).
            Length equals ``n_observations``.
        n_periods: Number of periods in ``periods`` (after top-N truncation).
        max_depth: Worst single drawdown depth across all detected periods
            (positive fraction).
        avg_depth: Mean depth across all detected periods (positive fraction).
        avg_duration_bars: Mean bars from peak to trough across all periods.
        avg_recovery_bars: Mean bars from trough to recovery; ``None`` when
            no period has been fully recovered.
        current_drawdown: Drawdown depth at the final bar (positive; 0 if at
            an all-time high).
        n_observations: Length of the input returns series.
    """

    periods: tuple[DrawdownPeriod, ...]
    underwater_curve: tuple[float, ...]
    n_periods: int
    max_depth: float
    avg_depth: float
    avg_duration_bars: float
    avg_recovery_bars: float | None
    current_drawdown: float
    n_observations: int

    def __post_init__(self) -> None:
        """Validate drawdown analysis result fields."""
        if self.n_periods != len(self.periods):
            raise ValueError(f"n_periods ({self.n_periods}) must equal len(periods) ({len(self.periods)})")
        if len(self.underwater_curve) != self.n_observations:
            raise ValueError(
                f"underwater_curve length ({len(self.underwater_curve)}) must equal "
                f"n_observations ({self.n_observations})"
            )
        if self.max_depth < 0:
            raise ValueError(f"max_depth must be >= 0, got {self.max_depth}")
        if self.current_drawdown < 0:
            raise ValueError(f"current_drawdown must be >= 0, got {self.current_drawdown}")
        if self.n_observations < 1:
            raise ValueError(f"n_observations must be >= 1, got {self.n_observations}")


@dataclass(frozen=True, slots=True)
class DiversificationResult:
    """Portfolio-level diversification metrics derived from multi-asset returns.

    Attributes:
        n_assets: Number of assets.
        weights: Mapping from asset name to portfolio weight; values sum to 1.
        herfindahl_index: Herfindahl-Hirschman Index = sum(w^2); in (0, 1].
            Lower values indicate greater diversification.
        effective_n: Effective number of uncorrelated assets = 1 / HHI.
            Equals ``n_assets`` for equal weights.
        diversification_ratio: Weighted average of individual asset
            volatilities divided by portfolio volatility.  Values > 1 indicate
            diversification benefit.
        avg_pairwise_correlation: Mean of all unique pairwise correlations
            (upper-triangle of the correlation matrix, excluding diagonal).
        correlation_matrix: Full pairwise correlation as a nested dict
            ``{asset: {asset: corr}}`` (JSON-safe).
        individual_vols: Per-asset annualized volatility.
        portfolio_vol: Weighted portfolio annualized volatility.
        n_observations: Number of return observations in the input DataFrame.
        annualization_factor: Trading periods per year used for scaling.
    """

    n_assets: int
    weights: dict[str, float]
    herfindahl_index: float
    effective_n: float
    diversification_ratio: float
    avg_pairwise_correlation: float
    correlation_matrix: dict[str, dict[str, float]]
    individual_vols: dict[str, float]
    portfolio_vol: float
    n_observations: int
    annualization_factor: int

    def __post_init__(self) -> None:
        """Validate diversification result fields."""
        if self.n_assets < 2:
            raise ValueError(f"n_assets must be >= 2, got {self.n_assets}")
        if not (0.0 < self.herfindahl_index <= 1.0):
            raise ValueError(f"herfindahl_index must be in (0, 1], got {self.herfindahl_index}")
        if self.effective_n < 1.0:
            raise ValueError(f"effective_n must be >= 1.0, got {self.effective_n}")
        if self.portfolio_vol < 0:
            raise ValueError(f"portfolio_vol must be >= 0, got {self.portfolio_vol}")
        if not (-1.0 <= self.avg_pairwise_correlation <= 1.0):
            raise ValueError(f"avg_pairwise_correlation must be in [-1, 1], got {self.avg_pairwise_correlation}")
        weight_sum = sum(self.weights.values())
        if abs(weight_sum - 1.0) > 1e-9:
            raise ValueError(f"weights must sum to 1.0, got {weight_sum}")
        if self.annualization_factor < 1:
            raise ValueError(f"annualization_factor must be >= 1, got {self.annualization_factor}")
