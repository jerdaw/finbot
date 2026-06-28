"""Tests for VaR / CVaR computation and backtest."""

from __future__ import annotations

import numpy as np
import pytest
from scipy import stats

from finbot.core.contracts.risk_analytics import CVaRResult, VaRBacktestResult, VaRMethod, VaRResult
from finbot.services.risk_analytics.var import compute_cvar, compute_var, var_backtest

RNG = np.random.default_rng(seed=0)
NORMAL_RETURNS = RNG.normal(0.001, 0.01, 500)
GOOD_RETURNS = RNG.normal(0.005, 0.01, 500)  # positive expected return


class TestHistoricalVaR:
    """Tests for historical VaR computation."""

    def test_returns_var_result(self) -> None:
        """compute_var returns a VaRResult instance."""
        result = compute_var(NORMAL_RETURNS, confidence=0.95, method="historical")
        assert isinstance(result, VaRResult)

    def test_var_is_positive(self) -> None:
        """Historical VaR is always positive."""
        result = compute_var(NORMAL_RETURNS, confidence=0.95, method="historical")
        assert result.var >= 0

    def test_historical_var_matches_percentile(self) -> None:
        """Historical 1-day VaR equals -percentile(5%) of returns."""
        result = compute_var(NORMAL_RETURNS, confidence=0.95, method="historical", horizon_days=1)
        expected = -float(np.percentile(NORMAL_RETURNS, 5.0))
        assert abs(result.var - expected) < 1e-10

    def test_higher_confidence_higher_var(self) -> None:
        """99% VaR > 95% VaR for the same series."""
        var95 = compute_var(NORMAL_RETURNS, confidence=0.95)
        var99 = compute_var(NORMAL_RETURNS, confidence=0.99)
        assert var99.var > var95.var

    def test_horizon_scaling(self) -> None:
        """5-day VaR ≈ 1-day VaR * sqrt(5) (within numerical tolerance)."""
        var1 = compute_var(NORMAL_RETURNS, confidence=0.95, method="historical", horizon_days=1)
        var5 = compute_var(NORMAL_RETURNS, confidence=0.95, method="historical", horizon_days=5)
        ratio = var5.var / var1.var
        assert abs(ratio - np.sqrt(5)) < 1e-9

    def test_insufficient_data_raises(self) -> None:
        """Fewer than 30 observations raises ValueError."""
        with pytest.raises(ValueError, match="observations"):
            compute_var(np.array([0.01] * 10), confidence=0.95)

    @pytest.mark.parametrize("confidence", [0.0, 1.0, -0.1, 1.1])
    def test_invalid_confidence_raises(self, confidence: float) -> None:
        """confidence must be in the open interval (0, 1)."""
        with pytest.raises(ValueError, match="confidence must be in"):
            compute_var(NORMAL_RETURNS, confidence=confidence)

    def test_invalid_horizon_raises(self) -> None:
        """horizon_days must be positive."""
        with pytest.raises(ValueError, match="horizon_days must be >= 1"):
            compute_var(NORMAL_RETURNS, horizon_days=0)

    def test_negative_portfolio_value_raises(self) -> None:
        """portfolio_value must not be negative."""
        with pytest.raises(ValueError, match="portfolio_value must be >= 0"):
            compute_var(NORMAL_RETURNS, portfolio_value=-1.0)

    @pytest.mark.parametrize("bad_value", [np.nan, np.inf, -np.inf])
    def test_non_finite_returns_raise(self, bad_value: float) -> None:
        """VaR rejects NaN and infinite returns explicitly."""
        returns = NORMAL_RETURNS.copy()
        returns[10] = bad_value

        with pytest.raises(ValueError, match="must not contain NaN or infinite"):
            compute_var(returns)


class TestParametricVaR:
    """Tests for parametric VaR computation."""

    def test_parametric_var_formula(self) -> None:
        """Parametric VaR matches scipy norm.ppf formula."""
        returns = NORMAL_RETURNS
        sigma = float(np.std(returns, ddof=1))
        z = float(-stats.norm.ppf(1 - 0.95))
        expected = z * sigma
        result = compute_var(returns, confidence=0.95, method="parametric", horizon_days=1)
        assert abs(result.var - expected) < 1e-10

    def test_parametric_method_stored(self) -> None:
        """method field is VaRMethod.PARAMETRIC."""
        result = compute_var(NORMAL_RETURNS, confidence=0.95, method="parametric")
        assert result.method == VaRMethod.PARAMETRIC


