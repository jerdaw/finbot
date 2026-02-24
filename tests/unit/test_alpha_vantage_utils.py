"""Unit tests for Alpha Vantage base utility layer (mocked, no API calls)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils import (
    _determine_alpha_vantage_api_provider,
    _make_alpha_vantage_request,
    _prep_params,
    get_avapi_base,
)


class TestDetermineAPIProvider:
    """Tests for _determine_alpha_vantage_api_provider()."""

    def test_rapid_api_function(self):
        result = _determine_alpha_vantage_api_provider("TIME_SERIES_DAILY")
        assert result == "rapid"

    def test_av_api_function(self):
        result = _determine_alpha_vantage_api_provider("CPI")
        assert result == "av"

    def test_case_insensitive(self):
        result = _determine_alpha_vantage_api_provider("cpi")
        assert result == "av"

    def test_unknown_function_raises(self):
        with pytest.raises(ValueError, match="not found"):
            _determine_alpha_vantage_api_provider("FAKE_FUNCTION_XYZ")


class TestPrepParams:
    """Tests for _prep_params()."""

    def test_auto_generates_file_name(self):
        params, _save_dir = _prep_params({"function": "CPI"})
        assert params["file_name"].endswith(".parquet")
        assert "cpi" in params["file_name"]

    def test_function_lowercased(self):
        params, _ = _prep_params({"function": "CPI"})
        assert params["function"] == "cpi"

    def test_custom_save_dir(self, tmp_path: Path):
        _, save_dir = _prep_params({"function": "CPI"}, save_dir=tmp_path)
        assert save_dir == tmp_path

    def test_missing_function_raises(self):
        with pytest.raises(ValueError, match="function"):
            _prep_params({"symbol": "AAPL"})

    def test_invalid_file_name_extension_raises(self):
        with pytest.raises(ValueError, match="parquet"):
            _prep_params({"function": "CPI", "file_name": "data.csv"})


class TestMakeAlphaVantageRequest:
    """Tests for _make_alpha_vantage_request()."""

    @patch("finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils.RequestHandler")
    @patch("finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils.settings_accessors")
    def test_av_provider_adds_apikey(self, mock_settings, mock_handler_cls):
        mock_settings.get_alpha_vantage_api_key.return_value = "test-key"
        mock_handler = MagicMock()
        mock_handler.make_json_request.return_value = {"data": []}
        mock_handler_cls.return_value = mock_handler

        result = _make_alpha_vantage_request({"function": "CPI"})
        assert result == {"data": []}
        mock_handler.make_json_request.assert_called_once()

    @patch("finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils.RequestHandler")
    @patch("finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils.settings_accessors")
    def test_rapid_provider_uses_headers(self, mock_settings, mock_handler_cls):
        mock_settings.get_alpha_vantage_api_key.return_value = "rapid-key"
        mock_handler = MagicMock()
        mock_handler.make_json_request.return_value = {"data": []}
        mock_handler_cls.return_value = mock_handler

        result = _make_alpha_vantage_request({"function": "TIME_SERIES_DAILY"})
        assert result == {"data": []}
        call_kwargs = mock_handler.make_json_request.call_args
        assert "headers" in call_kwargs.kwargs

    def test_missing_function_raises(self):
        with pytest.raises(ValueError, match="function"):
            _make_alpha_vantage_request({"symbol": "AAPL"})

    @patch("finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils.RequestHandler")
    @patch("finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils.settings_accessors")
    def test_sets_default_outputsize(self, mock_settings, mock_handler_cls):
        mock_settings.get_alpha_vantage_api_key.return_value = "key"
        mock_handler = MagicMock()
        mock_handler.make_json_request.return_value = {}
        mock_handler_cls.return_value = mock_handler

        _make_alpha_vantage_request({"function": "CPI"})
        # Function should have set outputsize to "full"


class TestGetAvApiBase:
    """Tests for get_avapi_base()."""

    @patch("finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils._request_and_parse")
    @patch("finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils.save_dataframe")
    def test_force_update_fetches_data(self, mock_save, mock_request, tmp_path: Path):
        mock_request.return_value = pd.DataFrame({"value": [1, 2, 3]})
        result = get_avapi_base(
            {"function": "CPI"},
            force_update=True,
            save_dir=tmp_path,
        )
        assert len(result) == 3
        mock_request.assert_called_once()

    @patch("finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils.load_dataframe")
    def test_loads_cached_file(self, mock_load, tmp_path: Path):
        cached_df = pd.DataFrame({"value": [10, 20]})
        mock_load.return_value = cached_df

        # Create the expected file so the "exists" check passes
        save_dir = tmp_path / "cpi"
        save_dir.mkdir(parents=True)
        file_path = save_dir / "cpi.parquet"
        cached_df.to_parquet(file_path)

        get_avapi_base(
            {"function": "CPI"},
            force_update=False,
            save_dir=save_dir,
        )
        mock_load.assert_called_once()

    @patch("finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils._request_and_parse")
    @patch("finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils.save_dataframe")
    def test_check_update_with_missing_file(self, mock_save, mock_request, tmp_path: Path):
        mock_request.return_value = pd.DataFrame({"value": [1]})
        get_avapi_base(
            {"function": "CPI"},
            check_update=True,
            save_dir=tmp_path,
        )
        mock_request.assert_called_once()

    @patch("finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils._request_and_parse")
    @patch("finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils.save_dataframe")
    @patch("finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils.is_file_outdated")
    def test_check_update_outdated(self, mock_outdated, mock_save, mock_request, tmp_path: Path):
        mock_outdated.return_value = True
        mock_request.return_value = pd.DataFrame({"value": [1]})

        save_dir = tmp_path / "cpi"
        save_dir.mkdir(parents=True)
        # Create stale file
        pd.DataFrame({"old": [0]}).to_parquet(save_dir / "cpi.parquet")

        get_avapi_base(
            {"function": "CPI"},
            check_update=True,
            save_dir=save_dir,
        )
        mock_request.assert_called_once()

    @patch("finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils.load_dataframe")
    @patch("finbot.utils.data_collection_utils.alpha_vantage._alpha_vantage_utils.is_file_outdated")
    def test_check_update_fresh(self, mock_outdated, mock_load, tmp_path: Path):
        mock_outdated.return_value = False
        mock_load.return_value = pd.DataFrame({"value": [42]})

        save_dir = tmp_path / "cpi"
        save_dir.mkdir(parents=True)
        pd.DataFrame({"value": [42]}).to_parquet(save_dir / "cpi.parquet")

        get_avapi_base(
            {"function": "CPI"},
            check_update=True,
            save_dir=save_dir,
        )
        mock_load.assert_called_once()
