import datetime as dt

import pandas as pd

from finbot.utils.validation_utils.validation_helpers import validate_types


def filter_by_date(
    df: pd.DataFrame | pd.Series,
    start_date: dt.date | None,
    end_date: dt.date | None,
) -> pd.DataFrame | pd.Series:
    """
    Filters the given DataFrame based on the start and end dates.

    Args:
        df (pd.DataFrame | pd.Series): The DataFrame to be filtered.
        start_date (datetime.date): The start date for filtering.
        end_date (datetime.date): The end date for filtering.

    Returns:
        pd.DataFrame: The filtered DataFrame.
    """
    # Enesure the index is a DatetimeIndex
    if not isinstance(df.index, pd.DatetimeIndex) and "Date" in df.columns:
        df = df.set_index(pd.DatetimeIndex(df["Date"]))
    validate_types(df.index, "df.index", [pd.DatetimeIndex])
    validate_types(start_date, "start_date", [dt.date, type(None)])
    validate_types(end_date, "end_date", [dt.date, type(None)])

    if start_date:
        start_date = max(pd.Timestamp(start_date), df.index.min())
        df = df.loc[df.index >= start_date]

    if end_date:
        end_date = min(pd.Timestamp(end_date), df.index.max())
        df = df.loc[df.index <= end_date]

    return df


if __name__ == "__main__":
    from constants.data_constants import DEMO_DATA

    start_dt = dt.date(2021, 1, 1)
    end_dt = dt.date(2021, 1, 10)
    filtered_data = filter_by_date(DEMO_DATA["Close"], start_date=start_dt, end_date=end_dt)
    print(f"Start date: {start_dt}, End date: {end_dt}")
    print(filtered_data)
