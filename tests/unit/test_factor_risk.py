"""Tests for factor risk decomposition computation."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from finbot.core.contracts.factor_analytics import FactorRegressionResult, FactorRiskResult
from finbot.services.factor_analytics.factor_risk import compute_factor_risk


@pytest.fixture()
def rng() -> np.random.Generator:
    return np.random.default_rng(77)


@pytest.fixture()
def synthetic_data(rng: np.random.Generator) -> tuple[np.ndarray, pd.DataFrame]:
    """Synthetic portfolio = 1.0 * F1 + 0.3 * F2 + noise."""
    n = 500
    f1 = rng.normal(0.0003, 0.01, n)
    f2 = rng.normal(0.0001, 0.005, n)
    noise = rng.normal(0, 0.003, n)
    portfolio = 1.0 * f1 + 0.3 * f2 + noise
    factors = pd.DataFrame({"F1": f1, "F2": f2})
    return portfolio, factors


@pytest.fixture()
def reg_result(synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> FactorRegressionResult:
    from finbot.services.factor_analytics.factor_regression import compute_factor_regression

    portfolio, factors = synthetic_data
    return compute_factor_regression(portfolio, factors)


class TestComputeFactorRisk:
    """Tests for compute_factor_risk."""

    def test_basic(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_risk(portfolio, factors)
        assert isinstance(result, FactorRiskResult)
        assert result.n_observations == 500

    def test_with_precomputed_regression(
        self,
        synthetic_data: tuple[np.ndarray, pd.DataFrame],
        reg_result: FactorRegressionResult,
    ) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_risk(portfolio, factors, regression_result=reg_result)
        assert result.factor_names == reg_result.factor_names

    def test_variance_decomposition_sums(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        """systematic + idiosyncratic should equal total."""
        portfolio, factors = synthetic_data
        result = compute_factor_risk(portfolio, factors)
        recomposed = result.systematic_variance + result.idiosyncratic_variance
        assert abs(recomposed - result.total_variance) < 1e-10

    def test_pct_systematic_range(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_risk(portfolio, factors)
        assert 0.0 <= result.pct_systematic <= 1.0

    def test_systematic_positive(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_risk(portfolio, factors)
        assert result.systematic_variance >= 0

    def test_idiosyncratic_nonnegative(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_risk(portfolio, factors)
        assert result.idiosyncratic_variance >= 0

    def test_total_variance_positive(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_risk(portfolio, factors)
        assert result.total_variance > 0

    def test_marginal_contributions_sum_to_systematic(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        """Sum of marginal contributions should approximate systematic variance."""
        portfolio, factors = synthetic_data
        result = compute_factor_risk(portfolio, factors)
        mc_sum = sum(result.marginal_contributions.values())
        assert abs(mc_sum - result.systematic_variance) < 1e-10

    def test_dominant_factor_larger_marginal(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        """F1 (loading=1.0, higher vol) should have larger marginal contribution."""
        portfolio, factors = synthetic_data
        result = compute_factor_risk(portfolio, factors)
        assert abs(result.marginal_contributions["F1"]) > abs(result.marginal_contributions["F2"])

    def test_single_factor(self, rng: np.random.Generator) -> None:
        n = 200
        f1 = rng.normal(0, 0.01, n)
        portfolio = 1.5 * f1 + rng.normal(0, 0.001, n)
        factors = pd.DataFrame({"Mkt-RF": f1})
        result = compute_factor_risk(portfolio, factors)
        assert len(result.marginal_contributions) == 1
        # Marginal contribution should equal systematic variance for single factor
        mc = result.marginal_contributions["Mkt-RF"]
        assert abs(mc - result.systematic_variance) < 1e-10

    def test_too_few_observations_raises(self) -> None:
        portfolio = np.array([0.01] * 10)
        factors = pd.DataFrame({"F1": [0.01] * 10})
        with pytest.raises(ValueError, match="at least 30"):
            compute_factor_risk(portfolio, factors)

    def test_length_mismatch_raises(self) -> None:
        portfolio = np.array([0.01] * 50)
        factors = pd.DataFrame({"F1": [0.01] * 40})
        with pytest.raises(ValueError, match="length"):
            compute_factor_risk(portfolio, factors)

    def test_high_noise_low_systematic(self, rng: np.random.Generator) -> None:
        """High noise relative to signal => low pct_systematic."""
        n = 200
        f1 = rng.normal(0, 0.001, n)
        portfolio = 0.1 * f1 + rng.normal(0, 0.01, n)  # noise >> signal
        factors = pd.DataFrame({"F1": f1})
        result = compute_factor_risk(portfolio, factors)
        assert result.pct_systematic < 0.5

    def test_perfect_fit_all_systematic(self) -> None:
        """Zero noise => nearly all variance is systematic."""
        n = 200
        f1 = np.linspace(-0.01, 0.01, n)
        portfolio = 2.0 * f1
        factors = pd.DataFrame({"F1": f1})
        result = compute_factor_risk(portfolio, factors)
        assert result.pct_systematic > 0.99

    def test_many_factors(self, rng: np.random.Generator) -> None:
        n = 200
        factors = pd.DataFrame({f"F{i}": rng.normal(0, 0.01, n) for i in range(5)})
        portfolio = factors.sum(axis=1).to_numpy() + rng.normal(0, 0.001, n)
        result = compute_factor_risk(portfolio, factors)
        assert len(result.marginal_contributions) == 5
        mc_sum = sum(result.marginal_contributions.values())
        assert abs(mc_sum - result.systematic_variance) < 1e-10

    def test_precomputed_result_consistency(
        self,
        synthetic_data: tuple[np.ndarray, pd.DataFrame],
        reg_result: FactorRegressionResult,
    ) -> None:
        portfolio, factors = synthetic_data
        result_auto = compute_factor_risk(portfolio, factors)
        result_pre = compute_factor_risk(portfolio, factors, regression_result=reg_result)
        assert abs(result_auto.systematic_variance - result_pre.systematic_variance) < 1e-10

    def test_factor_names_match_regression(
        self,
        synthetic_data: tuple[np.ndarray, pd.DataFrame],
        reg_result: FactorRegressionResult,
    ) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_risk(portfolio, factors, regression_result=reg_result)
        assert result.factor_names == reg_result.factor_names
