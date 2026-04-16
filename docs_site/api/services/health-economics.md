# Health Economics

The health economics module provides tools for quality-adjusted life year
(QALY) simulation, cost-effectiveness analysis, and treatment schedule
optimization.

## Overview

The health economics module supports:

- **QALY Simulation**: Monte Carlo simulation with stochastic costs,
  utilities, and mortality.
- **Cost-Effectiveness Analysis**: ICER, NMB, CEAC, and cost-effectiveness
  planes.
- **Treatment Optimization**: Grid-search optimization across treatment
  schedules.
- **Standards-aligned framing**: NICE, CADTH, and WHO-style reference points
  for discounting and willingness-to-pay interpretation.

## Modules

### QALY Simulator

Simulates health economic outcomes using Monte Carlo methods:

::: finbot.services.health_economics.qaly_simulator
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### Cost-Effectiveness Analysis

Computes incremental cost-effectiveness ratios and net monetary benefit:

::: finbot.services.health_economics.cost_effectiveness
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### Treatment Optimizer

Optimizes treatment schedules using grid search:

::: finbot.services.health_economics.treatment_optimizer
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Quick Start

### QALY Simulation Example

```python
from finbot.services.health_economics.qaly_simulator import (
    HealthIntervention,
    simulate_qalys,
)

metformin = HealthIntervention(
    name="Metformin",
    cost_per_year=500.0,
    cost_std=100.0,
    utility_gain=0.08,
    utility_gain_std=0.02,
    mortality_reduction=0.003,
    mortality_reduction_std=0.001,
)

glp1 = HealthIntervention(
    name="GLP-1 Agonist",
    cost_per_year=10_000.0,
    cost_std=1_500.0,
    utility_gain=0.15,
    utility_gain_std=0.03,
    mortality_reduction=0.008,
    mortality_reduction_std=0.002,
)

baseline_utility = 0.65
baseline_mortality = 0.04

sim_metformin = simulate_qalys(
    metformin,
    baseline_utility=baseline_utility,
    baseline_mortality=baseline_mortality,
    time_horizon=15,
    n_sims=10_000,
    discount_rate=0.03,
    seed=42,
)

sim_glp1 = simulate_qalys(
    glp1,
    baseline_utility=baseline_utility,
    baseline_mortality=baseline_mortality,
    time_horizon=15,
    n_sims=10_000,
    discount_rate=0.03,
    seed=42,
)

print(f"Metformin mean QALYs: {sim_metformin['mean_qaly']:.2f}")
print(f"GLP-1 mean QALYs: {sim_glp1['mean_qaly']:.2f}")
```

### Cost-Effectiveness Analysis Example

```python
from finbot.services.health_economics.cost_effectiveness import cost_effectiveness_analysis

cea = cost_effectiveness_analysis(
    sim_results={
        "Metformin": sim_metformin,
        "GLP-1 Agonist": sim_glp1,
    },
    comparator="Metformin",
)

icer_row = cea["icer"].iloc[0]
print(f"ICER: ${icer_row['ICER']:,.0f} per QALY")
print(f"Incremental QALYs: {icer_row['Incremental QALYs']:.2f}")
print(f"Incremental Cost: ${icer_row['Incremental Cost']:,.0f}")

print(cea["summary"])
```

### Treatment Optimization Example

```python
from finbot.services.health_economics.treatment_optimizer import optimize_treatment

results = optimize_treatment(
    cost_per_dose=1000.0,
    qaly_gain_per_dose=0.02,
    frequencies=[1, 2, 4, 12],
    durations=[1, 2, 5, 10],
    wtp_threshold=50_000.0,
    seed=42,
)

best = results.iloc[0]
print(f"Best frequency: {int(best['Frequency'])} doses/year")
print(f"Best duration: {int(best['Duration'])} years")
print(f"Expected NMB: ${best['NMB']:,.0f}")
```

## Key Concepts

### Quality-Adjusted Life Years (QALYs)

QALYs combine:
- **Survival time**: Years of life gained
- **Quality of life**: Utility scores (0 = death, 1 = perfect health)

Calculation: `QALY = Σ(utility_i × duration_i)`

### Incremental Cost-Effectiveness Ratio (ICER)

Measures cost per additional QALY gained:

```
ICER = (Cost_treatment - Cost_control) / (QALY_treatment - QALY_control)
```

### Net Monetary Benefit (NMB)

Converts health outcomes to monetary terms:

```
NMB = (QALY_treatment - QALY_control) × WTP - (Cost_treatment - Cost_control)
```

### Cost-Effectiveness Acceptability Curve (CEAC)

Shows probability that treatment is cost-effective across different
willingness-to-pay thresholds.

## Implementation Notes

- Annual-cycle Monte Carlo simulation drives the QALY module.
- Discounting is applied to both costs and QALYs by default.
- Outputs are designed for downstream probabilistic sensitivity analysis.
- The treatment optimizer reuses the same decision-analysis logic and ranks
  schedules by expected NMB.

## International Thresholds

| Country/Region | Threshold (USD/QALY) | Organization |
|----------------|----------------------|--------------|
| **UK** | $25,000 - $37,500 | NICE |
| **Canada** | $37,500 - $75,000 | CADTH |
| **US** | $50,000 - $150,000 | Common practice |
| **WHO** | 1-3× GDP per capita | WHO-CHOICE |

## Clinical Applications

- Type 2 diabetes treatment comparisons.
- Population screening trade-off exploration.
- Treatment-schedule optimization for high-cost therapies.
- Classroom or portfolio demonstrations of ICER/NMB/CEAC workflows.

## Sensitivity Analysis

The module supports probabilistic sensitivity analysis (PSA):

```python
wtp_thresholds = [25_000.0, 50_000.0, 100_000.0]
cea = cost_effectiveness_analysis(
    sim_results={"Metformin": sim_metformin, "GLP-1 Agonist": sim_glp1},
    comparator="Metformin",
    wtp_thresholds=wtp_thresholds,
)

print(cea["ceac"])
```

## Validation

The module is documented and tested against standard methodological concepts
used in published health-economics literature. It is strongest as an open,
inspectable implementation of common methods rather than as a submission-grade
economic model.

## Limitations

- **Simplified mortality modeling**: Constant hazard rates (not age-dependent)
- **Illustrative parameterization**: Example scenarios are educational and not calibrated to a specific clinical dataset
- **Independent distributions**: Costs and utilities assumed independent
- **No indirect costs**: Productivity losses not included
- **No adverse events**: Treatment side effects not modeled

See [Health Economics Evidence](../../research/health-economics-evidence.md) and
[Health Economics Methodology](../../research/health-economics-methodology.md)
for the public discussion of scope, structure, and limitations.

## See Also

- [Health Economics Tutorial](../../user-guide/health-economics-tutorial.md) - Step-by-step guide
- [Health Economics Evidence](../../research/health-economics-evidence.md) - Scope, intended use, and validation posture
- [Health Economics Methodology](../../research/health-economics-methodology.md) - Public methodology summary
- [Health Economics Demo Notebook](https://github.com/jerdaw/finbot/blob/main/notebooks/06_health_economics_demo.ipynb) - Interactive examples
