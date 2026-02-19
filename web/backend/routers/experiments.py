"""Experiments router — wraps ExperimentRegistry."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from finbot.services.backtesting.experiment_registry import ExperimentRegistry
from web.backend.dependencies import EXPERIMENT_DIR
from web.backend.schemas.experiments import ExperimentCompareRequest, ExperimentCompareResponse, ExperimentSummary
from web.backend.services.serializers import sanitize_value

router = APIRouter()


def _get_registry() -> ExperimentRegistry:
    return ExperimentRegistry(storage_dir=EXPERIMENT_DIR)


@router.get("/list", response_model=list[ExperimentSummary])
def list_experiments(
    strategy: str | None = None,
    since: str | None = None,
    until: str | None = None,
    limit: int | None = 50,
) -> list[ExperimentSummary]:
    """List stored experiment runs."""
    registry = _get_registry()
    try:
        runs = registry.list_runs(strategy=strategy, since=since, until=until, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list experiments: {e}") from e

    return [
        ExperimentSummary(
            run_id=m.run_id,
            engine_name=m.engine_name,
            strategy_name=m.strategy_name,
            created_at=m.created_at.isoformat() if hasattr(m.created_at, "isoformat") else str(m.created_at),
            config_hash=m.config_hash,
        )
        for m in runs
    ]


@router.post("/compare", response_model=ExperimentCompareResponse)
def compare_experiments(req: ExperimentCompareRequest) -> ExperimentCompareResponse:
    """Compare metrics and assumptions across experiment runs."""
    registry = _get_registry()
    results = []
    for run_id in req.run_ids:
        try:
            result = registry.load(run_id)
            results.append(result)
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=f"Experiment not found: {run_id}") from e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load experiment {run_id}: {e}") from e

    assumptions = []
    metrics = []
    for r in results:
        assumptions.append(
            {
                "run_id": r.metadata.run_id,
                "strategy": r.metadata.strategy_name,
                "engine": r.metadata.engine_name,
                **{k: sanitize_value(v) for k, v in r.assumptions.items()},
            }
        )
        metrics.append(
            {
                "run_id": r.metadata.run_id,
                "strategy": r.metadata.strategy_name,
                **{k: sanitize_value(v) for k, v in r.metrics.items()},
            }
        )

    return ExperimentCompareResponse(assumptions=assumptions, metrics=metrics)
