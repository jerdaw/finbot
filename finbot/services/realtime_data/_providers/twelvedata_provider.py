"""Twelve Data real-time quote provider.

Supports US and Canadian (TSX/TSXV) equities via
``api.twelvedata.com/quote``.  Requires ``TWELVEDATA_API_KEY``
environment variable.
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from typing import Any

from finbot.core.contracts.realtime_data import Exchange, Quote, QuoteProvider
from finbot.utils.request_utils.request_handler import RequestHandler

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.twelvedata.com"


def is_available() -> bool:
    """Return True if Twelve Data API key is configured."""
    return bool(os.getenv("TWELVEDATA_API_KEY"))


def _get_api_key() -> str:
    """Lazy-load Twelve Data API key."""
    from finbot.config import settings_accessors

    return settings_accessors.get_twelvedata_api_key()


def transform_symbol(symbol: str) -> str:
    """Transform a standard symbol to Twelve Data format.

    ``RY.TO`` becomes ``RY:TSX``, ``ABC.V`` becomes ``ABC:TSXV``.
    US symbols pass through unchanged.

    Args:
        symbol: Ticker symbol in standard format.

    Returns:
        Symbol in Twelve Data format.
    """
    upper = symbol.upper()
    if upper.endswith(".TO"):
        return upper[: -len(".TO")] + ":TSX"
    if upper.endswith(".V"):
        return upper[: -len(".V")] + ":TSXV"
    return symbol


def get_quote(symbol: str) -> Quote:
    """Fetch a single real-time quote from Twelve Data.

    Args:
        symbol: Ticker symbol (e.g. ``"SPY"``, ``"RY.TO"``).

    Returns:
        A ``Quote`` with the latest price data.

    Raises:
        ValueError: If Twelve Data returns an error or no data.
    """
    td_symbol = transform_symbol(symbol)
    url = f"{_BASE_URL}/quote"
    params = {"symbol": td_symbol, "apikey": _get_api_key()}

    handler = RequestHandler()
    data = handler.make_json_request(url, payload_kwargs={"params": params})

    if "code" in data and data["code"] != 200:
        raise ValueError(f"Twelve Data error for {symbol}: {data.get('message', 'unknown')}")

    return _parse_quote(symbol, data)


def get_quotes(symbols: list[str]) -> dict[str, Quote]:
    """Fetch quotes for multiple symbols from Twelve Data.

    Uses the batch endpoint (comma-separated symbols).

    Args:
        symbols: List of ticker symbols.

    Returns:
        Mapping of symbol to ``Quote`` for successful fetches.
    """
    if not symbols:
        return {}

    td_symbols = [transform_symbol(s) for s in symbols]
    url = f"{_BASE_URL}/quote"
    params = {"symbol": ",".join(td_symbols), "apikey": _get_api_key()}

    handler = RequestHandler()
    try:
        # Twelve Data returns dict for single symbol, list for batch — use Any
        data: object = handler.make_json_request(url, payload_kwargs={"params": params})
    except Exception:
        logger.warning("Twelve Data: batch request failed for %s", symbols)
        return {}

    results: dict[str, Quote] = {}
    items: list[dict[str, Any]]
    # Single symbol returns a dict; multiple returns a list
    if isinstance(data, dict) and "symbol" in data:
        items = [data]
    elif isinstance(data, list):
        items = data
    else:
        return results

    for item, orig_symbol in zip(items, symbols, strict=False):
        try:
            if "code" in item and item["code"] != 200:
                continue
            results[orig_symbol] = _parse_quote(orig_symbol, item)
        except (KeyError, TypeError, ValueError):
            logger.warning("Twelve Data: failed to parse quote for %s", orig_symbol)

    return results


def _parse_quote(original_symbol: str, data: dict[str, Any]) -> Quote:
    """Convert a Twelve Data quote response to a Quote contract."""
    price = float(data.get("close", 0))
    exchange_str = data.get("exchange", "").upper()
    exchange = _map_exchange(exchange_str)

    prev_close = float(data["previous_close"]) if "previous_close" in data else None
    change = float(data["change"]) if "change" in data else None
    change_pct = float(data["percent_change"]) if "percent_change" in data else None
    volume = int(data["volume"]) if data.get("volume") else None

    try:
        ts = datetime.fromisoformat(data.get("datetime", "")).replace(tzinfo=UTC)
    except (ValueError, AttributeError):
        ts = datetime.now(tz=UTC)

    return Quote(
        symbol=original_symbol,
        price=price,
        timestamp=ts,
        provider=QuoteProvider.TWELVEDATA,
        volume=volume,
        previous_close=prev_close,
        change=change,
        change_percent=change_pct,
        open=float(data["open"]) if "open" in data else None,
        high=float(data["high"]) if "high" in data else None,
        low=float(data["low"]) if "low" in data else None,
        exchange=exchange,
    )


def _map_exchange(exchange_str: str) -> Exchange:
    """Map Twelve Data exchange name to Exchange enum."""
    mapping = {
        "NYSE": Exchange.NYSE,
        "NASDAQ": Exchange.NASDAQ,
        "TSX": Exchange.TSX,
        "TSXV": Exchange.TSXV,
    }
    return mapping.get(exchange_str, Exchange.UNKNOWN)
