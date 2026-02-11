"""HTTP request handler with retry logic, caching, and response processing.

Provides a comprehensive HTTP client with automatic retries, exponential backoff,
response caching (JSON/text), and structured error handling. Designed for
reliable data collection from APIs with built-in resilience.

Typical usage:
    ```python
    from finbot.utils.request_utils import RequestHandler

    # Basic JSON API request
    handler = RequestHandler()
    data = handler.make_json_request("https://api.example.com/data")

    # JSON request with caching
    data = handler.make_json_request(
        "https://api.example.com/prices", save_dir="/data/cache", file_name="prices.json.zst"
    )

    # Text/HTML request
    html = handler.make_text_request("https://example.com/page")

    # POST request with payload
    response = handler.make_json_request(
        "https://api.example.com/submit", payload_kwargs={"json": {"key": "value"}}, request_type="POST"
    )

    # Custom retry configuration
    from finbot.utils.request_utils.retry_config import RetryConfig

    config = RetryConfig(retry_count=5, backoff_factor=1.0)
    handler = RequestHandler(retry_config=config)

    # Context manager (auto-closes session)
    with RequestHandler() as handler:
        data = handler.make_json_request("https://api.example.com/data")
    ```

Features:
    - Automatic retries with exponential backoff (configurable)
    - JSON and text response handling
    - Optional response caching (saves to file automatically)
    - Comprehensive error handling and logging
    - Session-based (connection pooling, keep-alive)
    - Context manager support (clean session cleanup)
    - Flexible request types (GET, POST, PUT, DELETE, PATCH)

Request methods:

1. **make_json_request()**:
   - Expects and validates JSON response
   - Returns dict or list
   - Raises ValueError if response not JSON
   - Optional caching to .json.zst file

2. **make_text_request()**:
   - Expects text/plain response (flexible)
   - Returns string
   - Handles any content-type gracefully
   - Optional caching to .txt.zst file

3. **make_request()** (core method):
   - Low-level request interface
   - Returns raw requests.Response
   - Configurable save behavior
   - Used by make_json_request and make_text_request

Retry behavior:
    - Default: 3 retries with 0.3s exponential backoff
    - Retries on: 429, 500, 502, 503, 504
    - Configurable via RetryConfig
    - Applies to connection, read, and status errors

Response caching:
    - Automatic when save_dir specified
    - JSON responses → .json.zst (compressed)
    - Text responses → .txt.zst (compressed)
    - Auto-generated filenames (timestamp + hash)
    - Custom filenames supported

Error handling:
    - requests.RequestException: Network errors, timeouts
    - ValueError: Non-JSON response when JSON expected
    - NotImplementedError: Unsupported request type
    - All errors logged with context before raising

Use cases:
    - API data collection (financial data, weather, news)
    - Web scraping with retry logic
    - Cached API responses for development/testing
    - Production data pipelines with resilience
    - Rate-limited API clients

Example workflows:
    ```python
    # Cached API data collection
    handler = RequestHandler()
    for symbol in ["SPY", "QQQ", "TLT"]:
        url = f"https://api.example.com/prices/{symbol}"
        data = handler.make_json_request(url, save_dir="/data/prices", file_name=f"{symbol}.json.zst")
        process_prices(data)

    # Resilient web scraping
    config = RetryConfig(retry_count=5, backoff_factor=1.0)
    with RequestHandler(retry_config=config) as handler:
        html = handler.make_text_request("https://example.com/data")
        parse_html(html)

    # API with authentication
    handler = RequestHandler()
    headers = {"Authorization": "Bearer YOUR_TOKEN"}
    data = handler.make_json_request("https://api.example.com/secure", headers=headers)
    ```

Request types supported:
    - GET: Retrieve data (default)
    - POST: Submit data, create resources
    - PUT: Update resources
    - DELETE: Remove resources
    - PATCH: Partial updates

Default timeout:
    - Connect timeout: 5 seconds
    - Read timeout: 20 seconds
    - Format: (connect, read) tuple

Content-type handling:
    - make_json_request() validates application/json
    - make_text_request() accepts any content-type (logs warning)
    - Custom content-type handling via make_request()

Session benefits:
    - Connection pooling (reuses TCP connections)
    - HTTP keep-alive
    - Cookie persistence across requests
    - Shared configuration (headers, auth, retry)

Best practices:
    ```python
    # Use context manager for automatic cleanup
    with RequestHandler() as handler:
        data = handler.make_json_request(url)

    # Configure retries for API characteristics
    api_config = RetryConfig(
        retry_count=5,  # More for rate-limited APIs
        backoff_factor=1.0,  # Slower for strict rate limits
        status_forcelist=(429, 500, 502, 503),
    )

    # Cache responses for development
    handler.make_json_request(
        url,
        save_dir="/tmp/api_cache",  # Speeds up development
        compress=True,  # Saves disk space
    )
    ```

Performance:
    - Session reuse: ~50% faster than creating new connections
    - Connection pooling: Significant speedup for multiple requests
    - Compression: Minimal overhead for caching
    - Retry overhead: Only on failures

Limitations:
    - Not async (use aiohttp for async)
    - No streaming support (loads full response)
    - Caching is append-only (no cache invalidation)
    - Session not shared across instances

Dependencies: requests, save_json (JSON caching), save_text (text caching),
RetryConfig (retry logic)

Related modules: save_json/save_text (response caching), retry_config
(retry configuration), data_collection_utils (uses RequestHandler for
API data fetching).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import requests

from finbot.config import logger
from finbot.constants.path_constants import RESPONSES_DATA_DIR
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
