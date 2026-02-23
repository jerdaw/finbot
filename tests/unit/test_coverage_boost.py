"""Targeted tests to push coverage past 60%.

Covers small uncovered modules: error_constants, get_overlapping_date_range.

Priority 7, Item P7.2: Increase test coverage to 60%+
"""

from __future__ import annotations

import pandas as pd
import pytest


class TestErrorConstants:
    """Tests for finbot.constants.error_constants."""

    def test_constants_exist(self):
        from finbot.constants.error_constants import (
            GENERIC_ERROR_CODE,
            NOT_FOUND_ERROR_CODE,
            NOT_FOUND_ERROR_MSG,
        )

        assert isinstance(GENERIC_ERROR_CODE, int)
        assert isinstance(NOT_FOUND_ERROR_CODE, int)
        assert isinstance(NOT_FOUND_ERROR_MSG, str)

    def test_constant_values(self):
        from finbot.constants.error_constants import (
            GENERIC_ERROR_CODE,
            NOT_FOUND_ERROR_CODE,
            NOT_FOUND_ERROR_MSG,
        )

        assert GENERIC_ERROR_CODE == 1000
        assert NOT_FOUND_ERROR_CODE == 1001
        assert "not found" in NOT_FOUND_ERROR_MSG.lower()

    def test_error_codes_distinct(self):
        from finbot.constants.error_constants import GENERIC_ERROR_CODE, NOT_FOUND_ERROR_CODE

        assert GENERIC_ERROR_CODE != NOT_FOUND_ERROR_CODE


class TestGetOverlappingDateRange:
    """Tests for finbot.utils.datetime_utils.get_overlapping_date_range."""

    def _make_series(self, start: str, end: str, freq: str = "D") -> pd.Series:
        idx = pd.date_range(start, end, freq=freq)
        return pd.Series(range(len(idx)), index=idx)

    def test_two_series_overlap(self):
        from finbot.utils.datetime_utils.get_overlapping_date_range import get_overlapping_date_range

        s1 = self._make_series("2020-01-01", "2021-12-31")
        s2 = self._make_series("2020-06-01", "2022-06-01")
        start, end = get_overlapping_date_range(s1, s2)
        assert start == pd.Timestamp("2020-06-01")
        assert end == pd.Timestamp("2021-12-31")

    def test_three_series_overlap(self):
        from finbot.utils.datetime_utils.get_overlapping_date_range import get_overlapping_date_range

        s1 = self._make_series("2018-01-01", "2022-12-31")
        s2 = self._make_series("2019-01-01", "2023-12-31")
        s3 = self._make_series("2020-01-01", "2021-12-31")
        start, end = get_overlapping_date_range(s1, s2, s3)
        assert start == pd.Timestamp("2020-01-01")
        assert end == pd.Timestamp("2021-12-31")

    def test_no_overlap_raises(self):
        from finbot.utils.datetime_utils.get_overlapping_date_range import get_overlapping_date_range

        s1 = self._make_series("2020-01-01", "2020-06-30")
        s2 = self._make_series("2021-01-01", "2021-12-31")
        with pytest.raises(ValueError, match="No overlapping date range"):
            get_overlapping_date_range(s1, s2)

    def test_no_overlap_no_raise(self):
        from finbot.utils.datetime_utils.get_overlapping_date_range import get_overlapping_date_range

        s1 = self._make_series("2020-01-01", "2020-06-30")
        s2 = self._make_series("2021-01-01", "2021-12-31")
        start, end = get_overlapping_date_range(s1, s2, raise_error=False)
        assert start > end  # No overlap: start > end

    def test_identical_series(self):
        from finbot.utils.datetime_utils.get_overlapping_date_range import get_overlapping_date_range

        s1 = self._make_series("2020-01-01", "2020-12-31")
        s2 = self._make_series("2020-01-01", "2020-12-31")
        start, end = get_overlapping_date_range(s1, s2)
        assert start == pd.Timestamp("2020-01-01")
        assert end == pd.Timestamp("2020-12-31")


