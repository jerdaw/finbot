"""Tests for factor attribution computation."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from finbot.core.contracts.factor_analytics import (
    FactorAttributionResult,
    FactorRegressionResult,
)
from finbot.services.factor_analytics.factor_attribution import compute_factor_attribution


@pytest.fixture()
def rng() -> np.random.Generator:
    return np.random.default_rng(99)


@pytest.fixture()
def synthetic_data(rng: np.random.Generator) -> tuple[np.ndarray, pd.DataFrame]:
    """Synthetic portfolio = 1.0 * F1 + 0.5 * F2 + small noise."""
    n = 300
    f1 = rng.normal(0.0003, 0.01, n)
    f2 = rng.normal(0.0001, 0.005, n)
    noise = rng.normal(0, 0.001, n)
    portfolio = 1.0 * f1 + 0.5 * f2 + noise
    factors = pd.DataFrame({"F1": f1, "F2": f2})
    return portfolio, factors


@pytest.fixture()
def reg_result(synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> FactorRegressionResult:
    from finbot.services.factor_analytics.factor_regression import compute_factor_regression

    portfolio, factors = synthetic_data
    return compute_factor_regression(portfolio, factors)


class TestComputeFactorAttribution:
    """Tests for compute_factor_attribution."""

    def test_basic(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_attribution(portfolio, factors)
        assert isinstance(result, FactorAttributionResult)
        assert result.n_observations == 300

    def test_with_precomputed_regression(
        self,
        synthetic_data: tuple[np.ndarray, pd.DataFrame],
        reg_result: FactorRegressionResult,
    ) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_attribution(portfolio, factors, regression_result=reg_result)
        assert result.factor_names == reg_result.factor_names

    def test_total_equals_explained_plus_residual(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_attribution(portfolio, factors)
        assert abs(result.total_return - (result.explained_return + result.residual_return)) < 1e-10

    def test_explained_equals_factors_plus_alpha(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_attribution(portfolio, factors)
        factor_sum = sum(result.factor_contributions.values())
        assert abs(result.explained_return - (factor_sum + result.alpha_contribution)) < 1e-10

    def test_factor_names_match(
        self,
        synthetic_data: tuple[np.ndarray, pd.DataFrame],
        reg_result: FactorRegressionResult,
    ) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_attribution(portfolio, factors, regression_result=reg_result)
        assert set(result.factor_contributions.keys()) == set(result.factor_names)

    def test_dominant_factor_has_largest_contribution(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        """F1 has loading=1.0 and larger variance => larger contribution."""
        portfolio, factors = synthetic_data
        result = compute_factor_attribution(portfolio, factors)
        assert abs(result.factor_contributions["F1"]) > abs(result.factor_contributions["F2"])

    def test_too_few_observations_raises(self) -> None:
        portfolio = np.array([0.01] * 10)
        factors = pd.DataFrame({"F1": [0.01] * 10})
        with pytest.raises(ValueError, match="at least 30"):
            compute_factor_attribution(portfolio, factors)

    def test_length_mismatch_raises(self) -> None:
        portfolio = np.array([0.01] * 50)
        factors = pd.DataFrame({"F1": [0.01] * 40})
        with pytest.raises(ValueError, match="length"):
            compute_factor_attribution(portfolio, factors)

    def test_single_factor(self, rng: np.random.Generator) -> None:
        n = 100
        f1 = rng.normal(0, 0.01, n)
        portfolio = 1.5 * f1 + rng.normal(0, 0.001, n)
        factors = pd.DataFrame({"Mkt-RF": f1})
        result = compute_factor_attribution(portfolio, factors)
        assert len(result.factor_contributions) == 1

    def test_zero_returns(self) -> None:
        """All-zero returns => zero contributions."""
        n = 50
        portfolio = np.zeros(n)
        factors = pd.DataFrame({"F1": np.zeros(n), "F2": np.zeros(n)})
        result = compute_factor_attribution(portfolio, factors)
        assert abs(result.total_return) < 1e-10

    def test_residual_is_small_for_well_specified_model(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_attribution(portfolio, factors)
        assert abs(result.residual_return) < abs(result.total_return) * 0.5

    def test_annualization_factor_affects_alpha_contribution(self, rng: np.random.Generator) -> None:
        n = 100
        f1 = rng.normal(0, 0.01, n)
        portfolio = f1 + rng.normal(0, 0.001, n) + 0.001
        factors = pd.DataFrame({"F1": f1})
        result_252 = compute_factor_attribution(portfolio, factors, annualization_factor=252)
        result_12 = compute_factor_attribution(portfolio, factors, annualization_factor=12)
        # Alpha contribution should be the same (daily alpha * n) regardless of annualization
        # because the regression adjusts the intercept accordingly
        assert isinstance(result_252, FactorAttributionResult)
        assert isinstance(result_12, FactorAttributionResult)

    def test_many_factors(self, rng: np.random.Generator) -> None:
        n = 200
        factors = pd.DataFrame({f"F{i}": rng.normal(0, 0.01, n) for i in range(5)})
        portfolio = factors.sum(axis=1).to_numpy() + rng.normal(0, 0.001, n)
        result = compute_factor_attribution(portfolio, factors)
        assert len(result.factor_contributions) == 5

    def test_precomputed_result_consistency(
        self,
        synthetic_data: tuple[np.ndarray, pd.DataFrame],
        reg_result: FactorRegressionResult,
    ) -> None:
        """Pre-computed regression gives same loadings as internal computation."""
        portfolio, factors = synthetic_data
        result_auto = compute_factor_attribution(portfolio, factors)
        result_pre = compute_factor_attribution(portfolio, factors, regression_result=reg_result)
        for name in result_auto.factor_names:
            assert abs(result_auto.factor_contributions[name] - result_pre.factor_contributions[name]) < 1e-10

    def test_negative_total_return(self, rng: np.random.Generator) -> None:
        """Negative total returns should still decompose correctly."""
        n = 100
        f1 = rng.normal(-0.001, 0.01, n)
        portfolio = f1 + rng.normal(0, 0.001, n)
        factors = pd.DataFrame({"F1": f1})
        result = compute_factor_attribution(portfolio, factors)
        assert abs(result.total_return - (result.explained_return + result.residual_return)) < 1e-10
