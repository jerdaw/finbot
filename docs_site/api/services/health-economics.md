# Health Economics

The health economics module provides tools for quality-adjusted life year (QALY) simulation, cost-effectiveness analysis, and treatment schedule optimization.

## Overview

The health economics module supports:

- **QALY Simulation**: Monte Carlo simulation with stochastic costs, utilities, and mortality
- **Cost-Effectiveness Analysis**: ICER, NMB, CEAC, cost-effectiveness planes
- **Treatment Optimization**: Grid-search optimization across treatment schedules
- **Compliance with Standards**: NICE, CADTH, WHO willingness-to-pay thresholds

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
from finbot.services.health_economics.qaly_simulator import QALYSimulator
import numpy as np

# Define treatment parameters
treatment_params = {
    'cost_per_year': 5000,
    'cost_std': 500,
    'utility_per_year': 0.85,
    'utility_std': 0.05,
    'mortality_rate': 0.02,
    'duration_years': 10
}

control_params = {
    'cost_per_year': 1000,
    'cost_std': 100,
    'utility_per_year': 0.70,
    'utility_std': 0.05,
    'mortality_rate': 0.03,
    'duration_years': 10
}

# Run simulation
simulator = QALYSimulator()
treatment_results = simulator.simulate(treatment_params, n_simulations=10000)
control_results = simulator.simulate(control_params, n_simulations=10000)

print(f"Treatment QALYs: {treatment_results['qalys'].mean():.2f}")
print(f"Treatment Cost: ${treatment_results['costs'].mean():,.0f}")
```

### Cost-Effectiveness Analysis Example

```python
from finbot.services.health_economics.cost_effectiveness import (
    calculate_icer,
    calculate_nmb,
    calculate_ceac
)

# Calculate ICER
icer = calculate_icer(
    cost_treatment=treatment_results['costs'],
    cost_control=control_results['costs'],
    qaly_treatment=treatment_results['qalys'],
    qaly_control=control_results['qalys']
)
print(f"ICER: ${icer:,.0f} per QALY")

# Calculate NMB at NICE threshold (£20,000/QALY ≈ $25,000 USD)
nmb = calculate_nmb(
    cost_treatment=treatment_results['costs'],
    qaly_treatment=treatment_results['qalys'],
    cost_control=control_results['costs'],
    qaly_control=control_results['qalys'],
    wtp_threshold=25000
)
print(f"Net Monetary Benefit: ${nmb.mean():,.0f}")

# Calculate CEAC across thresholds
thresholds = np.linspace(0, 100000, 100)
ceac = calculate_ceac(
    cost_treatment=treatment_results['costs'],
    qaly_treatment=treatment_results['qalys'],
    cost_control=control_results['costs'],
    qaly_control=control_results['qalys'],
    wtp_thresholds=thresholds
)
```

### Treatment Optimization Example

```python
from finbot.services.health_economics.treatment_optimizer import optimize_treatment_schedule

# Optimize treatment dose frequency and duration
best_schedule = optimize_treatment_schedule(
    dose_frequencies=[1, 2, 4],  # doses per week
    durations=[6, 12, 24],  # months
    cost_per_dose=100,
    utility_improvement_per_dose=0.01,
    wtp_threshold=50000
)

print(f"Optimal frequency: {best_schedule['frequency']} doses/week")
print(f"Optimal duration: {best_schedule['duration']} months")
print(f"Expected NMB: ${best_schedule['nmb']:,.0f}")
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

**Interpretation:**
- **ICER < $50,000/QALY**: Highly cost-effective (US standard)
- **ICER < $100,000/QALY**: Cost-effective
- **ICER < $150,000/QALY**: Possibly cost-effective (varies by condition)

### Net Monetary Benefit (NMB)

Converts health outcomes to monetary terms:

```
NMB = (QALY_treatment - QALY_control) × WTP - (Cost_treatment - Cost_control)
```

**Interpretation:**
- **NMB > 0**: Treatment is cost-effective at the given WTP threshold
- **NMB < 0**: Treatment is not cost-effective

### Cost-Effectiveness Acceptability Curve (CEAC)

Shows probability that treatment is cost-effective across different willingness-to-pay thresholds.

## International Thresholds

| Country/Region | Threshold (USD/QALY) | Organization |
|----------------|----------------------|--------------|
| **UK** | $25,000 - $37,500 | NICE |
| **Canada** | $37,500 - $75,000 | CADTH |
| **US** | $50,000 - $150,000 | Common practice |
| **WHO** | 1-3× GDP per capita | WHO-CHOICE |

## Clinical Applications

### Type 2 Diabetes Management

Compare metformin vs. GLP-1 agonists:

```python
# Metformin (control)
metformin = {
    'cost_per_year': 500,
    'utility_per_year': 0.75,
    'mortality_rate': 0.025
}

# GLP-1 agonist (treatment)
glp1 = {
    'cost_per_year': 5000,
    'utility_per_year': 0.80,
    'mortality_rate': 0.020
}
```

### Hypertension Treatment

Compare standard vs. intensive blood pressure control:

```python
# Standard control
standard_bp = {
    'cost_per_year': 800,
    'utility_per_year': 0.82,
    'mortality_rate': 0.018
}

# Intensive control
intensive_bp = {
    'cost_per_year': 2000,
    'utility_per_year': 0.85,
    'mortality_rate': 0.014
}
```

## Sensitivity Analysis

The module supports probabilistic sensitivity analysis (PSA):

```python
# Vary parameters across distributions
results = []
for _ in range(1000):
    cost_multiplier = np.random.uniform(0.8, 1.2)
    utility_bonus = np.random.uniform(0.03, 0.07)

    params = {
        'cost_per_year': 5000 * cost_multiplier,
        'utility_per_year': 0.75 + utility_bonus,
        'mortality_rate': 0.02
    }

    sim_result = simulator.simulate(params, n_simulations=1000)
    results.append(sim_result)
```

## Validation

The module has been validated against:
- Published health economics literature
- WHO-CHOICE methodology guidelines
- NICE technology appraisal guidance

## Limitations

- **Simplified mortality modeling**: Constant hazard rates (not age-dependent)
- **No discounting**: Future costs/QALYs not discounted to present value
- **Independent distributions**: Costs and utilities assumed independent
- **No indirect costs**: Productivity losses not included
- **No adverse events**: Treatment side effects not modeled

See [Health Economics Methodology](../../research/health-economics-methodology.md) for detailed discussion.

## See Also

- [Health Economics Tutorial](../../user-guide/health-economics-tutorial.md) - Step-by-step guide
- [Health Economics Methodology](../../research/health-economics-methodology.md) - Research documentation
- [Example Notebook 06](../../examples/06-health-economics.ipynb) - Interactive examples
