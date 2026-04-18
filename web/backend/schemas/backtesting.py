"""Pydantic schemas for backtesting endpoints."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from finbot.core.contracts.missing_data import DEFAULT_MISSING_DATA_POLICY, MissingDataPolicy
from web.backend.schemas.portfolio_analytics import RollingMetricsResponse

CommissionMode = Literal["none", "per_share", "percentage"]


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


class BacktestCostAssumptions(BaseModel):
    """User-configurable execution friction assumptions for a web backtest."""

    commission_mode: CommissionMode = "none"
    commission_per_share: float = Field(default=0.0, ge=0.0)
    commission_bps: float = Field(default=0.0, ge=0.0)
    commission_minimum: float = Field(default=0.0, ge=0.0)
    spread_bps: float = Field(default=0.0, ge=0.0)
    slippage_bps: float = Field(default=0.0, ge=0.0)


class AppliedBacktestCostAssumptions(BacktestCostAssumptions):
    """Resolved cost assumptions returned alongside a run result."""

    commission_label: str
    spread_label: str
    slippage_label: str
    estimated_only: bool = True


class BacktestCostEventRecord(BaseModel):
    """A single estimated trading-cost event derived from an executed trade."""

    timestamp: str
    ticker: str
    cost_type: Literal["commission", "spread", "slippage", "borrow", "market_impact"]
    amount: float
    basis: str


class BacktestCostSummary(BaseModel):
    """Estimated trade-cost totals for the completed backtest."""

    total_commission: float = 0.0
    total_spread: float = 0.0
    total_slippage: float = 0.0
    total_costs: float = 0.0
    costs_by_symbol: dict[str, float] = Field(default_factory=dict)
    cost_events: list[BacktestCostEventRecord] = Field(default_factory=list)


class MissingDataTickerSummary(BaseModel):
    """Per-ticker summary of detected gaps before applying the chosen policy."""

    ticker: str
    rows_before: int
    rows_after: int
    rows_dropped: int
    missing_rows: int
    missing_cells: int
    remaining_missing_cells: int
    had_missing_data: bool


class BacktestMissingDataSummary(BaseModel):
    """Summary of how missing data was handled for this run."""

    policy: MissingDataPolicy = DEFAULT_MISSING_DATA_POLICY
    total_missing_rows: int = 0
    total_missing_cells: int = 0
    remaining_missing_cells: int = 0
    note: str | None = None
    tickers: list[MissingDataTickerSummary] = Field(default_factory=list)


class WalkForwardHandoff(BaseModel):
    """Prefilled walk-forward configuration derived from a completed backtest."""

    tickers: list[str] = Field(min_length=1)
    strategy: str
    strategy_params: dict[str, Any] = Field(default_factory=dict)
    start_date: str
    end_date: str
    initial_cash: float
    train_window: int
    test_window: int
    step_size: int
    anchored: bool = False
    include_train: bool = False
    reason: str


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
    recurring_cashflows: list[RecurringCashflowRule] = Field(default_factory=list)
    one_time_cashflows: list[OneTimeCashflowEvent] = Field(default_factory=list)
    inflation_rate: float = 0.0
    missing_data_policy: MissingDataPolicy = DEFAULT_MISSING_DATA_POLICY
    cost_assumptions: BacktestCostAssumptions = Field(default_factory=BacktestCostAssumptions)


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
    applied_cost_assumptions: AppliedBacktestCostAssumptions
    cost_summary: BacktestCostSummary | None = None
    missing_data_summary: BacktestMissingDataSummary
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
    walk_forward_request: WalkForwardHandoff | None = None
