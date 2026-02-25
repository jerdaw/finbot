"""Tests for real-time data providers (all mocked, no real API calls)."""

from __future__ import annotations

from typing import Any, ClassVar
from unittest.mock import MagicMock, patch

import pytest

from finbot.core.contracts.realtime_data import Exchange, Quote, QuoteProvider

# ── Alpaca Provider ──────────────────────────────────────────────────────────


class TestAlpacaProviderAvailability:
    """Tests for alpaca_provider.is_available()."""

    def test_available_when_keys_set(self) -> None:
        from finbot.services.realtime_data._providers import alpaca_provider

        with patch.dict("os.environ", {"ALPACA_API_KEY": "key", "ALPACA_SECRET_KEY": "secret"}):
            assert alpaca_provider.is_available() is True

    def test_unavailable_when_key_missing(self) -> None:
        from finbot.services.realtime_data._providers import alpaca_provider

        with patch.dict("os.environ", {}, clear=True):
            assert alpaca_provider.is_available() is False

    def test_unavailable_when_secret_missing(self) -> None:
        from finbot.services.realtime_data._providers import alpaca_provider

        with patch.dict("os.environ", {"ALPACA_API_KEY": "key"}, clear=True):
            assert alpaca_provider.is_available() is False


class TestAlpacaProviderGetQuotes:
    """Tests for alpaca_provider.get_quotes() with mocked HTTP."""

    _SNAPSHOT_RESPONSE: ClassVar[dict[str, Any]] = {
        "SPY": {
            "latestTrade": {"p": 500.12, "t": "2026-02-24T15:30:00Z"},
            "latestQuote": {"bp": 500.10, "ap": 500.14},
            "dailyBar": {"o": 499.50, "h": 501.00, "l": 499.00, "c": 500.12, "v": 1234567},
            "prevDailyBar": {"c": 499.80},
        },
        "QQQ": {
            "latestTrade": {"p": 420.50, "t": "2026-02-24T15:30:00Z"},
            "latestQuote": {"bp": 420.48, "ap": 420.52},
            "dailyBar": {"o": 419.00, "h": 421.00, "l": 418.50, "c": 420.50, "v": 987654},
            "prevDailyBar": {"c": 419.00},
        },
    }

    @patch("finbot.services.realtime_data._providers.alpaca_provider.RequestHandler")
    @patch(
        "finbot.services.realtime_data._providers.alpaca_provider._get_headers",
        return_value={"APCA-API-KEY-ID": "k", "APCA-API-SECRET-KEY": "s"},
    )
    def test_get_quotes_returns_quotes(self, _mock_headers: MagicMock, mock_handler_cls: MagicMock) -> None:
        from finbot.services.realtime_data._providers import alpaca_provider

        mock_handler_cls.return_value.make_json_request.return_value = self._SNAPSHOT_RESPONSE
        result = alpaca_provider.get_quotes(["SPY", "QQQ"])

        assert len(result) == 2
        assert "SPY" in result
        assert "QQQ" in result
        assert isinstance(result["SPY"], Quote)
        assert result["SPY"].price == 500.12
        assert result["SPY"].provider == QuoteProvider.ALPACA
        assert result["SPY"].bid == 500.10
        assert result["SPY"].ask == 500.14

    @patch("finbot.services.realtime_data._providers.alpaca_provider.RequestHandler")
    @patch("finbot.services.realtime_data._providers.alpaca_provider._get_headers", return_value={})
    def test_get_quotes_empty_list(self, _mock_headers: MagicMock, mock_handler_cls: MagicMock) -> None:
        from finbot.services.realtime_data._providers import alpaca_provider

        result = alpaca_provider.get_quotes([])
        assert result == {}

    @patch("finbot.services.realtime_data._providers.alpaca_provider.RequestHandler")
    @patch("finbot.services.realtime_data._providers.alpaca_provider._get_headers", return_value={})
    def test_get_quotes_handles_api_error(self, _mock_headers: MagicMock, mock_handler_cls: MagicMock) -> None:
        from finbot.services.realtime_data._providers import alpaca_provider

        mock_handler_cls.return_value.make_json_request.side_effect = RuntimeError("API error")
        result = alpaca_provider.get_quotes(["SPY"])
        assert result == {}

    @patch("finbot.services.realtime_data._providers.alpaca_provider.RequestHandler")
    @patch("finbot.services.realtime_data._providers.alpaca_provider._get_headers", return_value={})
    def test_get_quote_single(self, _mock_headers: MagicMock, mock_handler_cls: MagicMock) -> None:
        from finbot.services.realtime_data._providers import alpaca_provider

        mock_handler_cls.return_value.make_json_request.return_value = {
            "SPY": self._SNAPSHOT_RESPONSE["SPY"],
        }
        result = alpaca_provider.get_quote("SPY")
        assert result.symbol == "SPY"
        assert result.exchange == Exchange.IEX

    @patch("finbot.services.realtime_data._providers.alpaca_provider.RequestHandler")
    @patch("finbot.services.realtime_data._providers.alpaca_provider._get_headers", return_value={})
    def test_get_quote_raises_when_no_data(self, _mock_headers: MagicMock, mock_handler_cls: MagicMock) -> None:
        from finbot.services.realtime_data._providers import alpaca_provider

        mock_handler_cls.return_value.make_json_request.return_value = {}
        with pytest.raises(ValueError, match="No Alpaca snapshot data"):
            alpaca_provider.get_quote("INVALID")

    @patch("finbot.services.realtime_data._providers.alpaca_provider.RequestHandler")
    @patch("finbot.services.realtime_data._providers.alpaca_provider._get_headers", return_value={})
    def test_previous_close_and_change(self, _mock_headers: MagicMock, mock_handler_cls: MagicMock) -> None:
        from finbot.services.realtime_data._providers import alpaca_provider

        mock_handler_cls.return_value.make_json_request.return_value = {
            "SPY": self._SNAPSHOT_RESPONSE["SPY"],
        }
        quote = alpaca_provider.get_quote("SPY")
        assert quote.previous_close == 499.80
        assert quote.change is not None
        assert abs(quote.change - 0.32) < 0.01

    @patch("finbot.services.realtime_data._providers.alpaca_provider.RequestHandler")
    @patch("finbot.services.realtime_data._providers.alpaca_provider._get_headers", return_value={})
    def test_volume_parsed(self, _mock_headers: MagicMock, mock_handler_cls: MagicMock) -> None:
        from finbot.services.realtime_data._providers import alpaca_provider

        mock_handler_cls.return_value.make_json_request.return_value = {
            "SPY": self._SNAPSHOT_RESPONSE["SPY"],
        }
        quote = alpaca_provider.get_quote("SPY")
        assert quote.volume == 1234567


