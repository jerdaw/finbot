"""Realtime quotes router -- wraps CompositeQuoteProvider."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from finbot.services.realtime_data.composite_provider import CompositeQuoteProvider
from web.backend.schemas.realtime_quotes import (
    ProviderStatusResponse,
    ProviderStatusSchema,
    QuoteSchema,
    QuotesRequest,
    QuotesResponse,
)

router = APIRouter()

_provider = CompositeQuoteProvider()


@router.post("/quotes", response_model=QuotesResponse)
def get_quotes(req: QuotesRequest) -> QuotesResponse:
    """Fetch real-time quotes for the requested symbols."""
    try:
        batch = _provider.get_quotes(req.symbols)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch quotes: {e}") from e

    quotes = [
        QuoteSchema(
            symbol=quote.symbol,
            price=quote.price,
            change=quote.change,
            change_percent=quote.change_percent,
            volume=quote.volume,
            previous_close=quote.previous_close,
            open=quote.open,
            high=quote.high,
            low=quote.low,
            bid=quote.bid,
            ask=quote.ask,
            provider=quote.provider.name,
            timestamp=quote.timestamp.isoformat(),
        )
        for quote in batch.quotes.values()
    ]

    return QuotesResponse(quotes=quotes, errors=batch.errors)


@router.get("/provider-status", response_model=ProviderStatusResponse)
def get_provider_status() -> ProviderStatusResponse:
    """Return current health status of all quote providers."""
    try:
        statuses = _provider.get_provider_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get provider status: {e}") from e

    providers = [
        ProviderStatusSchema(
            provider=status.provider.name,
            is_available=status.is_available,
            last_success=status.last_success.isoformat() if status.last_success is not None else None,
            last_error=status.last_error,
            total_requests=status.total_requests,
            total_errors=status.total_errors,
        )
        for status in statuses
    ]

    return ProviderStatusResponse(providers=providers)
