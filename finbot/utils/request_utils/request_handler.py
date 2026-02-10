from __future__ import annotations

from pathlib import Path
from typing import Any

import requests

from config import logger
from constants.path_constants import RESPONSES_DATA_DIR
from finbot.utils.file_utils.save_text import save_text
from finbot.utils.json_utils.save_json import save_json
from finbot.utils.request_utils.retry_config import RetryConfig


class RequestHandler:
    """
    Handler class for making HTTP requests with retry logic and response processing.

    Methods:
        make_json_request: Makes an HTTP request and expects a JSON response.
        make_text_request: Makes an HTTP request and expects a text response.
        make_request: Core method for making HTTP requests.
        save_response: Saves the response to a file.
    """

    def __init__(self, retry_config: None | RetryConfig = None):
        """
        Initializes the RequestHandler with a given retry configuration.

        Args:
            retry_config (None | RetryConfig): Configuration for retry logic. Defaults to a standard configuration.
        """
        if retry_config is None:
            retry_config = RetryConfig()
        self.session = requests.Session()
        retry_config.apply_to_session(self.session)

    def make_json_request(
        self,
        url: str,
        payload_kwargs: None | dict[str, Any] = None,
        headers: None | dict[str, str] = None,
        request_type: str = "GET",
        **kwargs,
    ) -> dict[str, Any]:
        """
        Makes an HTTP request and expects a JSON response.

        Args:
            url (str): The URL to send the request to.
            payload_kwargs (None | dict[str, Any]): Additional keyword arguments to be sent as payload. Defaults to an empty dict.
            headers (None | dict[str, str]): HTTP headers for the request. Defaults to an empty dict.
            request_type (str): Type of HTTP request (e.g., 'GET', 'POST'). Defaults to 'GET'.
            **kwargs: Additional keyword arguments for response handling and saving.

        Returns:
            dict[str, Any]: The JSON response from the request.

        Raises:
            ValueError: If the response is not in JSON format.
            requests.RequestException: For network-related errors.
        """
        if payload_kwargs is None:
            payload_kwargs = {}
        if headers is None:
            headers = {}

        response = self.make_request(url, payload_kwargs, headers, request_type, **kwargs)

        content_type = response.headers.get("Content-Type", "").split(";")[0].strip()
        if content_type == "application/json":
            json_data = response.json()
        else:
            logger.error(f"Expected application/json response, got: {content_type}")
            raise ValueError("Response is not in JSON format")

        self.save_response(kwargs, json_data)
        return json_data

    def make_text_request(
        self,
        url: str,
        payload_kwargs: None | dict[str, Any] = None,
        headers: None | dict[str, str] = None,
        request_type: str = "GET",
        **kwargs,
    ) -> str:
        """
        Makes an HTTP request and expects a text response.

        Args:
            url (str): The URL to send the request to.
            payload_kwargs (None | dict[str, Any]): Additional keyword arguments to be sent as payload. Defaults to an empty dict.
            headers (None | dict[str, str]): HTTP headers for the request. Defaults to an empty dict.
            request_type (str): Type of HTTP request (e.g., 'GET', 'POST'). Defaults to 'GET'.
            **kwargs: Additional keyword arguments for response handling and saving.

        Returns:
            str: The text response from the request.

        Raises:
            ValueError: If the response is not in text format.
            requests.RequestException: For network-related errors.
        """
        if payload_kwargs is None:
            payload_kwargs = {}
        if headers is None:
            headers = {}

        response = self.make_request(url, payload_kwargs, headers, request_type, **kwargs)

        content_type = response.headers.get("Content-Type", "").split(";")[0].strip()
        if content_type == "text/plain":
            text_data = response.text
        else:
            logger.warning(f"Expected text/plain response, got: {content_type}. Returning raw response.")
            text_data = response.text  # or 'return response.content' for binary data

        self.save_response(kwargs, text_data)
        return text_data

    def make_request(
        self,
        url: str,
        payload_kwargs: None | dict[str, Any] = None,
        headers: None | dict[str, str] = None,
        request_type: str = "GET",
        save_dir: str | Path | None = RESPONSES_DATA_DIR,
        file_name: str | None = None,
        compress: bool = True,
        **kwargs,
    ) -> requests.Response:
        """
        Core method for making HTTP requests.

        Args:
            url (str): The URL to send the request to.
            payload_kwargs (None | dict[str, Any]): Additional keyword arguments to be sent as payload. Defaults to an empty dict.
            headers (None | dict[str, str]): HTTP headers for the request. Defaults to an empty dict.
            request_type (str): Type of HTTP request (e.g., 'GET', 'POST', 'PUT', 'DELETE', 'PATCH').
            save_dir (str | Path | None): Directory where the response will be saved. Defaults to RESPONSES_DATA_DIR.
            file_name (str | None): Name of the file to save the response. Default is None.
            compress (bool): Whether to compress the saved file. Defaults to True.
            kwargs: Additional keyword arguments for making the request.

        Returns:
            requests.Response: The raw response from the request.

        Raises:
            NotImplementedError: If the request type is not supported.
            requests.RequestException: For network-related errors.
        """
        try:
            if payload_kwargs is None:
                payload_kwargs = {}
            if headers is None:
                headers = {}

            request_type = request_type.upper()
            if request_type not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                raise NotImplementedError(f"Request type {request_type} is not supported.")

            request_kwargs = {"method": request_type, "url": url, "headers": headers, "timeout": (5, 20)}
            request_kwargs.update(payload_kwargs)
            request_kwargs.update(kwargs)

            response = self.session.request(**request_kwargs)  # type: ignore

            if not response.ok:
                logger.warning(
                    f"HTTP request to {url} with method {request_type} failed: {response.status_code} {response.reason}",
                )
                response.raise_for_status()

        except requests.RequestException as err:
            logger.error(f"HTTP request to {url} with method {request_type} failed: {err}", exc_info=True)
            raise

        return response

    def save_response(self, save_options: dict, response_data: Any):
        """
        Saves the response data to a file.
        """
        if save_options.get("save_dir"):
            if isinstance(response_data, dict):
                save_json(
                    data=response_data,
                    save_dir=save_options["save_dir"],
                    file_name=save_options.get("file_name"),
                    compress=save_options.get("compress", True),
                )
            else:
                save_text(
                    text=response_data,
                    save_dir=save_options["save_dir"],
                    file_name=save_options.get("file_name"),
                    compress=save_options.get("compress", True),
                )

    def __enter__(self):
        """
        Enables use of the RequestHandler with the 'with' statement for context management.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Ensures clean-up actions (like closing the session) when exiting the 'with' context.
        """
        self.session.close()


if __name__ == "__main__":
    # Example usage of RequestHandler
    url = "https://jsonplaceholder.typicode.com/todos/1"

    # Example 1: Making a JSON request
    handler = RequestHandler()
    try:
        json_response = handler.make_json_request(url)
        print("JSON Response:", json_response)
    except Exception as e:
        print("Error during JSON request:", e)

    # Example 2: Making a Text request
    try:
        text_response = handler.make_text_request(url)
        print("Text Response:", text_response)
    except Exception as e:
        print("Error during Text request:", e)
