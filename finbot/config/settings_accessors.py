"""
Settings accessors for commonly used config values.

This module provides convenient access to settings values with
computed defaults where appropriate.
"""

from __future__ import annotations

from finbot.config.api_key_manager import APIKeyManager
from finbot.config.project_config import settings
from finbot.utils.multithreading_utils.get_max_threads import get_max_threads as compute_max_threads

# Singleton APIKeyManager instance
_api_key_manager = APIKeyManager()


def get_max_threads() -> int:
    """
    Get the maximum number of threads for parallel operations.

    Returns from settings if configured, otherwise computes based on CPU count.
    """
    max_threads = settings.get("threading.max_threads")
    if max_threads is not None:
        return max_threads

    reserved_threads = settings.get("threading.reserved_threads", 1)
    return compute_max_threads(reserved_threads=reserved_threads)


def get_alpha_vantage_api_key() -> str:
    """Get Alpha Vantage API key from environment."""
    return _api_key_manager.get_key("ALPHA_VANTAGE_API_KEY")


def get_nasdaq_data_link_api_key() -> str:
    """Get NASDAQ Data Link API key from environment."""
    return _api_key_manager.get_key("NASDAQ_DATA_LINK_API_KEY")


def get_us_bureau_of_labor_statistics_api_key() -> str:
    """Get US Bureau of Labor Statistics API key from environment."""
    return _api_key_manager.get_key("US_BUREAU_OF_LABOR_STATISTICS_API_KEY")


def get_google_finance_service_account_credentials_path() -> str:
    """Get Google Finance service account credentials path from environment."""
    return _api_key_manager.get_key("GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH")


# Backward compatibility: expose as module-level constants for easy migration
MAX_THREADS = get_max_threads()
