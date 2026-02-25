"""Tests for risk analytics contract dataclasses and validation."""

from __future__ import annotations

import pytest

from finbot.core.contracts.risk_analytics import (
    CVaRResult,
    KellyResult,
    StressScenario,
    VaRMethod,
    VaRResult,
)


class TestVaRResultValidation:
    """Tests for VaRResult __post_init__ validation."""

    def test_valid_var_result(self) -> None:
        """VaRResult is created with valid fields."""
        result = VaRResult(
            var=0.02,
            confidence=0.95,
            method=VaRMethod.HISTORICAL,
            horizon_days=1,
            n_observations=252,
        )
        assert result.var == 0.02

    def test_invalid_confidence_zero(self) -> None:
        """Confidence of 0 raises ValueError."""
        with pytest.raises(ValueError, match="confidence"):
            VaRResult(var=0.02, confidence=0.0, method=VaRMethod.HISTORICAL, horizon_days=1, n_observations=252)

    def test_invalid_confidence_one(self) -> None:
        """Confidence of 1 raises ValueError."""
        with pytest.raises(ValueError, match="confidence"):
            VaRResult(var=0.02, confidence=1.0, method=VaRMethod.HISTORICAL, horizon_days=1, n_observations=252)

    def test_invalid_horizon_zero(self) -> None:
        """horizon_days of 0 raises ValueError."""
        with pytest.raises(ValueError, match="horizon_days"):
            VaRResult(var=0.02, confidence=0.95, method=VaRMethod.HISTORICAL, horizon_days=0, n_observations=252)

    def test_negative_var_raises(self) -> None:
        """Negative var raises ValueError."""
        with pytest.raises(ValueError, match="var must be >= 0"):
            VaRResult(var=-0.01, confidence=0.95, method=VaRMethod.HISTORICAL, horizon_days=1, n_observations=252)

    def test_var_with_portfolio_value(self) -> None:
        """VaRResult accepts portfolio_value and var_dollars."""
        result = VaRResult(
            var=0.02,
            confidence=0.95,
            method=VaRMethod.HISTORICAL,
            horizon_days=1,
            n_observations=252,
            portfolio_value=100_000.0,
            var_dollars=2_000.0,
        )
        assert result.var_dollars == 2_000.0


class TestCVaRResultValidation:
    """Tests for CVaRResult __post_init__ validation."""

    def test_valid_cvar_result(self) -> None:
        """CVaRResult is created when cvar >= var."""
        result = CVaRResult(
            cvar=0.03,
            var=0.02,
            confidence=0.95,
            method=VaRMethod.HISTORICAL,
            n_tail_obs=12,
            n_observations=252,
        )
        assert result.cvar == 0.03

    def test_cvar_less_than_var_raises(self) -> None:
        """CVaR < VaR raises ValueError."""
        with pytest.raises(ValueError, match="cvar"):
            CVaRResult(
                cvar=0.01,
                var=0.02,
                confidence=0.95,
                method=VaRMethod.HISTORICAL,
                n_tail_obs=12,
                n_observations=252,
            )

    def test_invalid_confidence_raises(self) -> None:
        """CVaRResult with invalid confidence raises ValueError."""
        with pytest.raises(ValueError, match="confidence"):
            CVaRResult(
                cvar=0.03,
                var=0.02,
                confidence=1.5,
                method=VaRMethod.HISTORICAL,
                n_tail_obs=12,
                n_observations=252,
            )


class TestStressScenarioValidation:
    """Tests for StressScenario __post_init__ validation."""

    def test_valid_scenario(self) -> None:
        """StressScenario is created with valid negative shock_return."""
        s = StressScenario(name="Test", shock_return=-0.3, shock_duration_days=10, recovery_days=30)
        assert s.shock_return == -0.3

    def test_positive_shock_raises(self) -> None:
        """Positive shock_return raises ValueError."""
        with pytest.raises(ValueError, match="shock_return"):
            StressScenario(name="Test", shock_return=0.1, shock_duration_days=10, recovery_days=30)

    def test_zero_shock_allowed(self) -> None:
        """Zero shock_return is allowed (boundary case)."""
        s = StressScenario(name="Test", shock_return=0.0, shock_duration_days=10, recovery_days=30)
        assert s.shock_return == 0.0


class TestKellyResultValidation:
    """Tests for KellyResult __post_init__ validation."""

    def test_valid_kelly_result(self) -> None:
        """KellyResult is created with valid win_rate."""
        r = KellyResult(
            full_kelly=0.25,
            half_kelly=0.125,
            quarter_kelly=0.0625,
            win_rate=0.55,
            win_loss_ratio=1.5,
            expected_value=0.1,
            is_positive_ev=True,
            n_observations=252,
        )
        assert r.win_rate == 0.55

    def test_invalid_win_rate_raises(self) -> None:
        """win_rate > 1 raises ValueError."""
        with pytest.raises(ValueError, match="win_rate"):
            KellyResult(
                full_kelly=0.25,
                half_kelly=0.125,
                quarter_kelly=0.0625,
                win_rate=1.5,
                win_loss_ratio=1.5,
                expected_value=0.1,
                is_positive_ev=True,
                n_observations=252,
            )
