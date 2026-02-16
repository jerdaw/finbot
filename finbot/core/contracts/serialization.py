"""Serialization and mapping helpers for contract result payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from finbot.core.contracts.costs import CostEvent, CostSummary, CostType
from finbot.core.contracts.models import BacktestRunMetadata, BacktestRunResult
from finbot.core.contracts.schemas import extract_canonical_metrics
from finbot.core.contracts.versioning import BACKTEST_RESULT_SCHEMA_VERSION, migrate_backtest_result_payload


def build_backtest_run_result_from_stats(
    stats_df: pd.DataFrame,
    metadata: BacktestRunMetadata,
    assumptions: dict[str, Any] | None = None,
    artifacts: dict[str, str] | None = None,
    warnings: tuple[str, ...] = (),
) -> BacktestRunResult:
    """Build a canonical result object from BacktestRunner output stats."""

    return BacktestRunResult(
        metadata=metadata,
        metrics=extract_canonical_metrics(stats_df),
        schema_version=BACKTEST_RESULT_SCHEMA_VERSION,
        assumptions=assumptions or {},
        artifacts=artifacts or {},
        warnings=warnings,
    )


def _serialize_costs(costs: CostSummary | None) -> dict[str, Any] | None:
    """Serialize CostSummary to JSON-serializable dictionary."""
    if costs is None:
        return None

    return {
        "total_commission": costs.total_commission,
        "total_spread": costs.total_spread,
        "total_slippage": costs.total_slippage,
        "total_borrow": costs.total_borrow,
        "total_market_impact": costs.total_market_impact,
        "cost_events": [
            {
                "timestamp": event.timestamp.isoformat(),
                "symbol": event.symbol,
                "cost_type": event.cost_type.value,
                "amount": event.amount,
                "basis": event.basis,
            }
            for event in costs.cost_events
        ],
    }


def _deserialize_costs(costs_payload: dict[str, Any] | None) -> CostSummary | None:
    """Deserialize CostSummary from JSON payload."""
    if costs_payload is None:
        return None

    cost_events = tuple(
        CostEvent(
            timestamp=pd.Timestamp(event["timestamp"]),
            symbol=event["symbol"],
            cost_type=CostType(event["cost_type"]),
            amount=float(event["amount"]),
            basis=event["basis"],
        )
        for event in costs_payload.get("cost_events", [])
    )

    return CostSummary(
        total_commission=float(costs_payload["total_commission"]),
        total_spread=float(costs_payload["total_spread"]),
        total_slippage=float(costs_payload["total_slippage"]),
        total_borrow=float(costs_payload["total_borrow"]),
        total_market_impact=float(costs_payload["total_market_impact"]),
        cost_events=cost_events,
    )


def backtest_result_to_payload(result: BacktestRunResult) -> dict[str, Any]:
    """Serialize a result dataclass to a JSON-like dictionary payload."""

    payload = {
        "schema_version": result.schema_version,
        "metadata": {
            "run_id": result.metadata.run_id,
            "engine_name": result.metadata.engine_name,
            "engine_version": result.metadata.engine_version,
            "strategy_name": result.metadata.strategy_name,
            "created_at": result.metadata.created_at.isoformat(),
            "config_hash": result.metadata.config_hash,
            "data_snapshot_id": result.metadata.data_snapshot_id,
            "random_seed": result.metadata.random_seed,
        },
        "metrics": dict(result.metrics),
        "assumptions": dict(result.assumptions),
        "artifacts": dict(result.artifacts),
        "warnings": list(result.warnings),
    }

    # Add costs if present
    if result.costs is not None:
        payload["costs"] = _serialize_costs(result.costs)

    return payload


def backtest_result_from_payload(payload: dict[str, Any]) -> BacktestRunResult:
    """Deserialize payload into BacktestRunResult, applying migrations if needed."""

    migrated = migrate_backtest_result_payload(payload)
    metadata_payload = migrated["metadata"]
    created_at = _parse_created_at(metadata_payload["created_at"])

    metadata = BacktestRunMetadata(
        run_id=str(metadata_payload["run_id"]),
        engine_name=str(metadata_payload["engine_name"]),
        engine_version=str(metadata_payload["engine_version"]),
        strategy_name=str(metadata_payload["strategy_name"]),
        created_at=created_at,
        config_hash=str(metadata_payload["config_hash"]),
        data_snapshot_id=str(metadata_payload["data_snapshot_id"]),
        random_seed=metadata_payload.get("random_seed"),
    )

    # Deserialize costs if present
    costs = _deserialize_costs(migrated.get("costs"))

    return BacktestRunResult(
        metadata=metadata,
        metrics={key: float(value) for key, value in migrated["metrics"].items()},
        schema_version=str(migrated["schema_version"]),
        assumptions=dict(migrated.get("assumptions", {})),
        artifacts=dict(migrated.get("artifacts", {})),
        warnings=tuple(str(item) for item in migrated.get("warnings", [])),
        costs=costs,
    )


def _parse_created_at(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)
