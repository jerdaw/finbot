"""
Base Configuration

This module contains the base configuration class for the application. These settings are the
default values for all environments and should be general enough to be applicable in development,
staging, and production environments. Environment-specific settings can override these defaults
by extending this base class.

Sensitive data and environment-specific configurations should not be stored here. Instead, use
environment variables or separate configuration files for different environments.
"""
from __future__ import annotations

import logging

from dotenv import load_dotenv

from config.api_key_manager import APIKeyManager
from config.logging_config import initialize_logger
from finbot.utils.multithreading_utils.get_max_threads import get_max_threads

# Load environment variables from a .env file
load_dotenv()


class BaseConfig:
    """
    Base configuration class for 'finbot' application.
    Contains default settings common to all environments, with methods to
    Retrieves API keys.
    """

    APP_NAME: str = "finbot"
    VERSION: str = "0.0.1"
    ENV_NAME: str = "base".lower()
    DEBUG_MODE: bool = False
    APP_LOGGING_LEVEL: str = "INFO"
    LOG_NAME: str = ENV_NAME
    LOGGING_LEVEL: str = "INFO"

    MAX_THREADS = get_max_threads(reserved_threads=1)

    # Placeholder: Default database URI, should be overridden in environment-specific configs
    # DEFAULT_DATABASE_URI: str = "sqlite:///:memory:"

    # Immutable configurations (API Keys, etc.)
    # pylint: disable=used-before-assignment

    def __init__(self) -> None:
        self.api_keys = APIKeyManager()
        self.logger: None | logging.Logger = None

    def initialize_logger(self) -> logging.Logger:
        return initialize_logger(logger_name=self.LOG_NAME, log_level=self.APP_LOGGING_LEVEL)

    @property
    def alpha_vantage_api_key(self) -> str:
        return self.api_keys.get_key("ALPHA_VANTAGE_API_KEY")

    @property
    def nasdaq_data_link_api_key(self) -> str:
        return self.api_keys.get_key("NASDAQ_DATA_LINK_API_KEY")

    @property
    def us_bureau_of_labor_statistics_api_key(self) -> str:
        return self.api_keys.get_key("US_BUREAU_OF_LABOR_STATISTICS_API_KEY")

    @property
    def google_finance_service_account_credentials_path(self) -> str:
        return self.api_keys.get_key("GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH")
