"""Rate limiter stub for API resource groups.

This module provides a simple RateLimiter class that wraps around
rate limit specifications. Currently a minimal implementation to satisfy
module imports - full rate limiting functionality is handled by the
limits library in APIResourceGroup.
"""

from __future__ import annotations


class RateLimiter:
    """Simple rate limiter wrapper.

    Args:
        rate_limits: Rate limit specification string (e.g., "5/minute;500/day")

    Note:
        This is a stub implementation. Actual rate limiting is handled by
        the limits library in APIResourceGroup.
    """

    def __init__(self, rate_limits: str):
        """Initialize rate limiter with rate limits specification.

        Args:
            rate_limits: Rate limit string in format "count/period;count/period"
                        Examples: "5/minute", "120/minute", "5/minute;500/day"
        """
        self.rate_limits = rate_limits

    def __repr__(self) -> str:
        """Return string representation."""
        return f"RateLimiter(rate_limits={self.rate_limits!r})"


# Default rate limit (120 requests per minute)
DEFAULT_RATE_LIMIT = RateLimiter(rate_limits="120/minute")
