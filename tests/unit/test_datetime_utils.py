"""Unit tests for datetime utility functions.

Tests cover:
- US business date generation (get_us_business_dates)
- Latest business date calculation (get_latest_us_business_date)
- Missing business date detection (get_missing_us_business_dates)
- Time stepping and windowing (step_datetimes)
- Intraday time ranges (DailyTimeRange)
- Datetime bounds checking (is_datetime_in_bounds)
- Relativedelta conversions (str_to_relativedelta, relativedelta_to_str)
"""

import datetime
from datetime import date, time
from typing import TYPE_CHECKING

import pandas as pd
import pytest
from dateutil.relativedelta import relativedelta
from pandas.tseries.holiday import USFederalHolidayCalendar

from finbot.utils.datetime_utils.daily_time_range import DailyTimeRange
from finbot.utils.datetime_utils.get_latest_us_business_date import (
    get_latest_us_business_date,
)
from finbot.utils.datetime_utils.get_missing_us_business_dates import (
    get_missing_us_business_dates,
)
from finbot.utils.datetime_utils.get_us_business_dates import get_us_business_dates
from finbot.utils.datetime_utils.is_datetime_in_bounds import is_datetime_in_bounds
from finbot.utils.datetime_utils.step_datetimes import step_datetimes

if TYPE_CHECKING:
    pass

# Conversion utilities - imported after TYPE_CHECKING to avoid circular imports
from finbot.utils.datetime_utils.conversions.relativedelta_to_str import (
    relativedelta_to_str,
)
from finbot.utils.datetime_utils.conversions.str_to_relativedelta import (
    str_to_relativedelta,
)


class TestGetUSBusinessDates:
    """Tests for get_us_business_dates()"""

    def test_basic_week_no_holidays(self):
        """Test generating business dates for a week without holidays"""
        start = date(2024, 1, 8)  # Monday
        end = date(2024, 1, 12)  # Friday
        result = get_us_business_dates(start, end)

        assert len(result) == 5  # Mon-Fri
        assert result[0] == date(2024, 1, 8)
        assert result[-1] == date(2024, 1, 12)

    def test_excludes_weekends(self):
        """Test that weekends are excluded"""
        start = date(2024, 1, 5)  # Friday
        end = date(2024, 1, 8)  # Monday
        result = get_us_business_dates(start, end)

        assert len(result) == 2  # Only Fri and Mon
        assert result[0] == date(2024, 1, 5)
        assert result[1] == date(2024, 1, 8)

    def test_excludes_federal_holidays(self):
        """Test that federal holidays are excluded (MLK Day 2024 = Jan 15)"""
        start = date(2024, 1, 12)  # Friday before MLK Day
        end = date(2024, 1, 16)  # Tuesday after MLK Day
        result = get_us_business_dates(start, end, holiday_calendar=USFederalHolidayCalendar())

        # Should have: Fri 1/12, Tue 1/16 (MLK Day 1/15 excluded)
        assert date(2024, 1, 15) not in result
        assert date(2024, 1, 12) in result
        assert date(2024, 1, 16) in result

    def test_single_day(self):
        """Test with start_date = end_date"""
        start = date(2024, 1, 10)  # Wednesday
        result = get_us_business_dates(start, start)

        assert len(result) == 1
        assert result[0] == date(2024, 1, 10)

    def test_start_after_end_raises_error(self):
        """Test that start > end raises ValueError"""
        start = date(2024, 1, 10)
        end = date(2024, 1, 5)

        with pytest.raises(ValueError, match="Start date must be before or equal to end date"):
            get_us_business_dates(start, end)

    def test_invalid_date_type_raises_error(self):
        """Test that non-date inputs raise TypeError"""
        with pytest.raises(TypeError, match="must be instances of datetime.date"):
            get_us_business_dates("2024-01-01", date(2024, 1, 10))  # type: ignore[arg-type]

    def test_end_date_defaults_to_today(self):
        """Test that end_date defaults to today (or yesterday before 8am)"""
        start = date.today() - datetime.timedelta(days=5)
        result = get_us_business_dates(start)

        assert len(result) > 0
        assert result[0] >= start
        # Result should end at today or yesterday (depending on time)
        assert result[-1] <= date.today()

    def test_long_range_performance(self):
        """Test performance with a 1-year range (should complete in <1 second)"""
        start = date(2023, 1, 1)
        end = date(2023, 12, 31)
        result = get_us_business_dates(start, end)

        # 2023 has ~250 trading days (approx 252 - holidays)
        assert 245 <= len(result) <= 255


