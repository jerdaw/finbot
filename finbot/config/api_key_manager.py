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
        self._keys: dict[str, str] = {}

    def get_key(self, key_name: str) -> str:
        if key_name not in self._keys:
            value = os.getenv(key_name)
            if not value:
                raise OSError(f"Couldn't load {key_name} - ensure it's set in the environment.")
            self._keys[key_name] = value
        return self._keys[key_name]
