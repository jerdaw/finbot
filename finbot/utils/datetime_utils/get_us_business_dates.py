"""Generate US business dates excluding weekends and federal holidays.

Calculates valid US trading days between two dates using pandas business day
frequency and the US Federal Holiday Calendar. Excludes Saturdays, Sundays,
and official US federal holidays (New Year's, MLK Day, Presidents' Day,
Memorial Day, Independence Day, Labor Day, Thanksgiving, Christmas).

Essential for financial data alignment and ensuring data requests only target
actual trading days.

Supports custom holiday calendars and optional timezone awareness.

Typical usage:
    - Generate date ranges for backtesting
    - Validate data completeness (check for missing trading days)
    - Calculate number of trading days in a period
    - Schedule automated data updates for business days only
"""

from __future__ import annotations

from datetime import date, datetime, time
from time import perf_counter

import pandas as pd
from pandas.tseries.holiday import AbstractHolidayCalendar, USFederalHolidayCalendar

from config import logger


def get_us_business_dates(
    start_date: date,
    end_date: date | None = None,
    holiday_calendar: AbstractHolidayCalendar | None = None,
    time_zone: str | None = None,
) -> list[date]:
    """
    Calculates business dates between two dates, excluding specified holidays, with optional time zone awareness.

    Args:
        start_date (datetime.date): The start date.
        end_date (datetime.date | None): The end date. Defaults to today's date.
        holiday_calendar (AbstractHolidayCalendar | None): The holiday calendar to use. Defaults to USFederalHolidayCalendar if None.
        time_zone (str | None): The time zone for date calculations. Defaults to None.

    Returns:
        list[date]: A list of datetime.date objects representing each business date, excluding holidays, between the given dates.
    """
    if not isinstance(start_date, date) or (end_date is not None and not isinstance(end_date, date)):
        logger.error("Invalid date type provided")
        raise TypeError(
            "start_date and end_date must be instances of datetime.date",
        )

    if end_date is None:
        end_date = date.today() if datetime.now().hour >= 8 else date.today() - pd.Timedelta(days=1)

    if start_date > end_date:
        logger.error("Start date is after end date")
        raise ValueError("Start date must be before or equal to end date")

    if holiday_calendar is None:
        holiday_calendar = USFederalHolidayCalendar()

    start_time = perf_counter()

    try:
        # Calculate holidays based on the provided calendar
        start_dt = datetime.combine(start_date, time.min)
        end_dt = datetime.combine(end_date, time.max)
        us_holidays = holiday_calendar.holidays(start=start_dt, end=end_dt)
        if time_zone:
            us_holidays = us_holidays.tz_localize(tz=time_zone)

        # Generate business dates, excluding holidays
        all_business_dates = pd.bdate_range(
            start=start_date,
            end=end_date,
            freq="B",
            tz=time_zone,  # type: ignore
        )
        business_dates_excluding_holidays = all_business_dates.drop(
            us_holidays,
        )

    except pd.errors.EmptyDataError as e:
        logger.error(f"Pandas EmptyDataError: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_us_business_dates: {e}")
        raise

    end_time = perf_counter()
    logger.info(
        f"Business dates calculation executed in {end_time - start_time:.2f} seconds",
    )

    return list(business_dates_excluding_holidays.date)
