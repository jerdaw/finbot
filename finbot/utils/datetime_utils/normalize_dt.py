from __future__ import annotations

from datetime import datetime

from dateutil.relativedelta import relativedelta


def _normalize_relativedelta_period(dt: datetime, rd: relativedelta) -> datetime:
    """
    Normalizes the datetime based on a relativedelta object representing the time period.

    Parameters:
    - dt (datetime): The current datetime.
    - rd (relativedelta): The relativedelta object representing the time period.

    Returns:
    - datetime: Normalized current time.
    """
    if rd.years > 0:
        return dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    if rd.months > 0:
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if rd.days > 0:
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    if rd.hours > 0:
        return dt.replace(minute=0, second=0, microsecond=0)
    if rd.minutes > 0:
        return dt.replace(second=0, microsecond=0)
    if rd.seconds > 0:
        return dt.replace(microsecond=0)
    return dt


def _normalize_str_period(dt: datetime, period: str) -> datetime:
    """
    Normalizes the datetime based on a string representation of the time period.

    Parameters:
    - dt (datetime): The current datetime.
    - period (str): The time period for normalization.

    Returns:
    - datetime: Normalized current time.
    """
    periods = {
        "minutely": lambda d: d.replace(second=0, microsecond=0),
        "hourly": lambda d: d.replace(minute=0, second=0, microsecond=0),
        "daily": lambda d: d.replace(hour=0, minute=0, second=0, microsecond=0),
        "weekly": lambda d: d - relativedelta(days=d.weekday(), hour=0, minute=0, second=0, microsecond=0),
        "monthly": lambda d: d.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
        "quarterly": lambda d: d.replace(
            month=((d.month - 1) // 3) * 3 + 1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        ),
        "yearly": lambda d: d.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
    }
    return periods.get(period, lambda d: d)(dt)


def normalize_dt(dt: datetime, time_period: str | relativedelta) -> datetime:
    """
    Normalizes the current datetime to the start of the specified time period.

    Parameters:
    - dt (datetime): The current datetime.
    - time_period (str | relativedelta): The time period for normalization.

    Returns:
    - datetime: Normalized current time.
    """

    if isinstance(time_period, str):
        return _normalize_str_period(dt, time_period)
    if isinstance(time_period, relativedelta):
        return _normalize_relativedelta_period(dt, time_period)
    raise TypeError(
        "time_period must be either a string or a relativedelta object.",
    )
