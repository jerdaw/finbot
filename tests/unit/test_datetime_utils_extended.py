"""Extended unit tests for datetime utility functions.

Tests cover modules with 0% coverage:
- ceil_datetime: Round datetime up to unit boundary
- floor_datetime: Round datetime down to unit boundary
- get_common_date_range: Find exact common dates across series
- get_duration: Calculate duration with flexible granularity
- get_months_between_dates: Generate set of months in range
- relativedelta_to_timedelta: Convert relativedelta to timedelta
- timedelta_to_relativedelta: Convert timedelta to relativedelta
"""

import datetime
from datetime import date, timedelta

import pandas as pd
import pytest
from dateutil.relativedelta import relativedelta

from finbot.constants.datetime_constants import (
    ALIGNED_DAILY_DATETIME,
    NYSE_AFTERMARKET_CLOSE_TIME,
    NYSE_MARKET_CLOSE_TIME,
    NYSE_MARKET_OPEN_TIME,
    NYSE_PREMARKET_OPEN_TIME,
)
from finbot.utils.datetime_utils.ceil_datetime import ceil_datetime
from finbot.utils.datetime_utils.conversions.relativedelta_to_timedelta import (
    relativedelta_to_timedelta,
)
from finbot.utils.datetime_utils.conversions.timedelta_to_relativedelta import (
    timedelta_to_relativedelta,
)
from finbot.utils.datetime_utils.floor_datetime import floor_datetime
from finbot.utils.datetime_utils.get_common_date_range import get_common_date_range
from finbot.utils.datetime_utils.get_duration import get_duration
from finbot.utils.datetime_utils.get_months_between_dates import (
    get_months_between_dates,
)


class TestCeilDatetime:
    """Tests for ceil_datetime()."""

    def test_ceil_microsecond(self):
        dt = datetime.datetime(2021, 2, 15, 12, 34, 56, 789012)
        result = ceil_datetime(dt, "microsecond")
        assert result == datetime.datetime(2021, 2, 15, 12, 34, 56, 999999)

    def test_ceil_second(self):
        dt = datetime.datetime(2021, 2, 15, 12, 34, 56, 789012)
        result = ceil_datetime(dt, "second")
        assert result.second == 59
        assert result.microsecond == 999999

    def test_ceil_minute(self):
        dt = datetime.datetime(2021, 2, 15, 12, 34, 56, 789012)
        result = ceil_datetime(dt, "minute")
        assert result.minute == 59
        assert result.second == 59

    def test_ceil_hour(self):
        dt = datetime.datetime(2021, 2, 15, 12, 34, 56, 789012)
        result = ceil_datetime(dt, "hour")
        assert result.hour == 23
        assert result.minute == 59

    def test_ceil_day(self):
        dt = datetime.datetime(2021, 2, 15, 12, 34, 56)
        result = ceil_datetime(dt, "day")
        assert result.day == 28  # Feb 2021 (non-leap)
        assert result.hour == 23
        assert result.minute == 59

    def test_ceil_day_leap_year(self):
        dt = datetime.datetime(2020, 2, 15, 12, 0, 0)
        result = ceil_datetime(dt, "day")
        assert result.day == 29  # Feb 2020 (leap year)

    def test_ceil_month(self):
        dt = datetime.datetime(2021, 6, 15, 12, 0, 0)
        result = ceil_datetime(dt, "month")
        assert result.month == 12
        assert result.day == 31  # Dec has 31 days

    def test_ceil_year(self):
        dt = datetime.datetime(2021, 6, 15, 12, 0, 0)
        result = ceil_datetime(dt, "year")
        assert result.year == 9999
        assert result.month == 12

    def test_ceil_default_is_day(self):
        dt = datetime.datetime(2021, 3, 15, 10, 0, 0)
        result = ceil_datetime(dt)
        assert result.day == 31  # March has 31 days
        assert result.hour == 23

    def test_ceil_accepts_date(self):
        d = date(2021, 7, 4)
        result = ceil_datetime(d, "day")
        assert isinstance(result, datetime.datetime)
        assert result.day == 31  # July has 31 days

    def test_ceil_accepts_timestamp(self):
        ts = pd.Timestamp("2021-03-15 10:30:00")
        result = ceil_datetime(ts, "hour")
        assert isinstance(result, datetime.datetime)
        assert result.hour == 23

    def test_ceil_with_tzinfo(self):
        dt = datetime.datetime(2021, 1, 15, 12, 0, 0)
        tz = datetime.UTC
        result = ceil_datetime(dt, "day", tzinfo=tz)
        assert result.tzinfo == tz

    def test_ceil_invalid_type_raises_type_error(self):
        with pytest.raises(TypeError, match="dt must be"):
            ceil_datetime("2021-01-01")  # type: ignore[arg-type]

    def test_ceil_invalid_target_raises_value_error(self):
        dt = datetime.datetime(2021, 1, 1)
        with pytest.raises(ValueError, match="Invalid ceil_to value"):
            ceil_datetime(dt, "week")  # type: ignore[arg-type]


