from types import SimpleNamespace

from config import logger
from libs.api_manager._apis.get_all_apis import get_all_apis
from libs.api_manager._resource_groups.get_all_resource_groups import get_all_resource_groups


# class APIManager:
class APIManager:
    def __init__(self, auto_load_apis: bool = True, auto_load_resource_groups: bool = True):
        self._apis = SimpleNamespace()
        self._api_resource_groups = SimpleNamespace()

        self.auto_load_apis = auto_load_apis
        if self.auto_load_apis:
            self.load_all_apis()

        self.auto_load_resource_groups = auto_load_resource_groups
        if self.auto_load_resource_groups:
            self.load_all_resource_groups()

    def add_api(self, identifier: str, api_instance) -> None:
        setattr(self.apis, identifier, api_instance)

    def get_api(self, identifier: str):
        # Validation has to be called in the getter rather than setter to give time for
        # both apis and api_resource_groups to be added
        try:
            api = getattr(self.apis, identifier)
            if not api.resource_group:
                logger.warning(f"API '{identifier}' does not have any associated API resource groups.")
        except AttributeError:
            logger.error(f"API '{identifier}' does not exist in API Manager instance.")
            raise

    def get_all_apis(self):
        return dict(sorted(self.apis.__dict__.items()))

    def add_api_resource_group(self, identifier: str, api_resource_group_instance) -> None:
        setattr(self.api_resource_groups, identifier, api_resource_group_instance)

    def get_api_resource_group(self, identifier: str):
        # Validation has to be called in the getter rather than setter to give time for
        # both apis and api_resource_groups to be added
        try:
            group = getattr(self.api_resource_groups, identifier)
            if not group.get_apis():
                logger.warning(f"API resource group '{identifier}' does not have any associated APIs.")
        except AttributeError:
            logger.error(f"API resource group '{identifier}' does not exist in API Manager instance.")
            raise

    def get_all_api_resource_groups(self):
        return dict(sorted(self.api_resource_groups.__dict__.items()))

    @property
    def apis(self):
        return self._apis

    @apis.setter
    def apis(self, value):
        self._apis = value

    @property
    def api_resource_groups(self):
        return self._api_resource_groups

    @api_resource_groups.setter
    def api_resource_groups(self, value):
        self._api_resource_groups = value

    def load_all_apis(self):
        apis = get_all_apis()
        for api in apis.values():
            self.add_api(identifier=api.identifier, api_instance=api)

    def load_all_resource_groups(self):
        groups = get_all_resource_groups()
        for group in groups.values():
            self.add_api_resource_group(identifier=group.identifier, api_resource_group_instance=group)


if __name__ == "__main__":
    from finbot.utils.request_utils.rate_limiter import DEFAULT_RATE_LIMIT
    from finbot.utils.request_utils.retry_strategy import DEFAULT_HTTPX_RETRY_KWARGS
    from libs.api_manager import api_manager
    from libs.api_manager._utils.api import API
    from libs.api_manager._utils.api_resource_group import APIResourceGroup

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
