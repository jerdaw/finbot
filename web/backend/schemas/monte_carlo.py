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


class MultiAssetMonteCarloRequest(BaseModel):
    """Request to run a correlated multi-asset Monte Carlo simulation."""

    tickers: list[str] = Field(min_length=2)
    weights: list[float] | None = None
    sim_periods: int = Field(default=252, ge=1, le=2520)
    n_sims: int = Field(default=1000, ge=100, le=10000)
    start_value: float = Field(default=10000.0, gt=0)


class MultiAssetWeight(BaseModel):
    """Normalized portfolio weight for a multi-asset simulation."""

    ticker: str
    weight: float


class MultiAssetAssetStat(BaseModel):
    """Historical asset statistics surfaced alongside the portfolio simulation."""

    ticker: str
    weight: float
    annual_return: float | None = None
    annual_volatility: float | None = None


class MultiAssetMonteCarloResponse(BaseModel):
    """Response from a multi-asset Monte Carlo simulation."""

    periods: list[int]
    portfolio_bands: list[PercentileBand]
    portfolio_sample_paths: list[list[float | None]]
    portfolio_statistics: dict[str, float | None]
    weights: list[MultiAssetWeight]
    asset_statistics: list[MultiAssetAssetStat]
    correlation_matrix: dict[str, dict[str, float]]
