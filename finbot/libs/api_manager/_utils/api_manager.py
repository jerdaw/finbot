"""Central API manager for registering and retrieving APIs and resource groups.

Provides a singleton-style registry that auto-loads all configured APIs and
their associated resource groups at initialization time.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING

from finbot.config import logger
from finbot.libs.api_manager._apis.get_all_apis import get_all_apis
from finbot.libs.api_manager._resource_groups.get_all_resource_groups import get_all_resource_groups

if TYPE_CHECKING:
    from finbot.libs.api_manager._utils.api import API
    from finbot.libs.api_manager._utils.api_resource_group import APIResourceGroup


class APIManager:
    """Central registry for API instances and their resource groups.

    Manages the lifecycle of API registrations and provides lookup by
    identifier. By default, all known APIs and resource groups are loaded
    automatically on construction.
    """

    def __init__(self, auto_load_apis: bool = True, auto_load_resource_groups: bool = True) -> None:
        """Initialize the API manager.

        Args:
            auto_load_apis: If True, load all pre-configured APIs on init.
            auto_load_resource_groups: If True, load all pre-configured
                resource groups on init.
        """
        self._apis = SimpleNamespace()
        self._api_resource_groups = SimpleNamespace()

        self.auto_load_apis = auto_load_apis
        if self.auto_load_apis:
            self.load_all_apis()

        self.auto_load_resource_groups = auto_load_resource_groups
        if self.auto_load_resource_groups:
            self.load_all_resource_groups()

    def add_api(self, identifier: str, api_instance: API) -> None:
        """Register an API instance under the given identifier.

        Args:
            identifier: Unique name for the API.
            api_instance: The API object to register.
        """
        setattr(self.apis, identifier, api_instance)

    def get_api(self, identifier: str) -> API:
        """Retrieve a registered API by its identifier.

        Logs a warning if the API has no associated resource group.

        Args:
            identifier: Unique name of the API to retrieve.

        Returns:
            The registered API instance.

        Raises:
            AttributeError: If no API with the given identifier exists.
        """
        # Validation has to be called in the getter rather than setter to give time for
        # both apis and api_resource_groups to be added
        try:
            api = getattr(self.apis, identifier)
            if not api.resource_group:
                logger.warning(f"API '{identifier}' does not have any associated API resource groups.")
        except AttributeError:
            logger.error(f"API '{identifier}' does not exist in API Manager instance.")
            raise
        return api

    def get_all_apis(self) -> dict[str, API]:
        """Return all registered APIs sorted alphabetically by identifier.

        Returns:
            Dictionary mapping identifier strings to API instances.
        """
        return dict(sorted(self.apis.__dict__.items()))

    def add_api_resource_group(self, identifier: str, api_resource_group_instance: APIResourceGroup) -> None:
        """Register an API resource group under the given identifier.

        Args:
            identifier: Unique name for the resource group.
            api_resource_group_instance: The resource group object to register.
        """
        setattr(self.api_resource_groups, identifier, api_resource_group_instance)

    def get_api_resource_group(self, identifier: str) -> APIResourceGroup:
        """Retrieve a registered resource group by its identifier.

        Logs a warning if the resource group has no associated APIs.

        Args:
            identifier: Unique name of the resource group to retrieve.

        Returns:
            The registered APIResourceGroup instance.

        Raises:
            AttributeError: If no resource group with the given identifier exists.
        """
        # Validation has to be called in the getter rather than setter to give time for
        # both apis and api_resource_groups to be added
        try:
            group = getattr(self.api_resource_groups, identifier)
            if not group.get_apis():
                logger.warning(f"API resource group '{identifier}' does not have any associated APIs.")
        except AttributeError:
            logger.error(f"API resource group '{identifier}' does not exist in API Manager instance.")
            raise
        return group

    def get_all_api_resource_groups(self) -> dict[str, APIResourceGroup]:
        """Return all registered resource groups sorted alphabetically.

        Returns:
            Dictionary mapping identifier strings to APIResourceGroup instances.
        """
        return dict(sorted(self.api_resource_groups.__dict__.items()))

    @property
    def apis(self) -> SimpleNamespace:
        """Namespace containing all registered API instances."""
        return self._apis

    @apis.setter
    def apis(self, value: SimpleNamespace) -> None:
        """Set the APIs namespace."""
        self._apis = value

    @property
    def api_resource_groups(self) -> SimpleNamespace:
        """Namespace containing all registered resource groups."""
        return self._api_resource_groups

    @api_resource_groups.setter
    def api_resource_groups(self, value: SimpleNamespace) -> None:
        """Set the resource groups namespace."""
        self._api_resource_groups = value

    def load_all_apis(self) -> None:
        """Load and register all pre-configured API instances."""
        apis = get_all_apis()
        for api in apis.values():
            self.add_api(identifier=api.identifier, api_instance=api)

    def load_all_resource_groups(self) -> None:
        """Load and register all pre-configured resource groups."""
        groups = get_all_resource_groups()
        for group in groups.values():
            self.add_api_resource_group(identifier=group.identifier, api_resource_group_instance=group)


if __name__ == "__main__":
    from finbot.libs.api_manager import api_manager
    from finbot.libs.api_manager._utils.api import API
    from finbot.libs.api_manager._utils.api_resource_group import APIResourceGroup
    from finbot.utils.request_utils.rate_limiter import DEFAULT_RATE_LIMIT
    from finbot.utils.request_utils.retry_strategy import DEFAULT_HTTPX_RETRY_KWARGS

    # Example usage
    api_resource_group = APIResourceGroup(
        identifier="testAPIResourceGroup",
        rate_limit=DEFAULT_RATE_LIMIT,
        retry_strategy_kwargs=DEFAULT_HTTPX_RETRY_KWARGS,
    )
    api_manager.add_api_resource_group(
        identifier=api_resource_group.identifier,
        api_resource_group_instance=api_resource_group,
    )
    api = API(identifier="testAPI", base_url="https://api.example.com", resource_group=api_resource_group)
    api_manager.add_api(identifier=api.identifier, api_instance=api)
    print(f"\nExample Api: {api.identifier, api_resource_group.identifier}")
    print(f"\nAll Apis: {api_manager.get_all_apis()}")
    print(f"\nAll Api Resource Groups: {api_manager.get_all_api_resource_groups()}")
