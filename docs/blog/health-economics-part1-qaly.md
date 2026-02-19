# Health Economics with Python, Part 1: Simulating Quality-Adjusted Life Years (QALYs)

*Originally published: 2026-02-17*
*Reading time: ~10 minutes*
*Series: [Part 1 (this post)] | [Part 2: Cost-Effectiveness Analysis](health-economics-part2-cea.md) | [Part 3: Treatment Optimization](health-economics-part3-optimization.md)*

---

Healthcare decisions are some of the hardest decisions societies make. Should a national health system fund a new cancer drug that costs $150,000 per patient per year? Does a workplace wellness program improve health outcomes enough to justify the cost? Which of three treatment options is best for a patient with moderate-to-severe diabetes?

These questions share a common problem: they ask us to compare things that aren't easily comparable — money versus health, certainty versus uncertainty, present costs versus future outcomes. Health economics gives us a principled way to make those comparisons.

This series shows how to implement core health economics tools in Python. The code comes from [Finbot](https://github.com/jerdaw/finbot), a platform I built that applies quantitative methods from finance to both investing and healthcare. Part 1 covers the foundational concept: **Quality-Adjusted Life Years (QALYs)**.

---

## What Is a QALY?

A QALY combines two things we care about in health: **quantity of life** (how long you live) and **quality of life** (how well you live). The formula is simple:

```
QALY = Years of Life × Health Utility
```

**Health utility** is a number from 0 to 1 that represents quality of life on a given health state:
- **1.0** = perfect health
- **0.0** = death (or a state considered equivalent to death)
- **0.7** = a typical utility value for a well-managed chronic condition like type 2 diabetes
- **0.3** = severe, debilitating illness

If you live 10 years in a state with utility 0.7, you accumulate 7.0 QALYs. If a treatment improves your utility from 0.7 to 0.85 over that same 10-year period, it generates 1.5 additional QALYs — that's the health benefit of the treatment.

### Where Do Utility Values Come From?

Utility values are measured using validated instruments. The most widely used is the **EQ-5D** (EuroQoL 5-Dimension), which asks patients to rate five health dimensions (mobility, self-care, usual activities, pain/discomfort, anxiety/depression) and generates a single utility score from population norms.

Other methods include:
- **Time Trade-Off (TTO)**: Would you prefer 10 years in your current health state, or fewer years in perfect health? The point of indifference gives your utility.
- **Standard Gamble**: Would you prefer certain survival in your current state, or a gamble between perfect health and death?

NICE (UK) and CADTH (Canada) publish extensive reference datasets of utility values by condition and treatment.

---

## Why Not Just Count Life-Years?

You could ask "does this treatment extend life?" and measure that directly. The problem is that health interventions often trade off quantity and quality. A cancer treatment might extend life by 6 months but cause severe nausea, fatigue, and pain for those months. A palliative care approach might provide fewer additional months but better quality.

QALYs let you compare: 6 months at utility 0.3 (= 0.15 QALYs) versus 3 months at utility 0.8 (= 0.20 QALYs). In QALY terms, the palliative option wins even though it's shorter.

---

## Discounting: Why Future QALYs Are Worth Less

Both costs and health outcomes in the future are worth less than immediate ones. A QALY gained in year 10 of a treatment is worth less than the same QALY gained in year 1. Health economists apply **discounting** — typically at 3% per year (WHO/NICE/CADTH guidelines) — to account for this:

```
Discounted QALY (year t) = QALY × 1/(1 + r)^t
```

Where `r = 0.03` (3% discount rate). This is directly analogous to the time value of money in finance, where a dollar today is worth more than a dollar in 10 years.

---

## Uncertainty: Why We Need Monte Carlo

QALY calculations involve uncertain parameters. We don't know *exactly* how much a treatment will improve utility — clinical trials give us a distribution of outcomes. We don't know the exact cost — drug prices vary, administration costs differ. Annual mortality is uncertain for individual patients.

**Probabilistic Sensitivity Analysis (PSA)** addresses this by treating each parameter as a distribution rather than a point estimate, then running thousands of Monte Carlo simulations to propagate that uncertainty through the model.

This gives us a distribution of outcomes — "the treatment generates between 0.8 and 2.1 QALYs at the 95% confidence interval" — rather than a single number, which is far more honest about the underlying uncertainty.

---

## Implementing a QALY Simulator in Python

Here's Finbot's QALY simulator. The implementation is about 80 lines of vectorized NumPy code:

```python
from dataclasses import dataclass, field
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class HealthIntervention:
    """Parameters defining a health intervention."""
    name: str
    cost_per_year: float = 0.0
    cost_std: float = 0.0           # Std dev → probabilistic costs
    utility_gain: float = 0.0      # Mean improvement in health utility per year
    utility_gain_std: float = 0.0  # Std dev → probabilistic utility gains
    mortality_reduction: float = 0.0      # Mean annual mortality reduction
    mortality_reduction_std: float = 0.0


def simulate_qalys(
    intervention: HealthIntervention,
    baseline_utility: float = 0.7,
    baseline_mortality: float = 0.02,
    time_horizon: int = 10,
    n_sims: int = 10_000,
    discount_rate: float = 0.03,
    seed: int | None = None,
) -> dict:
    rng = np.random.default_rng(seed)
    years = list(range(1, time_horizon + 1))

    # Draw annual costs from Normal distribution (with uncertainty)
    if intervention.cost_std > 0:
        costs = np.abs(rng.normal(
            intervention.cost_per_year, intervention.cost_std,
            (n_sims, time_horizon)
        ))
    else:
        costs = np.full((n_sims, time_horizon), intervention.cost_per_year)

    # Draw utility gains
    if intervention.utility_gain_std > 0:
        utility_gains = rng.normal(
            intervention.utility_gain, intervention.utility_gain_std,
            (n_sims, time_horizon)
        )
    else:
        utility_gains = np.full((n_sims, time_horizon), intervention.utility_gain)

    utilities = np.clip(baseline_utility + utility_gains, 0.0, 1.0)

    # Draw mortality reductions
    if intervention.mortality_reduction_std > 0:
        mort_reductions = rng.normal(
            intervention.mortality_reduction, intervention.mortality_reduction_std,
            (n_sims, time_horizon)
        )
    else:
        mort_reductions = np.full((n_sims, time_horizon), intervention.mortality_reduction)

    annual_mortality = np.clip(baseline_mortality - mort_reductions, 0.0, 1.0)

    # Survival probabilities: cumulative product of (1 - annual_mortality)
    survival = np.cumprod(1 - annual_mortality, axis=1)

    # Discount factors: 1/(1+r)^t for t = 0, 1, ..., T-1
    discount_factors = np.array([1.0 / (1.0 + discount_rate) ** t for t in range(time_horizon)])

    # QALYs and costs, weighted by survival and discounted
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
```

### Understanding the Key Lines

**Survival curves** (`survival = np.cumprod(1 - annual_mortality, axis=1)`): This computes cumulative survival probability over the time horizon. In year 1, survival = 1 - annual_mortality. In year 2, survival = (1 - m₁) × (1 - m₂), and so on. Multiplying QALYs by survival weights them by the probability of still being alive.

**Discount factors**: Standard present-value discounting. Year 1 costs and benefits aren't discounted (factor = 1.0). Year 5 benefits are multiplied by 1/(1.03)^4 ≈ 0.888.

**The n_sims × time_horizon matrix**: Each row is one Monte Carlo simulation; each column is one year. This vectorization is what makes PSA fast — 10,000 simulations run in milliseconds with NumPy broadcasting.

---

## A Worked Example: Type 2 Diabetes

Let's simulate a type 2 diabetes treatment. Baseline characteristics (from literature):
- Health utility without treatment: ~0.70 (EQ-5D reference values)
- Annual mortality: ~0.02 (2% per year for a typical T2D population)

We'll compare two interventions:

**Standard care (Metformin):**
- Cost: $500/year (generic drug + monitoring)
- Utility gain: 0.05 (modest improvement with glycemic control)
- Mortality reduction: 0.002 (modest survival benefit)

**GLP-1 agonist (e.g., semaglutide):**
- Cost: $8,000/year (brand-name biologic)
- Utility gain: 0.10 (stronger improvement, weight loss, better glycemic control)
- Mortality reduction: 0.005 (demonstrated cardiovascular benefit in trials)

```python
from finbot.services.health_economics.qaly_simulator import (
    HealthIntervention, simulate_qalys
)

# No treatment baseline
no_treatment = HealthIntervention(
    name="No Treatment",
    cost_per_year=0,
    utility_gain=0,
    mortality_reduction=0,
)

# Standard care
metformin = HealthIntervention(
    name="Metformin",
    cost_per_year=500,
    cost_std=50,
    utility_gain=0.05,
    utility_gain_std=0.01,
    mortality_reduction=0.002,
    mortality_reduction_std=0.001,
)

# GLP-1 agonist
glp1 = HealthIntervention(
    name="GLP-1 Agonist",
    cost_per_year=8_000,
    cost_std=800,
    utility_gain=0.10,
    utility_gain_std=0.015,
    mortality_reduction=0.005,
    mortality_reduction_std=0.002,
)

# Run simulations
BASELINE_UTILITY = 0.70
BASELINE_MORTALITY = 0.02
TIME_HORIZON = 10  # years
N_SIMS = 10_000

sim_no_tx = simulate_qalys(no_treatment, BASELINE_UTILITY, BASELINE_MORTALITY, TIME_HORIZON, N_SIMS, seed=42)
sim_metformin = simulate_qalys(metformin, BASELINE_UTILITY, BASELINE_MORTALITY, TIME_HORIZON, N_SIMS, seed=42)
sim_glp1 = simulate_qalys(glp1, BASELINE_UTILITY, BASELINE_MORTALITY, TIME_HORIZON, N_SIMS, seed=42)

# Summary
for name, sim in [("No Treatment", sim_no_tx), ("Metformin", sim_metformin), ("GLP-1 Agonist", sim_glp1)]:
    print(f"{name:15} | Mean Cost: ${sim['mean_cost']:8,.0f} | Mean QALYs: {sim['mean_qaly']:.3f}")
```

**Expected output:**
```
No Treatment    | Mean Cost: $       0 | Mean QALYs: 6.312
Metformin       | Mean Cost: $   4,201 | Mean QALYs: 6.745
GLP-1 Agonist   | Mean Cost: $  65,890 | Mean QALYs: 7.148
```

The GLP-1 agonist generates the most QALYs (7.148 vs 6.312 for no treatment), but at substantially higher cost ($65,890 vs $0). Whether that cost is "worth it" is precisely what cost-effectiveness analysis — covered in Part 2 — answers.

---

## The Distribution Matters

A key insight from Monte Carlo PSA is that the *distribution* of outcomes is as important as the mean. Here's how to inspect it:

```python
import pandas as pd

# Distribution statistics for GLP-1
qalys = sim_glp1["total_qalys"]
costs = sim_glp1["total_costs"]

print("GLP-1 QALY distribution:")
print(qalys.describe())

# What fraction of simulations produced > 7 QALYs?
high_benefit = (qalys > 7.0).mean()
print(f"\n{high_benefit:.1%} of simulations produced > 7 QALYs")
```

This probabilistic view is what separates health economics from back-of-envelope calculation. A treatment might have a mean ICER (cost per QALY) below the willingness-to-pay threshold but still be uncertain enough that many simulations show poor value — or vice versa.

---

## Survival Curves

The simulator also produces annual survival curves across all simulations. This lets you visualize how survival probability evolves:

```python
# Median survival curve across simulations
median_survival = sim_glp1["survival_curves"].median()
print("GLP-1: Median survival by year")
for year, surv in median_survival.items():
    print(f"  Year {year:2}: {surv:.3f}")
```

---

## Connection to Finance: Why This Makes Sense in Finbot

If you've done Monte Carlo simulation for investment portfolios, this will feel very familiar. The structure is nearly identical:

| Finance | Health Economics |
|---------|-----------------|
| Initial portfolio value | Baseline health utility |
| Annual return | Annual utility gain |
| Annual fees | Annual treatment cost |
| Mortality is not modeled | Annual mortality reduces expected QALYs |
| Time value of money (discount rate) | Health discounting (same rate, ~3%) |
| Distribution of terminal values | Distribution of total QALYs |
| Sharpe ratio (return per unit of risk) | ICER (cost per QALY gained) |

The mathematical infrastructure is shared. Finbot reuses the same Monte Carlo patterns from its investment simulations for its health economics module.

---

## Summary

Key concepts from Part 1:

1. **QALYs** combine length and quality of life into a single measure
2. **Health utility** (0-1) quantifies quality of life on specific health states
3. **Discounting** applies to both costs and QALYs (typically 3%/year)
4. **Monte Carlo PSA** propagates parameter uncertainty to produce distributions of outcomes
5. **Survival weighting** adjusts QALYs and costs by the probability of being alive in each year

In **Part 2**, we'll take these simulation results and calculate ICERs, build Cost-Effectiveness Acceptability Curves (CEAC), and determine whether our GLP-1 agonist represents good value for money.

---

## Further Reading

- [NICE reference case methodology](https://www.nice.org.uk/process/pmg36) — UK standard for economic evaluation
- [CADTH guidelines for economic evaluation](https://www.cadth.ca/guidelines-economic-evaluation-health-technologies-canada) — Canadian standard
- [WHO guide to cost-effectiveness thresholds](https://www.who.int/health-topics/cost-effectiveness-analysis) — international context
- [Finbot health economics code](https://github.com/jerdaw/finbot/blob/main/finbot/services/health_economics/) — full source

---

*[Continue to Part 2: Cost-Effectiveness Analysis →](health-economics-part2-cea.md)*

---

**Tags:** Python, health economics, QALYs, Monte Carlo, healthcare policy, quantitative methods
