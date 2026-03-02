import os


class APIKeyManager:
    """Manages API keys from environment variables. Keys are loaded lazily on first access."""

    _KEY_NAMES = (
        "ALPHA_VANTAGE_API_KEY",
        "ALPACA_API_KEY",
        "ALPACA_SECRET_KEY",
        "NASDAQ_DATA_LINK_API_KEY",
        "TWELVEDATA_API_KEY",
        "US_BUREAU_OF_LABOR_STATISTICS_API_KEY",
        "GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH",
    )

    def __init__(self) -> None:
        """Initialise the manager with an empty in-memory key cache."""
        self._keys: dict[str, str] = {}

    def get_key(self, key_name: str) -> str:
        """Return the API key for *key_name*, loading it from the environment on first access.

        Args:
            key_name: Environment variable name (e.g. ``"ALPHA_VANTAGE_API_KEY"``).

        Returns:
            The non-empty string value of the environment variable.

        Raises:
            OSError: If the environment variable is not set or is empty.
        """
        if key_name not in self._keys:
            value = os.getenv(key_name)
            if not value:
                raise OSError(f"Couldn't load {key_name} - ensure it's set in the environment.")
            self._keys[key_name] = value
        return self._keys[key_name]
