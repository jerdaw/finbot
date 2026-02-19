"""Health economics router — QALY, CEA, treatment optimizer, clinical scenarios."""

from __future__ import annotations

from typing import Any

import numpy as np
from fastapi import APIRouter, HTTPException

from finbot.services.health_economics.cost_effectiveness import cost_effectiveness_analysis
from finbot.services.health_economics.qaly_simulator import HealthIntervention, simulate_qalys
from finbot.services.health_economics.scenarios.cancer_screening import run_cancer_screening_scenario
from finbot.services.health_economics.scenarios.hypertension import run_hypertension_scenario
from finbot.services.health_economics.scenarios.vaccine import run_vaccine_scenario
from finbot.services.health_economics.treatment_optimizer import optimize_treatment
from web.backend.schemas.health_economics import (
    CEARequest,
    CEAResponse,
    QALYRequest,
    QALYResponse,
    ScenarioRequest,
    ScenarioResponse,
    TreatmentOptimizerRequest,
    TreatmentOptimizerResponse,
)
from web.backend.services.serializers import dataframe_to_records, sanitize_value

router = APIRouter()

SCENARIO_RUNNERS = {
    "cancer_screening": run_cancer_screening_scenario,
    "hypertension": run_hypertension_scenario,
    "vaccine": run_vaccine_scenario,
}


def _intervention_from_input(inp: Any) -> HealthIntervention:
    """Convert input schema to HealthIntervention dataclass."""
    return HealthIntervention(
        name=inp.name,
        cost_per_year=inp.cost_per_year,
        cost_std=inp.cost_std,
        utility_gain=inp.utility_gain,
        utility_gain_std=inp.utility_gain_std,
        mortality_reduction=inp.mortality_reduction,
        mortality_reduction_std=inp.mortality_reduction_std,
    )


def _percentiles(series: Any) -> dict[str, float]:
    """Compute standard percentiles."""
    vals = np.array(series)
    return {
        "p5": sanitize_value(np.percentile(vals, 5)),
        "p25": sanitize_value(np.percentile(vals, 25)),
        "p50": sanitize_value(np.percentile(vals, 50)),
        "p75": sanitize_value(np.percentile(vals, 75)),
        "p95": sanitize_value(np.percentile(vals, 95)),
        "mean": sanitize_value(np.mean(vals)),
        "std": sanitize_value(np.std(vals)),
    }


@router.post("/qaly", response_model=QALYResponse)
def run_qaly(req: QALYRequest) -> QALYResponse:
    """Run QALY Monte Carlo simulation."""
    intervention = _intervention_from_input(req.intervention)
    try:
        result = simulate_qalys(
            intervention=intervention,
            baseline_utility=req.baseline_utility,
            baseline_mortality=req.baseline_mortality,
            time_horizon=req.time_horizon,
            n_sims=req.n_sims,
            discount_rate=req.discount_rate,
            seed=req.seed,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QALY simulation failed: {e}") from e

    survival_mean = result["survival_curves"].mean(axis=0).tolist()
    annual_cost_means = result["annual_costs"].mean(axis=0).tolist()
    annual_qaly_means = result["annual_qalys"].mean(axis=0).tolist()

    return QALYResponse(
        mean_cost=sanitize_value(result["mean_cost"]),
        mean_qaly=sanitize_value(result["mean_qaly"]),
        cost_percentiles=_percentiles(result["total_costs"]),
        qaly_percentiles=_percentiles(result["total_qalys"]),
        survival_curve=[sanitize_value(v) for v in survival_mean],
        annual_cost_means=[sanitize_value(v) for v in annual_cost_means],
        annual_qaly_means=[sanitize_value(v) for v in annual_qaly_means],
    )


@router.post("/cea", response_model=CEAResponse)
def run_cea(req: CEARequest) -> CEAResponse:
    """Run cost-effectiveness analysis across multiple interventions."""
    sim_results: dict[str, dict] = {}
    for qaly_req in req.interventions:
        intervention = _intervention_from_input(qaly_req.intervention)
        result = simulate_qalys(
            intervention=intervention,
            baseline_utility=qaly_req.baseline_utility,
            baseline_mortality=qaly_req.baseline_mortality,
            time_horizon=qaly_req.time_horizon,
            n_sims=qaly_req.n_sims,
            discount_rate=qaly_req.discount_rate,
            seed=qaly_req.seed,
        )
        sim_results[qaly_req.intervention.name] = result

    if req.comparator not in sim_results:
        raise HTTPException(status_code=400, detail=f"Comparator '{req.comparator}' not found in interventions")

    try:
        cea = cost_effectiveness_analysis(
            sim_results=sim_results,
            comparator=req.comparator,
            wtp_thresholds=req.wtp_thresholds,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CEA failed: {e}") from e

    # Serialize CE plane
    ce_plane: dict[str, list[dict[str, float | None]]] = {}
    for name, df in cea.get("ce_plane", {}).items():
        ce_plane[name] = dataframe_to_records(df)

    return CEAResponse(
        icer_table=dataframe_to_records(cea["icer"]),
        ceac=dataframe_to_records(cea["ceac"].reset_index()),
        ce_plane=ce_plane,
        nmb=dataframe_to_records(cea["nmb"].reset_index()),
        summary=dataframe_to_records(cea["summary"].reset_index()),
    )


@router.post("/treatment-optimizer", response_model=TreatmentOptimizerResponse)
def run_treatment_optimizer(req: TreatmentOptimizerRequest) -> TreatmentOptimizerResponse:
    """Run treatment schedule optimization."""
    try:
        results_df = optimize_treatment(
            cost_per_dose=req.cost_per_dose,
            cost_per_dose_std=req.cost_per_dose_std,
            qaly_gain_per_dose=req.qaly_gain_per_dose,
            qaly_gain_per_dose_std=req.qaly_gain_per_dose_std,
            frequencies=req.frequencies,
            durations=req.durations,
            baseline_utility=req.baseline_utility,
            baseline_mortality=req.baseline_mortality,
            mortality_reduction_per_dose=req.mortality_reduction_per_dose,
            discount_rate=req.discount_rate,
            wtp_threshold=req.wtp_threshold,
            n_sims=req.n_sims,
            seed=req.seed,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Treatment optimizer failed: {e}") from e

    records = dataframe_to_records(results_df)
    best = records[0] if records else {}

    return TreatmentOptimizerResponse(results=records, best_schedule=best)


@router.post("/scenarios", response_model=ScenarioResponse)
def run_scenario(req: ScenarioRequest) -> ScenarioResponse:
    """Run a pre-built clinical scenario analysis."""
    if req.scenario not in SCENARIO_RUNNERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown scenario: {req.scenario}. Available: {list(SCENARIO_RUNNERS.keys())}",
        )

    try:
        result = SCENARIO_RUNNERS[req.scenario](
            n_sims=req.n_sims,
            seed=req.seed,
            wtp_threshold=req.wtp_threshold,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario failed: {e}") from e

    return ScenarioResponse(
        scenario_name=result.scenario_name,
        description=result.description,
        intervention_name=result.intervention_name,
        comparator_name=result.comparator_name,
        icer=sanitize_value(result.icer),
        nmb=sanitize_value(result.nmb),
        is_cost_effective=result.is_cost_effective,
        qaly_gain=sanitize_value(result.qaly_gain),
        cost_difference=sanitize_value(result.cost_difference),
        n_simulations=result.n_simulations,
        summary_stats={k: sanitize_value(v) for k, v in result.summary_stats.items()},
    )