class TestFloorDatetime:
    """Tests for floor_datetime()."""

    def test_floor_microsecond(self):
        dt = datetime.datetime(2021, 2, 15, 12, 34, 56, 789012)
        result = floor_datetime(dt, "microsecond")
        assert result == datetime.datetime(2021, 2, 15, 12, 34, 56, 0)

    def test_floor_second(self):
        dt = datetime.datetime(2021, 2, 15, 12, 34, 56, 789012)
        result = floor_datetime(dt, "second")
        assert result.second == 0
        assert result.microsecond == 0

    def test_floor_minute(self):
        dt = datetime.datetime(2021, 2, 15, 12, 34, 56, 789012)
        result = floor_datetime(dt, "minute")
        assert result.minute == 0
        assert result.second == 0

    def test_floor_hour(self):
        dt = datetime.datetime(2021, 2, 15, 12, 34, 56)
        result = floor_datetime(dt, "hour")
        assert result.hour == 0
        assert result.minute == 0

    def test_floor_day(self):
        dt = datetime.datetime(2021, 2, 15, 12, 34, 56)
        result = floor_datetime(dt, "day")
        assert result.day == 1
        assert result.hour == 0
        assert result.minute == 0

    def test_floor_month(self):
        dt = datetime.datetime(2021, 6, 15, 12, 0, 0)
        result = floor_datetime(dt, "month")
        assert result.month == 1
        assert result.day == 1

    def test_floor_year(self):
        dt = datetime.datetime(2021, 6, 15, 12, 0, 0)
        result = floor_datetime(dt, "year")
        assert result.year == 1
        assert result.month == 1
        assert result.day == 1

    def test_floor_default_is_day(self):
        dt = datetime.datetime(2021, 3, 15, 10, 30, 45)
        result = floor_datetime(dt)
        assert result == datetime.datetime(2021, 3, 1, 0, 0, 0)

    def test_floor_accepts_date(self):
        d = date(2021, 7, 4)
        result = floor_datetime(d, "month")
        assert isinstance(result, datetime.datetime)
        assert result.month == 1

    def test_floor_accepts_timestamp(self):
        ts = pd.Timestamp("2021-03-15 10:30:00")
        result = floor_datetime(ts, "hour")
        assert isinstance(result, datetime.datetime)
        assert result.hour == 0

    def test_floor_with_tzinfo(self):
        dt = datetime.datetime(2021, 1, 15, 12, 0, 0)
        tz = datetime.UTC
        result = floor_datetime(dt, "day", tzinfo=tz)
        assert result.tzinfo == tz

    def test_floor_invalid_type_raises_type_error(self):
        with pytest.raises(TypeError, match="dt must be"):
            floor_datetime(12345)  # type: ignore[arg-type]

    def test_floor_invalid_target_raises_value_error(self):
        dt = datetime.datetime(2021, 1, 1)
        with pytest.raises(ValueError, match="Invalid floor_to value"):
            floor_datetime(dt, "week")  # type: ignore[arg-type]


