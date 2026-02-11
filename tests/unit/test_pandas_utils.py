"""Unit tests for pandas utility functions."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pytest


class TestSaveLoadDataFrame:
    """Tests for DataFrame save/load operations."""

    def test_save_load_parquet(self):
        """Test saving and loading DataFrame as parquet."""
        from finbot.utils.pandas_utils.load_dataframe import load_dataframe
        from finbot.utils.pandas_utils.save_dataframe import save_dataframe

        df = pd.DataFrame({"A": [1, 2, 3], "B": [4.0, 5.0, 6.0]})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.parquet"
            save_dataframe(df, path)
            loaded = load_dataframe(path)

            pd.testing.assert_frame_equal(df, loaded)

    def test_load_dataframe_import(self):
        """Test that load_dataframe can be imported."""
        from finbot.utils.pandas_utils.load_dataframe import load_dataframe

        assert callable(load_dataframe)


class TestFilterByDate:
    """Tests for date filtering operations."""

    def test_filter_by_date_import(self):
        """Test that filter_by_date can be imported."""
        from finbot.utils.pandas_utils.filter_by_date import filter_by_date

        assert callable(filter_by_date)


class TestGetTimeseriesFrequency:
    """Tests for detecting time series frequency."""

    def test_get_timeseries_frequency_import(self):
        """Test that get_timeseries_frequency can be imported."""
        from finbot.utils.pandas_utils.get_timeseries_frequency import get_timeseries_frequency

        assert callable(get_timeseries_frequency)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
