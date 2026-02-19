"""Health economics analysis tools.

Provides Monte Carlo simulation, cost-effectiveness analysis, and
treatment schedule optimization for health interventions.  Adapts
finbot's financial analysis framework to health economics contexts.
"""

from finbot.services.health_economics.cost_effectiveness import (
    cost_effectiveness_analysis,
)
from finbot.services.health_economics.qaly_simulator import (
    HealthIntervention,
    simulate_qalys,
)
from finbot.services.health_economics.scenarios.cancer_screening import (
    run_cancer_screening_scenario,
)
from finbot.services.health_economics.scenarios.hypertension import (
    run_hypertension_scenario,
)
from finbot.services.health_economics.scenarios.models import ScenarioResult
from finbot.services.health_economics.scenarios.vaccine import run_vaccine_scenario
from finbot.services.health_economics.treatment_optimizer import optimize_treatment

__all__ = [
    "HealthIntervention",
    "ScenarioResult",
    "cost_effectiveness_analysis",
    "optimize_treatment",
    "run_cancer_screening_scenario",
    "run_hypertension_scenario",
    "run_vaccine_scenario",
    "simulate_qalys",
]
