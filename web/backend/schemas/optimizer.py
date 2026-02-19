"""Pydantic schemas for DCA optimizer endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DCAOptimizerRequest(BaseModel):
    """Request to run the DCA optimizer."""

    ticker: str
    ratio_range: list[float] = Field(default=[1, 1.5, 2, 3, 5, 10])
    dca_durations: list[int] = Field(default=[1, 5, 21, 63, 126, 252, 504, 756])
    dca_steps: list[int] = Field(default=[1, 5, 10, 21, 63])
    trial_durations: list[int] = Field(default=[756, 1260])
    starting_cash: float = 1000.0
    start_step: int = 5


class DCAOptimizerResponse(BaseModel):
    """Response from DCA optimizer."""

    by_ratio: list[dict[str, object]]
    by_duration: list[dict[str, object]]
    raw_results: list[dict[str, object]]
