"""Yahoo Finance real-time quote provider (fallback).

Wraps the existing ``get_current_price()`` utility to produce ``Quote``
contract objects.  Always available (no API key required), but slower
than the dedicated providers.
"""

from __future__ import annotations

import logging
from datetime import UTC

import yfinance as yf

from finbot.core.contracts.realtime_data import Exchange, Quote, QuoteProvider

logger = logging.getLogger(__name__)


def is_available() -> bool:
    """yfinance is always available (no API key required)."""
    return True


def get_quote(symbol: str) -> Quote:
    """Fetch a single real-time quote via yfinance.

    Args:
        symbol: Ticker symbol (e.g. ``"SPY"``, ``"RY.TO"``).

    Returns:
        A ``Quote`` with the most recent price.

    Raises:
        ValueError: If no price data could be fetched for *symbol*.
    """
    ticker = yf.Ticker(symbol)
    history = ticker.history(period="5d", interval="1m", prepost=True)
    if history.empty:
        raise ValueError(f"No price data from yfinance for {symbol}")

    latest_close = float(history["Close"].iloc[-1])
    latest_ts = history.index[-1].to_pydatetime()
    if latest_ts.tzinfo is None:
        latest_ts = latest_ts.replace(tzinfo=UTC)

    exchange = _detect_exchange(symbol)

    return Quote(
        symbol=symbol,
        price=latest_close,
        timestamp=latest_ts,
        provider=QuoteProvider.YFINANCE,
        volume=int(history["Volume"].iloc[-1]) if "Volume" in history.columns else None,
        high=float(history["High"].iloc[-1]) if "High" in history.columns else None,
        low=float(history["Low"].iloc[-1]) if "Low" in history.columns else None,
        open=float(history["Open"].iloc[-1]) if "Open" in history.columns else None,
        exchange=exchange,
    )


def get_quotes(symbols: list[str]) -> dict[str, Quote]:
    """Fetch quotes for multiple symbols via yfinance.

    Args:
        symbols: List of ticker symbols.

    Returns:
        Mapping of symbol to ``Quote`` for successful fetches.
    """
    results: dict[str, Quote] = {}
    for sym in symbols:
        try:
            results[sym] = get_quote(sym)
        except (ValueError, Exception):
            logger.warning("yfinance: failed to fetch quote for %s", sym)
    return results


def _detect_exchange(symbol: str) -> Exchange:
    """Detect exchange from symbol suffix."""
    upper = symbol.upper()
    if upper.endswith(".TO"):
        return Exchange.TSX
    if upper.endswith(".V"):
        return Exchange.TSXV
    return Exchange.UNKNOWN
