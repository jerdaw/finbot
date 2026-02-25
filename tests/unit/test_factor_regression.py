"""Tests for factor regression computation."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from finbot.core.contracts.factor_analytics import FactorModelType, FactorRegressionResult
from finbot.services.factor_analytics.factor_regression import (
    compute_factor_regression,
    compute_rolling_r_squared,
)


@pytest.fixture()
def rng() -> np.random.Generator:
    return np.random.default_rng(42)


@pytest.fixture()
def synthetic_data(rng: np.random.Generator) -> tuple[np.ndarray, pd.DataFrame]:
    """Generate synthetic portfolio returns driven by known factor loadings.

    Portfolio = 0.01 + 1.2 * Mkt + 0.5 * SMB + noise
    """
    n = 500
    mkt = rng.normal(0.0004, 0.01, n)
    smb = rng.normal(0.0001, 0.005, n)
    noise = rng.normal(0, 0.002, n)
    portfolio = 0.01 / 252 + 1.2 * mkt + 0.5 * smb + noise
    factor_df = pd.DataFrame({"Mkt-RF": mkt, "SMB": smb})
    return portfolio, factor_df


class TestComputeFactorRegression:
    """Tests for compute_factor_regression."""

    def test_basic_regression(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_regression(portfolio, factors)
        assert isinstance(result, FactorRegressionResult)
        assert result.n_observations == 500
        assert result.factor_names == ("Mkt-RF", "SMB")

    def test_loadings_recovery(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        """True betas (1.2, 0.5) should be recovered approximately."""
        portfolio, factors = synthetic_data
        result = compute_factor_regression(portfolio, factors)
        assert abs(result.loadings["Mkt-RF"] - 1.2) < 0.15
        assert abs(result.loadings["SMB"] - 0.5) < 0.15

    def test_r_squared_high(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        """R-squared should be high for data generated from the model."""
        portfolio, factors = synthetic_data
        result = compute_factor_regression(portfolio, factors)
        assert result.r_squared > 0.7

    def test_alpha_near_zero(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        """Annualized alpha should be close to the true value (0.01)."""
        portfolio, factors = synthetic_data
        result = compute_factor_regression(portfolio, factors)
        assert abs(result.alpha - 0.01) < 0.05

    def test_t_stats_significant(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_regression(portfolio, factors)
        assert abs(result.t_stats["Mkt-RF"]) > 2.0
        assert abs(result.t_stats["SMB"]) > 2.0

    def test_p_values_low(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_regression(portfolio, factors)
        assert result.p_values["Mkt-RF"] < 0.05
        assert result.p_values["SMB"] < 0.05

    def test_single_factor_capm(self, rng: np.random.Generator) -> None:
        """Single factor => CAPM auto-detection."""
        n = 100
        mkt = rng.normal(0, 0.01, n)
        portfolio = 1.0 * mkt + rng.normal(0, 0.001, n)
        factors = pd.DataFrame({"Mkt-RF": mkt})
        result = compute_factor_regression(portfolio, factors)
        assert result.model_type == FactorModelType.CAPM
        assert len(result.factor_names) == 1

    def test_ff3_detection(self, rng: np.random.Generator) -> None:
        """Three FF columns => FF3 auto-detection."""
        n = 100
        factors = pd.DataFrame(
            {
                "Mkt-RF": rng.normal(0, 0.01, n),
                "SMB": rng.normal(0, 0.005, n),
                "HML": rng.normal(0, 0.005, n),
            }
        )
        portfolio = factors["Mkt-RF"].to_numpy() + rng.normal(0, 0.001, n)
        result = compute_factor_regression(portfolio, factors)
        assert result.model_type == FactorModelType.FF3

    def test_ff5_detection(self, rng: np.random.Generator) -> None:
        """Five FF columns => FF5 auto-detection."""
        n = 100
        factors = pd.DataFrame(
            {
                "Mkt-RF": rng.normal(0, 0.01, n),
                "SMB": rng.normal(0, 0.005, n),
                "HML": rng.normal(0, 0.005, n),
                "RMW": rng.normal(0, 0.005, n),
                "CMA": rng.normal(0, 0.005, n),
            }
        )
        portfolio = factors["Mkt-RF"].to_numpy() + rng.normal(0, 0.001, n)
        result = compute_factor_regression(portfolio, factors)
        assert result.model_type == FactorModelType.FF5

    def test_custom_model_type(self, rng: np.random.Generator) -> None:
        """Non-standard column names => CUSTOM auto-detection."""
        n = 100
        factors = pd.DataFrame(
            {
                "Momentum": rng.normal(0, 0.01, n),
                "Quality": rng.normal(0, 0.005, n),
            }
        )
        portfolio = factors["Momentum"].to_numpy() + rng.normal(0, 0.001, n)
        result = compute_factor_regression(portfolio, factors)
        assert result.model_type == FactorModelType.CUSTOM

    def test_explicit_model_type_override(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_regression(portfolio, factors, model_type=FactorModelType.CUSTOM)
        assert result.model_type == FactorModelType.CUSTOM

    def test_too_few_observations_raises(self) -> None:
        portfolio = np.array([0.01] * 10)
        factors = pd.DataFrame({"F1": [0.01] * 10})
        with pytest.raises(ValueError, match="at least 30"):
            compute_factor_regression(portfolio, factors)

    def test_length_mismatch_raises(self) -> None:
        portfolio = np.array([0.01] * 50)
        factors = pd.DataFrame({"F1": [0.01] * 40})
        with pytest.raises(ValueError, match="length"):
            compute_factor_regression(portfolio, factors)

    def test_nan_in_portfolio_raises(self) -> None:
        portfolio = np.array([0.01] * 50)
        portfolio[5] = float("nan")
        factors = pd.DataFrame({"F1": [0.01] * 50})
        with pytest.raises(ValueError, match="NaN"):
            compute_factor_regression(portfolio, factors)

    def test_nan_in_factors_raises(self) -> None:
        portfolio = np.array([0.01] * 50)
        f_vals = [0.01] * 50
        f_vals[5] = float("nan")
        factors = pd.DataFrame({"F1": f_vals})
        with pytest.raises(ValueError, match="NaN"):
            compute_factor_regression(portfolio, factors)

    def test_no_factor_columns_raises(self) -> None:
        portfolio = np.array([0.01] * 50)
        factors = pd.DataFrame()
        with pytest.raises(ValueError):
            compute_factor_regression(portfolio, factors)

    def test_residual_std_nonnegative(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_regression(portfolio, factors)
        assert result.residual_std >= 0

    def test_adj_r_squared_less_than_r_squared(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_regression(portfolio, factors)
        assert result.adj_r_squared <= result.r_squared

    def test_annualization_factor_propagated(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        portfolio, factors = synthetic_data
        result = compute_factor_regression(portfolio, factors, annualization_factor=12)
        assert result.annualization_factor == 12

    def test_perfect_fit(self) -> None:
        """Zero noise => R-squared ~ 1."""
        n = 100
        mkt = np.linspace(-0.01, 0.01, n)
        portfolio = 1.5 * mkt + 0.001
        factors = pd.DataFrame({"Mkt-RF": mkt})
        result = compute_factor_regression(portfolio, factors)
        assert result.r_squared > 0.999

    def test_many_factors(self, rng: np.random.Generator) -> None:
        """Regression with 10 factors should not crash."""
        n = 200
        factors = pd.DataFrame({f"F{i}": rng.normal(0, 0.01, n) for i in range(10)})
        portfolio = factors.sum(axis=1).to_numpy() + rng.normal(0, 0.001, n)
        result = compute_factor_regression(portfolio, factors)
        assert len(result.loadings) == 10


class TestComputeRollingRSquared:
    """Tests for compute_rolling_r_squared."""

    def test_basic(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        portfolio, factors = synthetic_data
        values, dates = compute_rolling_r_squared(portfolio, factors, window=63)
        assert len(values) == 500
        assert len(dates) == 500

    def test_nan_prefix(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        """First window-1 values should be NaN."""
        portfolio, factors = synthetic_data
        values, _dates = compute_rolling_r_squared(portfolio, factors, window=63)
        for v in values[:62]:
            assert v != v  # NaN check

    def test_valid_suffix(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        """Values after window-1 should be in [0, 1]."""
        portfolio, factors = synthetic_data
        values, _dates = compute_rolling_r_squared(portfolio, factors, window=63)
        for v in values[62:]:
            assert 0.0 <= v <= 1.0

    def test_window_too_small_raises(self, synthetic_data: tuple[np.ndarray, pd.DataFrame]) -> None:
        portfolio, factors = synthetic_data
        with pytest.raises(ValueError, match="window must be >= 2"):
            compute_rolling_r_squared(portfolio, factors, window=1)

    def test_data_shorter_than_window_raises(self) -> None:
        portfolio = np.array([0.01] * 30)
        factors = pd.DataFrame({"F1": [0.01] * 30})
        with pytest.raises(ValueError, match="at least 63"):
            compute_rolling_r_squared(portfolio, factors, window=63)
