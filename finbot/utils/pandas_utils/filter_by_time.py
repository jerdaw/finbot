"""Filter DataFrame by time-of-day range.

Filters pandas DataFrame or Series to specific times of day (e.g., market hours).
Requires DatetimeIndex with time information, not just dates.

Complements filter_by_date.py which filters by date range.

Typical usage:
    - Filter to market hours (9:30 AM - 4:00 PM)
    - Extract intraday trading data
    - Remove after-hours data
    - Analyze specific time windows
"""

import datetime as dt

import pandas as pd

from finbot.utils.validation_utils.validation_helpers import validate_types


def filter_by_time(
    df: pd.DataFrame | pd.Series,
    start_time: dt.time | None,
    end_time: dt.time | None,
) -> pd.DataFrame | pd.Series:
    """
    Filters the given DataFrame based on the start and end times of day.

    Args:
        df (pd.DataFrame | pd.Series): The DataFrame to be filtered.
        start_time (datetime.time): The start time of day for filtering.
        end_time (datetime.time): The end time of day for filtering.

    Returns:
        pd.DataFrame | pd.Series: The filtered DataFrame.
    """

    # Ensure the index is a DatetimeIndex with a time component
    if not isinstance(df.index, pd.DatetimeIndex) and "Date" in df.columns:
        df = df.set_index(pd.DatetimeIndex(df["Date"]))
    if not isinstance(df.index, pd.DatetimeIndex) or not hasattr(df.index, "time"):
        raise ValueError("DataFrame index must be a DatetimeIndex with a time component")
    validate_types(start_time, "start_time", [dt.time, type(None)])
    validate_types(end_time, "end_time", [dt.time, type(None)])

    # Filtering logic based on time
    if start_time is not None or end_time is not None:
        if start_time:
            df = df.loc[df.index.time >= start_time]
        if end_time:
            df = df.loc[df.index.time <= end_time]  # type: ignore

    return df


if __name__ == "__main__":
    # Example usage of filter_by_time

    # Create a sample DataFrame with datetime index
    dates = pd.date_range(start="2023-01-01", end="2023-01-07", freq="H")
    data = range(len(dates))
    df = pd.DataFrame(data, index=dates, columns=["Value"])

    # Define start and end times for filtering
    start_time = dt.time(9, 0)
    end_time = dt.time(9, 20)

    # Filter the DataFrame
    filtered_df = filter_by_time(df, start_time, end_time)

    # Display the original and filtered DataFrames
    print("Original:")
    print(df)
    print("\nFiltered:")
    print(filtered_df)
