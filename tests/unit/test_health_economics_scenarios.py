"""Tests for health economics clinical scenario modules (P7.21)."""

from __future__ import annotations

import dataclasses

import pytest

from finbot.services.health_economics.scenarios.cancer_screening import (
    run_cancer_screening_scenario,
)
from finbot.services.health_economics.scenarios.hypertension import (
    run_hypertension_scenario,
)
from finbot.services.health_economics.scenarios.models import ScenarioResult
from finbot.services.health_economics.scenarios.vaccine import run_vaccine_scenario

# ---------------------------------------------------------------------------
# ScenarioResult model tests
# ---------------------------------------------------------------------------


class TestScenarioResult:
    def test_scenario_result_has_required_fields(self):
        field_names = {f.name for f in dataclasses.fields(ScenarioResult)}
        required = {
            "scenario_name",
            "description",
            "intervention_name",
            "comparator_name",
            "icer",
            "nmb",
            "is_cost_effective",
            "qaly_gain",
            "cost_difference",
            "n_simulations",
            "summary_stats",
        }
        assert required <= field_names

    def test_scenario_result_is_frozen(self):
        result = ScenarioResult(
            scenario_name="Test",
            description="desc",
            intervention_name="A",
            comparator_name="B",
            icer=10_000.0,
            nmb=5_000.0,
            is_cost_effective=True,
            qaly_gain=0.1,
            cost_difference=1_000.0,
            n_simulations=100,
            summary_stats={},
        )
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            result.nmb = 99.0  # type: ignore[misc]

    def test_scenario_result_cost_effective_when_nmb_positive(self):
        result = ScenarioResult(
            scenario_name="Test",
            description="desc",
            intervention_name="A",
            comparator_name="B",
            icer=50_000.0,
            nmb=2_000.0,
            is_cost_effective=True,
            qaly_gain=0.1,
            cost_difference=3_000.0,
            n_simulations=100,
            summary_stats={},
        )
        assert result.nmb > 0
        assert result.is_cost_effective is True

    def test_scenario_result_not_cost_effective_when_nmb_negative(self):
        result = ScenarioResult(
            scenario_name="Test",
            description="desc",
            intervention_name="A",
            comparator_name="B",
            icer=200_000.0,
            nmb=-5_000.0,
            is_cost_effective=False,
            qaly_gain=0.05,
            cost_difference=15_000.0,
            n_simulations=100,
            summary_stats={},
        )
        assert result.nmb < 0
        assert result.is_cost_effective is False


# ---------------------------------------------------------------------------
# Cancer screening scenario tests
# ---------------------------------------------------------------------------


class TestCancerScreeningScenario:
    # Use small n_sims for speed; seed ensures determinism
    _N = 1_000

    def test_cancer_screening_returns_scenario_result(self):
        result = run_cancer_screening_scenario(n_sims=self._N, seed=42)
        assert isinstance(result, ScenarioResult)

    def test_cancer_screening_icer_is_positive_or_none(self):
        result = run_cancer_screening_scenario(n_sims=self._N, seed=42)
        # ICER is None (dominated) or positive (more costly, more effective)
        assert result.icer is None or result.icer > 0

    def test_cancer_screening_nmb_is_float(self):
        result = run_cancer_screening_scenario(n_sims=self._N, seed=42)
        assert isinstance(result.nmb, float)

    def test_cancer_screening_qaly_gain_positive(self):
        result = run_cancer_screening_scenario(n_sims=self._N, seed=42)
        # Screening adds QALYs via utility gain and mortality reduction
        assert result.qaly_gain > 0

    def test_cancer_screening_deterministic_with_seed(self):
        r1 = run_cancer_screening_scenario(n_sims=self._N, seed=7)
        r2 = run_cancer_screening_scenario(n_sims=self._N, seed=7)
        assert r1.qaly_gain == r2.qaly_gain
        assert r1.cost_difference == r2.cost_difference
        assert r1.nmb == r2.nmb

    def test_cancer_screening_custom_wtp_changes_cost_effectiveness(self):
        # At very low WTP ($10,000/QALY) screening is unlikely to be cost-effective
        result_low = run_cancer_screening_scenario(n_sims=self._N, seed=42, wtp_threshold=10_000.0)
        # At very high WTP ($200,000/QALY) screening should be cost-effective
        result_high = run_cancer_screening_scenario(n_sims=self._N, seed=42, wtp_threshold=200_000.0)
        assert result_high.nmb > result_low.nmb
        assert result_high.is_cost_effective is True


# ---------------------------------------------------------------------------
# Hypertension scenario tests
# ---------------------------------------------------------------------------


class TestHypertensionScenario:
    _N = 1_000

    def test_hypertension_returns_scenario_result(self):
        result = run_hypertension_scenario(n_sims=self._N, seed=42)
        assert isinstance(result, ScenarioResult)

    def test_hypertension_icer_is_numeric_or_none(self):
        result = run_hypertension_scenario(n_sims=self._N, seed=42)
        assert result.icer is None or isinstance(result.icer, float)

    def test_hypertension_n_simulations_matches_input(self):
        n = 500
        result = run_hypertension_scenario(n_sims=n, seed=42)
        assert result.n_simulations == n

    def test_hypertension_summary_stats_nonempty(self):
        result = run_hypertension_scenario(n_sims=self._N, seed=42)
        assert len(result.summary_stats) > 0

    def test_hypertension_deterministic_with_seed(self):
        r1 = run_hypertension_scenario(n_sims=self._N, seed=15)
        r2 = run_hypertension_scenario(n_sims=self._N, seed=15)
        assert r1.qaly_gain == r2.qaly_gain
        assert r1.nmb == r2.nmb

    def test_hypertension_cost_difference_is_float(self):
        result = run_hypertension_scenario(n_sims=self._N, seed=42)
        assert isinstance(result.cost_difference, float)


# ---------------------------------------------------------------------------
# Vaccine scenario tests
# ---------------------------------------------------------------------------


class TestVaccineScenario:
    _N = 1_000

    def test_vaccine_returns_scenario_result(self):
        result = run_vaccine_scenario(n_sims=self._N, seed=42)
        assert isinstance(result, ScenarioResult)

    def test_vaccine_qaly_gain_within_plausible_range(self):
        result = run_vaccine_scenario(n_sims=self._N, seed=42)
        # 1-year horizon: QALY gain must be positive and < 1 full QALY
        assert 0 < result.qaly_gain < 1.0

    def test_vaccine_n_simulations_correct(self):
        n = 200
        result = run_vaccine_scenario(n_sims=n, seed=42)
        assert result.n_simulations == n

    def test_vaccine_summary_stats_have_expected_keys(self):
        result = run_vaccine_scenario(n_sims=self._N, seed=42)
        expected_keys = {
            "mean_cost_vaccine",
            "mean_cost_no_vaccine",
            "mean_qaly_vaccine",
            "mean_qaly_no_vaccine",
        }
        assert expected_keys <= set(result.summary_stats.keys())

    def test_vaccine_deterministic_with_seed(self):
        r1 = run_vaccine_scenario(n_sims=self._N, seed=99)
        r2 = run_vaccine_scenario(n_sims=self._N, seed=99)
        assert r1.qaly_gain == r2.qaly_gain
        assert r1.cost_difference == r2.cost_difference

    def test_vaccine_different_seeds_may_differ(self):
        r1 = run_vaccine_scenario(n_sims=self._N, seed=1)
        r2 = run_vaccine_scenario(n_sims=self._N, seed=2)
        # Different seeds should produce different Monte Carlo draws
        assert r1.qaly_gain != r2.qaly_gain or r1.cost_difference != r2.cost_difference