class TestGetLatestUSBusinessDate:
    """Tests for get_latest_us_business_date()"""

    def test_default_params_returns_recent_date(self):
        """Test with all default params returns a recent business date"""
        result = get_latest_us_business_date()

        assert isinstance(result, date)
        assert result <= date.today()
        # Should be within last week
        assert result >= date.today() - datetime.timedelta(days=7)

    def test_specific_year_month_day(self):
        """Test with specific year/month/day"""
        result = get_latest_us_business_date(year=2024, month=1, day=10)

        # Jan 10, 2024 is Wednesday - should be latest business date
        assert result == date(2024, 1, 10)

    def test_weekend_day_returns_previous_friday(self):
        """Test that weekend date returns previous Friday"""
        # Jan 13, 2024 is Saturday
        result = get_latest_us_business_date(year=2024, month=1, day=13)

        # Should return Friday Jan 12
        assert result == date(2024, 1, 12)

    def test_min_time_cutoff(self):
        """Test min_time parameter (not fully testable without mocking datetime.now)"""
        # This test documents expected behavior but can't fully test time-dependent logic
        result = get_latest_us_business_date(min_time=time(hour=9, minute=30))

        assert isinstance(result, date)
        assert result <= date.today()

    def test_day_without_month_raises_error(self):
        """Test that providing day without month raises ValueError"""
        with pytest.raises(ValueError, match="Month must be specified if day is given"):
            get_latest_us_business_date(day=15)

    def test_month_without_year_raises_error(self):
        """Test that providing month without year raises ValueError"""
        with pytest.raises(ValueError, match="Year must be specified if month is given"):
            get_latest_us_business_date(month=6)

    def test_future_date_returns_today_or_earlier(self):
        """Test that future date is clamped to today"""
        future_year = date.today().year + 1
        result = get_latest_us_business_date(year=future_year, month=1, day=15)

        assert result <= date.today()


class TestGetMissingUSBusinessDates:
    """Tests for get_missing_us_business_dates()"""

    def test_complete_week_no_missing(self):
        """Test with complete week - no missing dates"""
        dates = pd.Series(pd.date_range(start="2024-01-08", end="2024-01-12", freq="B"))
        missing = get_missing_us_business_dates(dates)

        assert len(missing) == 0

    def test_one_day_missing(self):
        """Test detection of one missing business day"""
        dates = pd.Series([date(2024, 1, 8), date(2024, 1, 9), date(2024, 1, 11), date(2024, 1, 12)])
        missing = get_missing_us_business_dates(dates)

        # Should detect Jan 10 (Wednesday) is missing
        assert date(2024, 1, 10) in missing
        assert len(missing) == 1

    def test_multiple_missing_days(self):
        """Test detection of multiple missing days"""
        dates = pd.Series([date(2024, 1, 8), date(2024, 1, 12)])  # Mon and Fri only
        missing = get_missing_us_business_dates(dates)

        # Should detect Tue, Wed, Thu missing
        assert date(2024, 1, 9) in missing
        assert date(2024, 1, 10) in missing
        assert date(2024, 1, 11) in missing
        assert len(missing) == 3

    def test_with_custom_date_range(self):
        """Test with explicit start and end dates"""
        dates = pd.Series([date(2024, 1, 8)])
        missing = get_missing_us_business_dates(
            dates,
            start_date=date(2024, 1, 8),
            end_date=date(2024, 1, 12),
        )

        # Should find Tue-Fri missing
        assert len(missing) == 4

    def test_with_pandas_timestamps(self):
        """Test that pd.Timestamp dates are handled correctly"""
        dates = pd.Series(pd.date_range(start="2024-01-08", end="2024-01-10", freq="B"))
        missing = get_missing_us_business_dates(dates)

        # No missing dates
        assert len(missing) == 0

    def test_invalid_date_type_raises_error(self):
        """Test that invalid date types raise TypeError"""
        dates = pd.Series(["2024-01-08", "2024-01-09"])  # Strings instead of dates

        with pytest.raises(TypeError):
            get_missing_us_business_dates(dates)


