"""
Production Configuration

This module extends the base configuration and applies settings specifically
for the production environment. The production environment is where the
application runs for end users, and thus, these settings prioritize security,
performance, and stability.

Configurations typically include database connections, logging levels, API keys,
and other critical settings that differ from the development and staging environments.
Sensitive information should be loaded from environment variables or secure secret
management tools.

"""
from __future__ import annotations

from config.base_config import BaseConfig


class ProductionConfig(BaseConfig):
    """
    Configuration for production environment.
    """

    ENV_NAME: str = "production".lower()
    DEBUG_MODE: bool = False
    APP_LOGGING_LEVEL: str = "ERROR"
