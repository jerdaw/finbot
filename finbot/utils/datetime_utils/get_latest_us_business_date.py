from __future__ import annotations

import calendar
from datetime import date, datetime, time

from dateutil.relativedelta import relativedelta

from config import logger
from finbot.utils.datetime_utils.get_us_business_dates import get_us_business_dates


def get_latest_us_business_date(
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
    time_zone: str | None = None,
    min_time: time | None = None,
) -> date:
    """
    Get the latest business date that has occurred by a given year, month, and day.
    Defaults: year - current year, month and day - entire year considered.
    If only month is provided, the entire month is considered.
    If month and day are provided, up to that day in the specified month is considered.
    Only returns dates up to the present.

    Args:
        year (int | None): Year to find the latest business date.
        month (int | None): Month to find the latest business date.
        day (int | None): Day up to which to find the latest business date.
        time_zone (str | None): The time zone for date calculations. Defaults to None.
        min_time (datetime.time | None): The minimum time it must be for a date to qualify. Defaults to None.

    Returns:
        date: The latest business date by the specified time frame.

    Raises:
        ValueError: If the day is provided without month or if the month is provided without year.
        Exception: Unknown or other error in getting latest US business date
    """
    if day and not month:
        raise ValueError("Month must be specified if day is given.")
    if month and not year:
        raise ValueError("Year must be specified if month is given.")
    if min_time is None:
        min_time = datetime.min.time()

    # Set default end_date to present date values
    latest_possible = date.today() if datetime.now().time() >= min_time else date.today() - relativedelta(days=1)
    year = year or latest_possible.year
    month = month or 12
    day = day or calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, day).date()

    # Ensure the end date is not in the future
    end_date = min(end_date, latest_possible)

    # Select start date guaranteed to be before last us business date
    start_date = end_date - relativedelta(weeks=1)

    try:
        bdate_range = get_us_business_dates(
            start_date,
            end_date,
            time_zone=time_zone,
        )

        latest_business_date = max(bdate_range)

        if latest_business_date:
            logger.info(
                f"Latest business date calculated: {latest_business_date}",
            )
            return latest_business_date

        logger.error("No business dates found in the specified range")
        raise ValueError("No business dates found in the specified range")
    except Exception as e:
        logger.error(f"Error in getting latest business date: {e}")
        raise


if __name__ == "__main__":
    # Example
    latest_business_date = get_latest_us_business_date()
    print(latest_business_date)
    latest_business_date = get_latest_us_business_date(min_time=time(hour=9, minute=30))
    print(latest_business_date)
