"""Tests for backend JSON serialization helpers."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

import numpy as np
import pandas as pd
import pytest

from web.backend.services.serializers import (
    dataframe_to_records,
    sanitize_value,
    series_to_timeseries,
    stats_df_to_dict,
)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf"), np.float64("nan"), np.float64("inf")])
def test_sanitize_value_non_finite_numbers_to_none(value: float | np.floating) -> None:
    assert sanitize_value(value) is None


@pytest.mark.parametrize(
    ("value", "expected", "expected_type"),
    [
        (1.25, 1.25, float),
        (np.float64(1.25), 1.25, float),
        (np.int64(7), 7, int),
        (np.bool_(True), True, bool),
        (Decimal("12.34"), 12.34, float),
    ],
)
def test_sanitize_value_returns_json_safe_scalar_types(
    value: object,
    expected: object,
    expected_type: type[object],
) -> None:
    result = sanitize_value(value)
    assert result == expected
    assert isinstance(result, expected_type)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (datetime(2026, 6, 28, 9, 30, tzinfo=UTC), "2026-06-28T09:30:00+00:00"),
        (date(2026, 6, 28), "2026-06-28"),
        (pd.Timestamp("2026-06-28T09:30:00Z"), "2026-06-28T09:30:00+00:00"),
    ],
)
def test_sanitize_value_formats_dates(value: datetime | date | pd.Timestamp, expected: str) -> None:
    assert sanitize_value(value) == expected


def test_sanitize_value_recurses_into_numpy_arrays() -> None:
    value = np.array([1, np.nan, np.float64(2.5), np.int64(3)])

    assert sanitize_value(value) == [1, None, 2.5, 3]


def test_dataframe_to_records_uses_iso_date_key_and_sanitized_values() -> None:
    df = pd.DataFrame(
        {
            "price": [np.float64(101.5), np.nan],
            "volume": [np.int64(1000), np.int64(1200)],
        },
        index=pd.to_datetime(["2026-06-27", "2026-06-28"], utc=True),
    )

    assert dataframe_to_records(df) == [
        {"date": "2026-06-27T00:00:00+00:00", "price": 101.5, "volume": 1000},
        {"date": "2026-06-28T00:00:00+00:00", "price": None, "volume": 1200},
    ]


def test_dataframe_to_records_uses_index_key_for_string_and_numeric_indices() -> None:
    string_df = pd.DataFrame({"value": [np.inf]}, index=["SPY"])
    numeric_df = pd.DataFrame({"value": [Decimal("3.50")]}, index=[np.int64(7)])

    assert dataframe_to_records(string_df) == [{"index": "SPY", "value": None}]
    assert dataframe_to_records(numeric_df) == [{"index": 7, "value": 3.5}]


def test_dataframe_to_records_empty_input_returns_empty_list() -> None:
    assert dataframe_to_records(pd.DataFrame()) == []


def test_series_to_timeseries_preserves_name_dates_and_sanitized_values() -> None:
    series = pd.Series(
        [np.float64(1.5), np.nan],
        index=pd.to_datetime(["2026-06-27", "2026-06-28"], utc=True),
        name="portfolio",
    )

    assert series_to_timeseries(series) == {
        "name": "portfolio",
        "dates": ["2026-06-27T00:00:00+00:00", "2026-06-28T00:00:00+00:00"],
        "values": [1.5, None],
    }


def test_series_to_timeseries_explicit_name_and_empty_series() -> None:
    assert series_to_timeseries(pd.Series(dtype=float), name="empty") == {"name": "empty", "dates": [], "values": []}


def test_stats_df_to_dict_uses_first_row_and_sanitizes_values() -> None:
    stats_df = pd.DataFrame(
        [
            {"Sharpe": np.float64(1.25), "Max Drawdown": np.nan, "Trades": np.int64(5)},
            {"Sharpe": np.float64(2.0), "Max Drawdown": -0.1, "Trades": np.int64(9)},
        ]
    )

    assert stats_df_to_dict(stats_df) == {"Sharpe": 1.25, "Max Drawdown": None, "Trades": 5}


def test_stats_df_to_dict_empty_input_returns_empty_dict() -> None:
    assert stats_df_to_dict(pd.DataFrame()) == {}