# ── Twelve Data Provider ─────────────────────────────────────────────────────


class TestTwelveDataProviderAvailability:
    """Tests for twelvedata_provider.is_available()."""

    def test_available_when_key_set(self) -> None:
        from finbot.services.realtime_data._providers import twelvedata_provider

        with patch.dict("os.environ", {"TWELVEDATA_API_KEY": "key"}):
            assert twelvedata_provider.is_available() is True

    def test_unavailable_when_key_missing(self) -> None:
        from finbot.services.realtime_data._providers import twelvedata_provider

        with patch.dict("os.environ", {}, clear=True):
            assert twelvedata_provider.is_available() is False


class TestTwelveDataSymbolTransform:
    """Tests for symbol transformation logic."""

    def test_tsx_symbol(self) -> None:
        from finbot.services.realtime_data._providers.twelvedata_provider import transform_symbol

        assert transform_symbol("RY.TO") == "RY:TSX"

    def test_tsxv_symbol(self) -> None:
        from finbot.services.realtime_data._providers.twelvedata_provider import transform_symbol

        assert transform_symbol("ABC.V") == "ABC:TSXV"

    def test_us_symbol_passthrough(self) -> None:
        from finbot.services.realtime_data._providers.twelvedata_provider import transform_symbol

        assert transform_symbol("SPY") == "SPY"

    def test_case_insensitive(self) -> None:
        from finbot.services.realtime_data._providers.twelvedata_provider import transform_symbol

        assert transform_symbol("ry.to") == "RY:TSX"


class TestTwelveDataProviderGetQuote:
    """Tests for twelvedata_provider.get_quote() with mocked HTTP."""

    _QUOTE_RESPONSE: ClassVar[dict[str, str]] = {
        "symbol": "RY",
        "exchange": "TSX",
        "close": "145.32",
        "open": "144.80",
        "high": "145.90",
        "low": "144.50",
        "volume": "2345678",
        "previous_close": "144.90",
        "change": "0.42",
        "percent_change": "0.29",
        "datetime": "2026-02-24 15:30:00",
    }

    @patch("finbot.services.realtime_data._providers.twelvedata_provider._get_api_key", return_value="testkey")
    @patch("finbot.services.realtime_data._providers.twelvedata_provider.RequestHandler")
    def test_get_quote_returns_quote(self, mock_handler_cls: MagicMock, _mock_key: MagicMock) -> None:
        from finbot.services.realtime_data._providers import twelvedata_provider

        mock_handler_cls.return_value.make_json_request.return_value = self._QUOTE_RESPONSE
        result = twelvedata_provider.get_quote("RY.TO")

        assert isinstance(result, Quote)
        assert result.symbol == "RY.TO"
        assert result.price == 145.32
        assert result.provider == QuoteProvider.TWELVEDATA
        assert result.exchange == Exchange.TSX

    @patch("finbot.services.realtime_data._providers.twelvedata_provider._get_api_key", return_value="testkey")
    @patch("finbot.services.realtime_data._providers.twelvedata_provider.RequestHandler")
    def test_get_quote_error_response(self, mock_handler_cls: MagicMock, _mock_key: MagicMock) -> None:
        from finbot.services.realtime_data._providers import twelvedata_provider

        mock_handler_cls.return_value.make_json_request.return_value = {
            "code": 400,
            "message": "Symbol not found",
        }
        with pytest.raises(ValueError, match="Twelve Data error"):
            twelvedata_provider.get_quote("INVALID")

    @patch("finbot.services.realtime_data._providers.twelvedata_provider._get_api_key", return_value="testkey")
    @patch("finbot.services.realtime_data._providers.twelvedata_provider.RequestHandler")
    def test_get_quotes_single(self, mock_handler_cls: MagicMock, _mock_key: MagicMock) -> None:
        from finbot.services.realtime_data._providers import twelvedata_provider

        mock_handler_cls.return_value.make_json_request.return_value = self._QUOTE_RESPONSE
        result = twelvedata_provider.get_quotes(["RY.TO"])
        assert "RY.TO" in result

    @patch("finbot.services.realtime_data._providers.twelvedata_provider._get_api_key", return_value="testkey")
    @patch("finbot.services.realtime_data._providers.twelvedata_provider.RequestHandler")
    def test_get_quotes_empty(self, mock_handler_cls: MagicMock, _mock_key: MagicMock) -> None:
        from finbot.services.realtime_data._providers import twelvedata_provider

        result = twelvedata_provider.get_quotes([])
        assert result == {}

    @patch("finbot.services.realtime_data._providers.twelvedata_provider._get_api_key", return_value="testkey")
    @patch("finbot.services.realtime_data._providers.twelvedata_provider.RequestHandler")
    def test_previous_close_parsed(self, mock_handler_cls: MagicMock, _mock_key: MagicMock) -> None:
        from finbot.services.realtime_data._providers import twelvedata_provider

        mock_handler_cls.return_value.make_json_request.return_value = self._QUOTE_RESPONSE
        result = twelvedata_provider.get_quote("RY.TO")
        assert result.previous_close == 144.90
        assert result.change == 0.42


