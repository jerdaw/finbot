"""Composite real-time quote provider with priority fallback.

Routes requests through available providers in priority order:
- Canadian symbols (``.TO``, ``.V``) → Twelve Data → yfinance
- US symbols → Alpaca → Twelve Data → yfinance

Skips providers silently when their ``is_available()`` returns ``False``
(i.e. API key not configured).
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import UTC, datetime

from finbot.core.contracts.realtime_data import ProviderStatus, Quote, QuoteBatch, QuoteProvider
from finbot.services.realtime_data._providers import alpaca_provider, twelvedata_provider, yfinance_provider
from finbot.services.realtime_data.quote_cache import QuoteCache

logger = logging.getLogger(__name__)

# Type aliases for the provider function tuples
_SingleChain = list[tuple[QuoteProvider, Callable[[str], Quote], Callable[[], bool]]]
_BatchChain = list[tuple[QuoteProvider, Callable[[list[str]], dict[str, Quote]], Callable[[], bool]]]

_DEFAULT_CACHE_TTL = 15.0


class CompositeQuoteProvider:
    """Multi-provider quote fetcher with caching and fallback.

    Args:
        cache_ttl: Cache TTL in seconds. Defaults to 15.
    """

    def __init__(self, cache_ttl: float = _DEFAULT_CACHE_TTL) -> None:
        self._cache = QuoteCache(ttl_seconds=cache_ttl)
        self._stats: dict[QuoteProvider, _ProviderStats] = {
            QuoteProvider.ALPACA: _ProviderStats(),
            QuoteProvider.TWELVEDATA: _ProviderStats(),
            QuoteProvider.YFINANCE: _ProviderStats(),
        }

    @property
    def cache(self) -> QuoteCache:
        """Access the underlying quote cache."""
        return self._cache

    def get_quote(self, symbol: str) -> Quote:
        """Fetch a single quote with caching and fallback.

        Args:
            symbol: Ticker symbol (e.g. ``"SPY"``, ``"RY.TO"``).

        Returns:
            A ``Quote`` from the highest-priority available provider.

        Raises:
            ValueError: If no provider can supply a quote for *symbol*.
        """
        cached = self._cache.get(symbol)
        if cached is not None:
            return cached

        providers = self._provider_chain(symbol)
        last_error: Exception | None = None

        for provider_name, get_fn, avail_fn in providers:
            if not avail_fn():
                continue
            try:
                self._stats[provider_name].total_requests += 1
                quote = get_fn(symbol)
                self._stats[provider_name].last_success = datetime.now(tz=UTC)
                self._cache.put(symbol, quote)
                return quote
            except Exception as exc:
                self._stats[provider_name].total_errors += 1
                self._stats[provider_name].last_error = str(exc)
                last_error = exc
                logger.debug("%s failed for %s: %s", provider_name, symbol, exc)

        msg = f"All providers failed for {symbol}"
        if last_error is not None:
            msg += f": {last_error}"
        raise ValueError(msg)

    def get_quotes(self, symbols: list[str]) -> QuoteBatch:
        """Fetch quotes for multiple symbols with caching and fallback.

        Separates Canadian and US symbols for optimal routing, then
        merges results.

        Args:
            symbols: List of ticker symbols.

        Returns:
            A ``QuoteBatch`` with all successful quotes and any errors.
        """
        results: dict[str, Quote] = {}
        errors: dict[str, str] = {}

        # Check cache first
        uncached: list[str] = []
        for sym in symbols:
            cached = self._cache.get(sym)
            if cached is not None:
                results[sym] = cached
            else:
                uncached.append(sym)

        # Partition uncached symbols
        canadian = [s for s in uncached if _is_canadian(s)]
        us = [s for s in uncached if not _is_canadian(s)]

        # Fetch US symbols
        if us:
            fetched = self._fetch_batch_with_fallback(us, canadian=False)
            results.update(fetched)
            for sym in us:
                if sym not in fetched:
                    errors[sym] = "No provider returned data"

        # Fetch Canadian symbols
        if canadian:
            fetched = self._fetch_batch_with_fallback(canadian, canadian=True)
            results.update(fetched)
            for sym in canadian:
                if sym not in fetched:
                    errors[sym] = "No provider returned data"

        # Cache all new results
        new_results = {k: v for k, v in results.items() if k not in {s for s in symbols if self._cache.get(s)}}
        self._cache.put_many(new_results)

        # Determine primary provider from results
        primary = QuoteProvider.YFINANCE
        if results:
            first_quote = next(iter(results.values()))
            primary = first_quote.provider

        return QuoteBatch(
            quotes=results,
            requested_symbols=tuple(symbols),
            provider=primary,
            fetched_at=datetime.now(tz=UTC),
            errors=errors,
        )

    def get_provider_status(self) -> list[ProviderStatus]:
        """Return the current health status of all providers.

        Returns:
            List of ``ProviderStatus`` for each provider.
        """
        return [
            ProviderStatus(
                provider=QuoteProvider.ALPACA,
                is_available=alpaca_provider.is_available(),
                last_success=self._stats[QuoteProvider.ALPACA].last_success,
                last_error=self._stats[QuoteProvider.ALPACA].last_error,
                total_requests=self._stats[QuoteProvider.ALPACA].total_requests,
                total_errors=self._stats[QuoteProvider.ALPACA].total_errors,
            ),
            ProviderStatus(
                provider=QuoteProvider.TWELVEDATA,
                is_available=twelvedata_provider.is_available(),
                last_success=self._stats[QuoteProvider.TWELVEDATA].last_success,
                last_error=self._stats[QuoteProvider.TWELVEDATA].last_error,
                total_requests=self._stats[QuoteProvider.TWELVEDATA].total_requests,
                total_errors=self._stats[QuoteProvider.TWELVEDATA].total_errors,
            ),
            ProviderStatus(
                provider=QuoteProvider.YFINANCE,
                is_available=yfinance_provider.is_available(),
                last_success=self._stats[QuoteProvider.YFINANCE].last_success,
                last_error=self._stats[QuoteProvider.YFINANCE].last_error,
                total_requests=self._stats[QuoteProvider.YFINANCE].total_requests,
                total_errors=self._stats[QuoteProvider.YFINANCE].total_errors,
            ),
        ]

    def _fetch_batch_with_fallback(self, symbols: list[str], *, canadian: bool) -> dict[str, Quote]:
        """Try each provider in priority order, collecting as many quotes as possible."""
        results: dict[str, Quote] = {}
        remaining = list(symbols)

        for provider_name, batch_fn, avail_fn in self._batch_provider_chain(canadian=canadian):
            if not remaining:
                break
            if not avail_fn():
                continue
            try:
                self._stats[provider_name].total_requests += 1
                fetched = batch_fn(remaining)
                self._stats[provider_name].last_success = datetime.now(tz=UTC)
                results.update(fetched)
                remaining = [s for s in remaining if s not in fetched]
            except Exception as exc:
                self._stats[provider_name].total_errors += 1
                self._stats[provider_name].last_error = str(exc)
                logger.debug("%s batch failed: %s", provider_name, exc)

        return results

    @staticmethod
    def _provider_chain(symbol: str) -> _SingleChain:
        """Return the provider chain for a single symbol fetch."""
        if _is_canadian(symbol):
            return [
                (QuoteProvider.TWELVEDATA, twelvedata_provider.get_quote, twelvedata_provider.is_available),
                (QuoteProvider.YFINANCE, yfinance_provider.get_quote, yfinance_provider.is_available),
            ]
        return [
            (QuoteProvider.ALPACA, alpaca_provider.get_quote, alpaca_provider.is_available),
            (QuoteProvider.TWELVEDATA, twelvedata_provider.get_quote, twelvedata_provider.is_available),
            (QuoteProvider.YFINANCE, yfinance_provider.get_quote, yfinance_provider.is_available),
        ]

    @staticmethod
    def _batch_provider_chain(*, canadian: bool) -> _BatchChain:
        """Return the batch provider chain."""
        if canadian:
            return [
                (QuoteProvider.TWELVEDATA, twelvedata_provider.get_quotes, twelvedata_provider.is_available),
                (QuoteProvider.YFINANCE, yfinance_provider.get_quotes, yfinance_provider.is_available),
            ]
        return [
            (QuoteProvider.ALPACA, alpaca_provider.get_quotes, alpaca_provider.is_available),
            (QuoteProvider.TWELVEDATA, twelvedata_provider.get_quotes, twelvedata_provider.is_available),
            (QuoteProvider.YFINANCE, yfinance_provider.get_quotes, yfinance_provider.is_available),
        ]


class _ProviderStats:
    """Mutable stats tracker for a single provider."""

    def __init__(self) -> None:
        self.last_success: datetime | None = None
        self.last_error: str | None = None
        self.total_requests: int = 0
        self.total_errors: int = 0


def _is_canadian(symbol: str) -> bool:
    """Return True if *symbol* appears to be a Canadian equity."""
    upper = symbol.upper()
    return upper.endswith(".TO") or upper.endswith(".V")
