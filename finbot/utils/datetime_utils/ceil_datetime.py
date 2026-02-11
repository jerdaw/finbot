"""Round datetime up (ceiling) to specified unit.

Rounds a datetime object up to the end of a specified time unit (year, month,
day, hour, minute, second, microsecond). For example, ceiling to "month" would
return the last moment of that month (day=31, hour=23, minute=59, etc.).

Complements floor_datetime.py for datetime rounding operations.

Supports datetime.datetime, datetime.date, and pandas.Timestamp inputs.
Handles variable month lengths correctly.

Typical usage:
    - Round query dates to period boundaries
    - Standardize time series to end-of-period values
    - Create time range buckets for aggregation
    - Ensure consistent datetime formatting
"""

import datetime
from calendar import monthrange
from typing import Literal

import pandas as pd


def ceil_datetime(
    dt: datetime.datetime | datetime.date | pd.Timestamp,
    ceil_target: Literal["year", "month", "day", "hour", "minute", "second", "microsecond"] = "day",
    tzinfo: datetime.tzinfo | None = None,
) -> datetime.datetime:
    """
    Ceil a datetime object to the specified target unit.

    Args:
        dt: The datetime object to ceil.
        ceil_target: The target unit to ceil to. Valid values are "year", "month", "day", "hour", "minute", "second", "microsecond".
        tzinfo: Optional timezone information to apply to the resulting datetime object.

    Returns:
        The ceiled datetime object.

    Raises:
        TypeError: If dt is not a datetime.datetime, datetime.date, or pandas.Timestamp object.
        ValueError: If ceil_target is not a valid target unit.
    """
    if not isinstance(dt, datetime.datetime | datetime.date | pd.Timestamp):
        raise TypeError("dt must be a datetime.datetime, datetime.date, or pandas.Timestamp object")

    if ceil_target not in {"year", "month", "day", "hour", "minute", "second", "microsecond"}:
        raise ValueError(f"Invalid ceil_to value: {ceil_target}")

    # Convert to datetime.datetime if necessary
    if isinstance(dt, datetime.date) and not isinstance(dt, datetime.datetime):
        dt = datetime.datetime(dt.year, dt.month, dt.day)
    elif isinstance(dt, pd.Timestamp):
        dt = dt.to_pydatetime()

    ceil_vals = {
        "year": 9999,
        "month": 12,
        "day": monthrange(dt.year, dt.month)[1],
        "hour": 23,
        "minute": 59,
        "second": 59,
        "microsecond": 999999,
    }
    order = ["microsecond", "second", "minute", "hour", "day", "month", "year"]
    index = order.index(ceil_target) + 1
    replace_args = {k: ceil_vals[k] for k in order[:index]}
    updated_dt = dt.replace(**replace_args, tzinfo=tzinfo)
    if ceil_target in ["year", "month", "day"]:
        updated_dt = updated_dt.replace(day=monthrange(updated_dt.year, updated_dt.month)[1], tzinfo=tzinfo)
    return updated_dt


# Example usage
if __name__ == "__main__":
    t = datetime.datetime(2021, 2, 15, 12, 34, 56, 789012)
    print(f"Unceiled:\t\t{t}")
    for i in ("year", "month", "day", "hour", "minute", "second", "microsecond")[::-1]:
        print(f"Ceil {i}:\t{ceil_datetime(t, i)}")
