"""Pydantic schemas for simulation endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


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


class BondLadderRequest(BaseModel):
    """Request to run the bond ladder research view."""

    min_maturity_years: int = Field(default=1, ge=1, le=30)
    max_maturity_years: int = Field(default=10, ge=1, le=30)
    compare_tickers: list[str] = Field(default_factory=lambda: ["SHY", "IEF", "TLT"])
    normalize: bool = True


class BondLadderMetric(BaseModel):
    """Performance summary row for a bond ladder comparison series."""

    ticker: str
    name: str
    start_value: float | None = None
    end_value: float | None = None
    total_return: float | None = None
    cagr: float | None = None
    volatility: float | None = None
    max_drawdown: float | None = None


class BondLadderResponse(BaseModel):
    """Response from the bond ladder research endpoint."""

    series: list[TimeSeries]
    metrics: list[BondLadderMetric]
