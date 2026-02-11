"""Unit tests for datetime utility functions."""

from __future__ import annotations

import datetime
from datetime import date

import pytest


class TestGetDuration:
    """Tests for duration calculation."""

    def test_duration_days(self):
        """Test duration calculation in days."""
        from finbot.utils.datetime_utils.get_duration import get_duration

        start = date(2020, 1, 1)
        end = date(2020, 1, 10)

        result = get_duration(start, end)
        assert result.days == 9

    def test_duration_with_datetime(self):
        """Test duration with datetime objects."""
        from finbot.utils.datetime_utils.get_duration import get_duration

        start = datetime.datetime(2020, 1, 1, 12, 0)
        end = datetime.datetime(2020, 1, 2, 12, 0)

        result = get_duration(start, end)
        assert result.days == 1


class TestGetUSBusinessDates:
    """Tests for US business dates."""

    def test_get_business_dates_import(self):
        """Test that get_us_business_dates can be imported."""
        from finbot.utils.datetime_utils.get_us_business_dates import get_us_business_dates

        assert callable(get_us_business_dates)


class TestValidateStartEndDates:
    """Tests for start/end date validation."""

    def test_validate_start_end_dates_import(self):
        """Test that validate_start_end_dates can be imported."""
        from finbot.utils.datetime_utils.validate_start_end_dates import validate_start_end_dates

        assert callable(validate_start_end_dates)


class TestConversions:
    """Tests for datetime conversions."""

    def test_conversion_modules_import(self):
        """Test that conversion modules can be imported."""
        from finbot.utils.datetime_utils import conversions

        assert conversions is not None


class TestGetMonthsBetweenDates:
    """Tests for calculating months between dates."""

    def test_get_months_between_dates_import(self):
        """Test that get_months_between_dates can be imported."""
        from finbot.utils.datetime_utils.get_months_between_dates import get_months_between_dates

        assert callable(get_months_between_dates)


class TestCeilDatetime:
    """Tests for ceiling datetime to frequency."""

    def test_ceil_datetime_import(self):
        """Test that ceil_datetime can be imported."""
        from finbot.utils.datetime_utils.ceil_datetime import ceil_datetime

        assert callable(ceil_datetime)


class TestGetOverlappingDateRange:
    """Tests for finding overlapping date ranges."""

    def test_get_overlapping_date_range_import(self):
        """Test that get_overlapping_date_range can be imported."""
        from finbot.utils.datetime_utils.get_overlapping_date_range import get_overlapping_date_range

        assert callable(get_overlapping_date_range)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
