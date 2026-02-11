from __future__ import annotations

from pathlib import Path

# TODO: Re-implement type hints. Makes sure they don't cause circular imports.


class API:
    def _add_api_resource_group(self):
        """Adds this API instance to its resource group."""
        if self.resource_group is not None:
            self.resource_group.add_api(api=self)

    def __init__(
        self,
        identifier: str,
        resource_group,
        response_save_dir: Path | None = None,  # TODO: Implement
        data_save_dir: Path | None = None,  # TODO: Implement
        base_url: None | str = None,
        headers: None | dict[str, str] = None,
        endpoints: None | list[str] = None,
    ):
        """
        Initializes the API instance with necessary details.

        :param identifier: A unique identifier for the API.
        :param base_url: The base URL for the API endpoints.
        :param resource_group: The group of resources this API belongs to.
        :param response_save_dir: The directory to save API responses to.
        :param data_save_dir: The directory to save API data to.
        :param headers: Default headers to use for API requests.
        :param endpoints: A list of available endpoints.
        """
        self._identifier = identifier
        self._base_url = base_url
        self._resource_group = resource_group
        self._response_save_dir = response_save_dir
        self._data_save_dir = data_save_dir
        self._headers = headers  # TODO: change to `headers if headers is not None else {}``
        self._endpoints = endpoints if endpoints else []

        self._add_api_resource_group()

    @property
    def identifier(self):
        return self._identifier

    @property
    def base_url(self):
        return self._base_url

    @property
    def resource_group(self):
        return self._resource_group

    @property
    def response_save_dir(self):
        return self._response_save_dir

    @property
    def data_save_dir(self):
        return self._data_save_dir

    @property
    def headers(self):
        return self._headers

    @property
    def endpoints(self):
        return self._endpoints


if __name__ == "__main__":
    # Example usage
    api = API(identifier="example_api", base_url="https://api.example.com", resource_group=None)
    print(f"API identifier: {api.identifier}")
    print(f"API base URL: {api.base_url}")
    print(f"API resource group: {api.resource_group}")
    print(f"API response save dir: {api.response_save_dir}")
    print(f"API data save dir: {api.data_save_dir}")
    print(f"API headers: {api.headers}")
    print(f"API endpoints: {api.endpoints}")
