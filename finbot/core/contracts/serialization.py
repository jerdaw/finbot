"""Serialization and mapping helpers for contract result payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

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


def backtest_result_to_payload(result: BacktestRunResult) -> dict[str, Any]:
    """Serialize a result dataclass to a JSON-like dictionary payload."""

    return {
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

    return BacktestRunResult(
        metadata=metadata,
        metrics={key: float(value) for key, value in migrated["metrics"].items()},
        schema_version=str(migrated["schema_version"]),
        assumptions=dict(migrated.get("assumptions", {})),
        artifacts=dict(migrated.get("artifacts", {})),
        warnings=tuple(str(item) for item in migrated.get("warnings", [])),
    )


def _parse_created_at(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)
