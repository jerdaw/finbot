"""Monte Carlo QALY (Quality-Adjusted Life Year) simulator.

Models health intervention outcomes with probabilistic uncertainty using
Monte Carlo simulation.  Generates distributions of costs and QALYs for
downstream cost-effectiveness analysis.

Standard health economics discounting (default 3% per WHO/NICE guidelines)
is applied to both costs and health outcomes.

Typical usage:
    intervention = HealthIntervention("Drug A", cost_per_year=5000, ...)
    results = simulate_qalys(intervention, n_sims=10000)
    median_qaly = results["total_qalys"].median()
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class HealthIntervention:
    """Parameters defining a health intervention.

    Attributes:
        name: Human-readable intervention name.
        cost_per_year: Mean annual cost of the intervention.
        cost_std: Standard deviation of annual cost (0 = deterministic).
        utility_gain: Mean improvement in health utility per year (0-1 scale).
            E.g. 0.1 means the treatment improves quality of life by 0.1 QALYs/year.
        utility_gain_std: Standard deviation of annual utility gain.
        mortality_reduction: Mean reduction in annual mortality probability.
        mortality_reduction_std: Standard deviation of mortality reduction.
    """

    name: str
    cost_per_year: float = 0.0
    cost_std: float = 0.0
    utility_gain: float = 0.0
    utility_gain_std: float = 0.0
    mortality_reduction: float = 0.0
    mortality_reduction_std: float = 0.0
    # Reserved for future extensions (e.g. side-effect profiles)
    metadata: dict[str, float] = field(default_factory=dict, repr=False)


def simulate_qalys(
    intervention: HealthIntervention,
    baseline_utility: float = 0.7,
    baseline_mortality: float = 0.02,
    time_horizon: int = 10,
    n_sims: int = 10000,
    discount_rate: float = 0.03,
    seed: int | None = None,
) -> dict[str, pd.Series | pd.DataFrame | float]:
    """Simulate QALYs and costs for a health intervention via Monte Carlo.

    Parameters
    ----------
    intervention : HealthIntervention
        The intervention to simulate.
    baseline_utility : float
        Health utility without intervention (0 = death, 1 = perfect health).
    baseline_mortality : float
        Baseline annual mortality probability (0-1).
    time_horizon : int
        Number of years to simulate (default 10).
    n_sims : int
        Number of Monte Carlo trials (default 10 000).
    discount_rate : float
        Annual discount rate for costs and QALYs (default 0.03 per guidelines).
    seed : int | None
        Random seed for reproducibility.

    Returns
    -------
    dict with keys:
        ``total_costs``      : pd.Series   — total discounted cost per simulation
        ``total_qalys``      : pd.Series   — total discounted QALYs per simulation
        ``annual_costs``     : pd.DataFrame — discounted costs by year (n_sims x time_horizon)
        ``annual_qalys``     : pd.DataFrame — discounted QALYs by year
        ``survival_curves``  : pd.DataFrame — survival probability by year
        ``mean_cost``        : float
        ``mean_qaly``        : float
    """
    rng = np.random.default_rng(seed)
    years = list(range(1, time_horizon + 1))

    # --- Draw annual costs ---
    if intervention.cost_std > 0:
        costs = np.abs(rng.normal(intervention.cost_per_year, intervention.cost_std, (n_sims, time_horizon)))
    else:
        costs = np.full((n_sims, time_horizon), intervention.cost_per_year)

    # --- Draw utility gains ---
    if intervention.utility_gain_std > 0:
        utility_gains = rng.normal(intervention.utility_gain, intervention.utility_gain_std, (n_sims, time_horizon))
    else:
        utility_gains = np.full((n_sims, time_horizon), intervention.utility_gain)

    utilities = np.clip(baseline_utility + utility_gains, 0.0, 1.0)

    # --- Draw mortality reductions ---
    if intervention.mortality_reduction_std > 0:
        mort_reductions = rng.normal(
            intervention.mortality_reduction,
            intervention.mortality_reduction_std,
            (n_sims, time_horizon),
        )
    else:
        mort_reductions = np.full((n_sims, time_horizon), intervention.mortality_reduction)

    annual_mortality = np.clip(baseline_mortality - mort_reductions, 0.0, 1.0)

    # --- Survival and discounting ---
    survival = np.cumprod(1 - annual_mortality, axis=1)
    discount_factors = np.array([1.0 / (1.0 + discount_rate) ** t for t in range(time_horizon)])

    qalys_annual = utilities * survival * discount_factors
    costs_discounted = costs * survival * discount_factors

    total_qalys = qalys_annual.sum(axis=1)
    total_costs = costs_discounted.sum(axis=1)

    return {
        "total_costs": pd.Series(total_costs, name="Total Cost"),
        "total_qalys": pd.Series(total_qalys, name="Total QALYs"),
        "annual_costs": pd.DataFrame(costs_discounted, columns=years),
        "annual_qalys": pd.DataFrame(qalys_annual, columns=years),
        "survival_curves": pd.DataFrame(survival, columns=years),
        "mean_cost": float(total_costs.mean()),
        "mean_qaly": float(total_qalys.mean()),
    }
