"""Unit tests for core contract models, interfaces, and schema versioning."""

from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd

from finbot.core.contracts import (
    BACKTEST_RESULT_SCHEMA_VERSION,
    BACKTEST_STATS_COLUMN_TO_METRIC,
    BAR_DATAFRAME_COLUMNS,
    CANONICAL_METRIC_KEYS,
    CONTRACT_SCHEMA_VERSION,
    LEGACY_BACKTEST_RESULT_VERSION,
    BacktestEngine,
    BacktestRunMetadata,
    BacktestRunRequest,
    BacktestRunResult,
    BarEvent,
    ExecutionSimulator,
    FillEvent,
    MarketDataProvider,
    OrderRequest,
    OrderSide,
    OrderType,
    PortfolioSnapshot,
    PortfolioStateStore,
    backtest_result_from_payload,
    backtest_result_to_payload,
    build_backtest_run_result_from_stats,
    extract_canonical_metrics,
    is_schema_compatible,
    migrate_backtest_result_payload,
    validate_bar_dataframe,
)


def test_schema_versions_are_compatible_with_themselves() -> None:
    assert is_schema_compatible(CONTRACT_SCHEMA_VERSION, CONTRACT_SCHEMA_VERSION)
    assert is_schema_compatible(BACKTEST_RESULT_SCHEMA_VERSION, BACKTEST_RESULT_SCHEMA_VERSION)


def test_schema_compatibility_major_version_mismatch() -> None:
    assert is_schema_compatible("1.2.3", "1.9.0")
    assert not is_schema_compatible("1.2.3", "2.0.0")


def test_backtest_result_contract_defaults() -> None:
    metadata = BacktestRunMetadata(
        run_id="run-001",
        engine_name="backtrader",
        engine_version="1.9.78.123",
        strategy_name="NoRebalance",
        created_at=datetime.now(UTC),
        config_hash="cfg-abc",
        data_snapshot_id="snapshot-2026-02-14",
    )
    result = BacktestRunResult(metadata=metadata, metrics={"cagr": 0.1})

    assert result.metrics["cagr"] == 0.1
    assert result.schema_version == BACKTEST_RESULT_SCHEMA_VERSION
    assert result.assumptions == {}
    assert result.artifacts == {}
    assert result.warnings == ()


def test_protocol_runtime_conformance() -> None:
    class DummyMarketDataProvider:
        def get_bars(
            self,
            symbol: str,
            start: pd.Timestamp | None = None,
            end: pd.Timestamp | None = None,
            timeframe: str = "1d",
        ) -> pd.DataFrame:
            del symbol, start, end, timeframe
            return pd.DataFrame({"close": [100.0]})

    class DummyExecutionSimulator:
        def simulate_fill(self, order: OrderRequest, bar: BarEvent) -> FillEvent:
            return FillEvent(
                order_id=order.order_id,
                timestamp=bar.timestamp,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                fill_price=bar.close,
            )

    class DummyPortfolioStateStore:
        def __init__(self):
            self._snapshot = PortfolioSnapshot(
                timestamp=pd.Timestamp("2024-01-01"),
                cash=100000.0,
                equity=100000.0,
                gross_exposure=0.0,
                net_exposure=0.0,
                positions={},
            )

        def snapshot(self) -> PortfolioSnapshot:
            return self._snapshot

        def apply_fill(self, fill: FillEvent) -> PortfolioSnapshot:
            del fill
            return self._snapshot

    class DummyBacktestEngine:
        def run(self, request: BacktestRunRequest) -> BacktestRunResult:
            metadata = BacktestRunMetadata(
                run_id="run-002",
                engine_name="dummy",
                engine_version="0.1.0",
                strategy_name=request.strategy_name,
                created_at=datetime.now(UTC),
                config_hash="cfg",
                data_snapshot_id="snapshot",
            )
            return BacktestRunResult(metadata=metadata, metrics={"final_value": request.initial_cash})

    assert isinstance(DummyMarketDataProvider(), MarketDataProvider)
    assert isinstance(DummyExecutionSimulator(), ExecutionSimulator)
    assert isinstance(DummyPortfolioStateStore(), PortfolioStateStore)
    assert isinstance(DummyBacktestEngine(), BacktestEngine)


