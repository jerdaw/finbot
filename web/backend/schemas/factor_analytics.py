"""Pydantic schemas for factor analytics endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class FactorRegressionRequest(BaseModel):
    """Request to run OLS factor regression on a ticker's returns."""

    ticker: str
    factor_data: list[dict[str, float]]
    factor_names: list[str]
    model_type: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class FactorRegressionResponse(BaseModel):
    """OLS factor regression result."""

    loadings: dict[str, float | None]
    alpha: float | None
    r_squared: float | None
    adj_r_squared: float | None
    residual_std: float | None
    t_stats: dict[str, float | None]
    p_values: dict[str, float | None]
    factor_names: list[str]
    model_type: str
    n_observations: int


class FactorAttributionResponse(BaseModel):
    """Factor-based return attribution result."""

    factor_contributions: dict[str, float | None]
    alpha_contribution: float | None
    total_return: float | None
    explained_return: float | None
    residual_return: float | None
    factor_names: list[str]
    n_observations: int


class FactorRiskResponse(BaseModel):
    """Factor-based risk decomposition result."""

    systematic_variance: float | None
    idiosyncratic_variance: float | None
    total_variance: float | None
    pct_systematic: float | None
    marginal_contributions: dict[str, float | None]
    factor_names: list[str]
    n_observations: int


class RollingRSquaredRequest(BaseModel):
    """Request to compute rolling R-squared for factor model fit."""

    ticker: str
    factor_data: list[dict[str, float]]
    factor_names: list[str]
    window: int = Field(default=63, ge=2)
    start_date: str | None = None
    end_date: str | None = None


class RollingRSquaredResponse(BaseModel):
    """Rolling R-squared time series result."""

    values: list[float | None]
    dates: list[str]
