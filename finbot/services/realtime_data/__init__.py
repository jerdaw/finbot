"""Real-time market data services.

Provides real-time stock/ETF quotes from multiple providers (Alpaca,
Twelve Data, yfinance) with automatic fallback, symbol routing for
Canadian markets, and thread-safe caching.
"""

from finbot.services.realtime_data.composite_provider import CompositeQuoteProvider
from finbot.services.realtime_data.quote_cache import QuoteCache
from finbot.services.realtime_data.viz import (
    plot_provider_status,
    plot_quote_table,
    plot_sparkline,
)

__all__ = [
    "CompositeQuoteProvider",
    "QuoteCache",
    "plot_provider_status",
    "plot_quote_table",
    "plot_sparkline",
]
