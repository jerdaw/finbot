"""Unit tests for Yahoo Finance base utility layer (mocked, no API calls)."""

from __future__ import annotations

import datetime

import pandas as pd
import pytest
from dateutil.relativedelta import relativedelta

from finbot.utils.data_collection_utils.yfinance._yfinance_utils import (
    _filter_yfinance_data,
    _get_yf_req_params,
    _map_yf_time_strs_to_relativedelta,
    _prep_params,
)


class TestGetYfReqParams:
    """Tests for _get_yf_req_params()."""

    def test_default_params(self):
        params = _get_yf_req_params()
        assert params["period"] == "max"
        assert params["interval"] == "1d"
        assert params["prepost"] is False

    def test_override_period(self):
        params = _get_yf_req_params(period="1y")
        assert params["period"] == "1y"

    def test_override_interval(self):
        params = _get_yf_req_params(interval="1h")
        assert params["interval"] == "1h"

    def test_all_keys_present(self):
        params = _get_yf_req_params()
        expected_keys = {
            "period",
            "interval",
            "start",
            "end",
            "prepost",
            "auto_adjust",
            "actions",
            "progress",
            "group_by",
            "threads",
        }
        assert expected_keys.issubset(params.keys())


class TestMapYfTimeStrs:
    """Tests for _map_yf_time_strs_to_relativedelta()."""

    def test_days(self):
        result = _map_yf_time_strs_to_relativedelta("5d")
        assert result == relativedelta(days=5)

    def test_months(self):
        result = _map_yf_time_strs_to_relativedelta("3mo")
        assert result == relativedelta(months=3)

    def test_years(self):
        result = _map_yf_time_strs_to_relativedelta("1y")
        assert result == relativedelta(years=1)

    def test_weeks(self):
        result = _map_yf_time_strs_to_relativedelta("2wk")
        assert result == relativedelta(weeks=2)

    def test_invalid_suffix_raises(self):
        with pytest.raises(ValueError, match="Invalid time string"):
            _map_yf_time_strs_to_relativedelta("5x")


class TestPrepParamsYF:
    """Tests for _prep_params() (yfinance)."""

    def test_single_symbol_uppercased(self):
        symbols, _, _ = _prep_params("spy", datetime.date(2020, 1, 1), None, "1d", "history")
        assert symbols == ["SPY"]

    def test_list_symbols_sorted_deduped(self):
        symbols, _, _ = _prep_params(["qqq", "spy", "spy"], datetime.date(2020, 1, 1), None, "1d", "history")
        assert symbols == ["QQQ", "SPY"]

    def test_end_date_defaults_to_today(self):
        _, _, end_date = _prep_params("SPY", datetime.date(2020, 1, 1), None, "1d", "history")
        assert end_date == datetime.date.today()

    def test_datetime_converted_to_date(self):
        dt = datetime.datetime(2020, 6, 15, 12, 30, 0)
        _, start, _ = _prep_params("SPY", dt, None, "1d", "history")
        assert isinstance(start, datetime.date)
        assert not isinstance(start, datetime.datetime)

    def test_invalid_interval_raises(self):
        with pytest.raises(ValueError, match="interval"):
            _prep_params("SPY", datetime.date(2020, 1, 1), None, "invalid", "history")

    def test_invalid_request_type_raises(self):
        with pytest.raises(ValueError, match="request_type"):
            _prep_params("SPY", datetime.date(2020, 1, 1), None, "1d", "invalid")


class TestFilterYfinanceData:
    """Tests for _filter_yfinance_data()."""

    def test_filters_by_date_range(self):
        dates = pd.date_range("2020-01-01", "2020-12-31", freq="D")
        df = pd.DataFrame({"price": range(len(dates))}, index=dates)
        result = _filter_yfinance_data(df, datetime.date(2020, 6, 1), datetime.date(2020, 6, 30), "1d", False)
        assert result.index.min().date() >= datetime.date(2020, 6, 1)
        assert result.index.max().date() <= datetime.date(2020, 6, 30)

    def test_non_datetime_index_returns_unchanged(self):
        df = pd.DataFrame({"price": [1, 2, 3]}, index=[0, 1, 2])
        result = _filter_yfinance_data(df, datetime.date(2020, 1, 1), datetime.date(2020, 12, 31), "1d", False)
        assert len(result) == 3

    def test_daily_interval_no_time_filter(self):
        dates = pd.date_range("2020-01-01", periods=5, freq="D")
        df = pd.DataFrame({"price": range(5)}, index=dates)
        result = _filter_yfinance_data(df, datetime.date(2020, 1, 1), datetime.date(2020, 1, 10), "1d", False)
        assert len(result) == 5

    def test_prepost_true_no_time_filter(self):
        # Even intraday intervals shouldn't filter when prepost=True
        dates = pd.date_range("2020-01-02 08:00", periods=10, freq="h")
        df = pd.DataFrame({"price": range(10)}, index=dates)
        result = _filter_yfinance_data(df, datetime.date(2020, 1, 1), datetime.date(2020, 1, 3), "1h", True)
        assert len(result) == 10
