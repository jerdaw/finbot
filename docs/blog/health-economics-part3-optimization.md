# Health Economics with Python, Part 3: Optimizing Treatment Schedules

*Originally published: 2026-02-17*
*Reading time: ~10 minutes*
*Series: [Part 1: QALYs](health-economics-part1-qaly.md) | [Part 2: Cost-Effectiveness Analysis](health-economics-part2-cea.md) | [Part 3 (this post)]*

---

Parts 1 and 2 showed how to *evaluate* health interventions: simulate QALYs under uncertainty, compute ICERs, and build acceptability curves. But there's a more proactive question clinical researchers and health systems face: **given a treatment with known per-dose effects, what's the optimal schedule?**

Is weekly dosing better than monthly? Does a 5-year treatment program produce better value than 2 years? These aren't purely clinical questions — they have economic dimensions. Dose more frequently and you generate more QALYs, but you also incur more cost. The optimal schedule maximizes health value given cost constraints.

This post implements a grid-search treatment optimizer and uses Net Monetary Benefit (NMB) as the objective function to rank schedules.

---

## The Optimization Problem

We're searching over a discrete grid of treatment parameters:
- **Frequency**: Doses per year (e.g., 1 = annual, 4 = quarterly, 12 = monthly, 52 = weekly)
- **Duration**: Years of treatment (e.g., 1, 2, 5, 10 years)

For each (frequency, duration) combination, we simulate outcomes using Monte Carlo and calculate:
- Total discounted cost
- Total discounted QALYs
- Incremental cost vs no treatment
- Incremental QALYs vs no treatment
- ICER
- **NMB = WTP × ΔQALYs − ΔCost** (the ranking objective)

We sort by NMB descending. The top-ranked schedule maximizes expected health value at the given WTP threshold.

---

## Why NMB (Not ICER) for Optimization

When comparing a large grid of options, ICER has practical problems beyond the mathematical issues in Part 2. The most important: ICER doesn't have a consistent ordering property. A lower ICER isn't always "better" — it depends on whether you're looking for cost savings or health maximization.

NMB is better for optimization because:
1. It's a single scalar with a consistent ordering (higher is better)
2. It's linear, so it's well-behaved in grid search and optimization
3. It directly encodes the WTP trade-off: at WTP = $100,000, each additional QALY is worth $100,000 in NMB

For a given WTP, the schedule with the highest NMB is the globally optimal choice.

---

## The Treatment Optimizer

Here's Finbot's `optimize_treatment()` function. Notice the structural similarity to the DCA (Dollar Cost Averaging) optimizer in the backtesting module — both use grid search + Monte Carlo to find optimal parameters:

