from __future__ import annotations

from finbot.config import settings_accessors
from finbot.config.project_config import settings
from finbot.libs.logger import logger

# Determine the running environment
permitted_envs = ["production", "development"]
if settings.current_env not in permitted_envs:
    raise ValueError(f"Environment variable 'ENV' must be one of {permitted_envs}.")

__all__ = ["logger", "settings", "settings_accessors"]
