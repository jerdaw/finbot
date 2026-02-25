# Implementation Plan 12: P8 Cluster C — Real-Time Stock/ETF Data (US + Canada)

**Status:** ✅ COMPLETE
**Completed:** 2026-02-25
**Tests added:** 92 (1561 → 1653 total)

---

## What Was Done

Added free real-time quote functionality using Alpaca (US, IEX feed), Twelve Data (US + Canada/TSX), and yfinance (fallback). Implemented as `finbot/services/realtime_data/` with three individual providers, a composite provider with priority-based fallback and symbol routing, a thread-safe TTL cache, and Plotly visualisations. Added `RealtimeQuoteProvider` Protocol to contracts, API infrastructure (resource groups, rate limiters), and an 11th dashboard page with 3 tabs. All result types are immutable frozen dataclasses with `__post_init__` validation. No new dependencies required — all REST via existing `RequestHandler`. 92 new tests across 5 test files, all passing. mypy strict registered for all new modules.

## Context

P7 items 18–19 (real-time data) were blocked on paid API access. This plan added free real-time quote functionality using three data providers with graceful degradation when API keys are missing.

## Key Architecture Decisions

1. **Plain REST via existing `RequestHandler`** — no vendor SDKs. Zero new dependencies.
2. **New `RealtimeQuoteProvider` Protocol** — separate from `MarketDataProvider` (bar/historical). Quotes are point-in-time snapshots.
3. **Composite provider with fallback** — Alpaca → Twelve Data → yfinance. Routes Canadian symbols (`.TO`, `.V`) to Twelve Data.
4. **Synchronous + threading** — `QuoteCache` with `threading.Lock` and TTL.
5. **Phase 2 deferred**: WebSocket streaming, live order execution, intraday bar caching.

## Files Created (18)

### Contracts
- `finbot/core/contracts/realtime_data.py` — `Quote`, `QuoteBatch`, `ProviderStatus`, `QuoteProvider` (StrEnum), `Exchange` (StrEnum)

### Service Module
- `finbot/services/realtime_data/__init__.py` — Public API + `__all__`
- `finbot/services/realtime_data/_providers/__init__.py`
- `finbot/services/realtime_data/_providers/alpaca_provider.py` — REST → `data.alpaca.markets/v2/stocks/snapshots`
- `finbot/services/realtime_data/_providers/twelvedata_provider.py` — REST → `api.twelvedata.com/quote`
- `finbot/services/realtime_data/_providers/yfinance_provider.py` — Wraps `yf.Ticker().history()`
- `finbot/services/realtime_data/composite_provider.py` — Priority fallback + symbol routing
- `finbot/services/realtime_data/quote_cache.py` — Thread-safe TTL cache
- `finbot/services/realtime_data/viz.py` — Quote table, sparklines, provider status charts

### API Infrastructure
- `finbot/libs/api_manager/_apis/alpaca_api.py` — API registration (200/min)
- `finbot/libs/api_manager/_apis/twelvedata_api.py` — API registration (8/min, 800/day)

### Dashboard
- `finbot/dashboard/pages/11_realtime_quotes.py` — 3 tabs: Live Quotes, Watchlist, Provider Status

### Tests
- `tests/unit/test_realtime_data_contracts.py` — 26 tests (validation, enums)
- `tests/unit/test_realtime_data_providers.py` — 29 tests (mocked HTTP for all 3 providers)
- `tests/unit/test_realtime_data_cache.py` — 15 tests (TTL, thread safety)
- `tests/unit/test_realtime_data_composite.py` — 13 tests (routing, fallback)
- `tests/unit/test_realtime_data_viz.py` — 9 tests (smoke tests)

## Files Modified (10)

- `finbot/core/contracts/interfaces.py` — Added `RealtimeQuoteProvider` Protocol
- `finbot/core/contracts/__init__.py` — Export new contracts
- `finbot/config/api_key_manager.py` — Added 3 API key names
- `finbot/config/settings_accessors.py` — Added 3 accessor functions
- `finbot/constants/api_constants.py` — Added Alpaca and Twelve Data base URLs
- `finbot/libs/api_manager/_resource_groups/api_resource_groups.py` — Added 2 resource groups
- `finbot/libs/api_manager/_resource_groups/get_all_resource_groups.py` — Registered new groups
- `finbot/libs/api_manager/_apis/get_all_apis.py` — Registered new APIs
- `pyproject.toml` — Added mypy strict override
- `CLAUDE.md` (symlink → AGENTS.md) — Updated architecture docs, entry points, dashboard page count

## Verification

- `uv run pytest tests/ -v` — 1653 passed, 10 skipped, 0 failures
- `uv run mypy finbot/services/realtime_data/ finbot/core/contracts/realtime_data.py` — 0 errors
- `uv run ruff check . && uv run ruff format --check .` — clean
