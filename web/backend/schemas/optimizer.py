"""Pydantic schemas for optimizer endpoints."""

from __future__ import annotations

from typing import Any

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


class ParetoOptimizerRequest(BaseModel):
    """Request to evaluate a strategy sweep on a Pareto front."""

    tickers: list[str] = Field(min_length=1)
    strategies: list[str] = Field(
        default_factory=lambda: [
            "NoRebalance",
            "Rebalance",
            "SMACrossover",
            "RiskParity",
            "DualMomentum",
        ]
    )
    start_date: str | None = None
    end_date: str | None = None
    initial_cash: float = 10000.0
    objective_a: str = "cagr"
    objective_b: str = "max_drawdown"
    maximize_a: bool = True
    maximize_b: bool = False


class ParetoPointResponse(BaseModel):
    """A single evaluated point in the strategy Pareto sweep."""

    strategy_name: str
    tickers_used: list[str]
    params: dict[str, Any]
    metrics: dict[str, float | None]
    objective_a: float
    objective_b: float
    is_pareto_optimal: bool


class ParetoOptimizerResponse(BaseModel):
    """Response from the strategy Pareto optimizer endpoint."""

    objective_a_name: str
    objective_b_name: str
    n_evaluated: int
    all_points: list[ParetoPointResponse]
    pareto_front: list[ParetoPointResponse]
    dominated_points: list[ParetoPointResponse]
    warnings: list[str] = Field(default_factory=list)


class EfficientFrontierRequest(BaseModel):
    """Request to compute an efficient frontier from historical assets."""

    tickers: list[str] = Field(min_length=2)
    start_date: str | None = None
    end_date: str | None = None
    risk_free_rate: float = Field(default=0.04, ge=0.0, le=1.0)
    n_portfolios: int = Field(default=2500, ge=100, le=10000)


class EfficientFrontierPortfolioResponse(BaseModel):
    """A sampled or highlighted portfolio on the efficient frontier surface."""

    expected_return: float
    volatility: float
    sharpe_ratio: float
    weights: dict[str, float]


class EfficientFrontierAssetStatResponse(BaseModel):
    """Historical summary for an asset in the frontier analysis."""

    ticker: str
    annual_return: float
    annual_volatility: float


class EfficientFrontierResponse(BaseModel):
    """Response from the efficient frontier endpoint."""

    portfolios: list[EfficientFrontierPortfolioResponse]
    frontier: list[EfficientFrontierPortfolioResponse]
    max_sharpe: EfficientFrontierPortfolioResponse
    min_volatility: EfficientFrontierPortfolioResponse
    asset_stats: list[EfficientFrontierAssetStatResponse]
    correlation_matrix: dict[str, dict[str, float]]
