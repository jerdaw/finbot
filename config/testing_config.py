"""
Testing Configuration

This module extends the base configuration and applies settings specifically
for the testing environment. These settings should facilitate automated testing
and ensure that tests do not interfere with production or development environments.

It typically includes configurations for a separate test database, different logging levels,
and any other testing-specific parameters.
"""
from __future__ import annotations

from config.base_config import BaseConfig


class TestingConfig(BaseConfig):
    """
    Configuration for the testing environment.
    """

    ENV_NAME: str = "testing".lower()
    DEBUG_MODE: bool = True
    APP_LOGGING_LEVEL: str = "DEBUG"
