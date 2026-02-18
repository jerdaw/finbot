"""Retry strategy configuration for HTTP requests.

This module provides default retry strategy kwargs for use with httpx
or other HTTP clients. The retry strategy handles transient failures
like rate limiting, server errors, and timeouts.
"""

from __future__ import annotations

# Default retry strategy kwargs for httpx or similar HTTP clients
# These are common retry-related configurations
DEFAULT_HTTPX_RETRY_KWARGS: dict[str, int | float | tuple[int, ...]] = {
    "max_retries": 3,
    "backoff_factor": 0.3,
    "status_forcelist": (429, 500, 502, 503, 504),
}

# Alternative: more aggressive retry strategy for unreliable APIs
AGGRESSIVE_RETRY_KWARGS: dict[str, int | float | tuple[int, ...]] = {
    "max_retries": 5,
    "backoff_factor": 0.5,
    "status_forcelist": (408, 429, 500, 502, 503, 504),
}

# Conservative: minimal retries for well-behaved APIs
CONSERVATIVE_RETRY_KWARGS: dict[str, int | float | tuple[int, ...]] = {
    "max_retries": 2,
    "backoff_factor": 0.1,
    "status_forcelist": (429, 503),
}