class TestRetryStrategy:
    """Tests for finbot.utils.request_utils.retry_strategy constants."""

    def test_default_retry_kwargs_exist(self):
        from finbot.utils.request_utils.retry_strategy import DEFAULT_HTTPX_RETRY_KWARGS

        assert "attempts" in DEFAULT_HTTPX_RETRY_KWARGS
        assert "backoff" in DEFAULT_HTTPX_RETRY_KWARGS
        assert "retry_on" in DEFAULT_HTTPX_RETRY_KWARGS

    def test_aggressive_retry_kwargs_exist(self):
        from finbot.utils.request_utils.retry_strategy import AGGRESSIVE_RETRY_KWARGS

        assert AGGRESSIVE_RETRY_KWARGS["attempts"] >= 4

    def test_conservative_retry_kwargs_exist(self):
        from finbot.utils.request_utils.retry_strategy import CONSERVATIVE_RETRY_KWARGS

        assert CONSERVATIVE_RETRY_KWARGS["attempts"] <= 3

    def test_max_retries_ordering(self):
        from finbot.utils.request_utils.retry_strategy import (
            AGGRESSIVE_RETRY_KWARGS,
            CONSERVATIVE_RETRY_KWARGS,
            DEFAULT_HTTPX_RETRY_KWARGS,
        )

        assert CONSERVATIVE_RETRY_KWARGS["attempts"] < DEFAULT_HTTPX_RETRY_KWARGS["attempts"]
        assert DEFAULT_HTTPX_RETRY_KWARGS["attempts"] < AGGRESSIVE_RETRY_KWARGS["attempts"]


class TestRateLimiter:
    """Tests for finbot.utils.request_utils.rate_limiter."""

    def test_rate_limiter_init(self):
        from finbot.utils.request_utils.rate_limiter import RateLimiter

        rl = RateLimiter("5/minute")
        assert rl.rate_limits == "5/minute"

    def test_rate_limiter_repr(self):
        from finbot.utils.request_utils.rate_limiter import RateLimiter

        rl = RateLimiter("120/minute")
        assert "120/minute" in repr(rl)

    def test_default_rate_limit(self):
        from finbot.utils.request_utils.rate_limiter import DEFAULT_RATE_LIMIT, RateLimiter

        assert isinstance(DEFAULT_RATE_LIMIT, RateLimiter)
        assert "minute" in DEFAULT_RATE_LIMIT.rate_limits

    def test_complex_rate_limit_string(self):
        from finbot.utils.request_utils.rate_limiter import RateLimiter

        rl = RateLimiter("5/minute;500/day")
        assert rl.rate_limits == "5/minute;500/day"


class TestNetworkingConstants:
    """Tests for finbot.constants.networking_constants."""

    def test_default_timeout_exists(self):
        from finbot.constants.networking_constants import DEFAULT_TIMEOUT

        assert isinstance(DEFAULT_TIMEOUT, tuple)
        assert len(DEFAULT_TIMEOUT) == 4

    def test_default_timeout_positive(self):
        from finbot.constants.networking_constants import DEFAULT_TIMEOUT

        assert all(t > 0 for t in DEFAULT_TIMEOUT)


class TestConstantsImportable:
    """Smoke tests ensuring all constants modules import cleanly."""

    def test_app_constants_importable(self):
        import finbot.constants.app_constants  # noqa: F401

    def test_config_constants_importable(self):
        import finbot.constants.config_constants  # noqa: F401

    def test_logging_constants_importable(self):
        import finbot.constants.logging_constants  # noqa: F401

    def test_security_constants_importable(self):
        import finbot.constants.security_constants  # noqa: F401

    def test_message_constants_importable(self):
        import finbot.constants.message_constants  # noqa: F401

    def test_ui_constants_importable(self):
        import finbot.constants.ui_constants  # noqa: F401

    def test_db_constants_importable(self):
        import finbot.constants.db_constants  # noqa: F401


class TestApiResourceGroups:
    """Tests for API resource group utilities."""

    def test_get_all_resource_groups_returns_dict(self):
        from finbot.libs.api_manager._resource_groups.get_all_resource_groups import get_all_resource_groups

        result = get_all_resource_groups()
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_get_all_resource_groups_keys_are_strings(self):
        from finbot.libs.api_manager._resource_groups.get_all_resource_groups import get_all_resource_groups

        result = get_all_resource_groups()
        assert all(isinstance(k, str) for k in result)

    def test_get_all_resource_groups_contains_fred(self):
        from finbot.libs.api_manager._resource_groups.get_all_resource_groups import get_all_resource_groups

        result = get_all_resource_groups()
        assert any("fred" in k.lower() for k in result)