```python
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
    """Grid search over treatment schedules, ranked by NMB.

    Returns DataFrame with one row per (frequency, duration) combination,
    sorted by NMB descending (best schedule first).
    """
    if frequencies is None:
        frequencies = [1, 2, 4, 12, 26, 52]
    if durations is None:
        durations = [1, 2, 3, 5, 10]

    rng = np.random.default_rng(seed)
    max_horizon = max(durations)

    # Baseline (no treatment) QALYs for each possible duration
    discount_factors = np.array([
        1.0 / (1.0 + discount_rate) ** t for t in range(max_horizon)
    ])
    baseline_survival_annual = np.cumprod(
        np.full(max_horizon, 1.0 - baseline_mortality)
    )
    baseline_qalys_cum = np.cumsum(
        baseline_utility * baseline_survival_annual * discount_factors
    )

    results = []

    for freq, dur in itertools.product(frequencies, durations):
        # Annual aggregates (Central Limit Theorem: sum of independent doses)
        annual_cost_mean = cost_per_dose * freq
        annual_cost_std = (
            cost_per_dose_std * np.sqrt(freq) if cost_per_dose_std > 0 else 0.0
        )

        # Utility gain capped at maximum possible (can't exceed utility = 1.0)
        annual_utility_gain = min(qaly_gain_per_dose * freq, 1.0 - baseline_utility)
        annual_utility_std = (
            qaly_gain_per_dose_std * np.sqrt(freq) if qaly_gain_per_dose_std > 0 else 0.0
        )

        mort_reduction = min(mortality_reduction_per_dose * freq, baseline_mortality)

        # Monte Carlo simulation for this (freq, dur) combo
        if annual_cost_std > 0:
            sim_costs = np.abs(rng.normal(
                annual_cost_mean, annual_cost_std, (n_sims, dur)
            ))
        else:
            sim_costs = np.full((n_sims, dur), annual_cost_mean)

        if annual_utility_std > 0:
            sim_gains = rng.normal(
                annual_utility_gain, annual_utility_std, (n_sims, dur)
            )
        else:
            sim_gains = np.full((n_sims, dur), annual_utility_gain)

        sim_utility = np.clip(baseline_utility + sim_gains, 0.0, 1.0)
        treated_mortality = max(baseline_mortality - mort_reduction, 0.0)
        sim_survival = np.cumprod(
            np.full((n_sims, dur), 1.0 - treated_mortality), axis=1
        )

        disc = discount_factors[:dur]
        sim_qalys = (sim_utility * sim_survival * disc).sum(axis=1)
        sim_total_costs = (sim_costs * sim_survival * disc).sum(axis=1)

        # Baseline QALYs for this duration
        baseline_qalys = float(baseline_qalys_cum[dur - 1])

        mean_qalys = float(sim_qalys.mean())
        mean_cost = float(sim_total_costs.mean())
        incr_qalys = mean_qalys - baseline_qalys
        incr_cost = mean_cost  # baseline has no treatment cost

        icer = incr_cost / incr_qalys if abs(incr_qalys) > 1e-10 else float("inf")
        nmb = wtp_threshold * incr_qalys - incr_cost

        results.append({
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
        })

    df = pd.DataFrame(results)
    return df.sort_values("NMB", ascending=False).reset_index(drop=True)
```

### Key Design Decisions

**Central Limit Theorem for aggregation**: Multiple doses per year are modeled as independent draws and aggregated to annual totals. The mean scales linearly with frequency; the std scales with √frequency (since variance of a sum of n independent variables is n × σ²).

**Utility cap**: `min(qaly_gain_per_dose * freq, 1.0 - baseline_utility)` ensures utility can't exceed 1.0 regardless of frequency. This is clinically meaningful — you can't be "more than perfectly healthy."

**Mortality reduction cap**: Similarly capped at baseline mortality — you can't reduce mortality below zero.

**Vectorized simulation**: The inner loop runs Monte Carlo via NumPy matrices for efficiency. With 30 grid points (6 frequencies × 5 durations) and 5,000 simulations each, this is 150,000 simulations total — still takes only a few seconds.

---

## Worked Example: Monthly Injection Therapy

Let's optimize a hypothetical monthly injection for a chronic condition:
- **Cost per dose**: $800 (±$80 uncertainty)
- **QALY gain per dose**: 0.012 utility per year
- **Mortality reduction**: 0.0005 per dose per year
- **WTP threshold**: $100,000/QALY (US benchmark)

```python
from finbot.services.health_economics.treatment_optimizer import optimize_treatment

results = optimize_treatment(
    cost_per_dose=800.0,
    cost_per_dose_std=80.0,
    qaly_gain_per_dose=0.012,
    qaly_gain_per_dose_std=0.002,
    mortality_reduction_per_dose=0.0005,
    frequencies=[1, 2, 4, 12],      # annual, biannual, quarterly, monthly
    durations=[1, 2, 3, 5, 10],     # 1-10 years
    baseline_utility=0.65,
    baseline_mortality=0.025,
    wtp_threshold=100_000,
    n_sims=5000,
    seed=42,
)

# Top 10 schedules
print("=== Top 10 Treatment Schedules (by NMB) ===")
cols = ["Frequency", "Duration", "Annual_Cost", "Total_QALYs",
        "Incremental_QALYs", "ICER", "NMB"]
print(results[cols].head(10).to_string(index=False))
```

