"""Tests for factor analytics contract dataclasses and validation."""

from __future__ import annotations

import pytest

from finbot.core.contracts.factor_analytics import (
    FactorAttributionResult,
    FactorModelType,
    FactorRegressionResult,
    FactorRiskResult,
)

# ── FactorModelType ──────────────────────────────────────────────────────────


class TestFactorModelType:
    """Tests for FactorModelType enum."""

    def test_capm_value(self) -> None:
        assert FactorModelType.CAPM == "CAPM"

    def test_ff3_value(self) -> None:
        assert FactorModelType.FF3 == "FF3"

    def test_ff5_value(self) -> None:
        assert FactorModelType.FF5 == "FF5"

    def test_custom_value(self) -> None:
        assert FactorModelType.CUSTOM == "CUSTOM"

    def test_all_members(self) -> None:
        assert len(FactorModelType) == 4


# ── FactorRegressionResult ───────────────────────────────────────────────────


class TestFactorRegressionResultValidation:
    """Tests for FactorRegressionResult __post_init__ validation."""

    def _make_valid(self, **overrides: object) -> FactorRegressionResult:
        defaults: dict[str, object] = {
            "loadings": {"Mkt-RF": 1.1, "SMB": 0.3},
            "alpha": 0.02,
            "r_squared": 0.85,
            "adj_r_squared": 0.84,
            "residual_std": 0.01,
            "t_stats": {"alpha": 2.0, "Mkt-RF": 15.0, "SMB": 3.0},
            "p_values": {"alpha": 0.05, "Mkt-RF": 0.001, "SMB": 0.01},
            "factor_names": ("Mkt-RF", "SMB"),
            "model_type": FactorModelType.CUSTOM,
            "n_observations": 252,
            "annualization_factor": 252,
        }
        defaults.update(overrides)
        return FactorRegressionResult(**defaults)  # type: ignore[arg-type]

    def test_valid_result(self) -> None:
        result = self._make_valid()
        assert result.r_squared == 0.85
        assert result.factor_names == ("Mkt-RF", "SMB")

    def test_r_squared_negative_raises(self) -> None:
        with pytest.raises(ValueError, match="r_squared"):
            self._make_valid(r_squared=-0.1)

    def test_r_squared_above_one_raises(self) -> None:
        with pytest.raises(ValueError, match="r_squared"):
            self._make_valid(r_squared=1.1)

    def test_residual_std_negative_raises(self) -> None:
        with pytest.raises(ValueError, match="residual_std"):
            self._make_valid(residual_std=-0.01)

    def test_n_observations_too_small_raises(self) -> None:
        with pytest.raises(ValueError, match="n_observations"):
            self._make_valid(n_observations=1)

    def test_annualization_factor_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="annualization_factor"):
            self._make_valid(annualization_factor=0)

    def test_loadings_keys_mismatch_raises(self) -> None:
        with pytest.raises(ValueError, match="loadings keys"):
            self._make_valid(loadings={"WRONG": 1.0, "SMB": 0.3})

    def test_t_stats_keys_mismatch_raises(self) -> None:
        with pytest.raises(ValueError, match="t_stats keys"):
            self._make_valid(t_stats={"alpha": 2.0, "WRONG": 15.0, "SMB": 3.0})

    def test_p_values_keys_mismatch_raises(self) -> None:
        with pytest.raises(ValueError, match="p_values keys"):
            self._make_valid(p_values={"alpha": 0.05, "WRONG": 0.001, "SMB": 0.01})

    def test_frozen(self) -> None:
        result = self._make_valid()
        with pytest.raises(AttributeError):
            result.alpha = 0.5  # type: ignore[misc]

    def test_r_squared_boundary_zero(self) -> None:
        result = self._make_valid(r_squared=0.0)
        assert result.r_squared == 0.0

    def test_r_squared_boundary_one(self) -> None:
        result = self._make_valid(r_squared=1.0)
        assert result.r_squared == 1.0


