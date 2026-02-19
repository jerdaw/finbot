"""Pydantic schemas for simulation endpoints."""

from pydantic import BaseModel


class TimeSeries(BaseModel):
    """Time-series data with dates and values."""

    name: str
    dates: list[str]
    values: list[float | None]


class FundInfo(BaseModel):
    """Metadata about a simulable fund."""

    ticker: str
    name: str
    leverage: float
    annual_er_pct: float


class SimulationResponse(BaseModel):
    """Response for fund simulation."""

    series: list[TimeSeries]
    metrics: list[dict[str, object]]
