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
