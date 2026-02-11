"""Check if datetime falls within specified date and time bounds.

Validates whether a datetime object is within a specified date range and/or
time-of-day range. Supports separate date and time constraints with configurable
inclusivity.

More flexible than simple comparison operators by allowing separate date and
time bounds (e.g., "trading days between 9:30 AM and 4:00 PM").

Typical usage:
    - Filter data to market hours
    - Validate datetime inputs are within acceptable range
    - Check if event occurred during specific time windows
    - Implement time-based access control
"""

from __future__ import annotations

from datetime import date, datetime, time


def is_datetime_in_bounds(  # noqa: C901 - Multiple optional parameter checks required
    dt: datetime,
    start_date: date | None = None,
    end_date: date | None = None,
    start_time: time | None = None,
    end_time: time | None = None,
    inclusive: bool = True,
) -> bool:
    """
    Check if a datetime is within a specified date and/or time bounds.

    Args:
        dt (datetime): The datetime to check.
        start_date (date | None): The start date of the range.
        end_date (date | None): The end date of the range.
        start_time (time | None): The start time of the day.
        end_time (time | None): The end time of the day.
        inclusive (bool): Whether the end of the range is inclusive.

    Returns:
        bool: True if dt is within the bounds, False otherwise.
    """
    # Check for date lower bound violation
    if start_date and dt.date() < start_date:
        return False
    # Check for date upper bound violation
    if end_date:
        if inclusive:
            if dt.date() > end_date:
                return False
        elif dt.date() >= end_date:
            return False
    # Check for time lower bound violation
    if start_time and dt.time() < start_time:
        return False
    # Check for time upper bound violation
    if end_time:
        if inclusive:
            if dt.time() > end_time:
                return False
        elif dt.time() >= end_time:
            return False

    # No bounds violated, datetime is within range
    return True
