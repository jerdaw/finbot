"""Versioning helpers for contract and result schemas."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

CONTRACT_SCHEMA_VERSION = "1.0.0"
BACKTEST_RESULT_SCHEMA_VERSION = "1.0.0"
LEGACY_BACKTEST_RESULT_VERSION = "0.9.0"


def is_schema_compatible(expected_version: str, candidate_version: str) -> bool:
    """Return True when schema major versions match."""

    return _major(expected_version) == _major(candidate_version)


def migrate_backtest_result_payload(
    payload: dict[str, Any],
    target_version: str = BACKTEST_RESULT_SCHEMA_VERSION,
) -> dict[str, Any]:
    """Migrate legacy payload shapes into the current result payload shape."""

    working = deepcopy(payload)
    source_version = str(working.get("schema_version", LEGACY_BACKTEST_RESULT_VERSION))

    if _major(source_version) == "0":
        working = _migrate_v0_to_v1_payload(working)
        source_version = BACKTEST_RESULT_SCHEMA_VERSION

    if not is_schema_compatible(target_version, source_version):
        raise ValueError(f"Incompatible schema migration from {source_version} to {target_version}")

    working["schema_version"] = target_version
    return working


def _major(version: str) -> str:
    return version.split(".", maxsplit=1)[0]


def _migrate_v0_to_v1_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Convert a pre-1.0 payload into the v1 structure."""

    if "metadata" in payload and "metrics" in payload:
        payload.setdefault("assumptions", {})
        payload.setdefault("artifacts", {})
        payload.setdefault("warnings", [])
        return payload

    legacy_metric_mapping = {
        "Starting Value": "starting_value",
        "Ending Value": "ending_value",
        "ROI": "roi",
        "CAGR": "cagr",
        "Sharpe": "sharpe",
        "Max Drawdown": "max_drawdown",
        "Mean Cash Utilization": "mean_cash_utilization",
    }

    metrics_raw = payload.get("metrics")
    legacy_metrics_source: dict[str, Any] = metrics_raw if isinstance(metrics_raw, dict) else payload
    metrics: dict[str, float] = {}
    for legacy_key, canonical_key in legacy_metric_mapping.items():
        if legacy_key in legacy_metrics_source:
            metrics[canonical_key] = float(legacy_metrics_source[legacy_key])

    metadata = {
        "run_id": str(payload.get("run_id", "legacy-run")),
        "engine_name": str(payload.get("engine_name", payload.get("engine", "unknown-engine"))),
        "engine_version": str(payload.get("engine_version", "unknown")),
        "strategy_name": str(payload.get("strategy_name", payload.get("strategy", "unknown-strategy"))),
        "created_at": payload.get("created_at", datetime.now(UTC).isoformat()),
        "config_hash": str(payload.get("config_hash", "legacy-config-hash")),
        "data_snapshot_id": str(payload.get("data_snapshot_id", "legacy-data-snapshot")),
        "random_seed": payload.get("random_seed"),
    }

    return {
        "metadata": metadata,
        "metrics": metrics,
        "assumptions": payload.get("assumptions", {}),
        "artifacts": payload.get("artifacts", {}),
        "warnings": payload.get("warnings", []),
    }
