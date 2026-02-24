"""Unit tests for representative Alpha Vantage wrapper functions (mocked)."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
import pytest


class TestGetCPI:
    """Tests for get_cpi() wrapper."""

    @patch("finbot.utils.data_collection_utils.alpha_vantage.cpi.get_avapi_base")
    def test_default_monthly(self, mock_base):
        from finbot.utils.data_collection_utils.alpha_vantage.cpi import get_cpi

        mock_base.return_value = pd.DataFrame({"value": [100, 101]})
        result = get_cpi()
        assert len(result) == 2
        call_kwargs = mock_base.call_args
        assert call_kwargs.kwargs["req_params"]["interval"] == "monthly"

    @patch("finbot.utils.data_collection_utils.alpha_vantage.cpi.get_avapi_base")
    def test_semiannual_interval(self, mock_base):
        from finbot.utils.data_collection_utils.alpha_vantage.cpi import get_cpi

        mock_base.return_value = pd.DataFrame({"value": [100]})
        get_cpi(interval="semiannual")
        call_kwargs = mock_base.call_args
        assert call_kwargs.kwargs["req_params"]["interval"] == "semiannual"

    def test_invalid_interval_raises(self):
        from finbot.utils.data_collection_utils.alpha_vantage.cpi import get_cpi

        with pytest.raises(ValueError):
            get_cpi(interval="yearly")  # type: ignore[arg-type]

    @patch("finbot.utils.data_collection_utils.alpha_vantage.cpi.get_avapi_base")
    def test_passes_flags(self, mock_base):
        from finbot.utils.data_collection_utils.alpha_vantage.cpi import get_cpi

        mock_base.return_value = pd.DataFrame()
        get_cpi(check_update=True, force_update=True)
        call_kwargs = mock_base.call_args.kwargs
        assert call_kwargs["check_update"] is True
        assert call_kwargs["force_update"] is True


class TestGetTreasuryYields:
    """Tests for get_treasury_yields() wrapper."""

    @patch("finbot.utils.data_collection_utils.alpha_vantage.treasury_yields.get_avapi_base")
    def test_single_maturity(self, mock_base):
        from finbot.utils.data_collection_utils.alpha_vantage.treasury_yields import (
            get_treasury_yields,
        )

        mock_base.return_value = pd.DataFrame(
            {"value": [1.5, 1.6]},
            index=pd.to_datetime(["2020-01-01", "2020-01-02"]),
        )
        result = get_treasury_yields(maturity="10year")
        assert "10year" in result.columns

    @patch("finbot.utils.data_collection_utils.alpha_vantage.treasury_yields.get_avapi_base")
    def test_all_maturities(self, mock_base):
        from finbot.utils.data_collection_utils.alpha_vantage.treasury_yields import (
            get_treasury_yields,
        )

        mock_base.return_value = pd.DataFrame(
            {"value": [1.0]},
            index=pd.to_datetime(["2020-01-01"]),
        )
        get_treasury_yields(maturity="all")
        assert mock_base.call_count == 6  # 6 maturities

    def test_invalid_maturity_raises(self):
        from finbot.utils.data_collection_utils.alpha_vantage.treasury_yields import (
            get_treasury_yields,
        )

        with pytest.raises(ValueError):
            get_treasury_yields(maturity="1year")  # type: ignore[arg-type]

    def test_invalid_interval_raises(self):
        from finbot.utils.data_collection_utils.alpha_vantage.treasury_yields import (
            get_treasury_yields,
        )

        with pytest.raises(ValueError):
            get_treasury_yields(interval="yearly")  # type: ignore[arg-type]


class TestGetGlobalQuote:
    """Tests for get_global_quote() wrapper."""

    @patch("finbot.utils.data_collection_utils.alpha_vantage.global_quote._make_alpha_vantage_request")
    def test_parses_response(self, mock_request):
        from finbot.utils.data_collection_utils.alpha_vantage.global_quote import (
            get_global_quote,
        )

        mock_request.return_value = {
            "Global Quote": {
                "01. symbol": "SPY",
                "02. open": "450.00",
                "05. price": "455.00",
            },
        }
        result = get_global_quote("SPY")
        assert isinstance(result, pd.DataFrame)
        assert "symbol" in result.columns
        assert "price" in result.columns

    @patch("finbot.utils.data_collection_utils.alpha_vantage.global_quote._make_alpha_vantage_request")
    def test_empty_response_raises(self, mock_request):
        from finbot.utils.data_collection_utils.alpha_vantage.global_quote import (
            get_global_quote,
        )

        mock_request.return_value = {"Global Quote": {}}
        with pytest.raises(ValueError, match="No data returned"):
            get_global_quote("FAKE")

    @patch("finbot.utils.data_collection_utils.alpha_vantage.global_quote._make_alpha_vantage_request")
    def test_symbol_uppercased(self, mock_request):
        from finbot.utils.data_collection_utils.alpha_vantage.global_quote import (
            get_global_quote,
        )

        mock_request.return_value = {
            "Global Quote": {"01. symbol": "SPY", "02. open": "100"},
        }
        get_global_quote("spy")
        call_args = mock_request.call_args[0][0]
        assert call_args["symbol"] == "SPY"


class TestGetInflation:
    """Tests for get_inflation() wrapper."""

    @patch("finbot.utils.data_collection_utils.alpha_vantage.inflation.get_avapi_base")
    def test_returns_dataframe(self, mock_base):
        from finbot.utils.data_collection_utils.alpha_vantage.inflation import (
            get_inflation,
        )

        mock_base.return_value = pd.DataFrame({"value": [2.1, 2.3]})
        result = get_inflation()
        assert isinstance(result, pd.DataFrame)

    @patch("finbot.utils.data_collection_utils.alpha_vantage.inflation.get_avapi_base")
    def test_passes_function_param(self, mock_base):
        from finbot.utils.data_collection_utils.alpha_vantage.inflation import (
            get_inflation,
        )

        mock_base.return_value = pd.DataFrame()
        get_inflation()
        call_kwargs = mock_base.call_args.kwargs
        assert call_kwargs["req_params"]["function"] == "INFLATION"
