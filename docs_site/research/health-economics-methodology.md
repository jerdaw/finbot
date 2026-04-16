# Health Economics Methodology

This page summarizes the modeling approach behind Finbot's health-economics
tooling. It is a public-facing companion to the deeper repository research
notes and focuses on the main equations, design choices, and scope boundaries
that shape the implementation.

## Core Workflow

Finbot's health-economics pipeline follows a simple progression:

1. Define a `HealthIntervention` with cost, utility-gain, and mortality-
   reduction assumptions.
2. Run `simulate_qalys()` to generate Monte Carlo distributions of discounted
   costs and QALYs.
3. Compare interventions with `cost_effectiveness_analysis()`.
4. Explore treatment frequency and duration with `optimize_treatment()`.

## Key Equations

### Quality-Adjusted Life Years

$$
QALY = utility \times time
$$

QALYs combine survival duration with a quality-of-life weight on a $0$ to $1$
scale.

### Discounting

$$
PV = \frac{FV}{(1 + r)^t}
$$

Finbot applies annual discounting to both costs and outcomes. The default
discount rate is $3\%$, which is consistent with commonly cited WHO and NICE-
style reference cases.

### Incremental Cost-Effectiveness Ratio

$$
ICER = \frac{Cost_{intervention} - Cost_{comparator}}{QALY_{intervention} - QALY_{comparator}}
$$

### Net Monetary Benefit

$$
NMB = WTP \times \Delta QALY - \Delta Cost
$$

### Cost-Effectiveness Acceptability Curve

$$
CEAC(WTP) = P(NMB > 0 \mid WTP)
$$

## Implementation Choices

The current implementation uses annual-cycle Monte Carlo simulation with the
following choices:

- stochastic annual costs,
- stochastic annual utility gains,
- stochastic annual mortality reduction,
- clipped utility and mortality values to preserve valid ranges,
- cumulative survival curves,
- discounted annual costs and QALYs,
- and summary outputs suitable for downstream ICER, NMB, CEAC, and cost-
  effectiveness-plane analysis.

Treatment optimization reuses the same overall logic but searches across dose
frequency and treatment duration to rank schedules by net monetary benefit.

## Standards Alignment

Finbot intentionally uses recognizable health-economics conventions rather than
custom metrics:

- **WHO-style discounting reference point**: default $3\%$ annual discounting.
- **NICE/CADTH-style framing**: use of QALYs, ICER, NMB, and threshold-based
  interpretation.
- **Probabilistic sensitivity analysis mindset**: uncertainty represented as a
  distribution, not just a single deterministic point estimate.

## Current Limitations

This methodology is intentionally simpler than a formal HTA submission model.
Important omissions include:

- Markov state-transition disease progression,
- patient-level heterogeneity,
- real-world adherence and switching behavior,
- indirect cost and equity analysis,
- adverse-event modeling,
- and submission-grade calibration against empirical trial datasets.

These limits do not invalidate the tool's educational and research value. They
define what kinds of claims the repository can responsibly support.

## Further Reading

- [Health Economics Evidence](health-economics-evidence.md)
- [Health Economics Tutorial](../user-guide/health-economics-tutorial.md)
- [Full repository research note](https://github.com/jerdaw/finbot/blob/main/docs/research/health-economics-methodology.md)
- [Health Economics Demo Notebook](https://github.com/jerdaw/finbot/blob/main/notebooks/06_health_economics_demo.ipynb)

## Reference Points

The implementation and documentation are informed by standard references such
as:

- Drummond et al., *Methods for the Economic Evaluation of Health Care
  Programmes*
- Briggs, Claxton, and Sculpher, *Decision Modelling for Health Economic
  Evaluation*
- NICE methods guidance
- CADTH economic evaluation guidelines
- WHO CHOICE reference materials

For the extended discussion, equations, and broader bibliography, use the full
repository research note linked above.