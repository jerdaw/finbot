"""
Development Configuration

This module extends the base configuration and applies settings specifically
for the development environment. The development environment is where developers
write, debug, and test the application. Configurations in this environment are
optimized for developer convenience and may include more verbose logging, detailed
error reports, and local database connections.

Configurations should not include sensitive data directly and should instead load
them from environment variables or other secure sources.

"""

from __future__ import annotations

import pandas as pd

from config.base_config import BaseConfig


class DevelopmentConfig(BaseConfig):
    """
    Configuration for development environment.
    """

    ENV_NAME: str = "development".lower()
    DEBUG_MODE: bool = True
    APP_LOGGING_LEVEL: str = "DEBUG"

    def set_pandas_options(self):
        pd.set_option("display.expand_frame_repr", False)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_rows", 500)
