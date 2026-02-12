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
from finbot.services.health_economics.treatment_optimizer import optimize_treatment

__all__ = [
    "HealthIntervention",
    "cost_effectiveness_analysis",
    "optimize_treatment",
    "simulate_qalys",
]
