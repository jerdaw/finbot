"""Tests for request utility compatibility modules."""

from __future__ import annotations

from limits.limits import RateLimitItem

from finbot.utils.request_utils.rate_limiter import DEFAULT_RATE_LIMIT, RateLimiter
from finbot.utils.request_utils.retry_strategy import DEFAULT_HTTPX_RETRY_KWARGS


def test_rate_limiter_parses_string_limits() -> None:
    limiter = RateLimiter("5/minute;500/day")
    assert len(limiter.parsed_limits) == 2
    assert all(isinstance(item, RateLimitItem) for item in limiter.parsed_limits)


def test_rate_limiter_accepts_preparsed_limits() -> None:
    parsed = DEFAULT_RATE_LIMIT.parsed_limits
    limiter = RateLimiter(parsed)
    assert limiter.parsed_limits == parsed


def test_retry_strategy_defaults_have_expected_keys() -> None:
    assert set(DEFAULT_HTTPX_RETRY_KWARGS) == {"attempts", "backoff", "retry_on"}
    assert DEFAULT_HTTPX_RETRY_KWARGS["attempts"] == 3
