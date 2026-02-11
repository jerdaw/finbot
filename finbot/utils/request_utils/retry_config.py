"""Configurable retry logic for HTTP requests with exponential backoff.

Provides a reusable configuration class for setting up intelligent retry
behavior in HTTP requests. Handles transient failures (rate limits, server
errors, timeouts) with exponential backoff to avoid overwhelming servers.

Typical usage:
    ```python
    import requests
    from finbot.utils.request_utils.retry_config import RetryConfig

    # Default configuration (3 retries, exponential backoff)
    config = RetryConfig()
    session = requests.Session()
    config.apply_to_session(session)
    response = session.get("https://api.example.com/data")

    # Custom configuration (5 retries, slower backoff)
    config = RetryConfig(retry_count=5, backoff_factor=1.0, status_forcelist=(429, 500, 502, 503, 504))
    session = requests.Session()
    config.apply_to_session(session)

    # Use with RequestHandler
    from finbot.utils.request_utils.request_handler import RequestHandler

    handler = RequestHandler(retry_config=config)
    ```

Exponential backoff:
    - First retry: backoff_factor seconds
    - Second retry: backoff_factor * 2 seconds
    - Third retry: backoff_factor * 4 seconds
    - Formula: backoff_factor * (2 ** (retry_number - 1))

Backoff factor examples:
    - 0.3 (default): 0.3s, 0.6s, 1.2s, 2.4s...
    - 1.0: 1s, 2s, 4s, 8s...
    - 2.0: 2s, 4s, 8s, 16s...

Default retry behavior:
    - Retry count: 3 attempts
    - Backoff factor: 0.3 seconds
    - Status codes: 429, 500, 502, 503, 504
    - Applies to: HTTP, HTTPS

Status codes that trigger retry (default):
    - 429: Too Many Requests (rate limiting)
    - 500: Internal Server Error
    - 502: Bad Gateway
    - 503: Service Unavailable
    - 504: Gateway Timeout

Features:
    - Configurable retry count
    - Exponential backoff to prevent server overload
    - Customizable HTTP status codes for retry
    - Applies to both read and connect operations
    - Works with both HTTP and HTTPS
    - Thread-safe (per-session configuration)

Parameters:
    - retry_count: Number of retry attempts (default: 3)
    - backoff_factor: Base delay for exponential backoff (default: 0.3)
    - status_forcelist: HTTP status codes that trigger retry

Use cases:
    - API clients with rate limits
    - Fetching data from occasionally unreliable services
    - Production applications requiring robustness
    - Automated data collection pipelines
    - Services behind load balancers (502, 503 errors)

Why retry these status codes:
    - 429: Rate limit - wait and retry automatically
    - 500: Server error - may be transient, worth retrying
    - 502: Bad gateway - upstream service may recover quickly
    - 503: Service unavailable - temporary overload, retry helps
    - 504: Gateway timeout - may succeed on retry

Best practices:
    ```python
    # For rate-limited APIs (slower backoff)
    config = RetryConfig(retry_count=5, backoff_factor=1.0, status_forcelist=(429, 500, 502, 503, 504))

    # For internal APIs (faster retries)
    config = RetryConfig(retry_count=2, backoff_factor=0.1, status_forcelist=(500, 502, 503))

    # For unreliable external APIs (more retries)
    config = RetryConfig(
        retry_count=6,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504, 408),  # Add timeout
    )
    ```

Session application:
    - Mounts adapters for both http:// and https://
    - Applies to all requests made through the session
    - Retry strategy applies to read, connect, and status
    - Does not modify global requests behavior

Retry types:
    - Read retries: Retry on read timeouts
    - Connect retries: Retry on connection failures
    - Status retries: Retry on specific HTTP status codes

Limitations:
    - Does not retry 4xx errors (except 429)
    - Does not retry POST/PUT/PATCH by default (safety)
    - Cannot retry if response body already consumed
    - Exponential backoff may be too slow for some use cases

Why exponential backoff:
    - Prevents overwhelming recovering servers
    - Automatically adapts to server load
    - Industry best practice for retry logic
    - Required by many API providers (rate limiting)

Dependencies: requests, urllib3

Related modules: request_handler (uses RetryConfig), request_utils package
(HTTP request utilities), save_json/save_text (response caching).
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class RetryConfig:
    """
    Configuration class for setting up retry logic in HTTP requests.

    Attributes:
        retry_count (int): Number of retries for a request.
        backoff_factor (float): Factor for exponential delay between retries.
        status_forcelist (tuple[int, ...]): HTTP statuses that trigger a retry.
    """

    def __init__(
        self,
        retry_count: int = 3,
        backoff_factor: float = 0.3,
        status_forcelist: tuple[int, ...] = (429, 500, 502, 503, 504),
    ):
        """
        Initializes the RetryConfig with default or custom settings.

        Args:
            retry_count (int): Number of retries. Default is 3.
            backoff_factor (float): Exponential backoff factor. Default is 0.3.
            status_forcelist (tuple[int, ...]): Tuple of HTTP status codes to retry. Defaults to (429, 500, 502, 503, 504).
        """
        self.retry_count = retry_count
        self.backoff_factor = backoff_factor
        self.status_forcelist = status_forcelist

    def apply_to_session(self, session: requests.Session):
        """
        Applies the retry configuration to a given requests session.

        Args:
            session (requests.Session): The session to which the retry strategy will be applied.
        """
        retry_strategy = Retry(
            total=self.retry_count,
            read=self.retry_count,
            connect=self.retry_count,
            backoff_factor=self.backoff_factor,
            status_forcelist=self.status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
