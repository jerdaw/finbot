"""Pydantic schemas for Monte Carlo endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class MonteCarloRequest(BaseModel):
    """Request to run a Monte Carlo simulation."""

    ticker: str
    sim_periods: int = Field(default=252, ge=1, le=2520)
    n_sims: int = Field(default=1000, ge=100, le=10000)
    start_price: float | None = None


class PercentileBand(BaseModel):
    """A single percentile band across time."""

    label: str
    values: list[float | None]


class MonteCarloResponse(BaseModel):
    """Response from Monte Carlo simulation."""

    periods: list[int]
    bands: list[PercentileBand]
    sample_paths: list[list[float | None]]
    statistics: dict[str, float | None]
