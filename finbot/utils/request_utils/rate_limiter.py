"""Rate limiter compatibility shim used by the API manager layer.

This module provides a lightweight `RateLimiter` type that stores parsed limits.
The current API manager contracts only require configuration storage, not active
request throttling behavior.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from limits import parse, parse_many
from limits.limits import RateLimitItem


@dataclass(frozen=True)
class RateLimiter:
    """Container for configured API rate limits."""

    rate_limits: str | Iterable[RateLimitItem]
    parsed_limits: tuple[RateLimitItem, ...] = field(init=False)

    def __post_init__(self) -> None:
        parsed = self._parse_limits(self.rate_limits)
        object.__setattr__(self, "parsed_limits", parsed)

    @staticmethod
    def _parse_limits(limits_input: str | Iterable[RateLimitItem]) -> tuple[RateLimitItem, ...]:
        if isinstance(limits_input, str):
            if ";" in limits_input:
                return tuple(parse_many(limits_input))
            return (parse(limits_input),)
        return tuple(limits_input)


DEFAULT_RATE_LIMIT = RateLimiter("60/minute")
