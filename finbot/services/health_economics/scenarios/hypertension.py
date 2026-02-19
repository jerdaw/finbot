"""Hypertension scenario: ACE inhibitor vs. lifestyle modification.

Models the cost-effectiveness of antihypertensive medication (ACE inhibitor)
compared with lifestyle modification (diet, exercise, sodium restriction) for
Stage 1 hypertension over a 5-year horizon.

References:
    - SPRINT Research Group (2015): NEJM 373:2103-16.
    - Kalaitzidis et al. (2011): ACE inhibitors in hypertension, Expert Rev.
    - Weinstein MC & Stason WB (1976): Hypertension cost-effectiveness framework.

DISCLAIMER: Parameters are illustrative estimates for EDUCATIONAL purposes
only.  Do not use for actual clinical decisions or health policy.
"""

from __future__ import annotations

import math

from finbot.services.health_economics.cost_effectiveness import cost_effectiveness_analysis
from finbot.services.health_economics.qaly_simulator import HealthIntervention, simulate_qalys
from finbot.services.health_economics.scenarios.models import ScenarioResult

_SCENARIO_NAME = "Antihypertensive Therapy: ACE Inhibitor vs. Lifestyle"
_DESCRIPTION = (
    "ACE inhibitor (ramipril) vs. lifestyle modification (diet + exercise) for "
    "Stage 1 hypertension over a 5-year horizon.  Models stroke risk reduction, "
    "medication costs, and quality-of-life differences between approaches."
)
_INTERVENTION = "ACE Inhibitor"
_COMPARATOR = "Lifestyle Modification"

# Baseline cohort: Stage 1 hypertension patient (~55 years old)
_BASELINE_UTILITY = 0.75  # Reduced from population norm due to hypertension
_BASELINE_MORTALITY = 0.025  # Elevated all-cause mortality with uncontrolled HTN
_TIME_HORIZON = 5  # years

# ACE inhibitor arm: generic ramipril (~$300/yr) + monitoring (~$300/yr)
_ACE_INHIBITOR = HealthIntervention(
    name=_INTERVENTION,
    cost_per_year=600.0,
    cost_std=100.0,
    utility_gain=0.03,  # Better BP control → fewer symptoms, less anxiety
    utility_gain_std=0.010,
    mortality_reduction=0.008,  # ~25-30% RRR stroke x ~3% annual stroke risk
    mortality_reduction_std=0.003,
)

# Lifestyle modification arm: gym, dietitian, monitoring visits
_LIFESTYLE = HealthIntervention(
    name=_COMPARATOR,
    cost_per_year=400.0,
    cost_std=150.0,
    utility_gain=0.02,  # Exercise/weight-loss benefit, partial BP control
    utility_gain_std=0.010,
    mortality_reduction=0.005,  # Partial stroke risk reduction
    mortality_reduction_std=0.002,
)


def run_hypertension_scenario(
    n_sims: int = 10_000,
    seed: int = 42,
    wtp_threshold: float = 100_000.0,
) -> ScenarioResult:
    """Run the hypertension treatment cost-effectiveness scenario.

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
    sim_ace = simulate_qalys(
        _ACE_INHIBITOR,
        baseline_utility=_BASELINE_UTILITY,
        baseline_mortality=_BASELINE_MORTALITY,
        time_horizon=_TIME_HORIZON,
        n_sims=n_sims,
        seed=seed,
    )
    sim_lifestyle = simulate_qalys(
        _LIFESTYLE,
        baseline_utility=_BASELINE_UTILITY,
        baseline_mortality=_BASELINE_MORTALITY,
        time_horizon=_TIME_HORIZON,
        n_sims=n_sims,
        seed=seed + 1,
    )

    wtp_thresholds = sorted({50_000.0, 100_000.0, wtp_threshold})
    cea = cost_effectiveness_analysis(
        sim_results={_INTERVENTION: sim_ace, _COMPARATOR: sim_lifestyle},
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
        "mean_cost_ace": float(sim_ace["mean_cost"]),  # type: ignore[arg-type]
        "mean_cost_lifestyle": float(sim_lifestyle["mean_cost"]),  # type: ignore[arg-type]
        "mean_qaly_ace": float(sim_ace["mean_qaly"]),  # type: ignore[arg-type]
        "mean_qaly_lifestyle": float(sim_lifestyle["mean_qaly"]),  # type: ignore[arg-type]
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