def test_order_request_defaults() -> None:
    order = OrderRequest(
        order_id="ord-001",
        timestamp=pd.Timestamp("2024-01-02"),
        symbol="SPY",
        side=OrderSide.BUY,
        quantity=10.0,
    )

    assert order.order_type is OrderType.MARKET
    assert order.limit_price is None
    assert order.stop_price is None
    assert order.tags == {}


def test_validate_bar_dataframe_accepts_required_columns() -> None:
    valid = pd.DataFrame(columns=BAR_DATAFRAME_COLUMNS)
    validate_bar_dataframe(valid)


def test_extract_canonical_metrics_maps_stats_columns() -> None:
    stats_df = pd.DataFrame(
        {
            "Starting Value": [100000.0],
            "Ending Value": [125000.0],
            "ROI": [0.25],
            "CAGR": [0.05],
            "Sharpe": [0.75],
            "Max Drawdown": [-0.2],
            "Mean Cash Utilization": [0.8],
        }
    )
    metrics = extract_canonical_metrics(stats_df)
    assert tuple(metrics.keys()) == CANONICAL_METRIC_KEYS
    assert metrics["ending_value"] == 125000.0


def test_build_backtest_run_result_from_stats_sets_version() -> None:
    stats_df = pd.DataFrame({column: [1.0] for column in BACKTEST_STATS_COLUMN_TO_METRIC})
    metadata = BacktestRunMetadata(
        run_id="run-003",
        engine_name="backtrader",
        engine_version="1.9.78.123",
        strategy_name="NoRebalance",
        created_at=datetime.now(UTC),
        config_hash="cfg-hash",
        data_snapshot_id="snapshot-001",
    )

    result = build_backtest_run_result_from_stats(stats_df=stats_df, metadata=metadata)
    assert result.schema_version == BACKTEST_RESULT_SCHEMA_VERSION
    assert result.metrics["roi"] == 1.0


def test_result_payload_roundtrip() -> None:
    metadata = BacktestRunMetadata(
        run_id="run-004",
        engine_name="backtrader",
        engine_version="1.9.78.123",
        strategy_name="RiskParity",
        created_at=datetime.now(UTC),
        config_hash="cfg-roundtrip",
        data_snapshot_id="snapshot-roundtrip",
        random_seed=42,
    )
    result = BacktestRunResult(
        metadata=metadata,
        metrics={"roi": 0.2},
        assumptions={"frequency": "1d"},
        artifacts={"stats_csv": "path/to/stats.csv"},
        warnings=("none",),
    )

    payload = backtest_result_to_payload(result)
    restored = backtest_result_from_payload(payload)

    assert restored.metadata.run_id == result.metadata.run_id
    assert restored.schema_version == BACKTEST_RESULT_SCHEMA_VERSION
    assert restored.metrics == result.metrics
    assert restored.assumptions == result.assumptions
    assert restored.artifacts == result.artifacts
    assert restored.warnings == result.warnings


def test_migrate_legacy_payload_to_v1_shape() -> None:
    legacy_payload = {
        "schema_version": LEGACY_BACKTEST_RESULT_VERSION,
        "run_id": "legacy-1",
        "engine": "backtrader",
        "strategy": "NoRebalance",
        "Starting Value": 100000.0,
        "Ending Value": 130000.0,
        "ROI": 0.3,
        "CAGR": 0.07,
        "Sharpe": 0.8,
        "Max Drawdown": -0.22,
        "Mean Cash Utilization": 0.95,
    }

    migrated = migrate_backtest_result_payload(legacy_payload)
    assert migrated["schema_version"] == BACKTEST_RESULT_SCHEMA_VERSION
    assert migrated["metadata"]["run_id"] == "legacy-1"
    assert migrated["metrics"]["ending_value"] == 130000.0
