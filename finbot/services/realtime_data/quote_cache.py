"""Thread-safe TTL cache for real-time quotes.

Stores ``Quote`` objects in memory with a configurable time-to-live.
Uses ``threading.Lock`` for thread safety — no asyncio required.
"""

from __future__ import annotations

import threading
import time

from finbot.core.contracts.realtime_data import Quote

_DEFAULT_TTL_SECONDS = 15.0


class QuoteCache:
    """In-memory quote cache with per-entry TTL expiry.

    Args:
        ttl_seconds: Time-to-live for each cache entry in seconds.
            Defaults to 15 seconds.
    """

    def __init__(self, ttl_seconds: float = _DEFAULT_TTL_SECONDS) -> None:
        self._ttl = ttl_seconds
        self._lock = threading.Lock()
        self._store: dict[str, tuple[Quote, float]] = {}

    @property
    def ttl_seconds(self) -> float:
        """Current TTL setting in seconds."""
        return self._ttl

    def get(self, symbol: str) -> Quote | None:
        """Return a cached quote if still valid, else ``None``.

        Args:
            symbol: Ticker symbol to look up.

        Returns:
            The cached ``Quote`` or ``None`` if expired or missing.
        """
        with self._lock:
            entry = self._store.get(symbol)
            if entry is None:
                return None
            quote, stored_at = entry
            if time.monotonic() - stored_at > self._ttl:
                del self._store[symbol]
                return None
            return quote

    def put(self, symbol: str, quote: Quote) -> None:
        """Store a quote in the cache.

        Args:
            symbol: Ticker symbol key.
            quote: Quote to cache.
        """
        with self._lock:
            self._store[symbol] = (quote, time.monotonic())

    def put_many(self, quotes: dict[str, Quote]) -> None:
        """Store multiple quotes in the cache.

        Args:
            quotes: Mapping of symbol to ``Quote``.
        """
        now = time.monotonic()
        with self._lock:
            for sym, q in quotes.items():
                self._store[sym] = (q, now)

    def invalidate(self, symbol: str) -> None:
        """Remove a single symbol from the cache.

        Args:
            symbol: Ticker symbol to remove.
        """
        with self._lock:
            self._store.pop(symbol, None)

    def clear(self) -> None:
        """Remove all entries from the cache."""
        with self._lock:
            self._store.clear()

    def size(self) -> int:
        """Return the number of entries currently in the cache (including expired)."""
        with self._lock:
            return len(self._store)
