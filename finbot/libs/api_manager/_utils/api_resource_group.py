"""API resource group model for shared rate-limiting and retry configuration.

A resource group bundles rate limits, retry strategies, concurrency limits,
and timeouts that are shared across one or more API instances.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

from finbot.constants.networking_constants import DEFAULT_TIMEOUT

# Avoid circular import
if TYPE_CHECKING:
    from finbot.libs.api_manager._utils.api import API
    from finbot.utils.request_utils.rate_limiter import RateLimiter


class APIResourceGroup:
    """Groups shared networking constraints for one or more API instances."""

    def __init__(
        self,
        identifier: str,
        rate_limit: RateLimiter,
        retry_strategy_kwargs: dict[str, Any],
        concurrency_limit: int = 99999,  # TODO: Implement
        timeout: int | tuple[int, ...] = DEFAULT_TIMEOUT,
        **kwargs: Any,
    ) -> None:
        """Initialize the resource group with networking constraints.

        Args:
            identifier: Unique name for this resource group.
            rate_limit: RateLimiter instance controlling request frequency.
            retry_strategy_kwargs: Keyword arguments for the retry strategy.
            concurrency_limit: Maximum concurrent requests allowed.
            timeout: Request timeout in seconds (int or tuple of ints).
            **kwargs: Additional attributes to set on the instance.

        Raises:
            ValueError: If a kwarg conflicts with an existing attribute name.
        """
        self._identifier = identifier
        self._rate_limit = rate_limit
        self._retry_strategy_kwargs = retry_strategy_kwargs
        self._concurrency_limit = concurrency_limit
        self._timeout = timeout
        self._apis = SimpleNamespace()

        for kwarg, value in kwargs.items():
            if kwarg in dir(self):
                raise ValueError(f"Attribute '{kwarg}' already exists in APIResourceGroup")
            setattr(self, kwarg, value)

    def add_api(self, api: API) -> None:
        """Register an API instance with this resource group.

        Args:
            api: The API instance to add.
        """
        setattr(self.apis, api.identifier, api)

    def get_apis(self) -> dict[str, API]:
        """Return all APIs registered under this resource group.

        Returns:
            Dictionary mapping identifier strings to API instances.
        """
        apis: dict[str, API] = {}
        for api in self.apis.__dict__:
            cur_api = getattr(self.apis, api)
            apis[cur_api.identifier] = cur_api
        return apis

    @property
    def identifier(self) -> str:
        """Unique identifier for this resource group."""
        return self._identifier

    @property
    def rate_limit(self) -> RateLimiter:
        """Rate limiter controlling request frequency."""
        return self._rate_limit

    @property
    def retry_strategy_kwargs(self) -> dict[str, Any]:
        """Keyword arguments for the HTTP retry strategy."""
        return self._retry_strategy_kwargs

    @property
    def concurrency_limit(self) -> int:
        """Maximum number of concurrent requests allowed."""
        return self._concurrency_limit

    @property
    def timeout(self) -> int | tuple[int, ...]:
        """Request timeout in seconds."""
        return self._timeout

    @property
    def apis(self) -> SimpleNamespace:
        """Namespace containing all APIs registered under this group."""
        return self._apis

    def __contains__(self, api_instance: str | API) -> bool:
        """Check whether an API (by identifier string or instance) belongs to this group."""
        if isinstance(api_instance, str):
            return api_instance in [v.identifier for v in self.apis.__dict__.values()]
        return api_instance in self.apis.__dict__.values()
