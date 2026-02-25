"""Typed contracts for engine-agnostic backtesting and execution."""

from finbot.core.contracts.batch import BatchItemResult, BatchRun, BatchStatus, ErrorCategory
from finbot.core.contracts.checkpoint import CHECKPOINT_VERSION, ExecutionCheckpoint
from finbot.core.contracts.costs import CostEvent, CostModel, CostSummary, CostType
from finbot.core.contracts.interfaces import BacktestEngine, ExecutionSimulator, MarketDataProvider, PortfolioStateStore
from finbot.core.contracts.latency import LATENCY_FAST, LATENCY_INSTANT, LATENCY_NORMAL, LATENCY_SLOW, LatencyConfig
from finbot.core.contracts.missing_data import DEFAULT_MISSING_DATA_POLICY, MissingDataPolicy
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
from finbot.core.contracts.optimization import ParetoPoint, ParetoResult
from finbot.core.contracts.orders import Order, OrderExecution, OrderStatus, RejectionReason
from finbot.core.contracts.portfolio_analytics import (
    BenchmarkComparisonResult,
    DiversificationResult,
    DrawdownAnalysisResult,
    DrawdownPeriod,
    RollingMetricsResult,
)
from finbot.core.contracts.regime import MarketRegime, RegimeConfig, RegimeDetector, RegimeMetrics, RegimePeriod
from finbot.core.contracts.risk import (
    DrawdownLimitRule,
    ExposureLimitRule,
    PositionLimitRule,
    RiskConfig,
    RiskRuleType,
    RiskViolation,
)
from finbot.core.contracts.risk_analytics import (
    CVaRResult,
    KellyResult,
    MultiAssetKellyResult,
    StressScenario,
    StressTestResult,
    VaRBacktestResult,
    VaRMethod,
    VaRResult,
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
from finbot.core.contracts.snapshot import DataSnapshot, compute_data_content_hash, compute_snapshot_hash
from finbot.core.contracts.versioning import (
    BACKTEST_RESULT_SCHEMA_VERSION,
    CONTRACT_SCHEMA_VERSION,
    LEGACY_BACKTEST_RESULT_VERSION,
    is_schema_compatible,
    migrate_backtest_result_payload,
)
from finbot.core.contracts.walkforward import WalkForwardConfig, WalkForwardResult, WalkForwardWindow

__all__ = [
    "BACKTEST_RESULT_SCHEMA_VERSION",
    "BACKTEST_STATS_COLUMN_TO_METRIC",
    "BAR_DATAFRAME_COLUMNS",
    "CANONICAL_METRIC_KEYS",
    "CHECKPOINT_VERSION",
    "CONTRACT_SCHEMA_VERSION",
    "DEFAULT_MISSING_DATA_POLICY",
    "LATENCY_FAST",
    "LATENCY_INSTANT",
    "LATENCY_NORMAL",
    "LATENCY_SLOW",
    "LEGACY_BACKTEST_RESULT_VERSION",
    "BacktestEngine",
    "BacktestRunMetadata",
    "BacktestRunRequest",
    "BacktestRunResult",
    "BarEvent",
    "BatchItemResult",
    "BatchRun",
    "BatchStatus",
    "BenchmarkComparisonResult",
    "CVaRResult",
    "CostEvent",
    "CostModel",
    "CostSummary",
    "CostType",
    "DataSnapshot",
    "DiversificationResult",
    "DrawdownAnalysisResult",
    "DrawdownLimitRule",
    "DrawdownPeriod",
    "ErrorCategory",
    "ExecutionCheckpoint",
    "ExecutionSimulator",
    "ExposureLimitRule",
    "FillEvent",
    "KellyResult",
    "LatencyConfig",
    "MarketDataProvider",
    "MarketRegime",
    "MissingDataPolicy",
    "MultiAssetKellyResult",
    "Order",
    "OrderExecution",
    "OrderRequest",
    "OrderSide",
    "OrderStatus",
    "OrderType",
    "ParetoPoint",
    "ParetoResult",
    "PortfolioSnapshot",
    "PortfolioStateStore",
    "PositionLimitRule",
    "RegimeConfig",
    "RegimeDetector",
    "RegimeMetrics",
    "RegimePeriod",
    "RejectionReason",
    "RiskConfig",
    "RiskRuleType",
    "RiskViolation",
    "RollingMetricsResult",
    "StressScenario",
    "StressTestResult",
    "VaRBacktestResult",
    "VaRMethod",
    "VaRResult",
    "WalkForwardConfig",
    "WalkForwardResult",
    "WalkForwardWindow",
    "backtest_result_from_payload",
    "backtest_result_to_payload",
    "build_backtest_run_result_from_stats",
    "compute_data_content_hash",
    "compute_snapshot_hash",
    "extract_canonical_metrics",
    "is_schema_compatible",
    "migrate_backtest_result_payload",
    "validate_bar_dataframe",
]
