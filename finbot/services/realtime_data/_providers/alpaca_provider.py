"""Alpaca Market Data real-time quote provider.

Uses the IEX feed (free tier) via ``data.alpaca.markets/v2/stocks/snapshots``
to fetch real-time US equity snapshots.  Requires ``ALPACA_API_KEY`` and
``ALPACA_SECRET_KEY`` environment variables.
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from typing import Any

from finbot.core.contracts.realtime_data import Exchange, Quote, QuoteProvider
from finbot.utils.request_utils.request_handler import RequestHandler

logger = logging.getLogger(__name__)

_BASE_URL = "https://data.alpaca.markets"


def is_available() -> bool:
    """Return True if Alpaca API keys are configured."""
    return bool(os.getenv("ALPACA_API_KEY")) and bool(os.getenv("ALPACA_SECRET_KEY"))


def _get_headers() -> dict[str, str]:
    """Build Alpaca authentication headers (lazy load)."""
    from finbot.config import settings_accessors

    return {
        "APCA-API-KEY-ID": settings_accessors.get_alpaca_api_key(),
        "APCA-API-SECRET-KEY": settings_accessors.get_alpaca_secret_key(),
    }


def get_quote(symbol: str) -> Quote:
    """Fetch a single real-time snapshot from Alpaca.

    Args:
        symbol: US equity ticker (e.g. ``"SPY"``).

    Returns:
        A ``Quote`` with latest trade and quote data.

    Raises:
        ValueError: If Alpaca returns no data for *symbol*.
    """
    quotes = get_quotes([symbol])
    if symbol not in quotes:
        raise ValueError(f"No Alpaca snapshot data for {symbol}")
    return quotes[symbol]


def get_quotes(symbols: list[str]) -> dict[str, Quote]:
    """Fetch snapshots for multiple US equities from Alpaca.

    Args:
        symbols: List of US equity tickers.

    Returns:
        Mapping of symbol to ``Quote`` for successful fetches.
    """
    if not symbols:
        return {}

    url = f"{_BASE_URL}/v2/stocks/snapshots"
    params = {"symbols": ",".join(symbols), "feed": "iex"}
    headers = _get_headers()

    handler = RequestHandler()
    try:
        data = handler.make_json_request(url, headers=headers, payload_kwargs={"params": params})
    except Exception:
        logger.warning("Alpaca: failed to fetch snapshots for %s", symbols)
        return {}

    results: dict[str, Quote] = {}
    for sym in symbols:
        snap = data.get(sym)
        if snap is None:
            continue
        try:
            results[sym] = _parse_snapshot(sym, snap)
        except (KeyError, TypeError, ValueError):
            logger.warning("Alpaca: failed to parse snapshot for %s", sym)

    return results


def _parse_snapshot(symbol: str, snap: dict[str, Any]) -> Quote:
    """Convert an Alpaca snapshot dict to a Quote contract."""
    latest_trade = snap.get("latestTrade", {})
    latest_quote = snap.get("latestQuote", {})
    daily_bar = snap.get("dailyBar", {})
    prev_bar = snap.get("prevDailyBar", {})

    price = float(latest_trade.get("p", 0))
    timestamp_str = latest_trade.get("t", "")
    try:
        ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        ts = datetime.now(tz=UTC)

    prev_close = float(prev_bar.get("c", 0)) if prev_bar else None
    change = price - prev_close if prev_close else None
    change_pct = (change / prev_close * 100) if (change is not None and prev_close) else None

    return Quote(
        symbol=symbol,
        price=price,
        timestamp=ts,
        provider=QuoteProvider.ALPACA,
        bid=float(latest_quote["bp"]) if "bp" in latest_quote else None,
        ask=float(latest_quote["ap"]) if "ap" in latest_quote else None,
        volume=int(daily_bar.get("v", 0)) if daily_bar else None,
        previous_close=prev_close,
        change=change,
        change_percent=change_pct,
        open=float(daily_bar.get("o", 0)) if daily_bar else None,
        high=float(daily_bar.get("h", 0)) if daily_bar else None,
        low=float(daily_bar.get("l", 0)) if daily_bar else None,
        exchange=Exchange.IEX,
    )
