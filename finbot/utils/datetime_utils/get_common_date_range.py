"""Find exact common dates across multiple time series.

Identifies dates that exist in ALL provided pandas Series using index intersection.
More restrictive than get_overlapping_date_range.py which only requires time overlap.

Returns the min and max of the intersected dates, or None if no common dates exist.

Typical usage:
    - Ensure perfect date alignment before correlation analysis
    - Find trading days present in all data sources
    - Validate synchronized data collection
    - Merge time series with guaranteed no missing data
"""

import datetime as dt

import pandas as pd


def get_common_date_range(
    *series: pd.Series,
    raise_error: bool = True,
) -> tuple[pd.Timestamp | dt.date | None, pd.Timestamp | dt.date | None]:
    """
    Find the actual common date range among a list of pandas Series.
    This is the range where all series share the exact same dates.
    :param series: A variable number of pandas Series.
    :param raise_error: If True, raise an error if no common range exists.
    :return: A tuple containing the start and end dates of the common range, or None if no common range exists.
    """
    # Intersect the index of all series to find common dates
    common_dates = series[0].index
    for serie in series[1:]:
        common_dates = common_dates.intersection(serie.index)

    if len(common_dates) > 0:
        return common_dates.min(), common_dates.max()
    elif raise_error:
        raise ValueError("No common date range exists among the provided series.")
    else:
        return None, None
