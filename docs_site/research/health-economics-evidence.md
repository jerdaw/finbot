# Health Economics Evidence

Finbot's health economics module is a research and teaching toolkit for
probabilistic cost-effectiveness analysis. It is designed to make common
health-economics workflows inspectable, reproducible, and easy to adapt for
coursework, exploratory analysis, and method familiarization.

!!! warning "Research and Education Use Only"

    Finbot is not a clinical decision-support system, a reimbursement
    submission package, or a substitute for formal health technology
    assessment. The models and scenarios in this repository are appropriate
    for research, teaching, and exploratory analysis. Real-world clinical or
    policy decisions require domain experts, empirical data, and jurisdiction-
    specific review.

## What This Module Covers

- **QALY simulation** using Monte Carlo sampling of costs, utility gains, and
  mortality reduction.
- **Cost-effectiveness analysis** using ICER, NMB, CEAC, and cost-
  effectiveness planes.
- **Treatment-schedule optimization** using grid search over treatment
  frequency and duration.
- **Illustrative clinical scenarios** that show how the same quantitative
  framework can be applied to questions relevant to healthcare funding and
  intervention design.

## Standards and Reference Points

The current implementation aligns its framing with widely used health-
economics reference points rather than inventing a novel evaluative standard.

- **WHO**: 3% discounting convention for costs and outcomes.
- **NICE (UK)**: reference-case style thinking around QALYs and
  cost-effectiveness thresholds.
- **CADTH (Canada)**: willingness-to-pay framing and population-level
  decision-analysis context.

This does **not** mean Finbot is an official NICE or CADTH model. It means the
toolkit uses recognizably standard concepts so readers can inspect, test, and
learn from an open implementation.

## What Evidence Claims Finbot Can Support

Finbot can support claims about:

- how a transparent Monte Carlo cost-effectiveness model is structured,
- how uncertainty propagates through QALY and cost outputs,
- how willingness-to-pay thresholds change interpretation,
- and how optimization or scenario design changes projected value.

Finbot cannot by itself support claims that:

- a real intervention is definitively cost-effective in practice,
- a policy body should reimburse a treatment,
- or a specific patient should receive a specific therapy.

Those stronger claims require empirical validation, calibrated data sources,
and domain review beyond the scope of this repository.

## Validation Status

The health-economics module is currently strongest as an open, reproducible
implementation of standard methods.

- The codebase includes a dedicated health-economics service layer and tests
  for simulation behavior, scenario outputs, and interface stability.
- The methodology and tutorial materials document assumptions explicitly.
- The public docs now expose the modeling approach, intended use, and key
  limitations in one place.

The current limitation is external validation depth. The repository contains
research-grade methodological documentation, but it is not presented as a
clinical-trial-validated economic model.

## Scope Boundaries

The current implementation deliberately leaves out several categories that
formal HTA work often needs:

- age-dependent or state-transition disease models,
- patient-level heterogeneity and subgroup-specific calibration,
- real-world adherence modeling,
- indirect costs, equity weighting, and distributional analysis,
- adverse-event modeling,
- and jurisdiction-specific reimbursement submission requirements.

These omissions are not hidden. They are part of the intended educational and
research framing of the project.

## Suggested Reading Path

If you want to understand the health-economics portion of Finbot quickly:

1. Read the [Health Economics Tutorial](../user-guide/health-economics-tutorial.md).
2. Review the [Health Economics Methodology](health-economics-methodology.md).
3. Explore the
   [Health Economics Demo Notebook](https://github.com/jerdaw/finbot/blob/main/notebooks/06_health_economics_demo.ipynb).
4. Review the repository's
   [Responsible Use Guidelines](https://github.com/jerdaw/finbot/blob/main/docs/ethics/responsible-use.md)
   and
   [Disclaimer](https://github.com/jerdaw/finbot/blob/main/DISCLAIMER.md).

## Why This Matters

The value of this module is not that it replaces formal health-economics work.
The value is that it makes the structure of that work visible. Readers can see
how QALY simulation, discounting, cost-effectiveness thresholds, and scenario
analysis fit together in an inspectable codebase rather than a black box.

That makes Finbot useful for:

- teaching and self-study,
- software portfolio review,
- research prototyping,
- and demonstrating evidence-oriented reasoning across finance and health.