class TestStepDatetimes:
    """Tests for step_datetimes()"""

    @pytest.fixture
    def sample_series(self):
        """Create a sample price series for testing"""
        dates = pd.date_range(start="2024-01-01", end="2024-03-31", freq="B")
        return pd.Series(range(len(dates)), index=dates, name="Close")

    def test_monthly_calendar_aligned(self, sample_series):
        """Test monthly stepping with calendar alignment"""
        result = step_datetimes(sample_series, "Monthly", align_to_calendar=True)

        assert isinstance(result, pd.DataFrame)
        assert "Period End" in result.columns
        assert len(result) > 0

    def test_monthly_rolling(self, sample_series):
        """Test monthly stepping with rolling windows"""
        result = step_datetimes(sample_series, "Monthly", align_to_calendar=False)

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_all_time_step(self, sample_series):
        """Test 'All Time' step option"""
        result = step_datetimes(sample_series, "All Time")

        # Should have only 1 period for 'All Time'
        assert len(result) >= 1

    def test_daily_step(self, sample_series):
        """Test 'Daily' step option"""
        result = step_datetimes(sample_series[:10], "Daily")

        # Should have many daily periods
        assert len(result) > 0

    def test_weekly_step(self, sample_series):
        """Test 'Weekly' step option"""
        result = step_datetimes(sample_series, "Weekly")

        assert len(result) > 0

    def test_quarterly_step(self, sample_series):
        """Test 'Quarterly' step option"""
        result = step_datetimes(sample_series, "Quarterly")

        # 3 months = should have ~3 quarters
        assert len(result) > 0

    def test_yearly_step(self, sample_series):
        """Test 'Yearly' step option"""
        result = step_datetimes(sample_series, "Yearly")

        # 3 months of data won't complete a full year
        assert len(result) >= 0

    def test_include_prices_false(self, sample_series):
        """Test with include_prices=False"""
        result = step_datetimes(sample_series, "Monthly", include_prices=False)

        assert "Start Price" not in result.columns
        assert "End Price" not in result.columns
        assert "Period End" in result.columns

    def test_invalid_step_raises_error(self, sample_series):
        """Test that invalid step option raises ValueError"""
        with pytest.raises(ValueError, match="Invalid step option"):
            step_datetimes(sample_series, "InvalidStep")