# ── yfinance Provider ────────────────────────────────────────────────────────


class TestYfinanceProviderAvailability:
    """Tests for yfinance_provider.is_available()."""

    def test_always_available(self) -> None:
        from finbot.services.realtime_data._providers import yfinance_provider

        assert yfinance_provider.is_available() is True


class TestYfinanceProviderGetQuote:
    """Tests for yfinance_provider.get_quote() with mocked yfinance."""

    @patch("finbot.services.realtime_data._providers.yfinance_provider.yf")
    def test_get_quote_returns_quote(self, mock_yf: MagicMock) -> None:
        import pandas as pd

        from finbot.services.realtime_data._providers import yfinance_provider

        # Create mock history DataFrame
        idx = pd.DatetimeIndex([pd.Timestamp("2026-02-24 15:30", tz="US/Eastern")])
        history = pd.DataFrame(
            {"Close": [500.12], "Open": [499.50], "High": [501.00], "Low": [499.00], "Volume": [1234567]},
            index=idx,
        )
        mock_yf.Ticker.return_value.history.return_value = history

        result = yfinance_provider.get_quote("SPY")
        assert isinstance(result, Quote)
        assert result.symbol == "SPY"
        assert result.price == 500.12
        assert result.provider == QuoteProvider.YFINANCE
        assert result.volume == 1234567

    @patch("finbot.services.realtime_data._providers.yfinance_provider.yf")
    def test_get_quote_empty_history_raises(self, mock_yf: MagicMock) -> None:
        import pandas as pd

        from finbot.services.realtime_data._providers import yfinance_provider

        mock_yf.Ticker.return_value.history.return_value = pd.DataFrame()
        with pytest.raises(ValueError, match="No price data"):
            yfinance_provider.get_quote("INVALID")

    @patch("finbot.services.realtime_data._providers.yfinance_provider.yf")
    def test_get_quotes_multiple(self, mock_yf: MagicMock) -> None:
        import pandas as pd

        from finbot.services.realtime_data._providers import yfinance_provider

        idx = pd.DatetimeIndex([pd.Timestamp("2026-02-24 15:30", tz="US/Eastern")])
        history = pd.DataFrame(
            {"Close": [500.12], "Open": [499.50], "High": [501.00], "Low": [499.00], "Volume": [1234567]},
            index=idx,
        )
        mock_yf.Ticker.return_value.history.return_value = history

        result = yfinance_provider.get_quotes(["SPY", "QQQ"])
        assert len(result) == 2

    @patch("finbot.services.realtime_data._providers.yfinance_provider.yf")
    def test_get_quotes_handles_failure(self, mock_yf: MagicMock) -> None:
        import pandas as pd

        from finbot.services.realtime_data._providers import yfinance_provider

        mock_yf.Ticker.return_value.history.return_value = pd.DataFrame()
        result = yfinance_provider.get_quotes(["INVALID"])
        assert result == {}

    def test_detect_tsx_exchange(self) -> None:
        from finbot.services.realtime_data._providers.yfinance_provider import _detect_exchange

        assert _detect_exchange("RY.TO") == Exchange.TSX

    def test_detect_tsxv_exchange(self) -> None:
        from finbot.services.realtime_data._providers.yfinance_provider import _detect_exchange

        assert _detect_exchange("ABC.V") == Exchange.TSXV

    def test_detect_unknown_exchange(self) -> None:
        from finbot.services.realtime_data._providers.yfinance_provider import _detect_exchange

        assert _detect_exchange("SPY") == Exchange.UNKNOWN
