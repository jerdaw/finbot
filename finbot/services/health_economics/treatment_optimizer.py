"""Treatment schedule optimizer using grid search.

Adapts the DCA (Dollar Cost Averaging) optimization pattern to health
economics: instead of optimizing investment timing, optimizes treatment
schedules (dose frequency and duration) for cost-effectiveness.

Grid-searches across treatment parameters and evaluates each combination
using Monte Carlo simulation.  Ranks schedules by Net Monetary Benefit
(NMB = WTP x incremental_QALYs - incremental_cost).

Typical usage:
    results = optimize_treatment(
        cost_per_dose=1000.0,
        qaly_gain_per_dose=0.02,
        frequencies=[1, 2, 4, 12],
        durations=[1, 2, 5, 10],
    )
    best = results.iloc[0]  # highest NMB
"""

from __future__ import annotations

import itertools

import numpy as np
import pandas as pd


def optimize_treatment(
    cost_per_dose: float,
    cost_per_dose_std: float = 0.0,
    qaly_gain_per_dose: float = 0.02,
    qaly_gain_per_dose_std: float = 0.0,
    frequencies: list[int] | None = None,
    durations: list[int] | None = None,
    baseline_utility: float = 0.7,
    baseline_mortality: float = 0.02,
    mortality_reduction_per_dose: float = 0.0,
    discount_rate: float = 0.03,
    wtp_threshold: float = 50_000.0,
    n_sims: int = 5000,
    seed: int | None = None,
) -> pd.DataFrame:
    """Optimize treatment schedule via grid search over frequency and duration.

    Parameters
    ----------
    cost_per_dose : float
        Mean cost per treatment dose.
    cost_per_dose_std : float
        Std dev of cost per dose (0 = deterministic).
    qaly_gain_per_dose : float
        QALY utility gain per dose per year.  Annual gain is
        ``qaly_gain_per_dose * frequency``, capped at ``1 - baseline_utility``.
    qaly_gain_per_dose_std : float
        Std dev of utility gain per dose.
    frequencies : list[int] | None
        Doses per year to evaluate.  Defaults to ``[1, 2, 4, 12, 26, 52]``.
    durations : list[int] | None
        Treatment durations in years.  Defaults to ``[1, 2, 3, 5, 10]``.
    baseline_utility : float
        Health utility without treatment (0-1 scale).
    baseline_mortality : float
        Baseline annual mortality probability.
    mortality_reduction_per_dose : float
        Reduction in annual mortality per dose per year.
    discount_rate : float
        Annual discount rate (default 0.03).
    wtp_threshold : float
        Willingness-to-pay per QALY for NMB calculation (default $50 000).
    n_sims : int
        Monte Carlo simulations per parameter combination (default 5000).
    seed : int | None
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        One row per (frequency, duration) combination.  Columns include
        ``Frequency``, ``Duration``, ``Annual_Cost``, ``Total_Cost``,
        ``Total_QALYs``, ``Incremental_Cost``, ``Incremental_QALYs``,
        ``ICER``, ``NMB``.  Sorted by NMB descending (best first).
    """
    if frequencies is None:
        frequencies = [1, 2, 4, 12, 26, 52]
    if durations is None:
        durations = [1, 2, 3, 5, 10]

    rng = np.random.default_rng(seed)
    max_horizon = max(durations)

    # Pre-compute baseline (no-treatment) QALYs for each duration
    discount_factors = np.array([1.0 / (1.0 + discount_rate) ** t for t in range(max_horizon)])
    baseline_survival_annual = np.cumprod(np.full(max_horizon, 1.0 - baseline_mortality))
    baseline_qalys_cum = np.cumsum(baseline_utility * baseline_survival_annual * discount_factors)

    results: list[dict[str, float | int]] = []

    for freq, dur in itertools.product(frequencies, durations):
        # Annual aggregates (CLT for independent doses within a year)
        annual_cost_mean = cost_per_dose * freq
        annual_cost_std = cost_per_dose_std * np.sqrt(freq) if cost_per_dose_std > 0 else 0.0

        annual_utility_gain = min(qaly_gain_per_dose * freq, 1.0 - baseline_utility)
        annual_utility_std = qaly_gain_per_dose_std * np.sqrt(freq) if qaly_gain_per_dose_std > 0 else 0.0

        mort_reduction = min(mortality_reduction_per_dose * freq, baseline_mortality)

        # --- Monte Carlo for this (freq, dur) combination ---
        if annual_cost_std > 0:
            sim_costs = np.abs(rng.normal(annual_cost_mean, annual_cost_std, (n_sims, dur)))
        else:
            sim_costs = np.full((n_sims, dur), annual_cost_mean)

        if annual_utility_std > 0:
            sim_gains = rng.normal(annual_utility_gain, annual_utility_std, (n_sims, dur))
        else:
            sim_gains = np.full((n_sims, dur), annual_utility_gain)

        sim_utility = np.clip(baseline_utility + sim_gains, 0.0, 1.0)

        treated_mortality = max(baseline_mortality - mort_reduction, 0.0)
        sim_survival = np.cumprod(np.full((n_sims, dur), 1.0 - treated_mortality), axis=1)

        disc = discount_factors[:dur]
        sim_qalys = (sim_utility * sim_survival * disc).sum(axis=1)
        sim_total_costs = (sim_costs * sim_survival * disc).sum(axis=1)

        baseline_qalys = float(baseline_qalys_cum[dur - 1])

        mean_qalys = float(sim_qalys.mean())
        mean_cost = float(sim_total_costs.mean())
        incr_qalys = mean_qalys - baseline_qalys
        incr_cost = mean_cost  # baseline has zero treatment cost

        icer = incr_cost / incr_qalys if abs(incr_qalys) > 1e-10 else float("inf")
        nmb = wtp_threshold * incr_qalys - incr_cost

        results.append(
            {
                "Frequency": freq,
                "Duration": dur,
                "Annual_Cost": annual_cost_mean,
                "Total_Cost": mean_cost,
                "Total_QALYs": mean_qalys,
                "Baseline_QALYs": baseline_qalys,
                "Incremental_Cost": incr_cost,
                "Incremental_QALYs": incr_qalys,
                "ICER": icer,
                "NMB": nmb,
            }
        )

    df = pd.DataFrame(results)
    return df.sort_values("NMB", ascending=False).reset_index(drop=True)
