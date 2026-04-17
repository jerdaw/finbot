"""Experiments router — wraps ExperimentRegistry."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import backtrader as bt
import pandas as pd
from fastapi import APIRouter, HTTPException

from finbot.core.contracts.models import BacktestRunMetadata
from finbot.core.contracts.serialization import build_backtest_run_result_from_stats
from finbot.services.backtesting.experiment_registry import ExperimentRegistry
from finbot.services.backtesting.snapshot_registry import DataSnapshotRegistry
from finbot.utils.data_collection_utils.yfinance.get_history import get_history
from finbot.utils.dict_utils.hash_dictionary import hash_dictionary
from web.backend.dependencies import EXPERIMENT_DIR, SNAPSHOT_DIR
from web.backend.schemas.experiments import (
    ExperimentCompareRequest,
    ExperimentCompareResponse,
    ExperimentSummary,
    SaveExperimentRequest,
    SaveExperimentResponse,
)
from web.backend.services.serializers import sanitize_value

router = APIRouter()


def _get_registry() -> ExperimentRegistry:
    return ExperimentRegistry(storage_dir=EXPERIMENT_DIR)


def _get_snapshot_registry() -> DataSnapshotRegistry:
    return DataSnapshotRegistry(storage_dir=SNAPSHOT_DIR)


def _load_filtered_history(
    ticker: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    try:
        df = get_history(ticker.upper())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to load price data for {ticker}: {exc}") from exc

    if df is None or df.empty:
        raise HTTPException(status_code=400, detail=f"No price data available for {ticker}")

    filtered = df.copy()
    if start_date is not None:
        filtered = filtered[filtered.index >= pd.Timestamp(start_date)]
    if end_date is not None:
        filtered = filtered[filtered.index <= pd.Timestamp(end_date)]
    if filtered.empty:
        raise HTTPException(status_code=400, detail=f"Insufficient price data for {ticker} after filtering")

    return filtered


def _parse_range_boundary(value: str | None, fallback: pd.Timestamp) -> datetime:
    timestamp = pd.Timestamp(value) if value is not None else fallback
    dt = timestamp.to_pydatetime()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt


def _build_config_hash(req: SaveExperimentRequest, tickers: list[str]) -> str:
    hash_input = {
        "strategy_name": req.strategy,
        "symbols": tickers,
        "start": req.start_date,
        "end": req.end_date,
        "initial_cash": req.initial_cash,
        "parameters": req.strategy_params,
        "benchmark_ticker": req.benchmark_ticker,
        "risk_free_rate": req.risk_free_rate,
        "source": "web-backtesting",
    }
    return hash_dictionary(hash_input)


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
            data_snapshot_id=m.data_snapshot_id,
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
                "created_at": r.metadata.created_at.isoformat(),
                "config_hash": r.metadata.config_hash,
                "data_snapshot_id": r.metadata.data_snapshot_id,
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


@router.post("/save", response_model=SaveExperimentResponse)
def save_experiment(req: SaveExperimentRequest) -> SaveExperimentResponse:
    """Persist a web backtest result as a tracked experiment with snapshot lineage."""
    cleaned_tickers = [ticker.strip().upper() for ticker in req.tickers if ticker.strip()]
    if not cleaned_tickers:
        raise HTTPException(status_code=400, detail="At least one ticker is required")
    if len(set(cleaned_tickers)) != len(cleaned_tickers):
        raise HTTPException(status_code=400, detail="Tickers must be unique")

    benchmark_ticker = req.benchmark_ticker.strip().upper() if req.benchmark_ticker else None
    snapshot_symbols = list(dict.fromkeys(cleaned_tickers + ([benchmark_ticker] if benchmark_ticker else [])))

    try:
        histories = {
            symbol: _load_filtered_history(symbol, req.start_date, req.end_date)
            for symbol in snapshot_symbols
        }
        min_start = min(df.index.min() for df in histories.values())
        max_end = max(df.index.max() for df in histories.values())
        snapshot = _get_snapshot_registry().create_snapshot(
            symbols=snapshot_symbols,
            data=histories,
            start=_parse_range_boundary(req.start_date, min_start),
            end=_parse_range_boundary(req.end_date, max_end),
        )

        metadata = BacktestRunMetadata(
            run_id=f"bt-{uuid4()}",
            engine_name="backtrader",
            engine_version=str(getattr(bt, "__version__", "unknown")),
            strategy_name=req.strategy,
            created_at=datetime.now(UTC),
            config_hash=_build_config_hash(req, cleaned_tickers),
            data_snapshot_id=snapshot.snapshot_id,
            random_seed=None,
        )

        assumptions = {
            "symbols": cleaned_tickers,
            "parameters": req.strategy_params,
            "start": req.start_date,
            "end": req.end_date,
            "initial_cash": req.initial_cash,
            "benchmark_ticker": benchmark_ticker,
            "risk_free_rate": req.risk_free_rate,
            "save_source": "web-backtesting",
        }
        stats_df = pd.DataFrame([req.stats])
        result = build_backtest_run_result_from_stats(
            stats_df=stats_df,
            metadata=metadata,
            assumptions=assumptions,
            artifacts={"source": "web-backtesting"},
        )
        _get_registry().save(result)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save experiment: {exc}") from exc

    return SaveExperimentResponse(
        run_id=result.metadata.run_id,
        strategy_name=result.metadata.strategy_name,
        created_at=result.metadata.created_at.isoformat(),
        config_hash=result.metadata.config_hash,
        data_snapshot_id=result.metadata.data_snapshot_id,
    )
