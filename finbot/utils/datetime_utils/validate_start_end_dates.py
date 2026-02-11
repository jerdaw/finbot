"""Validate date range inputs with configurable constraints.

Provides comprehensive validation for start/end date pairs with options to:
    - Enforce type constraints (must be datetime.date objects)
    - Prevent future dates (useful for historical data fetching)
    - Allow None values (for open-ended ranges)
    - Check logical ordering (start before end)

Raises descriptive TypeErrors and ValueErrors for invalid inputs.

Typical usage:
    - Validate user input in data collection functions
    - Enforce business logic constraints in backtesting
    - Prevent common date range errors early in call stack
"""

import datetime as dt
from typing import Any


def validate_start_end_dates(
    start_date: Any,
    end_date: Any,
    prevent_future_dates: bool = True,
    permit_none: bool = False,
):
    """
    Validate start and end dates.

    Args:
    start_date: The start date.
    end_date: The end date.
    prevent_future_dates (bool): Flag to prevent future dates.

    Raises:
    TypeError: If start_date or end_date is not a datetime.date object.
    ValueError: If start_date is after end_date or dates are in the future.
    """
    if not permit_none:
        if not isinstance(start_date, dt.date):
            raise TypeError("start_date must be a datetime.date object")
        if not isinstance(end_date, dt.date):
            raise TypeError("end_date must be a datetime.date object")
    else:
        if not isinstance(start_date, dt.date | type(None)):
            raise TypeError("start_date must be a datetime.date object or None")
        if not isinstance(end_date, dt.date | type(None)):
            raise TypeError("end_date must be a datetime.date object or None")

    if prevent_future_dates:
        if start_date is not None and start_date > dt.date.today():
            raise ValueError("start_date cannot be in the future")
        if end_date is not None and end_date > dt.date.today():
            raise ValueError("end_date cannot be in the future")

    if start_date is not None and end_date is not None and start_date > end_date:
        raise ValueError("start_date must be before end_date")
