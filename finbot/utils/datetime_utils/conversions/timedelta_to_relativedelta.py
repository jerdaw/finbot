"""Convert fixed Timedelta to calendar-aware relativedelta.

Converts datetime.timedelta (fixed duration) to dateutil.relativedelta
(calendar-aware duration) by approximating days, months, and years based on
provided day-count conventions.

Requires explicit day counts because month/year lengths vary:
    - days_in_month: e.g., [30] for 30-day months, [28, 29, 30, 31] for actual
    - days_in_year: e.g., [365] for non-leap, [365, 366] for with leap years

Part of the datetime_utils/conversions module for time representation conversions.

Typical usage:
    - Convert fixed-duration intervals to calendar periods
    - Bridge between timedelta-based and relativedelta-based code
    - Handle time unit conversions with business day conventions
"""

from collections.abc import Sequence
from datetime import timedelta

from dateutil.relativedelta import relativedelta


def timedelta_to_relativedelta(
    td: timedelta,
    days_in_month: Sequence[int],
    days_in_year: Sequence[int],
) -> relativedelta:
    """
    Converts a Timedelta to a relativedelta.

    Args:
        td (timedelta): The Timedelta object to convert.
        days_in_month (list[int]): A list containing possible days counts in a month.
        days_in_year (list[int]): A list containing possible days counts in a year.

    Returns:
        relativedelta: Corresponding relativedelta object.
    """
    total_days = td.days
    total_years = 0
    total_months = 0

    # Calculate total years
    for year_days in sorted(days_in_year, reverse=True):
        while total_days >= year_days:
            total_days -= year_days
            total_years += 1

    # Calculate total months
    for month_days in sorted(days_in_month, reverse=True):
        while total_days >= month_days:
            total_days -= month_days
            total_months += 1

    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return relativedelta(
        years=total_years,
        months=total_months,
        days=total_days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
    )
