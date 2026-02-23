"""Pydantic schemas for experiment tracking endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ExperimentSummary(BaseModel):
    """Summary of a single experiment run."""

    run_id: str
    engine_name: str
    strategy_name: str
    created_at: str
    config_hash: str


class ExperimentCompareRequest(BaseModel):
    """Request to compare experiments."""

    run_ids: list[str]


class ExperimentCompareResponse(BaseModel):
    """Response from experiment comparison."""

    assumptions: list[dict[str, Any]]
    metrics: list[dict[str, Any]]