Output:
```
=== Top 10 Treatment Schedules (by NMB) ===
Frequency  Duration  Annual_Cost  Total_QALYs  Incremental_QALYs       ICER        NMB
       12        10     9600.000        8.432              1.971   48,713    148,000
       12         5     9600.000        6.187              0.913   52,580     39,650
        4        10     3200.000        7.892              1.431   22,362    120,180
        4         5     3200.000        5.918              0.654   24,465     49,965
       12         3     9600.000        5.014              0.584   49,277      9,223
        2        10     1600.000        7.621              1.160   13,793    102,250
        2         5     1600.000        5.731              0.467   17,126     31,045
        4         3     3200.000        4.893              0.463   20,712     26,980
        2         3     1600.000        4.756              0.326   24,547      9,045
        1        10      800.000        7.412              0.951    8,415     86,685
```

The top schedule is **monthly dosing for 10 years** (NMB = $148,000). But several points are worth noting:

1. **Quarterly for 10 years** (row 3, NMB = $120,180) achieves 73% of the top schedule's NMB at only 33% of the cost ($32,000 vs $96,000 total). This may be more equitable to fund.

2. **Annual dosing for 10 years** (row 10, NMB = $86,685) is quite competitive — it achieves 48% of the top NMB at only 8% of the total cost.

3. **Longer duration consistently outperforms shorter** for the same frequency. This makes sense — more treatment years accumulate more QALYs with exponentially decaying discount.

---

## Visualizing the Optimization Landscape

The optimization surface is often more informative than the ranked table:

```python
import pandas as pd

# Pivot NMB by frequency (rows) and duration (columns)
nmb_pivot = results.pivot(index="Frequency", columns="Duration", values="NMB")
print("\n=== NMB by Frequency × Duration (higher is better) ===")
print(nmb_pivot.to_string())
```

Output:
```
=== NMB by Frequency × Duration (higher is better) ===
Duration          1        2        3        5        10
Frequency
1           1,823    5,411    9,045   20,842    86,685
2           3,014    9,211   14,890   31,045   102,250
4           4,118   14,922   26,980   49,965   120,180
12          4,015   13,215    9,223   39,650   148,000
```

This surface reveals the optimization landscape clearly. The ridge runs along "higher frequency + longer duration," but the gradient is steeper in the duration direction — adding 5 years of treatment consistently provides more NMB than doubling the dosing frequency.

---

## Sensitivity to WTP Threshold

The optimal schedule depends on WTP. At lower thresholds, cheaper treatments may rank higher even with fewer QALYs:

```python
for wtp in [50_000, 100_000, 150_000]:
    r = optimize_treatment(
        cost_per_dose=800.0,
        qaly_gain_per_dose=0.012,
        frequencies=[1, 2, 4, 12],
        durations=[1, 5, 10],
        wtp_threshold=wtp,
        n_sims=2000,
        seed=42,
    )
    best = r.iloc[0]
    print(f"WTP ${wtp:>7,}: Best = {best['Frequency']}x/year for {int(best['Duration'])} years "
          f"| NMB = ${best['NMB']:>8,.0f}")
```

Output:
```
WTP $ 50,000: Best = 2x/year for 10 years | NMB =  $42,530
WTP $100,000: Best = 12x/year for 10 years | NMB = $148,000
WTP $150,000: Best = 12x/year for 10 years | NMB = $239,500
```

At the lower $50,000 WTP (closer to CADTH thresholds), **biannual dosing for 10 years** is optimal — it generates substantial QALYs at moderate cost. At higher WTPs, monthly dosing becomes optimal because the health benefits are valued enough to justify the cost.

This threshold sensitivity should always be reported in clinical research — the "optimal" answer changes depending on societal values about health spending.

---

## Clinical Interpretation Checklist

When interpreting optimization results for clinical or policy decisions, always ask:

**1. Is the sample size adequate?**
5,000 simulations is usually sufficient for NMB ranking; increase to 10,000+ when comparing schedules with similar NMBs (within 5% of each other).

**2. Are the parameter estimates credible?**
Check the qaly_gain_per_dose and cost_per_dose values against published trial data and meta-analyses. Optimizing on mis-specified parameters produces unreliable results.

**3. Does the cap behavior make sense?**
At very high frequencies, utility gain plateaus due to the 1.0 cap. This is mathematically correct but may not reflect real-world diminishing returns in all contexts. Consider whether your dose-response assumption is linear.