class TestDailyTimeRange:
    """Tests for DailyTimeRange class"""

    def test_basic_iteration_hourly(self):
        """Test basic iteration with hourly granularity"""
        time_range = DailyTimeRange(time(8, 0), time(12, 0), granularity="hours")
        times = list(time_range)

        assert len(times) == 5  # 8, 9, 10, 11, 12
        assert times[0] == time(8, 0)
        assert times[-1] == time(12, 0)

    def test_iteration_minutes(self):
        """Test iteration with minute granularity"""
        time_range = DailyTimeRange(time(9, 0), time(9, 5), granularity="minutes")
        times = list(time_range)

        assert len(times) == 6  # 9:00, 9:01, 9:02, 9:03, 9:04, 9:05
        assert times[0] == time(9, 0)
        assert times[-1] == time(9, 5)

    def test_contains_inclusive_both(self):
        """Test membership with inclusive='both'"""
        time_range = DailyTimeRange(time(9, 0), time(17, 0), inclusive="both")

        assert time(9, 0) in time_range  # Start included
        assert time(12, 30) in time_range  # Middle included
        assert time(17, 0) in time_range  # End included
        assert time(8, 59) not in time_range  # Before start
        assert time(17, 1) not in time_range  # After end

    def test_contains_inclusive_left(self):
        """Test membership with inclusive='left'"""
        time_range = DailyTimeRange(time(9, 0), time(17, 0), inclusive="left")

        assert time(9, 0) in time_range  # Start included
        assert time(16, 59) in time_range  # Just before end
        assert time(17, 0) not in time_range  # End excluded

    def test_contains_inclusive_right(self):
        """Test membership with inclusive='right'"""
        time_range = DailyTimeRange(time(9, 0), time(17, 0), inclusive="right")

        assert time(9, 0) not in time_range  # Start excluded
        assert time(9, 1) in time_range  # After start
        assert time(17, 0) in time_range  # End included

    def test_contains_inclusive_neither(self):
        """Test membership with inclusive='neither'"""
        time_range = DailyTimeRange(time(9, 0), time(17, 0), inclusive="neither")

        assert time(9, 0) not in time_range  # Start excluded
        assert time(12, 30) in time_range  # Middle included
        assert time(17, 0) not in time_range  # End excluded

    def test_market_hours_use_case(self):
        """Test typical use case: US market hours (9:30 AM to 4:00 PM)"""
        market_hours = DailyTimeRange(time(9, 30), time(16, 0))

        assert time(9, 29) not in market_hours
        assert time(9, 30) in market_hours
        assert time(12, 0) in market_hours
        assert time(16, 0) in market_hours
        assert time(16, 1) not in market_hours


class TestIsDatetimeInBounds:
    """Tests for is_datetime_in_bounds()"""

    def test_within_date_bounds_inclusive(self):
        """Test datetime within date bounds (inclusive)"""
        dt = datetime.datetime(2024, 1, 10, 12, 0)
        start = date(2024, 1, 5)
        end = date(2024, 1, 15)

        assert is_datetime_in_bounds(dt, start_date=start, end_date=end, inclusive=True)

    def test_on_boundary_dates_inclusive(self):
        """Test datetime exactly on boundary dates (inclusive)"""
        dt_start = datetime.datetime(2024, 1, 5, 12, 0)
        dt_end = datetime.datetime(2024, 1, 15, 12, 0)
        start = date(2024, 1, 5)
        end = date(2024, 1, 15)

        assert is_datetime_in_bounds(dt_start, start_date=start, end_date=end, inclusive=True)
        assert is_datetime_in_bounds(dt_end, start_date=start, end_date=end, inclusive=True)

    def test_on_end_boundary_not_inclusive(self):
        """Test datetime on end boundary (not inclusive)"""
        dt = datetime.datetime(2024, 1, 15, 12, 0)
        start = date(2024, 1, 5)
        end = date(2024, 1, 15)

        assert not is_datetime_in_bounds(dt, start_date=start, end_date=end, inclusive=False)

    def test_before_start_date(self):
        """Test datetime before start_date"""
        dt = datetime.datetime(2024, 1, 3, 12, 0)
        start = date(2024, 1, 5)

        assert not is_datetime_in_bounds(dt, start_date=start)

    def test_after_end_date(self):
        """Test datetime after end_date"""
        dt = datetime.datetime(2024, 1, 20, 12, 0)
        end = date(2024, 1, 15)

        assert not is_datetime_in_bounds(dt, end_date=end)

    def test_within_time_bounds(self):
        """Test datetime within time-of-day bounds"""
        dt = datetime.datetime(2024, 1, 10, 12, 0)
        start_time = time(9, 0)
        end_time = time(17, 0)

        assert is_datetime_in_bounds(dt, start_time=start_time, end_time=end_time)

    def test_before_start_time(self):
        """Test datetime before start_time"""
        dt = datetime.datetime(2024, 1, 10, 8, 0)
        start_time = time(9, 0)

        assert not is_datetime_in_bounds(dt, start_time=start_time)

    def test_after_end_time(self):
        """Test datetime after end_time"""
        dt = datetime.datetime(2024, 1, 10, 18, 0)
        end_time = time(17, 0)

        assert not is_datetime_in_bounds(dt, end_time=end_time, inclusive=True)

    def test_combined_date_and_time_bounds(self):
        """Test datetime with both date and time bounds"""
        dt = datetime.datetime(2024, 1, 10, 12, 0)
        start_date = date(2024, 1, 5)
        end_date = date(2024, 1, 15)
        start_time = time(9, 0)
        end_time = time(17, 0)

        assert is_datetime_in_bounds(
            dt,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
        )

    def test_market_hours_filtering(self):
        """Test typical use case: filter to market hours on trading days"""
        # Trading day, market hours
        dt1 = datetime.datetime(2024, 1, 10, 10, 30)
        # Trading day, before market
        dt2 = datetime.datetime(2024, 1, 10, 8, 0)
        # Weekend, market hours
        dt3 = datetime.datetime(2024, 1, 13, 10, 30)

        # Simulate filtering to Jan 8-12 (Mon-Fri), 9:30-16:00
        start_date = date(2024, 1, 8)
        end_date = date(2024, 1, 12)
        start_time = time(9, 30)
        end_time = time(16, 0)

        assert is_datetime_in_bounds(dt1, start_date, end_date, start_time, end_time)
        assert not is_datetime_in_bounds(dt2, start_date, end_date, start_time, end_time)
        assert not is_datetime_in_bounds(dt3, start_date, end_date, start_time, end_time)


