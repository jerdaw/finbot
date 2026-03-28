"""Pydantic schemas for portfolio analytics endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RollingMetricsRequest(BaseModel):
    """Request to compute rolling performance metrics."""

    ticker: str
    benchmark_ticker: str | None = None
    window: int = 63
    risk_free_rate: float = 0.04
    start_date: str | None = None
    end_date: str | None = None


class RollingMetricsResponse(BaseModel):
    """Response from rolling metrics computation."""

    window: int
    n_obs: int
    sharpe: list[float | None]
    volatility: list[float | None]
    beta: list[float | None] | None
    dates: list[str]
    mean_sharpe: float | None = None
    mean_vol: float | None = None
    mean_beta: float | None = None


class BenchmarkRequest(BaseModel):
    """Request to compute benchmark comparison statistics."""

    portfolio_ticker: str
    benchmark_ticker: str
    risk_free_rate: float = 0.04
    start_date: str | None = None
    end_date: str | None = None


class BenchmarkResponse(BaseModel):
    """Response from benchmark comparison computation."""

    alpha: float
    beta: float
    r_squared: float
    tracking_error: float
    information_ratio: float
    up_capture: float
    down_capture: float
    benchmark_name: str
    n_observations: int


class DrawdownRequest(BaseModel):
    """Request to compute drawdown analysis."""

    ticker: str
    top_n: int = 5
    start_date: str | None = None
    end_date: str | None = None


class DrawdownPeriodSchema(BaseModel):
    """A single drawdown episode."""

    start_idx: int
    trough_idx: int
    end_idx: int | None = None
    depth: float
    duration_bars: int
    recovery_bars: int | None = None


class DrawdownResponse(BaseModel):
    """Response from drawdown analysis."""

    periods: list[DrawdownPeriodSchema]
    underwater_curve: list[float]
    n_periods: int
    max_depth: float
    avg_depth: float
    avg_duration_bars: float
    avg_recovery_bars: float | None = None
    current_drawdown: float
    n_observations: int


class CorrelationRequest(BaseModel):
    """Request to compute correlation and diversification metrics."""

    tickers: list[str] = Field(min_length=2)
    weights: dict[str, float] | None = None
    start_date: str | None = None
    end_date: str | None = None


class CorrelationResponse(BaseModel):
    """Response from correlation/diversification computation."""

    n_assets: int
    weights: dict[str, float]
    herfindahl_index: float
    effective_n: float
    diversification_ratio: float
    avg_pairwise_correlation: float
    correlation_matrix: dict[str, dict[str, float]]
    individual_vols: dict[str, float]
    portfolio_vol: float
    n_observations: int