class TestGetCommonDateRange:
    """Tests for get_common_date_range()."""

    def test_two_overlapping_series(self):
        dates1 = pd.date_range("2021-01-01", "2021-12-31", freq="D")
        dates2 = pd.date_range("2021-06-01", "2022-06-30", freq="D")
        s1 = pd.Series(1.0, index=dates1)
        s2 = pd.Series(2.0, index=dates2)
        start, end = get_common_date_range(s1, s2)
        assert start == pd.Timestamp("2021-06-01")
        assert end == pd.Timestamp("2021-12-31")

    def test_three_series(self):
        s1 = pd.Series(1.0, index=pd.date_range("2021-01-01", "2021-12-31", freq="D"))
        s2 = pd.Series(2.0, index=pd.date_range("2021-03-01", "2022-03-31", freq="D"))
        s3 = pd.Series(3.0, index=pd.date_range("2021-06-01", "2021-09-30", freq="D"))
        start, end = get_common_date_range(s1, s2, s3)
        assert start == pd.Timestamp("2021-06-01")
        assert end == pd.Timestamp("2021-09-30")

    def test_no_overlap_raises_error(self):
        s1 = pd.Series(1.0, index=pd.date_range("2020-01-01", "2020-06-30", freq="D"))
        s2 = pd.Series(2.0, index=pd.date_range("2021-01-01", "2021-06-30", freq="D"))
        with pytest.raises(ValueError, match="No common date range"):
            get_common_date_range(s1, s2)

    def test_no_overlap_returns_none(self):
        s1 = pd.Series(1.0, index=pd.date_range("2020-01-01", "2020-06-30", freq="D"))
        s2 = pd.Series(2.0, index=pd.date_range("2021-01-01", "2021-06-30", freq="D"))
        start, end = get_common_date_range(s1, s2, raise_error=False)
        assert start is None
        assert end is None

    def test_single_series(self):
        dates = pd.date_range("2021-01-01", "2021-12-31", freq="D")
        s = pd.Series(1.0, index=dates)
        start, end = get_common_date_range(s)
        assert start == pd.Timestamp("2021-01-01")
        assert end == pd.Timestamp("2021-12-31")

    def test_identical_series(self):
        dates = pd.date_range("2021-01-01", "2021-06-30", freq="D")
        s1 = pd.Series(1.0, index=dates)
        s2 = pd.Series(2.0, index=dates)
        start, end = get_common_date_range(s1, s2)
        assert start == pd.Timestamp("2021-01-01")
        assert end == pd.Timestamp("2021-06-30")


class TestGetDuration:
    """Tests for get_duration()."""

    def test_no_granularity_returns_relativedelta(self):
        d1 = datetime.datetime(2020, 1, 1)
        d2 = datetime.datetime(2021, 7, 15, 12, 30)
        result = get_duration(d1, d2)
        assert isinstance(result, relativedelta)
        assert result.years == 1
        assert result.months == 6

    def test_granularity_years(self):
        d1 = datetime.datetime(2020, 1, 1)
        d2 = datetime.datetime(2022, 1, 1)
        result = get_duration(d1, d2, granularity="years")
        assert isinstance(result, float)
        assert result == pytest.approx(2.0, abs=0.01)

    def test_granularity_months(self):
        d1 = datetime.datetime(2020, 1, 1)
        d2 = datetime.datetime(2020, 7, 1)
        result = get_duration(d1, d2, granularity="months")
        assert isinstance(result, float)
        assert result == pytest.approx(6.0, abs=0.1)

    def test_granularity_days(self):
        d1 = datetime.datetime(2020, 1, 1)
        d2 = datetime.datetime(2020, 1, 11)
        result = get_duration(d1, d2, granularity="days")
        assert result == pytest.approx(10.0)

    def test_granularity_hours(self):
        d1 = datetime.datetime(2020, 1, 1, 0, 0, 0)
        d2 = datetime.datetime(2020, 1, 1, 12, 0, 0)
        result = get_duration(d1, d2, granularity="hours")
        assert result == pytest.approx(12.0)

    def test_granularity_minutes(self):
        d1 = datetime.datetime(2020, 1, 1, 0, 0, 0)
        d2 = datetime.datetime(2020, 1, 1, 1, 30, 0)
        result = get_duration(d1, d2, granularity="minutes")
        assert result == pytest.approx(90.0)

    def test_granularity_seconds(self):
        d1 = datetime.datetime(2020, 1, 1, 0, 0, 0)
        d2 = datetime.datetime(2020, 1, 1, 0, 1, 30)
        result = get_duration(d1, d2, granularity="seconds")
        assert result == pytest.approx(90.0)

    def test_granularity_microseconds(self):
        d1 = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
        d2 = datetime.datetime(2020, 1, 1, 0, 0, 1, 0)
        result = get_duration(d1, d2, granularity="microseconds")
        assert result == pytest.approx(1_000_000.0)

    def test_zero_duration(self):
        d = datetime.datetime(2020, 6, 15, 12, 0, 0)
        result = get_duration(d, d, granularity="days")
        assert result == 0.0

    def test_invalid_granularity_raises_value_error(self):
        d1 = datetime.datetime(2020, 1, 1)
        d2 = datetime.datetime(2021, 1, 1)
        with pytest.raises(ValueError, match="Invalid granularity"):
            get_duration(d1, d2, granularity="weeks")


