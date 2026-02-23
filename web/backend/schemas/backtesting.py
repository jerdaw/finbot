"""Pydantic schemas for backtesting endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


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


class BacktestRequest(BaseModel):
    """Request to run a backtest."""

    tickers: list[str] = Field(min_length=1)
    strategy: str
    strategy_params: dict[str, Any] = Field(default_factory=dict)
    start_date: str | None = None
    end_date: str | None = None
    initial_cash: float = 10000.0


class TradeRecord(BaseModel):
    """A single trade from a backtest."""

    date: str
    ticker: str
    action: str
    size: float
    price: float
    value: float


class BacktestResponse(BaseModel):
    """Response from a backtest run."""

    stats: dict[str, Any]
    value_history: list[dict[str, Any]]
    trades: list[TradeRecord]
