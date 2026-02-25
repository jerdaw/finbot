"""Typed contracts for Fama-French-style multi-factor model analysis.

Defines immutable result containers for factor regression, return
attribution, and risk decomposition.  Engine-agnostic; works with any
returns series and user-supplied factor data.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class FactorModelType(StrEnum):
    """Supported factor model types."""

    CAPM = "CAPM"
    FF3 = "FF3"
    FF5 = "FF5"
    CUSTOM = "CUSTOM"


@dataclass(frozen=True, slots=True)
class FactorRegressionResult:
    """OLS regression of portfolio returns on factor returns.

    Attributes:
        loadings: Factor betas (slope coefficients), keyed by factor name.
        alpha: Annualized intercept (excess return unexplained by factors).
        r_squared: Coefficient of determination in [0, 1].
        adj_r_squared: Adjusted R-squared accounting for number of factors.
        residual_std: Standard deviation of regression residuals.
        t_stats: T-statistics for each factor loading plus alpha, keyed
            by ``"alpha"`` and each factor name.
        p_values: Two-sided p-values corresponding to ``t_stats``.
        factor_names: Ordered factor names matching the regression columns.
        model_type: Inferred or specified factor model type.
        n_observations: Number of return observations used.
        annualization_factor: Trading periods per year used for alpha scaling.
    """

    loadings: dict[str, float]
    alpha: float
    r_squared: float
    adj_r_squared: float
    residual_std: float
    t_stats: dict[str, float]
    p_values: dict[str, float]
    factor_names: tuple[str, ...]
    model_type: FactorModelType
    n_observations: int
    annualization_factor: int

    def __post_init__(self) -> None:
        """Validate factor regression result fields."""
        if not (0.0 <= self.r_squared <= 1.0):
            raise ValueError(f"r_squared must be in [0, 1], got {self.r_squared}")
        if self.residual_std < 0:
            raise ValueError(f"residual_std must be >= 0, got {self.residual_std}")
        if self.n_observations < 2:
            raise ValueError(f"n_observations must be >= 2, got {self.n_observations}")
        if self.annualization_factor < 1:
            raise ValueError(f"annualization_factor must be >= 1, got {self.annualization_factor}")
        if set(self.loadings.keys()) != set(self.factor_names):
            raise ValueError(
                f"loadings keys {set(self.loadings.keys())} must match factor_names {set(self.factor_names)}"
            )
        expected_t_keys = {"alpha"} | set(self.factor_names)
        if set(self.t_stats.keys()) != expected_t_keys:
            raise ValueError(
                f"t_stats keys {set(self.t_stats.keys())} must match factor_names + 'alpha' {expected_t_keys}"
            )
        if set(self.p_values.keys()) != expected_t_keys:
            raise ValueError(
                f"p_values keys {set(self.p_values.keys())} must match factor_names + 'alpha' {expected_t_keys}"
            )


@dataclass(frozen=True, slots=True)
class FactorAttributionResult:
    """Return attribution decomposed by factor contributions.

    Attributes:
        factor_contributions: Per-factor contribution to total return,
            keyed by factor name.
        alpha_contribution: Return attributable to alpha (skill / residual
            intercept) over the period.
        total_return: Cumulative portfolio return over the period.
        explained_return: Sum of all factor contributions plus alpha.
        residual_return: ``total_return - explained_return``; the
            unexplained portion.
        factor_names: Ordered factor names.
        n_observations: Number of return observations used.
    """

    factor_contributions: dict[str, float]
    alpha_contribution: float
    total_return: float
    explained_return: float
    residual_return: float
    factor_names: tuple[str, ...]
    n_observations: int

    def __post_init__(self) -> None:
        """Validate factor attribution result fields."""
        if self.n_observations < 2:
            raise ValueError(f"n_observations must be >= 2, got {self.n_observations}")
        if set(self.factor_contributions.keys()) != set(self.factor_names):
            raise ValueError(
                f"factor_contributions keys {set(self.factor_contributions.keys())} "
                f"must match factor_names {set(self.factor_names)}"
            )


@dataclass(frozen=True, slots=True)
class FactorRiskResult:
    """Variance decomposition into systematic and idiosyncratic components.

    Attributes:
        systematic_variance: Variance explained by the factor model
            (``beta.T @ Sigma_f @ beta``).
        idiosyncratic_variance: Residual variance not explained by factors.
        total_variance: Total portfolio return variance.
        pct_systematic: Fraction of total variance that is systematic,
            in [0, 1].
        marginal_contributions: Per-factor marginal contribution to
            systematic variance, keyed by factor name.
        factor_names: Ordered factor names.
        n_observations: Number of return observations used.
    """

    systematic_variance: float
    idiosyncratic_variance: float
    total_variance: float
    pct_systematic: float
    marginal_contributions: dict[str, float]
    factor_names: tuple[str, ...]
    n_observations: int

    def __post_init__(self) -> None:
        """Validate factor risk result fields."""
        if self.systematic_variance < 0:
            raise ValueError(f"systematic_variance must be >= 0, got {self.systematic_variance}")
        if self.idiosyncratic_variance < 0:
            raise ValueError(f"idiosyncratic_variance must be >= 0, got {self.idiosyncratic_variance}")
        if self.total_variance < 0:
            raise ValueError(f"total_variance must be >= 0, got {self.total_variance}")
        if not (0.0 <= self.pct_systematic <= 1.0):
            raise ValueError(f"pct_systematic must be in [0, 1], got {self.pct_systematic}")
        if self.n_observations < 2:
            raise ValueError(f"n_observations must be >= 2, got {self.n_observations}")
        if set(self.marginal_contributions.keys()) != set(self.factor_names):
            raise ValueError(
                f"marginal_contributions keys {set(self.marginal_contributions.keys())} "
                f"must match factor_names {set(self.factor_names)}"
            )
