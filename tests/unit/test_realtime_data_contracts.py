"""Tests for real-time data contract dataclasses and validation."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from finbot.core.contracts.realtime_data import (
    Exchange,
    ProviderStatus,
    Quote,
    QuoteBatch,
    QuoteProvider,
)


class TestQuoteProviderEnum:
    """Tests for QuoteProvider StrEnum."""

    def test_alpaca_value(self) -> None:
        assert QuoteProvider.ALPACA == "alpaca"

    def test_twelvedata_value(self) -> None:
        assert QuoteProvider.TWELVEDATA == "twelvedata"

    def test_yfinance_value(self) -> None:
        assert QuoteProvider.YFINANCE == "yfinance"

    def test_is_str(self) -> None:
        assert isinstance(QuoteProvider.ALPACA, str)


class TestExchangeEnum:
    """Tests for Exchange StrEnum."""

    def test_nyse_value(self) -> None:
        assert Exchange.NYSE == "NYSE"

    def test_tsx_value(self) -> None:
        assert Exchange.TSX == "TSX"

    def test_unknown_default(self) -> None:
        assert Exchange.UNKNOWN == "UNKNOWN"


class TestQuoteValidation:
    """Tests for Quote __post_init__ validation."""

    def _make_quote(self, **overrides: object) -> Quote:
        defaults: dict[str, object] = {
            "symbol": "SPY",
            "price": 500.12,
            "timestamp": datetime(2026, 2, 24, 10, 30, tzinfo=UTC),
            "provider": QuoteProvider.ALPACA,
        }
        defaults.update(overrides)
        return Quote(**defaults)  # type: ignore[arg-type]

    def test_valid_quote(self) -> None:
        q = self._make_quote()
        assert q.symbol == "SPY"
        assert q.price == 500.12

    def test_empty_symbol_raises(self) -> None:
        with pytest.raises(ValueError, match="symbol must be non-empty"):
            self._make_quote(symbol="")

    def test_negative_price_raises(self) -> None:
        with pytest.raises(ValueError, match="price must be >= 0"):
            self._make_quote(price=-1.0)

    def test_zero_price_allowed(self) -> None:
        q = self._make_quote(price=0.0)
        assert q.price == 0.0

    def test_optional_fields_default_none(self) -> None:
        q = self._make_quote()
        assert q.bid is None
        assert q.ask is None
        assert q.volume is None
        assert q.previous_close is None

    def test_optional_fields_set(self) -> None:
        q = self._make_quote(
            bid=500.10,
            ask=500.14,
            volume=1_234_567,
            previous_close=499.80,
            change=0.32,
            change_percent=0.064,
            open=499.90,
            high=500.50,
            low=499.70,
            exchange=Exchange.NYSE,
        )
        assert q.bid == 500.10
        assert q.ask == 500.14
        assert q.volume == 1_234_567
        assert q.exchange == Exchange.NYSE

    def test_quote_is_frozen(self) -> None:
        q = self._make_quote()
        with pytest.raises(AttributeError):
            q.price = 999.0  # type: ignore[misc]

    def test_quote_provider_stored(self) -> None:
        q = self._make_quote(provider=QuoteProvider.TWELVEDATA)
        assert q.provider == QuoteProvider.TWELVEDATA

    def test_canadian_symbol(self) -> None:
        q = self._make_quote(symbol="RY.TO", exchange=Exchange.TSX)
        assert q.symbol == "RY.TO"
        assert q.exchange == Exchange.TSX


class TestQuoteBatchValidation:
    """Tests for QuoteBatch __post_init__ validation."""

    def _make_batch(self, **overrides: object) -> QuoteBatch:
        now = datetime(2026, 2, 24, 10, 30, tzinfo=UTC)
        defaults: dict[str, object] = {
            "quotes": {
                "SPY": Quote(
                    symbol="SPY",
                    price=500.12,
                    timestamp=now,
                    provider=QuoteProvider.ALPACA,
                ),
            },
            "requested_symbols": ("SPY",),
            "provider": QuoteProvider.ALPACA,
            "fetched_at": now,
        }
        defaults.update(overrides)
        return QuoteBatch(**defaults)  # type: ignore[arg-type]

    def test_valid_batch(self) -> None:
        b = self._make_batch()
        assert len(b.quotes) == 1
        assert "SPY" in b.quotes

    def test_empty_requested_symbols_raises(self) -> None:
        with pytest.raises(ValueError, match="requested_symbols must be non-empty"):
            self._make_batch(requested_symbols=())

    def test_errors_default_empty(self) -> None:
        b = self._make_batch()
        assert b.errors == {}

    def test_errors_populated(self) -> None:
        b = self._make_batch(errors={"INVALID": "Symbol not found"})
        assert b.errors["INVALID"] == "Symbol not found"

    def test_batch_is_frozen(self) -> None:
        b = self._make_batch()
        with pytest.raises(AttributeError):
            b.provider = QuoteProvider.YFINANCE  # type: ignore[misc]


class TestProviderStatus:
    """Tests for ProviderStatus dataclass."""

    def test_available_provider(self) -> None:
        s = ProviderStatus(provider=QuoteProvider.ALPACA, is_available=True)
        assert s.is_available is True
        assert s.last_success is None
        assert s.total_requests == 0

    def test_unavailable_provider(self) -> None:
        s = ProviderStatus(
            provider=QuoteProvider.TWELVEDATA,
            is_available=False,
            last_error="API key not set",
        )
        assert s.is_available is False
        assert s.last_error == "API key not set"

    def test_with_stats(self) -> None:
        now = datetime(2026, 2, 24, 10, 30, tzinfo=UTC)
        s = ProviderStatus(
            provider=QuoteProvider.YFINANCE,
            is_available=True,
            last_success=now,
            total_requests=42,
            total_errors=3,
        )
        assert s.total_requests == 42
        assert s.total_errors == 3

    def test_status_is_frozen(self) -> None:
        s = ProviderStatus(provider=QuoteProvider.ALPACA, is_available=True)
        with pytest.raises(AttributeError):
            s.is_available = False  # type: ignore[misc]


class TestContractImports:
    """Tests that contracts are accessible from the main contracts package."""

    def test_import_from_contracts_package(self) -> None:
        from finbot.core.contracts import (
            Exchange,
            ProviderStatus,
            Quote,
            QuoteBatch,
            QuoteProvider,
            RealtimeQuoteProvider,
        )

        assert Exchange is not None
        assert ProviderStatus is not None
        assert Quote is not None
        assert QuoteBatch is not None
        assert QuoteProvider is not None
        assert RealtimeQuoteProvider is not None
