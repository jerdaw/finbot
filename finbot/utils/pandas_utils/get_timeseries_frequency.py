"""Detect time series frequency automatically with outlier removal.

Analyzes time series DatetimeIndex to determine update frequency (daily,
weekly, monthly, etc.). Uses sophisticated approach with outlier removal
and fallback calculations for irregular data.

Returns frequency in multiple formats:
    - 'str': Pandas frequency string (e.g., 'D', 'W', 'M')
    - 'timedelta': pandas.Timedelta for fixed frequencies
    - 'relativedelta': dateutil.relativedelta for calendar frequencies

Handles edge cases:
    - Removes outlier time differences before analysis
    - Supports direct matching against common frequencies
    - Falls back to average-based calculation
    - Caches pandas offset conversions for performance

Used by get_periods_per_year.py and various data processing functions.

Typical usage:
    - Validate data collection frequency
    - Auto-detect resampling frequency
    - Verify expected data cadence
    - Support frequency-aware operations
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache

import pandas as pd
from dateutil.relativedelta import relativedelta
from pandas.tseries.frequencies import to_offset

from config import logger
from finbot.utils.data_science_utils.data_cleaning.outlier_handlers.get_outliers_quantile import get_outliers_quantile
from finbot.utils.datetime_utils.conversions.convert_frequency import convert_frequency
from finbot.utils.datetime_utils.conversions.str_to_timedelta import str_to_timedelta
from finbot.utils.datetime_utils.conversions.timedelta_to_str import timedelta_to_str


@lru_cache(maxsize=128)
def cached_to_offset(freq: str):
    return to_offset(freq)


def match_frequency(
    time_differences: pd.Series,
    return_type: str,
    common_frequencies: list,
    freq_counter: Counter,
    raise_error: bool = True,
) -> pd.Timedelta | relativedelta | str | None:
    """
    Attempts to match the most common frequency in the time series data.

    Args:
        time_differences (pd.Series): Series of time differences.
        return_type (str): The desired return type ('str', 'timedelta', or 'relativedelta').
        common_frequencies (list): List of common frequencies to check against.
        raise_error (bool): Whether to raise an error if no match is found. Defaults to True.

    Returns:
        str: The matched frequency or None if no match is found.
    """
    most_common_timedelta, _ = freq_counter.most_common(1)[0]

    if return_type == "str":
        for freq in common_frequencies:
            if cached_to_offset(freq) == most_common_timedelta:
                return freq
    else:
        most_common_offset = cached_to_offset(timedelta_to_str(most_common_timedelta))
        matching_freq_str = next(
            (freq for freq in common_frequencies if cached_to_offset(freq) == most_common_offset),
            "",
        )

        converted_freq = convert_frequency(matching_freq_str, return_type)

        if converted_freq:
            return converted_freq

    if raise_error:
        raise ValueError("Unable to determine DatetimeIndex update frequency")
    return None


def fallback_frequency_calculation(
    time_differences: pd.Series,
    return_type: str,
    common_frequencies: list,
    freq_counter: Counter,
    raise_error: bool = True,
):
    """
    Calculates the fallback frequency when a direct match is not found.
    Calculation is based on the average time difference between updates.

    Args:
        time_differences (pd.Series): Series of time differences.
        return_type (str): The desired return type ('str', 'timedelta', or 'relativedelta').
        common_frequencies (list): List of common frequencies to check against.
        raise_error (bool): Whether to raise an error if no match is found. Defaults to True.

    Returns:
        The closest frequency in the specified return type.
    """
    total_seconds = sum((td.total_seconds() * count for td, count in freq_counter.items()))
    average_diff = pd.Timedelta(seconds=total_seconds / sum(freq_counter.values()))
    threshold = average_diff * 0.1
    common_freq_timedeltas = [str_to_timedelta(freq) for freq in common_frequencies]

    closest_timedelta = min(common_freq_timedeltas, key=lambda f: abs(f - average_diff))

    if abs(closest_timedelta - average_diff) > threshold:
        return "Irregular" if return_type == "str" else convert_frequency("", return_type)

    closest_freq = next(
        (freq for freq, td in zip(common_frequencies, common_freq_timedeltas, strict=False) if td == closest_timedelta),
        "",
    )

    if not closest_freq and raise_error:
        raise ValueError("Unable to determine DatetimeIndex update frequency")

    return closest_freq if return_type == "str" else convert_frequency(closest_freq, return_type)


def get_timeseries_frequency(
    time_series: pd.DataFrame | pd.Series | pd.DatetimeIndex | list | tuple,
    return_type: str = "relativedelta",
    permit_fallback: bool = False,
) -> str | pd.Timedelta | relativedelta:
    """
    Detects the frequency of updates in a time series.

    Args:
        time_series (pd.Series | pd.DataFrame | pd.DatetimeIndex | list | tuple):
            A time series data structure.
        return_type (str): The type of the return value ('str', 'timedelta', or 'relativedelta').
        permit_fallback (bool): Whether to permit the fallback calculation. Defaults to False.

    Returns:
        str: The most common frequency in the specified return type.
    """
    logger.info("Analyzing time series frequency.")

    if time_series.empty if isinstance(time_series, pd.DataFrame | pd.Series | pd.DatetimeIndex) else not time_series:
        raise ValueError("time_series must not be empty")

    if isinstance(time_series, pd.DatetimeIndex):
        index = time_series
    elif isinstance(time_series, pd.DataFrame | pd.Series) and isinstance(time_series.index, pd.DatetimeIndex):
        index = time_series.index
    else:
        try:
            index = pd.DatetimeIndex(time_series)  # type: ignore
        except ValueError as e:
            raise TypeError("time_series must have a pd.DateTimeIndex or be convertible to one.") from e

    common_frequencies = ["S", "T", "H", "D", "W", "M", "Q", "A"]

    time_differences = pd.Series(get_outliers_quantile(index.to_series().diff().dropna(), remove=True))
    if not time_differences.any():
        raise ValueError("Unable to determine DatetimeIndex update frequency")

    freq_counter = Counter(time_differences)

    direct_match = match_frequency(time_differences, return_type, common_frequencies, freq_counter)
    if direct_match:
        logger.info(f"Direct frequency match found: {direct_match}")
        return direct_match

    if permit_fallback:
        logger.info("No direct match found, proceeding to fallback calculation.")
        fallback = fallback_frequency_calculation(time_differences, return_type, common_frequencies, freq_counter)

        if fallback:
            logger.info(f"Fallback frequency match found: {fallback}")
            return fallback

    raise ValueError("Unable to determine DatetimeIndex update frequency")


if __name__ == "__main__":
    from time import perf_counter

    from constants.path_constants import DATA_DIR
    from finbot.utils.pandas_utils.load_dataframe import load_dataframe

    MAX_DFS = 10000

    # Resurse DATA_DIR and add any .parquet files to a set
    potential_df_paths = sorted(DATA_DIR.rglob("*.parquet"))

    total_analysis_time = float("0")
    n_analyzed = 0
    n_failed = 0

    for path in potential_df_paths:
        try:
            df = load_dataframe(path)
            idx = pd.DatetimeIndex(df.index)
            start = perf_counter()
            get_timeseries_frequency(idx)
            total_analysis_time += perf_counter() - start
            n_analyzed += 1
        except ValueError:
            n_failed += 1
        if n_analyzed >= MAX_DFS:
            break

    print(
        f"Analyzed {n_analyzed}/{len(potential_df_paths)} files in {total_analysis_time:.2f} seconds, with an average of {total_analysis_time / n_analyzed:.4f} seconds per DataFrame.",
    )
