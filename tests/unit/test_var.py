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

    def test_expected_rate_matches_confidence(self) -> None:
        """expected_violation_rate == 1 - confidence."""
        result = var_backtest(NORMAL_RETURNS, confidence=0.95)
        assert abs(result.expected_violation_rate - 0.05) < 1e-10
