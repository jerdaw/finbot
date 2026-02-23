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


class TestSaveDataFrames:
    """Tests for batched save/load helper utilities."""

    def test_save_dataframes_with_save_dir_only(self, tmp_path: Path):
        """save_dataframes should support save_dir-only calls."""
        from finbot.utils.pandas_utils.load_dataframes import load_dataframes
        from finbot.utils.pandas_utils.save_dataframes import save_dataframes

        dfs = [
            pd.DataFrame({"A": [1, 2], "B": [3.0, 4.0]}),
            pd.DataFrame({"A": [5, 6], "B": [7.0, 8.0]}),
        ]
        save_dataframes(dataframes=dfs, save_dir=tmp_path)

        saved_paths = sorted(tmp_path.glob("*.parquet"))
        assert len(saved_paths) == 2

        loaded_dfs = load_dataframes(saved_paths)
        assert len(loaded_dfs) == 2

    def test_save_dataframes_length_mismatch_raises(self, tmp_path: Path):
        """save_dataframes should validate dataframe/file path cardinality."""
        from finbot.utils.pandas_utils.save_dataframes import save_dataframes

        df = pd.DataFrame({"A": [1], "B": [2.0]})
        with pytest.raises(ValueError, match="must match the number of file paths"):
            save_dataframes(
                dataframes=[df],
                file_paths=[tmp_path / "a.parquet", tmp_path / "b.parquet"],
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