class TestGetMonthsBetweenDates:
    """Tests for get_months_between_dates()."""

    def test_single_month(self):
        result = get_months_between_dates(date(2022, 3, 1), date(2022, 3, 31))
        assert result == {(2022, 3)}

    def test_full_year(self):
        result = get_months_between_dates(date(2022, 1, 1), date(2022, 12, 31))
        assert len(result) == 12
        assert (2022, 1) in result
        assert (2022, 12) in result

    def test_cross_year(self):
        result = get_months_between_dates(date(2021, 11, 1), date(2022, 2, 28))
        assert len(result) == 4
        assert (2021, 11) in result
        assert (2022, 2) in result

    def test_return_type_str(self):
        result = get_months_between_dates(date(2022, 1, 1), date(2022, 3, 31), return_type="str")
        assert ("2022", "01") in result
        assert ("2022", "03") in result

    def test_return_type_int_default(self):
        result = get_months_between_dates(date(2022, 6, 15), date(2022, 6, 15))
        assert result == {(2022, 6)}
        for year, month in result:
            assert isinstance(year, int)
            assert isinstance(month, int)

    def test_same_day(self):
        result = get_months_between_dates(date(2022, 5, 15), date(2022, 5, 15))
        assert result == {(2022, 5)}


class TestRelativedeltaToTimedelta:
    """Tests for relativedelta_to_timedelta()."""

    def test_one_month_default_reference(self):
        rd = relativedelta(months=1)
        result = relativedelta_to_timedelta(rd)
        assert isinstance(result, timedelta)
        assert result.days == 31  # Jan 2000 has 31 days

    def test_one_year(self):
        rd = relativedelta(years=1)
        result = relativedelta_to_timedelta(rd)
        assert result.days == 366  # 2000 is a leap year

    def test_custom_reference_date(self):
        rd = relativedelta(months=1)
        ref = pd.Timestamp("2021-02-01")  # Feb non-leap
        result = relativedelta_to_timedelta(rd, reference_date=ref)
        assert result.days == 28

    def test_days_only(self):
        rd = relativedelta(days=10)
        result = relativedelta_to_timedelta(rd)
        assert result.days == 10


class TestTimedeltaToRelativedelta:
    """Tests for timedelta_to_relativedelta()."""

    def test_simple_days(self):
        td = timedelta(days=10)
        result = timedelta_to_relativedelta(td, [30], [365])
        assert isinstance(result, relativedelta)
        assert result.days == 10
        assert result.months == 0
        assert result.years == 0

    def test_one_year(self):
        td = timedelta(days=365)
        result = timedelta_to_relativedelta(td, [30], [365])
        assert result.years == 1
        assert result.months == 0
        assert result.days == 0

    def test_year_plus_month(self):
        td = timedelta(days=395)
        result = timedelta_to_relativedelta(td, [30], [365])
        assert result.years == 1
        assert result.months == 1
        assert result.days == 0

    def test_hours_minutes_seconds(self):
        td = timedelta(hours=3, minutes=25, seconds=45)
        result = timedelta_to_relativedelta(td, [30], [365])
        assert result.hours == 3
        assert result.minutes == 25
        assert result.seconds == 45

    def test_with_leap_year_days(self):
        td = timedelta(days=366)
        result = timedelta_to_relativedelta(td, [30], [366])
        assert result.years == 1
        assert result.days == 0


class TestDatetimeConstants:
    """Tests for datetime_constants module values."""

    def test_market_open_time(self):
        assert datetime.time(9, 30, 0) == NYSE_MARKET_OPEN_TIME

    def test_market_close_time(self):
        assert datetime.time(16, 0, 0) == NYSE_MARKET_CLOSE_TIME

    def test_premarket_before_open(self):
        assert NYSE_PREMARKET_OPEN_TIME < NYSE_MARKET_OPEN_TIME

    def test_aftermarket_after_close(self):
        assert NYSE_AFTERMARKET_CLOSE_TIME > NYSE_MARKET_CLOSE_TIME

    def test_aligned_daily_equals_close(self):
        assert ALIGNED_DAILY_DATETIME == NYSE_MARKET_CLOSE_TIME