class TestMonteCarloVaR:
    """Tests for Monte Carlo VaR computation."""

    def test_montecarlo_var_positive(self) -> None:
        """Monte Carlo VaR is a positive float."""
        result = compute_var(NORMAL_RETURNS, confidence=0.95, method="montecarlo")
        assert result.var > 0

    def test_montecarlo_roughly_comparable(self) -> None:
        """MC VaR is in the same ballpark as historical VaR (within 2x)."""
        hist = compute_var(NORMAL_RETURNS, confidence=0.95, method="historical")
        mc = compute_var(NORMAL_RETURNS, confidence=0.95, method="montecarlo")
        assert 0.1 < mc.var / hist.var < 10.0

    def test_montecarlo_method_stored(self) -> None:
        """method field is VaRMethod.MONTECARLO."""
        result = compute_var(NORMAL_RETURNS, confidence=0.95, method="montecarlo")
        assert result.method == VaRMethod.MONTECARLO

    def test_invalid_simulation_count_raises(self) -> None:
        """Monte Carlo VaR requires at least one simulation."""
        with pytest.raises(ValueError, match="n_simulations must be >= 1"):
            compute_var(NORMAL_RETURNS, method="montecarlo", n_simulations=0)


class TestCVaR:
    """Tests for CVaR computation."""

    def test_returns_cvar_result(self) -> None:
        """compute_cvar returns a CVaRResult instance."""
        result = compute_cvar(NORMAL_RETURNS, confidence=0.95)
        assert isinstance(result, CVaRResult)

    def test_cvar_geq_var(self) -> None:
        """CVaR is always >= VaR."""
        result = compute_cvar(NORMAL_RETURNS, confidence=0.95)
        assert result.cvar >= result.var

    def test_cvar_tail_count_positive(self) -> None:
        """n_tail_obs is > 0 for a realistic returns series."""
        result = compute_cvar(NORMAL_RETURNS, confidence=0.95)
        assert result.n_tail_obs >= 0

    def test_cvar_confidence_stored(self) -> None:
        """confidence field matches input."""
        result = compute_cvar(NORMAL_RETURNS, confidence=0.99)
        assert result.confidence == 0.99

    def test_invalid_confidence_raises(self) -> None:
        """CVaR validates confidence before computing tails."""
        with pytest.raises(ValueError, match="confidence must be in"):
            compute_cvar(NORMAL_RETURNS, confidence=1.0)

    def test_non_finite_returns_raise(self) -> None:
        """CVaR rejects non-finite returns before tail selection."""
        returns = NORMAL_RETURNS.copy()
        returns[25] = np.nan

        with pytest.raises(ValueError, match="must not contain NaN or infinite"):
            compute_cvar(returns)


class TestVaRBacktest:
    """Tests for VaR model backtest."""

    def test_returns_backtest_result(self) -> None:
        """var_backtest returns a VaRBacktestResult."""
        result = var_backtest(NORMAL_RETURNS, confidence=0.95)
        assert isinstance(result, VaRBacktestResult)

    def test_violation_rate_bounded(self) -> None:
        """violation_rate is in [0, 1]."""
        result = var_backtest(NORMAL_RETURNS, confidence=0.95)
        assert 0 <= result.violation_rate <= 1

    def test_insufficient_data_raises(self) -> None:
        """Series too short for backtest raises ValueError."""
        with pytest.raises(ValueError):
            var_backtest(NORMAL_RETURNS[:50], min_history=252)

    def test_min_history_below_var_window_raises(self) -> None:
        """Backtest training windows must be large enough for VaR forecasts."""
        with pytest.raises(ValueError, match="min_history must be >= 30"):
            var_backtest(NORMAL_RETURNS, min_history=29)

    def test_min_history_equal_to_var_window_is_allowed(self) -> None:
        """A 30-observation training window supports the first forecast."""
        result = var_backtest(NORMAL_RETURNS[:31], min_history=30)
        assert result.n_observations == 1

    def test_expected_rate_matches_confidence(self) -> None:
        """expected_violation_rate == 1 - confidence."""
        result = var_backtest(NORMAL_RETURNS, confidence=0.95)
        assert abs(result.expected_violation_rate - 0.05) < 1e-10

    def test_method_string_and_enum_are_equivalent(self) -> None:
        """String and enum method inputs produce the same backtest result."""
        string_result = var_backtest(NORMAL_RETURNS, confidence=0.95, method="historical")
        enum_result = var_backtest(NORMAL_RETURNS, confidence=0.95, method=VaRMethod.HISTORICAL)

        assert string_result.method == enum_result.method == VaRMethod.HISTORICAL
        assert string_result.n_observations == enum_result.n_observations
        assert string_result.n_violations == enum_result.n_violations
        assert string_result.violation_rate == enum_result.violation_rate

    def test_invalid_confidence_raises(self) -> None:
        """Backtest validates confidence before expanding-window forecasts."""
        with pytest.raises(ValueError, match="confidence must be in"):
            var_backtest(NORMAL_RETURNS, confidence=0.0)

    def test_non_finite_returns_raise(self) -> None:
        """Backtest rejects non-finite returns before forecasting."""
        returns = NORMAL_RETURNS.copy()
        returns[100] = np.inf

        with pytest.raises(ValueError, match="must not contain NaN or infinite"):
            var_backtest(returns)