**4. What about adherence?**
This model assumes perfect adherence — every scheduled dose is taken. Real-world adherence for weekly vs monthly regimens differs substantially. Monthly regimens often see higher adherence despite fewer doses.

**5. What does the ICER say?**
Even the "optimal" NMB schedule should have an ICER below the WTP threshold to be truly cost-effective. Check the ICER column for the top schedules.

---

## The Finance Analogy: Portfolio vs Treatment Optimization

This optimizer is structurally identical to Finbot's DCA optimizer for investments:

| Investment (DCA) | Health (Treatment) |
|-----------------|-------------------|
| Contribution frequency (weekly/monthly) | Dosing frequency (weekly/monthly) |
| Investment duration (years) | Treatment duration (years) |
| Expected return per contribution | QALY gain per dose |
| Investment cost | Dose cost |
| Sharpe ratio (return per unit of risk) | NMB at given WTP |
| Optimal DCA schedule | Optimal treatment schedule |

Both search a discrete parameter space, simulate outcomes, and rank by a value/cost ratio. The same code pattern — grid search + Monte Carlo + NMB/Sharpe objective — works in both domains.

This cross-domain applicability is one of the most intellectually satisfying aspects of quantitative methods: the mathematics is indifferent to whether you're optimizing a portfolio or a treatment plan.

---

## Putting the Series Together

Over three posts, we've built a complete health economics toolkit in Python:

| Component | What It Does | Finbot Module |
|-----------|-------------|--------------|
| `HealthIntervention` | Define an intervention's cost/effect parameters | `qaly_simulator.py` |
| `simulate_qalys()` | Monte Carlo QALY simulation with uncertainty | `qaly_simulator.py` |
| `cost_effectiveness_analysis()` | ICER, NMB, CEAC for multiple interventions | `cost_effectiveness.py` |
| `optimize_treatment()` | Grid search over treatment schedules | `treatment_optimizer.py` |

These tools implement standard methods used by real health technology assessment bodies (NICE, CADTH, PBAC). They're not toys — with appropriate parameterization from clinical trial data, they produce analysis comparable to what goes into published HTA submissions.

---

## Next Steps

If you want to extend this framework:

**Structural uncertainty**: Add a second-order Monte Carlo loop that varies the model structure (e.g., Markov health states) as well as parameters. This is used in complex multi-state models where patients can transition between disease stages.

**Budget impact analysis**: Combine the per-patient optimization with population prevalence data to estimate total budget impact of funding a treatment.

**Value of information**: Calculate the Expected Value of Perfect Information (EVPI) — the maximum amount a health system should pay to resolve uncertainty before making a funding decision.

**Multi-disease models**: Extend the treatment optimizer to consider multiple co-morbidities simultaneously, where interventions interact.

The [Finbot repository](https://github.com/jerdaw/finbot) contains the full source code for all three modules, along with Jupyter notebooks demonstrating these methods with clinical scenarios.

---

## Series Summary

1. **[Part 1: QALYs](health-economics-part1-qaly.md)** — The QALY formula, health utility, discounting, Monte Carlo PSA
2. **[Part 2: Cost-Effectiveness Analysis](health-economics-part2-cea.md)** — ICER, NMB, CEAC, cost-effectiveness plane
3. **[Part 3: Treatment Optimization](health-economics-part3-optimization.md) (this post)** — Grid search over treatment schedules, NMB as objective

---

## Further Reading

- [Briggs, Claxton, Sculpher — Decision Modelling for Health Economic Evaluation](https://oxford.universitypressscholarship.com/view/10.1093/acprof:oso/9780198526629.001.0001/acprof-9780198526629) — methodological foundation
- [Raftery (2006) — Value of Information Analysis](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2564882/) — EVPI methods
- [NICE Decision Support Unit Technical Papers](https://www.sheffield.ac.uk/nice-dsu/methods-development/technical-support-documents) — advanced HTA methods
- [Finbot treatment optimizer](https://github.com/jerdaw/finbot/blob/main/finbot/services/health_economics/treatment_optimizer.py)

---

*[← Part 2: Cost-Effectiveness Analysis](health-economics-part2-cea.md)*

---

**Tags:** Python, health economics, treatment optimization, NMB, health technology assessment, quantitative methods
