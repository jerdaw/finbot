"""ScenarioResult dataclass for clinical health economics scenarios."""

from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class ScenarioResult:
    """Results from a clinical health economics scenario analysis.

    Attributes:
        scenario_name: Human-readable scenario name.
        description: Brief description of the clinical scenario.
        intervention_name: Name of the intervention arm.
        comparator_name: Name of the comparator arm.
        icer: Incremental cost-effectiveness ratio ($/QALY gained).
            None if the intervention is dominated (more costly, fewer QALYs)
            or dominant (lower cost, more QALYs — always adopt).
        nmb: Net monetary benefit at the base WTP threshold.
        is_cost_effective: True if NMB > 0 at the base WTP threshold.
        qaly_gain: Mean QALYs gained by the intervention vs the comparator.
        cost_difference: Mean cost difference (intervention minus comparator).
        n_simulations: Number of Monte Carlo simulations run.
        summary_stats: Additional metrics as a dict of name → float.
    """

    scenario_name: str
    description: str
    intervention_name: str
    comparator_name: str
    icer: float | None
    nmb: float
    is_cost_effective: bool
    qaly_gain: float
    cost_difference: float
    n_simulations: int
    summary_stats: dict[str, float]
