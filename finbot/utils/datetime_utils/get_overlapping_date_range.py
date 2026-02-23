"""Find overlapping date range across multiple time series.

Identifies the maximum date range where ALL provided pandas Series have data.
Returns the latest start date and earliest end date across all series.

Different from get_common_date_range.py which requires exact matching dates.
This function finds where series overlap in time, even if they have different
frequencies or missing dates.

Typical usage:
    - Align multiple time series before merging
    - Find valid comparison period for backtest vs benchmark
    - Ensure all data sources cover a common time period
    - Filter data to overlapping range before analysis
"""

import datetime as dt

import pandas as pd


def get_overlapping_date_range(
    *series: pd.Series,
    raise_error: bool = True,
) -> tuple[pd.Timestamp | dt.date, pd.Timestamp | dt.date]:
    """
    Find the overlapping date range among a list of pandas Series.
    This is the range where all series have data.
    :param series: A variable number of pandas Series.
    :param raise_error: If True, raise an error if no overlapping range exists.
    :return: A tuple containing the start and end dates of the overlapping range.
    """
    start_date: pd.Timestamp | dt.date = max(serie.index.min() for serie in series)
    end_date: pd.Timestamp | dt.date = min(serie.index.max() for serie in series)

    if raise_error and start_date > end_date:
        raise ValueError("No overlapping date range exists among the provided series.")

    return start_date, end_date