# ── FactorAttributionResult ──────────────────────────────────────────────────


class TestFactorAttributionResultValidation:
    """Tests for FactorAttributionResult __post_init__ validation."""

    def _make_valid(self, **overrides: object) -> FactorAttributionResult:
        defaults: dict[str, object] = {
            "factor_contributions": {"Mkt-RF": 0.05, "SMB": 0.01},
            "alpha_contribution": 0.005,
            "total_return": 0.07,
            "explained_return": 0.065,
            "residual_return": 0.005,
            "factor_names": ("Mkt-RF", "SMB"),
            "n_observations": 252,
        }
        defaults.update(overrides)
        return FactorAttributionResult(**defaults)  # type: ignore[arg-type]

    def test_valid_result(self) -> None:
        result = self._make_valid()
        assert result.total_return == 0.07

    def test_n_observations_too_small_raises(self) -> None:
        with pytest.raises(ValueError, match="n_observations"):
            self._make_valid(n_observations=1)

    def test_factor_contributions_keys_mismatch_raises(self) -> None:
        with pytest.raises(ValueError, match="factor_contributions keys"):
            self._make_valid(factor_contributions={"WRONG": 0.05, "SMB": 0.01})

    def test_frozen(self) -> None:
        result = self._make_valid()
        with pytest.raises(AttributeError):
            result.total_return = 0.1  # type: ignore[misc]

    def test_negative_returns_allowed(self) -> None:
        result = self._make_valid(
            factor_contributions={"Mkt-RF": -0.05, "SMB": -0.01},
            total_return=-0.06,
            explained_return=-0.05,
            residual_return=-0.01,
        )
        assert result.total_return == -0.06


# ── FactorRiskResult ─────────────────────────────────────────────────────────


class TestFactorRiskResultValidation:
    """Tests for FactorRiskResult __post_init__ validation."""

    def _make_valid(self, **overrides: object) -> FactorRiskResult:
        defaults: dict[str, object] = {
            "systematic_variance": 0.0004,
            "idiosyncratic_variance": 0.0001,
            "total_variance": 0.0005,
            "pct_systematic": 0.8,
            "marginal_contributions": {"Mkt-RF": 0.0003, "SMB": 0.0001},
            "factor_names": ("Mkt-RF", "SMB"),
            "n_observations": 252,
        }
        defaults.update(overrides)
        return FactorRiskResult(**defaults)  # type: ignore[arg-type]

    def test_valid_result(self) -> None:
        result = self._make_valid()
        assert result.pct_systematic == 0.8

    def test_systematic_variance_negative_raises(self) -> None:
        with pytest.raises(ValueError, match="systematic_variance"):
            self._make_valid(systematic_variance=-0.001)

    def test_idiosyncratic_variance_negative_raises(self) -> None:
        with pytest.raises(ValueError, match="idiosyncratic_variance"):
            self._make_valid(idiosyncratic_variance=-0.001)

    def test_total_variance_negative_raises(self) -> None:
        with pytest.raises(ValueError, match="total_variance"):
            self._make_valid(total_variance=-0.001)

    def test_pct_systematic_negative_raises(self) -> None:
        with pytest.raises(ValueError, match="pct_systematic"):
            self._make_valid(pct_systematic=-0.1)

    def test_pct_systematic_above_one_raises(self) -> None:
        with pytest.raises(ValueError, match="pct_systematic"):
            self._make_valid(pct_systematic=1.1)

    def test_n_observations_too_small_raises(self) -> None:
        with pytest.raises(ValueError, match="n_observations"):
            self._make_valid(n_observations=1)

    def test_marginal_contributions_keys_mismatch_raises(self) -> None:
        with pytest.raises(ValueError, match="marginal_contributions keys"):
            self._make_valid(marginal_contributions={"WRONG": 0.0003, "SMB": 0.0001})

    def test_frozen(self) -> None:
        result = self._make_valid()
        with pytest.raises(AttributeError):
            result.total_variance = 0.1  # type: ignore[misc]