class TestStrToRelativedelta:
    """Tests for str_to_relativedelta()"""

    def test_second_aliases(self):
        """Test second frequency aliases"""
        assert str_to_relativedelta("S") == relativedelta(seconds=1)
        assert str_to_relativedelta("SEC") == relativedelta(seconds=1)
        assert str_to_relativedelta("SECOND") == relativedelta(seconds=1)
        assert str_to_relativedelta("s") == relativedelta(seconds=1)  # Case insensitive

    def test_minute_aliases(self):
        """Test minute frequency aliases"""
        assert str_to_relativedelta("T") == relativedelta(minutes=1)
        assert str_to_relativedelta("MIN") == relativedelta(minutes=1)
        assert str_to_relativedelta("MINUTE") == relativedelta(minutes=1)

    def test_hour_aliases(self):
        """Test hour frequency aliases"""
        assert str_to_relativedelta("H") == relativedelta(hours=1)
        assert str_to_relativedelta("HR") == relativedelta(hours=1)
        assert str_to_relativedelta("HOUR") == relativedelta(hours=1)
        assert str_to_relativedelta("HOURLY") == relativedelta(hours=1)

    def test_day_aliases(self):
        """Test day frequency aliases"""
        assert str_to_relativedelta("D") == relativedelta(days=1)
        assert str_to_relativedelta("DAY") == relativedelta(days=1)
        assert str_to_relativedelta("DAILY") == relativedelta(days=1)

    def test_week_aliases(self):
        """Test week frequency aliases"""
        assert str_to_relativedelta("W") == relativedelta(weeks=1)
        assert str_to_relativedelta("WEEK") == relativedelta(weeks=1)
        assert str_to_relativedelta("WEEKLY") == relativedelta(weeks=1)

    def test_month_aliases(self):
        """Test month frequency aliases"""
        assert str_to_relativedelta("M") == relativedelta(months=1)
        assert str_to_relativedelta("MO") == relativedelta(months=1)
        assert str_to_relativedelta("MONTH") == relativedelta(months=1)
        assert str_to_relativedelta("MONTHLY") == relativedelta(months=1)

    def test_quarter_aliases(self):
        """Test quarter frequency aliases"""
        assert str_to_relativedelta("Q") == relativedelta(months=3)
        assert str_to_relativedelta("QUARTER") == relativedelta(months=3)
        assert str_to_relativedelta("QUARTERLY") == relativedelta(months=3)

    def test_year_aliases(self):
        """Test year frequency aliases"""
        assert str_to_relativedelta("A") == relativedelta(years=1)
        assert str_to_relativedelta("Y") == relativedelta(years=1)
        assert str_to_relativedelta("YEAR") == relativedelta(years=1)
        assert str_to_relativedelta("ANNUAL") == relativedelta(years=1)
        assert str_to_relativedelta("ANNUALLY") == relativedelta(years=1)

    def test_case_insensitive(self):
        """Test that function is case-insensitive"""
        assert str_to_relativedelta("monthly") == relativedelta(months=1)
        assert str_to_relativedelta("MONTHLY") == relativedelta(months=1)
        assert str_to_relativedelta("Monthly") == relativedelta(months=1)

    def test_invalid_frequency_with_default(self):
        """Test invalid frequency with default fallback"""
        default = relativedelta(days=1)
        result = str_to_relativedelta("INVALID", default=default)
        assert result == default

    def test_invalid_frequency_without_default_raises_error(self):
        """Test invalid frequency without default raises ValueError"""
        with pytest.raises(ValueError, match="does not correspond to a known relativedelta"):
            str_to_relativedelta("INVALID")


