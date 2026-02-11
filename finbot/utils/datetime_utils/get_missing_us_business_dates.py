"""Identify missing business dates in time series data.

Detects gaps in time series by comparing expected business dates (from
get_us_business_dates.py) with actual dates present in the data. Handles
both daily and monthly frequencies with special handling for end-of-month
dates.

Essential for data quality validation and identifying collection failures.

Returns lists of missing dates for investigation or automated re-fetching.

Typical usage:
    - Validate completeness of downloaded price data
    - Identify data collection failures
    - Generate lists of dates to backfill
    - Monitor data pipeline health
"""

import datetime
from calendar import monthrange

import pandas as pd
from dateutil.relativedelta import relativedelta
from pandas.tseries.holiday import AbstractHolidayCalendar, USFederalHolidayCalendar

from finbot.config import logger
from finbot.utils.datetime_utils.get_us_business_dates import get_us_business_dates
from finbot.utils.pandas_utils.get_timeseries_frequency import get_timeseries_frequency


def adjust_end_of_month(current_date, next_date):
    _, last_day_current_month = monthrange(current_date.year, current_date.month)
    _, last_day_next_month = monthrange(next_date.year, next_date.month)

    if current_date.day == last_day_current_month or (
        next_date.month != (current_date.month + 1) % 12 and next_date.day != last_day_next_month
    ):
        # Adjust to the last day of the next month
        return next_date.replace(day=last_day_next_month)
    else:
        return next_date


def get_expected_frequency_dates(
    start_date: datetime.date,
    end_date: datetime.date,
    dates: pd.Series | list[datetime.date],
    existing_dates: set[datetime.date],
    all_business_dates: list[datetime.date],
) -> set[datetime.date]:
    frequency = get_timeseries_frequency(pd.Series(dates))
    check_dates = [start_date]

    while check_dates[-1] <= end_date:
        cur_date = check_dates[-1]

        if isinstance(frequency, relativedelta):
            next_date = cur_date + frequency
            if frequency.months != 0:
                next_date = adjust_end_of_month(cur_date, next_date)
        else:
            raise ValueError("Frequency must be a relativedelta")

        # Ensure next_date day isn't greater than the last day of the month
        next_date = next_date.replace(day=min(next_date.day, monthrange(next_date.year, next_date.month)[1]))

        if next_date <= end_date:
            check_dates.append(next_date)
        else:
            break

    adj_freq_dates = []
    for d in check_dates:
        if d in existing_dates:
            adj_freq_dates.append(d)
        else:
            # get the last business date before date
            lbd = max(bd for bd in all_business_dates if d <= d)  # TODO: Make this more efficient
            adj_freq_dates.append(lbd)

    return set(adj_freq_dates)


def _prep_params(
    dates: pd.Series | list[datetime.date],
    start_date: datetime.date | None,
    end_date: datetime.date | None,
) -> tuple[datetime.date, datetime.date, pd.Series]:
    if not all(isinstance(d, datetime.date) for d in dates):
        logger.error("Invalid date type provided in the sequence")
        raise TypeError("All elements in dates must be instances of datetime.date")

    if start_date is None:
        start_date = min(dates)
        start_date = start_date if isinstance(start_date, datetime.date) else start_date.date()

    if end_date is None:
        end_date = max(dates)
        end_date = end_date if isinstance(end_date, datetime.date) else end_date.date()

    if not isinstance(start_date, datetime.date) or not isinstance(end_date, datetime.date):
        logger.error("Invalid date type provided")
        raise TypeError("start_date and end_date must be instances of datetime.date")

    if isinstance(start_date, pd.Timestamp):
        start_date = start_date.date()

    if isinstance(end_date, pd.Timestamp):
        end_date = end_date.date()

    if isinstance(dates, pd.Series) and not dates.empty and isinstance(dates.loc[0], pd.Timestamp):
        dates = dates.dt.date

    if not isinstance(dates[0], datetime.date):
        raise TypeError("dates must be instances of datetime.date")

    return start_date, end_date, pd.Series(dates)


def get_missing_us_business_dates(
    dates: pd.Series | list[datetime.date],
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    holiday_calendar: AbstractHolidayCalendar | None = None,
    time_zone: str | None = None,
    detect_frequency: bool = False,
) -> list[datetime.date]:
    start_date, end_date, dates = _prep_params(dates=dates, start_date=start_date, end_date=end_date)

    # Get all business dates within the range
    all_business_dates = get_us_business_dates(
        start_date,
        end_date,
        holiday_calendar=holiday_calendar,
        time_zone=time_zone,
    )
    expected_dates = set(all_business_dates)
    existing_dates = set(dates)

    # Detect time series frequency if required
    if detect_frequency:
        expected_dates = get_expected_frequency_dates(
            start_date=start_date,
            end_date=end_date,
            dates=dates,
            existing_dates=existing_dates,
            all_business_dates=all_business_dates,
        )

    # Find and return missing business dates
    missing_business_dates = sorted(expected_dates - existing_dates)

    return missing_business_dates


if __name__ == "__main__":
    # Test 1: Basic functionality with a small date range
    test_dates_1 = pd.Series(pd.date_range(start="2024-01-01", end="2024-01-31", freq="B"))
    missing_dates_1 = get_missing_us_business_dates(test_dates_1)
    print("Test 1 - Missing dates:", missing_dates_1, end="\n\n")

    # Test 2: Including a holiday calendar with a specific range
    test_dates_2 = pd.Series(pd.date_range(start="2024-07-01", end="2024-07-31", freq="B"))
    missing_dates_2 = get_missing_us_business_dates(test_dates_2, holiday_calendar=USFederalHolidayCalendar())
    print("Test 2 - Missing dates with holiday calendar:", missing_dates_2, end="\n\n")

    # Test 3: Detecting frequency - Monthly
    test_dates_3 = pd.Series(
        pd.date_range(start="2024-01-01", end="2024-12-01", freq="MS"),
        index=pd.date_range(start="2024-01-01", end="2024-12-01", freq="MS"),
    )
    test_dates_3 = test_dates_3[1:]
    missing_dates_3 = get_missing_us_business_dates(
        test_dates_3,
        detect_frequency=True,
        start_date=datetime.date(2024, 1, 1),
    )
    print("Test 3 - Missing monthly dates:", missing_dates_3, end="\n\n")

    # Test 4: Detecting frequency - Weekly
    test_dates_4 = list(pd.Series(pd.date_range(start="2024-01-01", end="2024-03-01", freq="W")).dt.date)
    test_dates_4 = test_dates_4[:5] + test_dates_4[6:]
    missing_dates_4 = get_missing_us_business_dates(test_dates_4, detect_frequency=True)
    print("Test 4 - Missing weekly dates:", missing_dates_4, end="\n\n")

    # Test 5: Detecting frequency - Yearly
    test_dates_5 = list(pd.Series(pd.date_range(start="2020-01-01", end="2024-01-01", freq="YS")).dt.date)
    test_dates_5 = test_dates_5[:-1]
    missing_dates_5 = get_missing_us_business_dates(
        test_dates_5,
        detect_frequency=True,
        end_date=datetime.date(2024, 1, 1),
    )
    print("Test 5 - Missing yearly dates:", missing_dates_5, end="\n\n")
