"""Tests for CompositeQuoteProvider routing and fallback logic."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from finbot.core.contracts.realtime_data import Quote, QuoteBatch, QuoteProvider
from finbot.services.realtime_data.composite_provider import CompositeQuoteProvider, _is_canadian


def _make_quote(symbol: str = "SPY", provider: QuoteProvider = QuoteProvider.ALPACA) -> Quote:
    return Quote(
        symbol=symbol,
        price=500.0,
        timestamp=datetime(2026, 2, 24, 10, 30, tzinfo=UTC),
        provider=provider,
    )


class TestIsCanadian:
    """Tests for _is_canadian helper."""

    def test_tsx_symbol(self) -> None:
        assert _is_canadian("RY.TO") is True

    def test_tsxv_symbol(self) -> None:
        assert _is_canadian("ABC.V") is True

    def test_us_symbol(self) -> None:
        assert _is_canadian("SPY") is False

    def test_case_insensitive(self) -> None:
        assert _is_canadian("ry.to") is True


class TestCompositeGetQuote:
    """Tests for CompositeQuoteProvider.get_quote() routing and fallback."""

    @patch("finbot.services.realtime_data.composite_provider.alpaca_provider")
    @patch("finbot.services.realtime_data.composite_provider.twelvedata_provider")
    @patch("finbot.services.realtime_data.composite_provider.yfinance_provider")
    def test_us_symbol_uses_alpaca_first(self, mock_yf: MagicMock, mock_td: MagicMock, mock_alpaca: MagicMock) -> None:
        mock_alpaca.is_available.return_value = True
        mock_alpaca.get_quote.return_value = _make_quote("SPY", QuoteProvider.ALPACA)

        provider = CompositeQuoteProvider()
        quote = provider.get_quote("SPY")

        assert quote.provider == QuoteProvider.ALPACA
        mock_alpaca.get_quote.assert_called_once_with("SPY")
        mock_td.get_quote.assert_not_called()

    @patch("finbot.services.realtime_data.composite_provider.alpaca_provider")
    @patch("finbot.services.realtime_data.composite_provider.twelvedata_provider")
    @patch("finbot.services.realtime_data.composite_provider.yfinance_provider")
    def test_us_symbol_falls_back_to_twelvedata(
        self, mock_yf: MagicMock, mock_td: MagicMock, mock_alpaca: MagicMock
    ) -> None:
        mock_alpaca.is_available.return_value = True
        mock_alpaca.get_quote.side_effect = RuntimeError("Alpaca down")
        mock_td.is_available.return_value = True
        mock_td.get_quote.return_value = _make_quote("SPY", QuoteProvider.TWELVEDATA)

        provider = CompositeQuoteProvider()
        quote = provider.get_quote("SPY")

        assert quote.provider == QuoteProvider.TWELVEDATA

    @patch("finbot.services.realtime_data.composite_provider.alpaca_provider")
    @patch("finbot.services.realtime_data.composite_provider.twelvedata_provider")
    @patch("finbot.services.realtime_data.composite_provider.yfinance_provider")
    def test_us_symbol_falls_back_to_yfinance(
        self, mock_yf: MagicMock, mock_td: MagicMock, mock_alpaca: MagicMock
    ) -> None:
        mock_alpaca.is_available.return_value = False
        mock_td.is_available.return_value = False
        mock_yf.is_available.return_value = True
        mock_yf.get_quote.return_value = _make_quote("SPY", QuoteProvider.YFINANCE)

        provider = CompositeQuoteProvider()
        quote = provider.get_quote("SPY")

        assert quote.provider == QuoteProvider.YFINANCE

    @patch("finbot.services.realtime_data.composite_provider.alpaca_provider")
    @patch("finbot.services.realtime_data.composite_provider.twelvedata_provider")
    @patch("finbot.services.realtime_data.composite_provider.yfinance_provider")
    def test_canadian_symbol_skips_alpaca(self, mock_yf: MagicMock, mock_td: MagicMock, mock_alpaca: MagicMock) -> None:
        mock_td.is_available.return_value = True
        mock_td.get_quote.return_value = _make_quote("RY.TO", QuoteProvider.TWELVEDATA)

        provider = CompositeQuoteProvider()
        quote = provider.get_quote("RY.TO")

        assert quote.provider == QuoteProvider.TWELVEDATA
        mock_alpaca.get_quote.assert_not_called()

    @patch("finbot.services.realtime_data.composite_provider.alpaca_provider")
    @patch("finbot.services.realtime_data.composite_provider.twelvedata_provider")
    @patch("finbot.services.realtime_data.composite_provider.yfinance_provider")
    def test_all_providers_fail_raises(self, mock_yf: MagicMock, mock_td: MagicMock, mock_alpaca: MagicMock) -> None:
        mock_alpaca.is_available.return_value = True
        mock_alpaca.get_quote.side_effect = RuntimeError("fail")
        mock_td.is_available.return_value = True
        mock_td.get_quote.side_effect = RuntimeError("fail")
        mock_yf.is_available.return_value = True
        mock_yf.get_quote.side_effect = RuntimeError("fail")

        provider = CompositeQuoteProvider()
        with pytest.raises(ValueError, match="All providers failed"):
            provider.get_quote("SPY")

    @patch("finbot.services.realtime_data.composite_provider.alpaca_provider")
    @patch("finbot.services.realtime_data.composite_provider.twelvedata_provider")
    @patch("finbot.services.realtime_data.composite_provider.yfinance_provider")
    def test_cache_hit_skips_providers(self, mock_yf: MagicMock, mock_td: MagicMock, mock_alpaca: MagicMock) -> None:
        mock_alpaca.is_available.return_value = True
        mock_alpaca.get_quote.return_value = _make_quote("SPY", QuoteProvider.ALPACA)

        provider = CompositeQuoteProvider()
        # First call populates cache
        provider.get_quote("SPY")
        # Second call should use cache
        quote = provider.get_quote("SPY")

        assert quote.provider == QuoteProvider.ALPACA
        # Only called once (first call)
        assert mock_alpaca.get_quote.call_count == 1


class TestCompositeGetQuotes:
    """Tests for CompositeQuoteProvider.get_quotes() batch routing."""

    @patch("finbot.services.realtime_data.composite_provider.alpaca_provider")
    @patch("finbot.services.realtime_data.composite_provider.twelvedata_provider")
    @patch("finbot.services.realtime_data.composite_provider.yfinance_provider")
    def test_batch_returns_quote_batch(self, mock_yf: MagicMock, mock_td: MagicMock, mock_alpaca: MagicMock) -> None:
        mock_alpaca.is_available.return_value = True
        mock_alpaca.get_quotes.return_value = {"SPY": _make_quote("SPY", QuoteProvider.ALPACA)}
        mock_td.is_available.return_value = False
        mock_yf.is_available.return_value = True
        mock_yf.get_quotes.return_value = {}

        provider = CompositeQuoteProvider()
        batch = provider.get_quotes(["SPY"])

        assert isinstance(batch, QuoteBatch)
        assert "SPY" in batch.quotes

    @patch("finbot.services.realtime_data.composite_provider.alpaca_provider")
    @patch("finbot.services.realtime_data.composite_provider.twelvedata_provider")
    @patch("finbot.services.realtime_data.composite_provider.yfinance_provider")
    def test_mixed_symbols_routed_correctly(
        self, mock_yf: MagicMock, mock_td: MagicMock, mock_alpaca: MagicMock
    ) -> None:
        mock_alpaca.is_available.return_value = True
        mock_alpaca.get_quotes.return_value = {"SPY": _make_quote("SPY", QuoteProvider.ALPACA)}
        mock_td.is_available.return_value = True
        mock_td.get_quotes.return_value = {"RY.TO": _make_quote("RY.TO", QuoteProvider.TWELVEDATA)}
        mock_yf.is_available.return_value = True
        mock_yf.get_quotes.return_value = {}

        provider = CompositeQuoteProvider()
        batch = provider.get_quotes(["SPY", "RY.TO"])

        assert "SPY" in batch.quotes
        assert "RY.TO" in batch.quotes

    @patch("finbot.services.realtime_data.composite_provider.alpaca_provider")
    @patch("finbot.services.realtime_data.composite_provider.twelvedata_provider")
    @patch("finbot.services.realtime_data.composite_provider.yfinance_provider")
    def test_errors_tracked_for_failed_symbols(
        self, mock_yf: MagicMock, mock_td: MagicMock, mock_alpaca: MagicMock
    ) -> None:
        mock_alpaca.is_available.return_value = True
        mock_alpaca.get_quotes.return_value = {}  # Returns nothing
        mock_td.is_available.return_value = False
        mock_yf.is_available.return_value = True
        mock_yf.get_quotes.return_value = {}

        provider = CompositeQuoteProvider()
        batch = provider.get_quotes(["INVALID"])

        assert "INVALID" in batch.errors


class TestCompositeProviderStatus:
    """Tests for provider status reporting."""

    @patch("finbot.services.realtime_data.composite_provider.alpaca_provider")
    @patch("finbot.services.realtime_data.composite_provider.twelvedata_provider")
    @patch("finbot.services.realtime_data.composite_provider.yfinance_provider")
    def test_get_provider_status_returns_three(
        self, mock_yf: MagicMock, mock_td: MagicMock, mock_alpaca: MagicMock
    ) -> None:
        mock_alpaca.is_available.return_value = True
        mock_td.is_available.return_value = False
        mock_yf.is_available.return_value = True

        provider = CompositeQuoteProvider()
        statuses = provider.get_provider_status()

        assert len(statuses) == 3
        providers = {s.provider for s in statuses}
        assert QuoteProvider.ALPACA in providers
        assert QuoteProvider.TWELVEDATA in providers
        assert QuoteProvider.YFINANCE in providers

    @patch("finbot.services.realtime_data.composite_provider.alpaca_provider")
    @patch("finbot.services.realtime_data.composite_provider.twelvedata_provider")
    @patch("finbot.services.realtime_data.composite_provider.yfinance_provider")
    def test_stats_track_requests(self, mock_yf: MagicMock, mock_td: MagicMock, mock_alpaca: MagicMock) -> None:
        mock_alpaca.is_available.return_value = True
        mock_alpaca.get_quote.return_value = _make_quote("SPY", QuoteProvider.ALPACA)
        mock_td.is_available.return_value = False
        mock_yf.is_available.return_value = False

        provider = CompositeQuoteProvider()
        provider.get_quote("SPY")
        # Clear cache to force another fetch
        provider.cache.clear()
        provider.get_quote("SPY")

        statuses = provider.get_provider_status()
        alpaca_status = next(s for s in statuses if s.provider == QuoteProvider.ALPACA)
        assert alpaca_status.total_requests == 2
