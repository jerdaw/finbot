"""Check if datetime belongs to a specific period (monthly, quarterly, etc.).

Determines whether a datetime falls within a specified period type (e.g., "monthly",
"quarterly") relative to the current time. Optionally aligns the comparison to
period starts.

Uses normalize_dt.py for period boundary calculations.

Typical usage:
    - Filter data to specific periods (current month, current quarter)
    - Validate datetime is within expected period
    - Implement period-based business logic
    - Schedule actions for specific time periods
"""

from __future__ import annotations

from datetime import datetime

from dateutil.relativedelta import relativedelta

from finbot.utils.datetime_utils.normalize_dt import normalize_dt


def is_datetime_in_period(
    datetime_obj: datetime,
    time_period: str | relativedelta,
    align_to_period_start: bool = False,
) -> bool:
    """
    Check if a given datetime object is within a specified time period.

    Args:
        datetime_obj (datetime): The datetime object to check.
        time_period (str | relativedelta): The time period to check against. It can be a string representing a pre-defined period
            ("minutely", "hourly", "daily", "weekly", "monthly", "quarterly", "yearly"), or a relativedelta object representing a custom period.
        align_to_period_start (bool, optional): Whether to align the minimum datetime to the start of the time period. Defaults to False.

    Returns:
        bool: True if the datetime object is within the specified time period, False otherwise.

    Raises:
        ValueError: If the provided time_period is not a valid pre-defined period.
        TypeError: If the provided time_period is neither a string nor a relativedelta object.
    """
    now = datetime.now()

    periods = {
        "minutely": relativedelta(minutes=1),
        "hourly": relativedelta(hours=1),
        "daily": relativedelta(days=1),
        "weekly": relativedelta(weeks=1),
        "monthly": relativedelta(months=1),
        "quarterly": relativedelta(months=3),
        "yearly": relativedelta(years=1),
    }

    if isinstance(time_period, str):
        delta = periods.get(time_period)
        if not delta:
            raise ValueError(
                f"Invalid time_period '{time_period}'. Choose from {list(periods.keys())}.",
            )
    elif isinstance(time_period, relativedelta):
        delta = time_period
    else:
        raise TypeError(
            "time_period must be a string or a relativedelta object.",
        )

    min_dt = (
        normalize_dt(
            now,
            time_period,
        )
        if align_to_period_start
        else now - delta
    )

    return datetime_obj >= min_dt
