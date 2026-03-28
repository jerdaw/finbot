"""Pydantic schemas for risk analytics endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class VaRRequest(BaseModel):
    """Request to compute Value at Risk across all methods."""

    ticker: str
    confidence: float = Field(default=0.95, gt=0, lt=1)
    horizon_days: int = Field(default=1, ge=1)
    portfolio_value: float | None = None
    start_date: str | None = None
    end_date: str | None = None


class VaRResultSchema(BaseModel):
    """Single VaR computation result."""

    var_: float = Field(alias="var")
    confidence: float
    method: str
    horizon_days: int
    n_observations: int
    var_dollars: float | None = None

    model_config = {"populate_by_name": True}


class CVaRResultSchema(BaseModel):
    """Conditional VaR (Expected Shortfall) result."""

    cvar: float
    var_: float = Field(alias="var")
    confidence: float
    method: str
    n_tail_obs: int
    n_observations: int

    model_config = {"populate_by_name": True}


class VaRResponse(BaseModel):
    """Response from VaR endpoint with all three methods plus CVaR."""

    historical: VaRResultSchema
    parametric: VaRResultSchema
    montecarlo: VaRResultSchema
    cvar: CVaRResultSchema


class StressTestRequest(BaseModel):
    """Request to run stress tests against one or more scenarios."""

    ticker: str
    scenarios: list[str] = Field(
        default_factory=lambda: [
            "2008_financial_crisis",
            "covid_crash_2020",
            "dot_com_bubble",
            "black_monday_1987",
        ],
    )
    initial_value: float = 100000.0
    start_date: str | None = None
    end_date: str | None = None


class StressTestResultSchema(BaseModel):
    """Result of a single stress scenario application."""

    scenario_name: str
    initial_value: float
    trough_value: float
    trough_return: float
    max_drawdown_pct: float
    shock_duration_days: int
    recovery_days: int
    price_path: list[float]


class StressTestResponse(BaseModel):
    """Response from stress test endpoint."""

    results: list[StressTestResultSchema]


class KellyRequest(BaseModel):
    """Request to compute Kelly criterion for a single asset."""

    ticker: str
    start_date: str | None = None
    end_date: str | None = None


class KellyResponse(BaseModel):
    """Response from single-asset Kelly criterion computation."""

    full_kelly: float
    half_kelly: float
    quarter_kelly: float
    win_rate: float
    win_loss_ratio: float
    expected_value: float
    is_positive_ev: bool
    n_observations: int


class MultiKellyRequest(BaseModel):
    """Request to compute multi-asset Kelly weights."""

    tickers: list[str] = Field(min_length=2)
    start_date: str | None = None
    end_date: str | None = None


class MultiKellyResponse(BaseModel):
    """Response from multi-asset Kelly criterion computation."""

    weights: dict[str, float]
    full_kelly_weights: dict[str, float]
    half_kelly_weights: dict[str, float]
    correlation_matrix: dict[str, dict[str, float]]
    asset_results: dict[str, KellyResponse]
    n_assets: int
    n_observations: int


class VaRBacktestRequest(BaseModel):
    """Request to run a VaR model backtest (violation analysis)."""

    ticker: str
    confidence: float = Field(default=0.95, gt=0, lt=1)
    method: str = "historical"
    start_date: str | None = None
    end_date: str | None = None


class VaRBacktestResponse(BaseModel):
    """Response from VaR backtest (violation analysis)."""

    confidence: float
    method: str
    n_observations: int
    n_violations: int
    violation_rate: float
    expected_violation_rate: float
    is_calibrated: bool
