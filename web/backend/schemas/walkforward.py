"""Pydantic schemas for walk-forward analysis endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class WalkForwardRequest(BaseModel):
    """Request to run walk-forward analysis."""

    tickers: list[str] = Field(min_length=1)
    strategy: str
    strategy_params: dict[str, Any] = Field(default_factory=dict)
    start_date: str
    end_date: str
    initial_cash: float = 10000.0
    train_window: int = Field(default=504, ge=21)
    test_window: int = Field(default=126, ge=5)
    step_size: int = Field(default=63, ge=1)
    anchored: bool = False
    include_train: bool = False


class WalkForwardWindowResult(BaseModel):
    """Result for a single walk-forward window."""

    window_id: int
    train_start: str
    train_end: str
    test_start: str
    test_end: str
    metrics: dict[str, float | None]


class WalkForwardResponse(BaseModel):
    """Response from walk-forward analysis."""

    config: dict[str, Any]
    windows: list[WalkForwardWindowResult]
    summary_metrics: dict[str, float | None]
    summary_table: list[dict[str, Any]]