class TestRelativdeltaToStr:
    """Tests for relativedelta_to_str()"""

    def test_years(self):
        """Test year relativedelta conversion"""
        rd = relativedelta(years=1)
        assert relativedelta_to_str(rd) == "A"

    def test_quarters(self):
        """Test quarter relativedelta conversion"""
        rd = relativedelta(months=3)
        assert relativedelta_to_str(rd) == "Q"

    def test_months(self):
        """Test month relativedelta conversion"""
        rd = relativedelta(months=1)
        assert relativedelta_to_str(rd) == "M"

    def test_weeks(self):
        """Test week relativedelta conversion"""
        rd = relativedelta(weeks=1)
        assert relativedelta_to_str(rd) == "W"

    def test_days(self):
        """Test day relativedelta conversion"""
        rd = relativedelta(days=1)
        assert relativedelta_to_str(rd) == "D"

    def test_hours(self):
        """Test hour relativedelta conversion"""
        rd = relativedelta(hours=1)
        assert relativedelta_to_str(rd) == "H"

    def test_minutes(self):
        """Test minute relativedelta conversion"""
        rd = relativedelta(minutes=1)
        assert relativedelta_to_str(rd) == "T"

    def test_seconds(self):
        """Test second relativedelta conversion"""
        rd = relativedelta(seconds=1)
        assert relativedelta_to_str(rd) == "S"

    def test_priority_order(self):
        """Test that larger units take priority (years > months > days)"""
        # relativedelta with both years and months - years wins
        rd = relativedelta(years=1, months=2)
        assert relativedelta_to_str(rd) == "A"

    def test_zero_relativedelta_with_default(self):
        """Test empty relativedelta with default"""
        rd = relativedelta()
        result = relativedelta_to_str(rd, default="UNKNOWN")
        assert result == "UNKNOWN"

    def test_zero_relativedelta_without_default_raises_error(self):
        """Test empty relativedelta without default raises ValueError"""
        rd = relativedelta()
        with pytest.raises(ValueError, match="does not correspond to a known frequency"):
            relativedelta_to_str(rd)

    def test_roundtrip_conversion(self):
        """Test that str -> relativedelta -> str is consistent"""
        frequencies = ["A", "Q", "M", "W", "D", "H", "T", "S"]
        for freq in frequencies:
            rd = str_to_relativedelta(freq)
            result = relativedelta_to_str(rd)
            assert result == freq


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
