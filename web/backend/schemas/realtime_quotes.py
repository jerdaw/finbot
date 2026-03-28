"""Pydantic schemas for realtime quotes endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class QuotesRequest(BaseModel):
    """Request to fetch real-time quotes for one or more symbols."""

    symbols: list[str] = Field(min_length=1)


class QuoteSchema(BaseModel):
    """Single real-time quote snapshot."""

    symbol: str
    price: float
    change: float | None = None
    change_percent: float | None = None
    volume: int | None = None
    previous_close: float | None = None
    open: float | None = None
    high: float | None = None
    low: float | None = None
    bid: float | None = None
    ask: float | None = None
    provider: str
    timestamp: str


class QuotesResponse(BaseModel):
    """Response containing fetched quotes and any per-symbol errors."""

    quotes: list[QuoteSchema]
    errors: dict[str, str]


class ProviderStatusSchema(BaseModel):
    """Health status for a single real-time data provider."""

    provider: str
    is_available: bool
    last_success: str | None = None
    last_error: str | None = None
    total_requests: int = 0
    total_errors: int = 0


class ProviderStatusResponse(BaseModel):
    """Response listing status of all quote providers."""

    providers: list[ProviderStatusSchema]
