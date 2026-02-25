"""Typed contracts for standalone risk analytics.

Defines immutable result containers for VaR/CVaR, stress testing,
and Kelly criterion analysis. Engine-agnostic; works with any
returns or price series.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class VaRMethod(StrEnum):
    """Value at Risk computation method."""

    HISTORICAL = "historical"
    PARAMETRIC = "parametric"
    MONTECARLO = "montecarlo"


@dataclass(frozen=True, slots=True)
class VaRResult:
    """Result of a single Value at Risk computation.

    Attributes:
        var: Positive loss magnitude (e.g. 0.02 = 2% loss at threshold).
        confidence: Confidence level (e.g. 0.95 for 95% VaR).
        method: Computation method used.
        horizon_days: Holding-period in trading days.
        n_observations: Number of return observations used.
        portfolio_value: Optional portfolio value in dollars.
        var_dollars: Optional VaR expressed in dollar terms.
    """

    var: float
    confidence: float
    method: VaRMethod
    horizon_days: int
    n_observations: int
    portfolio_value: float | None = None
    var_dollars: float | None = None

    def __post_init__(self) -> None:
        """Validate VaR result fields."""
        if not (0 < self.confidence < 1):
            raise ValueError(f"confidence must be in (0, 1), got {self.confidence}")
        if self.horizon_days < 1:
            raise ValueError(f"horizon_days must be >= 1, got {self.horizon_days}")
        if self.var < 0:
            raise ValueError(f"var must be >= 0, got {self.var}")


@dataclass(frozen=True, slots=True)
class CVaRResult:
    """Result of a Conditional Value at Risk (Expected Shortfall) computation.

    CVaR is the mean loss in the tail beyond the VaR threshold, so
    ``cvar >= var`` always holds.

    Attributes:
        cvar: Mean loss in the tail (>= var).
        var: VaR threshold used to define the tail.
        confidence: Confidence level used.
        method: Computation method used.
        n_tail_obs: Number of observations in the tail.
        n_observations: Total number of return observations.
    """

    cvar: float
    var: float
    confidence: float
    method: VaRMethod
    n_tail_obs: int
    n_observations: int

    def __post_init__(self) -> None:
        """Validate CVaR result fields."""
        if not (0 < self.confidence < 1):
            raise ValueError(f"confidence must be in (0, 1), got {self.confidence}")
        if self.cvar < self.var:
            raise ValueError(f"cvar ({self.cvar}) must be >= var ({self.var})")


@dataclass(frozen=True, slots=True)
class VaRBacktestResult:
    """Result of a VaR model backtest (violation analysis).

    Measures how often actual losses exceed predicted VaR — a well-calibrated
    model should have ``violation_rate ≈ (1 - confidence)``.

    Attributes:
        confidence: Confidence level used.
        method: VaR method under test.
        n_observations: Total observations in the backtest window.
        n_violations: Days where actual loss exceeded predicted VaR.
        violation_rate: Observed fraction of violations.
        expected_violation_rate: Theoretical fraction (1 - confidence).
        is_calibrated: True when |violation_rate - expected_rate| < 0.02.
    """

    confidence: float
    method: VaRMethod
    n_observations: int
    n_violations: int
    violation_rate: float
    expected_violation_rate: float
    is_calibrated: bool


@dataclass(frozen=True, slots=True)
class StressScenario:
    """A parametric market stress scenario.

    Attributes:
        name: Human-readable scenario name.
        shock_return: Cumulative return during shock phase (must be <= 0).
        shock_duration_days: Trading days over which the shock unfolds.
        recovery_days: Trading days until portfolio recovers to initial value.
        description: Optional narrative description.
    """

    name: str
    shock_return: float
    shock_duration_days: int
    recovery_days: int
    description: str = ""

    def __post_init__(self) -> None:
        """Validate stress scenario fields."""
        if self.shock_return > 0:
            raise ValueError(f"shock_return must be <= 0, got {self.shock_return}")
        if self.shock_duration_days < 1:
            raise ValueError(f"shock_duration_days must be >= 1, got {self.shock_duration_days}")
        if self.recovery_days < 0:
            raise ValueError(f"recovery_days must be >= 0, got {self.recovery_days}")


@dataclass(frozen=True, slots=True)
class StressTestResult:
    """Result of applying a stress scenario to a portfolio.

    Attributes:
        scenario_name: Name of the applied scenario.
        initial_value: Portfolio value at scenario start.
        trough_value: Minimum portfolio value during shock.
        trough_return: Fractional return at trough: (trough - initial) / initial.
        recovery_value: Portfolio value at end of recovery phase.
        max_drawdown_pct: Maximum percentage drawdown (positive number, e.g. 50.0).
        shock_duration_days: Shock phase length in trading days.
        recovery_days: Recovery phase length in trading days.
        price_path: Flat tuple of portfolio values over the full scenario path.
        scenario: The StressScenario that was applied.
    """

    scenario_name: str
    initial_value: float
    trough_value: float
    trough_return: float
    recovery_value: float
    max_drawdown_pct: float
    shock_duration_days: int
    recovery_days: int
    price_path: tuple[float, ...]
    scenario: StressScenario


@dataclass(frozen=True, slots=True)
class KellyResult:
    """Result of Kelly criterion computation for a single asset.

    Attributes:
        full_kelly: Unconstrained Kelly fraction.
        half_kelly: full_kelly * 0.5 (practical risk reduction).
        quarter_kelly: full_kelly * 0.25 (conservative sizing).
        win_rate: Fraction of periods with positive returns (in [0, 1]).
        win_loss_ratio: avg_win / avg_loss (absolute values).
        expected_value: Expected value per unit wagered.
        is_positive_ev: True when expected_value > 0.
        n_observations: Number of return observations used.
    """

    full_kelly: float
    half_kelly: float
    quarter_kelly: float
    win_rate: float
    win_loss_ratio: float
    expected_value: float
    is_positive_ev: bool
    n_observations: int

    def __post_init__(self) -> None:
        """Validate Kelly result fields."""
        if not (0 <= self.win_rate <= 1):
            raise ValueError(f"win_rate must be in [0, 1], got {self.win_rate}")


@dataclass(frozen=True, slots=True)
class MultiAssetKellyResult:
    """Result of multi-asset Kelly criterion optimisation.

    Uses the continuous Kelly formula ``f* = Σ⁻¹ μ`` where ``Σ`` is the
    covariance matrix and ``μ`` is the mean-returns vector.  Weights are
    clipped to ``[0, 1]`` and normalised to sum to 1.

    Attributes:
        weights: Practical weights clipped and normalised to [0, 1] sum=1.
        full_kelly_weights: Raw unconstrained Kelly weights (may exceed 1).
        half_kelly_weights: full_kelly_weights * 0.5.
        correlation_matrix: Pairwise correlation as nested dict (JSON-safe).
        asset_kelly_results: Per-asset single-asset Kelly results.
        n_assets: Number of assets.
        n_observations: Number of return observations (shared across assets).
    """

    weights: dict[str, float]
    full_kelly_weights: dict[str, float]
    half_kelly_weights: dict[str, float]
    correlation_matrix: dict[str, dict[str, float]]
    asset_kelly_results: dict[str, KellyResult]
    n_assets: int
    n_observations: int
