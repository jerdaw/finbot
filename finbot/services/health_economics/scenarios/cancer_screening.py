"""Cancer screening scenario: annual mammography vs. no routine screening.

Models the cost-effectiveness of annual mammography screening for
50-year-old women over a 10-year horizon.  Compares annual screening
against no routine screening using published benchmark parameters.

References:
    - Stout et al. (2006): Retrospective cost-effectiveness analysis of
      mammography screening, J Natl Cancer Inst.
    - Canadian Cancer Society breast cancer screening guidelines (2024).

DISCLAIMER: Parameters are illustrative estimates for EDUCATIONAL purposes
only.  Do not use for actual clinical decisions or health policy.
"""

from __future__ import annotations

import math

from finbot.services.health_economics.cost_effectiveness import cost_effectiveness_analysis
from finbot.services.health_economics.qaly_simulator import HealthIntervention, simulate_qalys
from finbot.services.health_economics.scenarios.models import ScenarioResult

_SCENARIO_NAME = "Annual Mammography Screening"
_DESCRIPTION = (
    "Annual mammography screening vs. no routine screening for 50-year-old women "
    "over a 10-year horizon.  Models direct screening costs, downstream diagnostic "
    "workup, and mortality/utility gains from earlier breast cancer detection."
)
_INTERVENTION = "Annual Screening"
_COMPARATOR = "No Routine Screening"

# Baseline cohort: 50-year-old women
_BASELINE_UTILITY = 0.82  # EQ-5D utility for average 50-year-old woman
_BASELINE_MORTALITY = 0.008  # ~0.8% annual all-cause mortality for age 50
_TIME_HORIZON = 10  # years

# Intervention arm: annual mammography screening
# Cost includes: screening (~$300) + downstream workup from false positives (~$500)
_SCREENING = HealthIntervention(
    name=_INTERVENTION,
    cost_per_year=800.0,
    cost_std=200.0,
    utility_gain=0.01,  # Reassurance + earlier detection benefit
    utility_gain_std=0.005,
    mortality_reduction=0.0015,  # ~15% RRR x ~1% breast cancer annual mortality
    mortality_reduction_std=0.0005,
)

# Comparator arm: no routine screening (baseline — no costs, no extra benefit)
_NO_SCREENING = HealthIntervention(name=_COMPARATOR)


def run_cancer_screening_scenario(
    n_sims: int = 10_000,
    seed: int = 42,
    wtp_threshold: float = 100_000.0,
) -> ScenarioResult:
    """Run the annual mammography screening cost-effectiveness scenario.

    Parameters
    ----------
    n_sims : int
        Number of Monte Carlo simulations (default 10,000).
    seed : int
        Random seed for reproducibility (default 42).
    wtp_threshold : float
        Willingness-to-pay threshold in $/QALY for cost-effectiveness
        determination (default $100,000 per WHO/NICE guidelines).

    Returns
    -------
    ScenarioResult
        Structured result with ICER, NMB, and summary statistics.
    """
    sim_screening = simulate_qalys(
        _SCREENING,
        baseline_utility=_BASELINE_UTILITY,
        baseline_mortality=_BASELINE_MORTALITY,
        time_horizon=_TIME_HORIZON,
        n_sims=n_sims,
        seed=seed,
    )
    sim_no_screening = simulate_qalys(
        _NO_SCREENING,
        baseline_utility=_BASELINE_UTILITY,
        baseline_mortality=_BASELINE_MORTALITY,
        time_horizon=_TIME_HORIZON,
        n_sims=n_sims,
        seed=seed + 1,
    )

    wtp_thresholds = sorted({50_000.0, 100_000.0, wtp_threshold})
    cea = cost_effectiveness_analysis(
        sim_results={_INTERVENTION: sim_screening, _COMPARATOR: sim_no_screening},
        comparator=_COMPARATOR,
        wtp_thresholds=wtp_thresholds,
    )

    icer_row = cea["icer"].iloc[0]  # type: ignore[union-attr]
    qaly_gain = float(icer_row["Incremental QALYs"])
    cost_diff = float(icer_row["Incremental Cost"])
    raw_icer = float(icer_row["ICER"])

    # ICER is None when dominated (infinite ICER) or negligible QALY gain
    icer: float | None = None if math.isinf(raw_icer) or qaly_gain <= 0 else raw_icer
    nmb = wtp_threshold * qaly_gain - cost_diff
    is_cost_effective = nmb > 0

    summary_stats: dict[str, float] = {
        "mean_cost_screening": float(sim_screening["mean_cost"]),  # type: ignore[arg-type]
        "mean_cost_no_screening": float(sim_no_screening["mean_cost"]),  # type: ignore[arg-type]
        "mean_qaly_screening": float(sim_screening["mean_qaly"]),  # type: ignore[arg-type]
        "mean_qaly_no_screening": float(sim_no_screening["mean_qaly"]),  # type: ignore[arg-type]
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
