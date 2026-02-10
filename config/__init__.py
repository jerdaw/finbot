from __future__ import annotations

from config.base_config import BaseConfig
from config.project_config import settings
from libs.logger import logger

# Determine the running environment
permitted_envs = ["production", "development"]
if settings.current_env not in permitted_envs:
    raise ValueError(f"Environment variable 'ENV' must be one of {permitted_envs}.")

# Singleton Config instance for backward compatibility (Config.MAX_THREADS, Config.alpha_vantage_api_key, etc.)
Config = BaseConfig()

__all__ = ["Config", "settings", "logger"]
