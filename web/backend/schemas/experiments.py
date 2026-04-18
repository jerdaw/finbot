"""Pydantic schemas for experiment tracking endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from finbot.core.contracts.missing_data import DEFAULT_MISSING_DATA_POLICY, MissingDataPolicy
from web.backend.schemas.backtesting import BacktestCostAssumptions


class ExperimentSummary(BaseModel):
    """Summary of a single experiment run."""

    run_id: str
    engine_name: str
    strategy_name: str
    created_at: str
    config_hash: str
    data_snapshot_id: str


class ExperimentCompareRequest(BaseModel):
    """Request to compare experiments."""

    run_ids: list[str]


class ExperimentCompareResponse(BaseModel):
    """Response from experiment comparison."""

    assumptions: list[dict[str, Any]]
    metrics: list[dict[str, Any]]


class SaveExperimentRequest(BaseModel):
    """Request to save a web backtest run as an experiment."""

    tickers: list[str]
    strategy: str
    strategy_params: dict[str, Any]
    start_date: str | None = None
    end_date: str | None = None
    initial_cash: float = 10000.0
    benchmark_ticker: str | None = None
    risk_free_rate: float = 0.04
    missing_data_policy: MissingDataPolicy = DEFAULT_MISSING_DATA_POLICY
    cost_assumptions: BacktestCostAssumptions = Field(default_factory=BacktestCostAssumptions)
    stats: dict[str, Any]


class SaveExperimentResponse(BaseModel):
    """Response returned after saving an experiment."""

    run_id: str
    strategy_name: str
    created_at: str
    config_hash: str
    data_snapshot_id: str
