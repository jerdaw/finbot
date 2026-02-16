"""Typed contracts for engine-agnostic backtesting and execution."""

from finbot.core.contracts.costs import CostEvent, CostModel, CostSummary, CostType
from finbot.core.contracts.interfaces import BacktestEngine, ExecutionSimulator, MarketDataProvider, PortfolioStateStore
from finbot.core.contracts.models import (
    BacktestRunMetadata,
    BacktestRunRequest,
    BacktestRunResult,
    BarEvent,
    FillEvent,
    OrderRequest,
    OrderSide,
    OrderType,
    PortfolioSnapshot,
)
from finbot.core.contracts.schemas import (
    BACKTEST_STATS_COLUMN_TO_METRIC,
    BAR_DATAFRAME_COLUMNS,
    CANONICAL_METRIC_KEYS,
    extract_canonical_metrics,
    validate_bar_dataframe,
)
from finbot.core.contracts.serialization import (
    backtest_result_from_payload,
    backtest_result_to_payload,
    build_backtest_run_result_from_stats,
)
from finbot.core.contracts.versioning import (
    BACKTEST_RESULT_SCHEMA_VERSION,
    CONTRACT_SCHEMA_VERSION,
    LEGACY_BACKTEST_RESULT_VERSION,
    is_schema_compatible,
    migrate_backtest_result_payload,
)

__all__ = [
    "BACKTEST_RESULT_SCHEMA_VERSION",
    "BACKTEST_STATS_COLUMN_TO_METRIC",
    "BAR_DATAFRAME_COLUMNS",
    "CANONICAL_METRIC_KEYS",
    "CONTRACT_SCHEMA_VERSION",
    "LEGACY_BACKTEST_RESULT_VERSION",
    "BacktestEngine",
    "BacktestRunMetadata",
    "BacktestRunRequest",
    "BacktestRunResult",
    "BarEvent",
    "CostEvent",
    "CostModel",
    "CostSummary",
    "CostType",
    "ExecutionSimulator",
    "FillEvent",
    "MarketDataProvider",
    "OrderRequest",
    "OrderSide",
    "OrderType",
    "PortfolioSnapshot",
    "PortfolioStateStore",
    "backtest_result_from_payload",
    "backtest_result_to_payload",
    "build_backtest_run_result_from_stats",
    "extract_canonical_metrics",
    "is_schema_compatible",
    "migrate_backtest_result_payload",
    "validate_bar_dataframe",
]
