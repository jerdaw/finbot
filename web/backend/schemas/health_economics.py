"""Pydantic schemas for health economics endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class InterventionInput(BaseModel):
    """Input for a health intervention."""

    name: str
    cost_per_year: float = 0.0
    cost_std: float = 0.0
    utility_gain: float = 0.0
    utility_gain_std: float = 0.0
    mortality_reduction: float = 0.0
    mortality_reduction_std: float = 0.0


class QALYRequest(BaseModel):
    """Request to run QALY simulation."""

    intervention: InterventionInput
    baseline_utility: float = 0.7
    baseline_mortality: float = 0.02
    time_horizon: int = Field(default=10, ge=1, le=50)
    n_sims: int = Field(default=10000, ge=100, le=50000)
    discount_rate: float = 0.03
    seed: int | None = None


class QALYResponse(BaseModel):
    """Response from QALY simulation."""

    mean_cost: float
    mean_qaly: float
    cost_percentiles: dict[str, float]
    qaly_percentiles: dict[str, float]
    survival_curve: list[float]
    annual_cost_means: list[float]
    annual_qaly_means: list[float]


class CEARequest(BaseModel):
    """Request to run cost-effectiveness analysis."""

    interventions: list[QALYRequest] = Field(min_length=2)
    comparator: str
    wtp_thresholds: list[float] | None = None


class CEAResponse(BaseModel):
    """Response from cost-effectiveness analysis."""

    icer_table: list[dict[str, Any]]
    ceac: list[dict[str, Any]]
    ce_plane: dict[str, list[dict[str, float | None]]]
    nmb: list[dict[str, Any]]
    summary: list[dict[str, Any]]


class TreatmentOptimizerRequest(BaseModel):
    """Request to run treatment optimizer."""

    cost_per_dose: float
    cost_per_dose_std: float = 0.0
    qaly_gain_per_dose: float = 0.02
    qaly_gain_per_dose_std: float = 0.0
    frequencies: list[int] | None = None
    durations: list[int] | None = None
    baseline_utility: float = 0.7
    baseline_mortality: float = 0.02
    mortality_reduction_per_dose: float = 0.0
    discount_rate: float = 0.03
    wtp_threshold: float = 50000.0
    n_sims: int = Field(default=5000, ge=100, le=50000)
    seed: int | None = None


class TreatmentOptimizerResponse(BaseModel):
    """Response from treatment optimizer."""

    results: list[dict[str, Any]]
    best_schedule: dict[str, Any]


class ScenarioRequest(BaseModel):
    """Request to run a clinical scenario."""

    scenario: str  # "cancer_screening", "hypertension", "vaccine"
    n_sims: int = Field(default=10000, ge=100, le=50000)
    seed: int = 42
    wtp_threshold: float = 100000.0


class ScenarioResponse(BaseModel):
    """Response from a clinical scenario."""

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
