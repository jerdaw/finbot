"""Typed contracts for real-time market data quotes.

Defines immutable result containers for real-time stock/ETF price
snapshots. Engine-agnostic; works with any market data provider
(Alpaca, Twelve Data, yfinance).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class QuoteProvider(StrEnum):
    """Real-time data provider identifier."""

    ALPACA = "alpaca"
    TWELVEDATA = "twelvedata"
    YFINANCE = "yfinance"


class Exchange(StrEnum):
    """Supported exchanges."""

    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    TSX = "TSX"
    TSXV = "TSXV"
    IEX = "IEX"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class Quote:
    """Point-in-time price snapshot for a single security.

    Attributes:
        symbol: Ticker symbol as requested (e.g. "SPY", "RY.TO").
        price: Last traded price.
        timestamp: Time of the quote (from the provider, not local clock).
        provider: Which provider supplied this quote.
        bid: Best bid price, if available.
        ask: Best ask price, if available.
        volume: Trading volume for the current session.
        previous_close: Previous session closing price.
        change: Absolute price change from previous close.
        change_percent: Percentage change from previous close.
        open: Session opening price.
        high: Session high price.
        low: Session low price.
        exchange: Exchange where the security trades.
    """

    symbol: str
    price: float
    timestamp: datetime
    provider: QuoteProvider
    bid: float | None = None
    ask: float | None = None
    volume: int | None = None
    previous_close: float | None = None
    change: float | None = None
    change_percent: float | None = None
    open: float | None = None
    high: float | None = None
    low: float | None = None
    exchange: Exchange = Exchange.UNKNOWN

    def __post_init__(self) -> None:
        """Validate quote fields."""
        if not self.symbol:
            raise ValueError("symbol must be non-empty")
        if self.price < 0:
            raise ValueError(f"price must be >= 0, got {self.price}")


@dataclass(frozen=True, slots=True)
class QuoteBatch:
    """Collection of quotes fetched in a single batch request.

    Attributes:
        quotes: Mapping of symbol to Quote.
        requested_symbols: Original symbols requested (may differ from quotes keys on failure).
        provider: Provider that fulfilled this batch.
        fetched_at: Local timestamp when the batch was fetched.
        errors: Mapping of symbol to error message for failed lookups.
    """

    quotes: dict[str, Quote]
    requested_symbols: tuple[str, ...]
    provider: QuoteProvider
    fetched_at: datetime
    errors: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate batch fields."""
        if not self.requested_symbols:
            raise ValueError("requested_symbols must be non-empty")


@dataclass(frozen=True, slots=True)
class ProviderStatus:
    """Health/availability status for a single quote provider.

    Attributes:
        provider: Provider identifier.
        is_available: Whether the provider can be used (API key present, etc.).
        last_success: Timestamp of last successful quote fetch, or None.
        last_error: Most recent error message, or None.
        total_requests: Total requests made to this provider in the session.
        total_errors: Total failed requests in the session.
    """

    provider: QuoteProvider
    is_available: bool
    last_success: datetime | None = None
    last_error: str | None = None
    total_requests: int = 0
    total_errors: int = 0
