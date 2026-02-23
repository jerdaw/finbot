from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

from finbot.constants.networking_constants import DEFAULT_TIMEOUT

# Avoid circular import
if TYPE_CHECKING:
    from finbot.libs.api_manager._utils.api import API
    from finbot.utils.request_utils.rate_limiter import RateLimiter


class APIResourceGroup:
    def __init__(
        self,
        identifier: str,
        rate_limit: RateLimiter,
        retry_strategy_kwargs: dict[str, Any],
        concurrency_limit: int = 99999,  # TODO: Implement
        timeout: int | tuple[int, ...] = DEFAULT_TIMEOUT,
        **kwargs: Any,
    ) -> None:
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
        setattr(self.apis, api.identifier, api)

    def get_apis(self) -> dict[str, API]:
        apis: dict[str, API] = {}
        for api in self.apis.__dict__:
            cur_api = getattr(self.apis, api)
            apis[cur_api.identifier] = cur_api
        return apis

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def rate_limit(self) -> RateLimiter:
        return self._rate_limit

    @property
    def retry_strategy_kwargs(self) -> dict[str, Any]:
        return self._retry_strategy_kwargs

    @property
    def concurrency_limit(self) -> int:
        return self._concurrency_limit

    @property
    def timeout(self) -> int | tuple[int, ...]:
        return self._timeout

    @property
    def apis(self) -> SimpleNamespace:
        return self._apis

    def __contains__(self, api_instance: str | API) -> bool:
        if isinstance(api_instance, str):
            return api_instance in [v.identifier for v in self.apis.__dict__.values()]
        return api_instance in self.apis.__dict__.values()
