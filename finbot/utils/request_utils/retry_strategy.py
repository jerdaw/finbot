"""HTTPX retry compatibility defaults for API manager resource groups."""

from __future__ import annotations

from typing import Any

_DEFAULT_STATUS_FORCELIST = (429, 500, 502, 503, 504)


def _compat_retry_kwargs(max_retries: int, backoff_factor: float) -> dict[str, Any]:
    """Return retry kwargs using canonical HTTPX compatibility key naming."""
    return {
        "attempts": max_retries,
        "backoff": backoff_factor,
        "retry_on": _DEFAULT_STATUS_FORCELIST,
    }


CONSERVATIVE_RETRY_KWARGS: dict[str, Any] = _compat_retry_kwargs(max_retries=2, backoff_factor=0.2)
DEFAULT_HTTPX_RETRY_KWARGS: dict[str, Any] = _compat_retry_kwargs(max_retries=3, backoff_factor=0.3)
AGGRESSIVE_RETRY_KWARGS: dict[str, Any] = _compat_retry_kwargs(max_retries=5, backoff_factor=0.5)
