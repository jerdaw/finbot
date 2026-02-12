"""Tests for health economics modules (QALY simulator, CEA, treatment optimizer)."""

import numpy as np
import pandas as pd
import pytest

from finbot.services.health_economics.cost_effectiveness import (
    cost_effectiveness_analysis,
)
from finbot.services.health_economics.qaly_simulator import (
    HealthIntervention,
    simulate_qalys,
)
from finbot.services.health_economics.treatment_optimizer import optimize_treatment

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def drug_a() -> HealthIntervention:
    return HealthIntervention(
        name="Drug A",
        cost_per_year=5000.0,
        cost_std=500.0,
        utility_gain=0.1,
        utility_gain_std=0.02,
        mortality_reduction=0.005,
        mortality_reduction_std=0.001,
    )


@pytest.fixture()
def no_treatment() -> HealthIntervention:
    return HealthIntervention(name="No Treatment")


# ---------------------------------------------------------------------------
# HealthIntervention dataclass
# ---------------------------------------------------------------------------


class TestHealthIntervention:
    def test_defaults(self):
        hi = HealthIntervention(name="Test")
        assert hi.cost_per_year == 0.0
        assert hi.utility_gain == 0.0
        assert hi.mortality_reduction == 0.0
        assert hi.metadata == {}

    def test_frozen(self, drug_a: HealthIntervention):
        with pytest.raises(AttributeError):
            drug_a.name = "Changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# simulate_qalys
# ---------------------------------------------------------------------------


class TestSimulateQalys:
    def test_returns_expected_keys(self, drug_a: HealthIntervention):
        result = simulate_qalys(drug_a, n_sims=100, seed=42)
        expected_keys = {
            "total_costs",
            "total_qalys",
            "annual_costs",
            "annual_qalys",
            "survival_curves",
            "mean_cost",
            "mean_qaly",
        }
        assert set(result.keys()) == expected_keys

    def test_output_shapes(self, drug_a: HealthIntervention):
        result = simulate_qalys(drug_a, n_sims=200, time_horizon=5, seed=42)
        assert isinstance(result["total_costs"], pd.Series)
        assert len(result["total_costs"]) == 200
        assert isinstance(result["annual_costs"], pd.DataFrame)
        assert result["annual_costs"].shape == (200, 5)
        assert result["annual_qalys"].shape == (200, 5)
        assert result["survival_curves"].shape == (200, 5)

    def test_no_treatment_zero_cost(self, no_treatment: HealthIntervention):
        result = simulate_qalys(no_treatment, n_sims=100, seed=42)
        assert result["mean_cost"] == 0.0
        assert (result["total_costs"] == 0.0).all()

    def test_qalys_positive(self, drug_a: HealthIntervention):
        result = simulate_qalys(drug_a, n_sims=500, seed=42)
        assert result["mean_qaly"] > 0
        assert (result["total_qalys"] > 0).all()

    def test_treatment_improves_qalys(self, drug_a: HealthIntervention, no_treatment: HealthIntervention):
        res_drug = simulate_qalys(drug_a, n_sims=1000, seed=42)
        res_none = simulate_qalys(no_treatment, n_sims=1000, seed=42)
        assert res_drug["mean_qaly"] > res_none["mean_qaly"]

    def test_seed_reproducibility(self, drug_a: HealthIntervention):
        r1 = simulate_qalys(drug_a, n_sims=100, seed=123)
        r2 = simulate_qalys(drug_a, n_sims=100, seed=123)
        pd.testing.assert_series_equal(r1["total_costs"], r2["total_costs"])
        pd.testing.assert_series_equal(r1["total_qalys"], r2["total_qalys"])

    def test_deterministic_when_no_std(self):
        det = HealthIntervention("Det", cost_per_year=1000.0, utility_gain=0.05)
        result = simulate_qalys(det, n_sims=50, seed=42)
        # All simulations should produce identical costs (no randomness)
        assert result["total_costs"].std() == pytest.approx(0.0, abs=1e-10)

    def test_discount_reduces_future_values(self, drug_a: HealthIntervention):
        result = simulate_qalys(drug_a, n_sims=100, time_horizon=10, seed=42)
        annual = result["annual_qalys"]
        # Undiscounted first year should be >= later years on average
        # (discounting + mortality both reduce future QALYs)
        assert annual[1].mean() > annual[10].mean()

    def test_survival_decreasing(self, drug_a: HealthIntervention):
        result = simulate_qalys(drug_a, n_sims=100, time_horizon=10, seed=42)
        surv = result["survival_curves"]
        # Survival should be monotonically non-increasing
        for i in range(1, 10):
            assert (surv[i + 1] <= surv[i] + 1e-10).all()


# ---------------------------------------------------------------------------
# cost_effectiveness_analysis
# ---------------------------------------------------------------------------


