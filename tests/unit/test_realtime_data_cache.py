"""Tests for QuoteCache thread-safe TTL cache."""

from __future__ import annotations

import threading
import time
from datetime import UTC, datetime

from finbot.core.contracts.realtime_data import Quote, QuoteProvider
from finbot.services.realtime_data.quote_cache import QuoteCache


def _make_quote(symbol: str = "SPY", price: float = 500.0) -> Quote:
    return Quote(
        symbol=symbol,
        price=price,
        timestamp=datetime(2026, 2, 24, 10, 30, tzinfo=UTC),
        provider=QuoteProvider.ALPACA,
    )


class TestQuoteCacheBasic:
    """Basic get/put operations."""

    def test_get_missing_returns_none(self) -> None:
        cache = QuoteCache()
        assert cache.get("SPY") is None

    def test_put_and_get(self) -> None:
        cache = QuoteCache()
        q = _make_quote()
        cache.put("SPY", q)
        assert cache.get("SPY") is q

    def test_put_overwrites(self) -> None:
        cache = QuoteCache()
        q1 = _make_quote(price=500.0)
        q2 = _make_quote(price=501.0)
        cache.put("SPY", q1)
        cache.put("SPY", q2)
        assert cache.get("SPY") is q2

    def test_put_many(self) -> None:
        cache = QuoteCache()
        quotes = {
            "SPY": _make_quote("SPY", 500.0),
            "QQQ": _make_quote("QQQ", 420.0),
        }
        cache.put_many(quotes)
        assert cache.get("SPY") is not None
        assert cache.get("QQQ") is not None

    def test_size(self) -> None:
        cache = QuoteCache()
        assert cache.size() == 0
        cache.put("SPY", _make_quote())
        assert cache.size() == 1
        cache.put("QQQ", _make_quote("QQQ"))
        assert cache.size() == 2


class TestQuoteCacheInvalidation:
    """Cache invalidation and clear operations."""

    def test_invalidate_removes_entry(self) -> None:
        cache = QuoteCache()
        cache.put("SPY", _make_quote())
        cache.invalidate("SPY")
        assert cache.get("SPY") is None

    def test_invalidate_nonexistent_noop(self) -> None:
        cache = QuoteCache()
        cache.invalidate("DOESNTEXIST")  # Should not raise

    def test_clear_removes_all(self) -> None:
        cache = QuoteCache()
        cache.put("SPY", _make_quote())
        cache.put("QQQ", _make_quote("QQQ"))
        cache.clear()
        assert cache.size() == 0
        assert cache.get("SPY") is None


class TestQuoteCacheTTL:
    """TTL expiry behavior."""

    def test_entry_expires_after_ttl(self) -> None:
        cache = QuoteCache(ttl_seconds=0.05)
        cache.put("SPY", _make_quote())
        assert cache.get("SPY") is not None
        time.sleep(0.1)
        assert cache.get("SPY") is None

    def test_entry_valid_within_ttl(self) -> None:
        cache = QuoteCache(ttl_seconds=10.0)
        cache.put("SPY", _make_quote())
        assert cache.get("SPY") is not None

    def test_ttl_property(self) -> None:
        cache = QuoteCache(ttl_seconds=30.0)
        assert cache.ttl_seconds == 30.0


class TestQuoteCacheThreadSafety:
    """Thread safety under concurrent access."""

    def test_concurrent_reads_and_writes(self) -> None:
        cache = QuoteCache(ttl_seconds=10.0)
        errors: list[Exception] = []

        def writer() -> None:
            try:
                for i in range(100):
                    cache.put(f"SYM{i}", _make_quote(f"SYM{i}", float(i)))
            except Exception as e:
                errors.append(e)

        def reader() -> None:
            try:
                for i in range(100):
                    cache.get(f"SYM{i}")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer) for _ in range(4)]
        threads += [threading.Thread(target=reader) for _ in range(4)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0

    def test_concurrent_put_many(self) -> None:
        cache = QuoteCache(ttl_seconds=10.0)
        errors: list[Exception] = []

        def batch_writer(offset: int) -> None:
            try:
                quotes = {f"SYM{offset + i}": _make_quote(f"SYM{offset + i}") for i in range(50)}
                cache.put_many(quotes)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=batch_writer, args=(i * 50,)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert cache.size() == 200
