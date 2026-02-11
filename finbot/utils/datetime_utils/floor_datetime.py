"""Round datetime down (floor) to specified unit.

Rounds a datetime object down to the beginning of a specified time unit (year,
month, day, hour, minute, second, microsecond). For example, flooring to "month"
would return the first moment of that month (day=1, hour=0, minute=0, etc.).

Complements ceil_datetime.py for datetime rounding operations.

Supports datetime.datetime, datetime.date, and pandas.Timestamp inputs.

Typical usage:
    - Round query dates to period boundaries
    - Standardize time series to start-of-period values
    - Create time range buckets for aggregation
    - Ensure consistent datetime formatting
"""

import datetime
from typing import Literal

import pandas as pd


def floor_datetime(
    dt: datetime.datetime | datetime.date | pd.Timestamp,
    floor_target: Literal["year", "month", "day", "hour", "minute", "second", "microsecond"] = "day",
    tzinfo: datetime.tzinfo | None = None,
) -> datetime.datetime:
    """
    Floors a datetime object to the specified granularity.

    Args:
        dt (datetime.datetime | datetime.date | pd.Timestamp): The datetime object to be floored.
        floor_target (Literal["year", "month", "day", "hour", "minute", "second", "microsecond"], optional):
            The granularity to which the datetime object should be floored. Defaults to "day".
        tzinfo (datetime.tzinfo | None, optional): The timezone information to be applied to the floored datetime object.
            Defaults to None.

    Returns:
        datetime.datetime: The floored datetime object.

    Raises:
        TypeError: If dt is not a datetime.datetime, datetime.date, or pandas.Timestamp object.
        ValueError: If an invalid floor_target value is provided.
    """
    if not isinstance(dt, datetime.datetime | datetime.date | pd.Timestamp):
        raise TypeError("dt must be a datetime.datetime, datetime.date, or pandas.Timestamp object")

    if floor_target not in {
        "year",
        "month",
        "day",
        "hour",
        "minute",
        "second",
        "microsecond",
    }:
        raise ValueError(f"Invalid floor_to value: {floor_target}")

    # Convert to datetime.datetime if necessary
    if isinstance(dt, datetime.date) and not isinstance(dt, datetime.datetime):
        dt = datetime.datetime(dt.year, dt.month, dt.day)
    elif isinstance(dt, pd.Timestamp):
        dt = dt.to_pydatetime()

    floored_vals = {
        "year": 1,
        "month": 1,
        "day": 1,
        "hour": 0,
        "minute": 0,
        "second": 0,
        "microsecond": 0,
    }
    order = ["microsecond", "second", "minute", "hour", "day", "month", "year"]
    index = order.index(floor_target) + 1
    replace_args = {k: floored_vals[k] for k in order[:index]}
    return dt.replace(**replace_args, tzinfo=tzinfo)


if __name__ == "__main__":
    t = datetime.datetime(2021, 2, 15, 12, 34, 56, 789012)
    print(f"Unfloored:\t\t{t}")
    for i in ("year", "month", "day", "hour", "minute", "second", "microsecond")[::-1]:
        print(f"Floor {i}:\t{floor_datetime(t, i)}")  # type: ignore