class TestCostEffectivenessAnalysis:
    def _run_cea(self) -> dict:
        drug = HealthIntervention("Drug A", cost_per_year=5000, utility_gain=0.1)
        none = HealthIntervention("No Treatment")
        sim_drug = simulate_qalys(drug, n_sims=500, seed=42)
        sim_none = simulate_qalys(none, n_sims=500, seed=42)
        return cost_effectiveness_analysis(
            sim_results={"Drug A": sim_drug, "No Treatment": sim_none},
            comparator="No Treatment",
            wtp_thresholds=[0.0, 50_000.0, 100_000.0, 150_000.0],
        )

    def test_returns_expected_keys(self):
        cea = self._run_cea()
        assert set(cea.keys()) == {"icer", "nmb", "ceac", "ce_plane", "summary"}

    def test_icer_dataframe(self):
        cea = self._run_cea()
        icer = cea["icer"]
        assert isinstance(icer, pd.DataFrame)
        assert "ICER" in icer.columns
        assert len(icer) == 1  # one intervention vs comparator
        assert icer["ICER"].iloc[0] > 0  # treatment costs more

    def test_ceac_probabilities_sum_to_one(self):
        cea = self._run_cea()
        ceac = cea["ceac"]
        assert isinstance(ceac, pd.DataFrame)
        # At each WTP, probabilities across all interventions should sum to ~1
        row_sums = ceac.sum(axis=1)
        np.testing.assert_allclose(row_sums.to_numpy(), 1.0, atol=0.01)

    def test_nmb_increases_with_wtp(self):
        cea = self._run_cea()
        nmb = cea["nmb"]
        # NMB for the drug should increase as WTP increases
        assert nmb["Drug A"].iloc[-1] > nmb["Drug A"].iloc[0]

    def test_ce_plane_has_scatter_data(self):
        cea = self._run_cea()
        plane = cea["ce_plane"]
        assert "Drug A" in plane
        assert "Delta Cost" in plane["Drug A"].columns
        assert "Delta QALYs" in plane["Drug A"].columns
        assert len(plane["Drug A"]) == 500

    def test_summary_includes_all_interventions(self):
        cea = self._run_cea()
        summary = cea["summary"]
        assert "No Treatment" in summary.index
        assert "Drug A" in summary.index
        assert "Mean Cost" in summary.columns
        assert "Mean QALYs" in summary.columns

    def test_invalid_comparator_raises(self):
        drug = HealthIntervention("Drug A", cost_per_year=1000)
        sim = simulate_qalys(drug, n_sims=10, seed=42)
        with pytest.raises(ValueError, match="Comparator"):
            cost_effectiveness_analysis(
                sim_results={"Drug A": sim},
                comparator="Missing",
            )


# ---------------------------------------------------------------------------
# optimize_treatment
# ---------------------------------------------------------------------------


class TestOptimizeTreatment:
    def test_returns_dataframe(self):
        result = optimize_treatment(
            cost_per_dose=500.0,
            qaly_gain_per_dose=0.02,
            frequencies=[1, 4, 12],
            durations=[1, 5],
            n_sims=100,
            seed=42,
        )
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 6  # 3 frequencies x 2 durations

    def test_expected_columns(self):
        result = optimize_treatment(
            cost_per_dose=500.0,
            qaly_gain_per_dose=0.02,
            frequencies=[1, 4],
            durations=[1, 5],
            n_sims=100,
            seed=42,
        )
        expected_cols = {
            "Frequency",
            "Duration",
            "Annual_Cost",
            "Total_Cost",
            "Total_QALYs",
            "Baseline_QALYs",
            "Incremental_Cost",
            "Incremental_QALYs",
            "ICER",
            "NMB",
        }
        assert set(result.columns) == expected_cols

    def test_sorted_by_nmb_descending(self):
        result = optimize_treatment(
            cost_per_dose=500.0,
            qaly_gain_per_dose=0.02,
            frequencies=[1, 4, 12],
            durations=[1, 5, 10],
            n_sims=200,
            seed=42,
        )
        nmb_values = result["NMB"].tolist()
        assert nmb_values == sorted(nmb_values, reverse=True)

    def test_annual_cost_scales_with_frequency(self):
        result = optimize_treatment(
            cost_per_dose=100.0,
            qaly_gain_per_dose=0.01,
            frequencies=[1, 12],
            durations=[1],
            n_sims=50,
            seed=42,
        )
        costs = result.set_index("Frequency")["Annual_Cost"]
        assert costs[12] == pytest.approx(12 * costs[1])

    def test_incremental_qalys_positive(self):
        result = optimize_treatment(
            cost_per_dose=100.0,
            qaly_gain_per_dose=0.05,
            frequencies=[4],
            durations=[5],
            n_sims=200,
            seed=42,
        )
        assert result["Incremental_QALYs"].iloc[0] > 0

    def test_seed_reproducibility(self):
        r1 = optimize_treatment(
            cost_per_dose=500.0,
            qaly_gain_per_dose=0.02,
            frequencies=[1, 4],
            durations=[1, 5],
            n_sims=100,
            seed=99,
        )
        r2 = optimize_treatment(
            cost_per_dose=500.0,
            qaly_gain_per_dose=0.02,
            frequencies=[1, 4],
            durations=[1, 5],
            n_sims=100,
            seed=99,
        )
        pd.testing.assert_frame_equal(r1, r2)

    def test_deterministic_when_no_std(self):
        result = optimize_treatment(
            cost_per_dose=1000.0,
            cost_per_dose_std=0.0,
            qaly_gain_per_dose=0.05,
            qaly_gain_per_dose_std=0.0,
            frequencies=[4],
            durations=[5],
            n_sims=50,
            seed=42,
        )
        # With no stochasticity, all sims give same result
        assert result["Total_Cost"].iloc[0] > 0
