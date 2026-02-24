"""Unit tests for pandas utility functions."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from finbot.utils.pandas_utils.get_data_mask import get_data_mask
from finbot.utils.pandas_utils.get_frequency_per_year import (
    get_frequency_per_interval,
)
from finbot.utils.pandas_utils.merge_data_on_closest_date import (
    merge_data_on_closest_date,
)


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


class TestGetDataMask:
    """Tests for get_data_mask()."""

    def test_series_with_callable_criteria(self):
        s = pd.Series([1, 5, 10, 15, 20])
        mask = get_data_mask(s, lambda x: x > 10)
        assert mask[0].iloc[3] is np.True_
        assert mask[0].iloc[0] is np.False_

    def test_dataframe_with_callable_criteria(self):
        df = pd.DataFrame({"A": [1, 2, 3], "B": [10, 20, 30]})
        mask = get_data_mask(df, lambda x: x > 5)
        assert mask["A"].iloc[0] is np.False_
        assert mask["B"].iloc[0] is np.True_

    def test_dict_criteria_per_column(self):
        df = pd.DataFrame({"A": [1, 10], "B": [5, 50]})
        criteria = {"A": lambda x: x > 5, "B": lambda x: x > 20}
        mask = get_data_mask(df, criteria)
        assert mask["A"].iloc[0] is np.False_
        assert mask["A"].iloc[1] is np.True_
        assert mask["B"].iloc[0] is np.False_
        assert mask["B"].iloc[1] is np.True_

    def test_vectorized_mode(self):
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        mask = get_data_mask(df, lambda col: col > 2, use_vectorization=True)
        assert mask["A"].iloc[2] is np.True_

    def test_missing_column_in_dict_criteria_ignored(self):
        df = pd.DataFrame({"A": [1, 2]})
        criteria = {"A": lambda x: x > 1, "Z": lambda x: x > 0}
        mask = get_data_mask(df, criteria)
        assert mask["A"].iloc[0] is np.False_
        assert mask["A"].iloc[1] is np.True_

    def test_invalid_type_raises_type_error(self):
        with pytest.raises(TypeError):
            get_data_mask("not a dataframe", lambda x: x > 0)  # type: ignore[arg-type]


class TestGetFrequencyPerInterval:
    """Tests for get_frequency_per_interval()."""

    def test_daily_data_yearly_interval_mode(self):
        dates = pd.bdate_range("2020-01-01", "2022-12-31")
        df = pd.DataFrame({"price": range(len(dates))}, index=dates)
        result = get_frequency_per_interval(df, pd.DateOffset(years=1), method="mode")
        assert result is not None
        assert 250 <= result <= 263

    def test_daily_data_yearly_interval_mean(self):
        dates = pd.bdate_range("2020-01-01", "2022-12-31")
        df = pd.DataFrame({"price": range(len(dates))}, index=dates)
        result = get_frequency_per_interval(df, pd.DateOffset(years=1), method="mean")
        assert result is not None
        assert 250 <= result <= 265

    def test_too_few_rows_returns_none(self):
        df = pd.DataFrame({"price": [100]}, index=pd.to_datetime(["2020-01-01"]))
        result = get_frequency_per_interval(df, pd.DateOffset(years=1))
        assert result is None

    def test_invalid_method_raises_value_error(self):
        dates = pd.bdate_range("2020-01-01", "2022-12-31")
        df = pd.DataFrame({"price": range(len(dates))}, index=dates)
        with pytest.raises(ValueError, match="method"):
            get_frequency_per_interval(df, pd.DateOffset(years=1), method="median")

    def test_insufficient_data_raises_value_error(self):
        dates = pd.bdate_range("2020-01-01", "2020-06-30")
        df = pd.DataFrame({"price": range(len(dates))}, index=dates)
        with pytest.raises(ValueError, match="full period"):
            get_frequency_per_interval(df, pd.DateOffset(years=1))

    def test_last_method(self):
        dates = pd.bdate_range("2020-01-01", "2022-12-31")
        df = pd.DataFrame({"price": range(len(dates))}, index=dates)
        result = get_frequency_per_interval(df, pd.DateOffset(years=1), method="last")
        assert result is not None
        assert result > 200


class TestMergeDataOnClosestDate:
    """Tests for merge_data_on_closest_date()."""

    def test_basic_merge(self):
        monthly = pd.DataFrame(
            {"val": [1, 2]},
            index=pd.to_datetime(["2022-01-01", "2022-02-01"]),
        )
        daily = pd.DataFrame(
            {"price": [100, 200, 300]},
            index=pd.to_datetime(["2022-01-02", "2022-01-15", "2022-02-03"]),
        )
        result = merge_data_on_closest_date(monthly, daily)
        assert len(result) == 2
        assert "price" in result.columns

    def test_column_subset(self):
        monthly = pd.DataFrame(
            {"val": [1]},
            index=pd.to_datetime(["2022-01-01"]),
        )
        daily = pd.DataFrame(
            {"price": [100], "volume": [1000]},
            index=pd.to_datetime(["2022-01-02"]),
        )
        result = merge_data_on_closest_date(monthly, daily, columns_to_merge=["price"])
        assert "price" in result.columns
        assert "volume" not in result.columns

    def test_non_datetime_index_raises_value_error(self):
        index_df = pd.DataFrame({"val": [1]}, index=[0])
        value_df = pd.DataFrame({"price": [100]}, index=pd.to_datetime(["2022-01-01"]))
        with pytest.raises(ValueError, match="DatetimeIndex"):
            merge_data_on_closest_date(index_df, value_df)

    def test_value_df_non_datetime_raises_value_error(self):
        index_df = pd.DataFrame({"val": [1]}, index=pd.to_datetime(["2022-01-01"]))
        value_df = pd.DataFrame({"price": [100]}, index=[0])
        with pytest.raises(ValueError, match="DatetimeIndex"):
            merge_data_on_closest_date(index_df, value_df)

    def test_result_has_index_df_dates(self):
        monthly_dates = pd.to_datetime(["2022-01-01", "2022-02-01", "2022-03-01"])
        monthly = pd.DataFrame({"val": [1, 2, 3]}, index=monthly_dates)
        daily = pd.DataFrame(
            {"price": range(90)},
            index=pd.bdate_range("2022-01-01", periods=90),
        )
        result = merge_data_on_closest_date(monthly, daily)
        pd.testing.assert_index_equal(result.index, monthly_dates)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
