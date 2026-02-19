"""Influenza vaccine scenario: vaccination vs. no vaccination in elderly.

Models the cost-effectiveness of annual influenza vaccination for adults
aged 65 and older over a 1-year horizon from a societal perspective.
Accounts for infection prevention, hospitalisation avoidance, and
mortality reduction.

References:
    - Maciosek et al. (2006): Prioritizing clinical preventive services,
      Am J Prev Med.
    - Nichol KL et al. (1998): Effectiveness of influenza vaccine, NEJM.
    - CDC Advisory Committee on Immunization Practices (ACIP) recommendations.

DISCLAIMER: Parameters are illustrative estimates for EDUCATIONAL purposes
only.  Do not use for actual clinical decisions or health policy.
"""

from __future__ import annotations

import math

from finbot.services.health_economics.cost_effectiveness import cost_effectiveness_analysis
from finbot.services.health_economics.qaly_simulator import HealthIntervention, simulate_qalys
from finbot.services.health_economics.scenarios.models import ScenarioResult

_SCENARIO_NAME = "Influenza Vaccination in Elderly (≥65)"
_DESCRIPTION = (
    "Annual influenza vaccination vs. no vaccination for adults aged ≥65 over a "
    "1-year horizon (societal perspective).  Models infection prevention, "
    "hospitalisation avoidance, and mortality reduction from influenza."
)
_INTERVENTION = "Annual Flu Vaccine"
_COMPARATOR = "No Vaccination"

# Baseline cohort: adults aged ≥65
_BASELINE_UTILITY = 0.72  # Average EQ-5D utility for elderly (≥65)
_BASELINE_MORTALITY = 0.04  # ~4% annual all-cause mortality for 65+ cohort
_TIME_HORIZON = 1  # 1-year societal perspective

# Vaccination arm: vaccine + administration
# Influenza infection rate in elderly ~10-15%; vaccine efficacy ~40-60%
# Hospitalisation cost ~$15,000; prevented per 100 vaccinated ≈ 1-2 admissions
_VACCINE = HealthIntervention(
    name=_INTERVENTION,
    cost_per_year=50.0,  # Vaccine + administration (publicly subsidised)
    cost_std=15.0,
    utility_gain=0.02,  # Avoided flu illness + reduced anxiety
    utility_gain_std=0.010,
    mortality_reduction=0.005,  # ~10-15% infection rate x 40% VE x ~10% IFR in elderly
    mortality_reduction_std=0.002,
)

# Comparator: no vaccination (baseline — no costs, no extra benefit)
_NO_VACCINE = HealthIntervention(name=_COMPARATOR)


def run_vaccine_scenario(
    n_sims: int = 10_000,
    seed: int = 42,
    wtp_threshold: float = 100_000.0,
) -> ScenarioResult:
    """Run the influenza vaccination cost-effectiveness scenario.

    Parameters
    ----------
    n_sims : int
        Number of Monte Carlo simulations (default 10,000).
    seed : int
        Random seed for reproducibility (default 42).
    wtp_threshold : float
        Willingness-to-pay threshold in $/QALY (default $100,000).

    Returns
    -------
    ScenarioResult
        Structured result with ICER, NMB, and summary statistics.
    """
    sim_vaccine = simulate_qalys(
        _VACCINE,
        baseline_utility=_BASELINE_UTILITY,
        baseline_mortality=_BASELINE_MORTALITY,
        time_horizon=_TIME_HORIZON,
        n_sims=n_sims,
        seed=seed,
    )
    sim_no_vaccine = simulate_qalys(
        _NO_VACCINE,
        baseline_utility=_BASELINE_UTILITY,
        baseline_mortality=_BASELINE_MORTALITY,
        time_horizon=_TIME_HORIZON,
        n_sims=n_sims,
        seed=seed + 1,
    )

    wtp_thresholds = sorted({50_000.0, 100_000.0, wtp_threshold})
    cea = cost_effectiveness_analysis(
        sim_results={_INTERVENTION: sim_vaccine, _COMPARATOR: sim_no_vaccine},
        comparator=_COMPARATOR,
        wtp_thresholds=wtp_thresholds,
    )

    icer_row = cea["icer"].iloc[0]  # type: ignore[union-attr]
    qaly_gain = float(icer_row["Incremental QALYs"])
    cost_diff = float(icer_row["Incremental Cost"])
    raw_icer = float(icer_row["ICER"])

    icer: float | None = None if math.isinf(raw_icer) else raw_icer
    nmb = wtp_threshold * qaly_gain - cost_diff
    is_cost_effective = nmb > 0

    summary_stats: dict[str, float] = {
        "mean_cost_vaccine": float(sim_vaccine["mean_cost"]),  # type: ignore[arg-type]
        "mean_cost_no_vaccine": float(sim_no_vaccine["mean_cost"]),  # type: ignore[arg-type]
        "mean_qaly_vaccine": float(sim_vaccine["mean_qaly"]),  # type: ignore[arg-type]
        "mean_qaly_no_vaccine": float(sim_no_vaccine["mean_qaly"]),  # type: ignore[arg-type]
    }

    return ScenarioResult(
        scenario_name=_SCENARIO_NAME,
        description=_DESCRIPTION,
        intervention_name=_INTERVENTION,
        comparator_name=_COMPARATOR,
        icer=icer,
        nmb=nmb,
        is_cost_effective=is_cost_effective,
        qaly_gain=qaly_gain,
        cost_difference=cost_diff,
        n_simulations=n_sims,
        summary_stats=summary_stats,
    )
