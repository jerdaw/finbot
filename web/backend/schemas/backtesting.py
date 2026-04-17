"""Pydantic schemas for backtesting endpoints."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from web.backend.schemas.portfolio_analytics import RollingMetricsResponse


class StrategyParam(BaseModel):
    """Definition of a strategy parameter."""

    name: str
    type: str  # "int", "float", "tuple"
    default: Any
    min: float | None = None
    description: str = ""


class StrategyInfo(BaseModel):
    """Metadata about a backtesting strategy."""

    name: str
    description: str
    params: list[StrategyParam]
    min_assets: int = 1


class BacktestRequest(BaseModel):
    """Request to run a backtest."""

    tickers: list[str] = Field(min_length=1)
    strategy: str
    strategy_params: dict[str, Any] = Field(default_factory=dict)
    start_date: str | None = None
    end_date: str | None = None
    initial_cash: float = 10000.0
    benchmark_ticker: str | None = None
    risk_free_rate: float = 0.04
    recurring_cashflows: list["RecurringCashflowRule"] = Field(default_factory=list)
    one_time_cashflows: list["OneTimeCashflowEvent"] = Field(default_factory=list)
    inflation_rate: float = 0.0


class RecurringCashflowRule(BaseModel):
    """A recurring portfolio-level cashflow rule."""

    amount: float
    frequency: Literal["monthly", "quarterly", "yearly"]
    start_date: str | None = None
    end_date: str | None = None
    label: str | None = None


class OneTimeCashflowEvent(BaseModel):
    """A single dated contribution or withdrawal."""

    date: str
    amount: float
    label: str | None = None


class TradeRecord(BaseModel):
    """A single trade from a backtest."""

    date: str
    ticker: str
    action: str
    size: float
    price: float
    value: float


class BacktestBenchmarkStats(BaseModel):
    """Benchmark-relative statistics for a completed backtest."""

    alpha: float | None = None
    beta: float | None = None
    r_squared: float | None = None
    tracking_error: float | None = None
    information_ratio: float | None = None
    up_capture: float | None = None
    down_capture: float | None = None
    benchmark_name: str
    n_observations: int


class ReturnTableRow(BaseModel):
    """A single period return row for one-run inspection tables."""

    period: str
    start_value: float | None = None
    end_value: float | None = None
    return_pct: float | None = None


class BacktestRegimeSummary(BaseModel):
    """Aggregated portfolio behavior under a detected market regime."""

    regime: str
    count_periods: int
    total_days: int
    cagr: float | None = None
    volatility: float | None = None
    sharpe: float | None = None
    total_return: float | None = None


class BacktestRegimePeriod(BaseModel):
    """A single detected market regime period with portfolio context."""

    regime: str
    start: str
    end: str
    days: int
    market_return: float | None = None
    market_volatility: float | None = None
    portfolio_return: float | None = None
    portfolio_volatility: float | None = None


class CashflowEventRecord(BaseModel):
    """A scheduled cashflow applied during the backtest."""

    scheduled_date: str
    applied_date: str
    label: str
    source: Literal["recurring", "one_time"]
    direction: Literal["contribution", "withdrawal"]
    amount: float
    cash_after: float | None = None
    portfolio_value_after: float | None = None


class WithdrawalDurabilitySummary(BaseModel):
    """Single-path durability summary for a withdrawal plan."""

    survived_to_end: bool
    depletion_date: str | None = None
    ending_nominal_value: float | None = None
    ending_real_value: float | None = None
    min_nominal_value: float | None = None
    min_real_value: float | None = None
    total_contributions: float = 0.0
    total_withdrawals: float = 0.0
    net_cashflow: float = 0.0
    real_total_return: float | None = None
    inflation_rate: float = 0.0


class RebalanceEventRecord(BaseModel):
    """Grouped execution log to expose rebalance-like portfolio changes."""

    date: str
    event_type: Literal["initial_allocation", "rebalance", "trade"]
    trade_count: int
    symbols: list[str]
    gross_trade_value: float | None = None
    net_trade_value: float | None = None
    portfolio_value: float | None = None
    cash_after: float | None = None


class BacktestResponse(BaseModel):
    """Response from a backtest run."""

    stats: dict[str, Any]
    value_history: list[dict[str, Any]]
    trades: list[TradeRecord]
    benchmark_stats: BacktestBenchmarkStats | None = None
    benchmark_value_history: list[dict[str, Any]] = Field(default_factory=list)
    rolling_metrics: RollingMetricsResponse | None = None
    regime_reference_ticker: str | None = None
    regime_summary: list[BacktestRegimeSummary] = Field(default_factory=list)
    regime_periods: list[BacktestRegimePeriod] = Field(default_factory=list)
    cashflow_events: list[CashflowEventRecord] = Field(default_factory=list)
    real_value_history: list[dict[str, Any]] = Field(default_factory=list)
    withdrawal_durability: WithdrawalDurabilitySummary | None = None
    allocation_history: list[dict[str, Any]] = Field(default_factory=list)
    rebalance_events: list[RebalanceEventRecord] = Field(default_factory=list)
    monthly_returns: list[ReturnTableRow] = Field(default_factory=list)
    annual_returns: list[ReturnTableRow] = Field(default_factory=list)
