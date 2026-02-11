"""
Due to python's import system, this file can't be named `config.py`
because it would conflict with the `config` package.
"""

import pandas as pd
from dynaconf import Dynaconf, Validator

from finbot.constants.host_constants import CURRENT_HOST_INFO
from finbot.constants.path_constants import CONFIG_DIR
from finbot.utils.multithreading_utils.get_max_threads import get_max_threads


def validate_settings(settings: Dynaconf):
    settings.validators.register(
        Validator("APP_NAME", must_exist=True, eq="finbot"),
        Validator("NAME", must_exist=True, eq="development", env="development"),
        Validator("NAME", must_exist=True, eq="production", env="production"),
        Validator("VERSION", must_exist=True),
        Validator("DEBUG_MODE", must_exist=True),
    )
    settings.validators.validate()


def configure_settings(settings: Dynaconf):
    # Host configuration
    settings.set("host.host_identifier", CURRENT_HOST_INFO.host_identifier)
    settings.set("host.max_threads", get_max_threads(reserved_threads=1))

    # Logger configuration
    if settings.get("debug_mode"):
        settings.set("logging.level", "DEBUG")

    # Library configuration
    if settings.get("libraries.pandas_settings") == "expanded":
        pd.set_option("display.expand_frame_repr", False)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_rows", 50)


def load_settings():
    """
    Load settings from the configuration files and environment variables.

    Note: configure_settings and validate_settings are tightly coupled with this function
    to ensure the settings cannot be used without being properly configured and validated.
    """
    settings = Dynaconf(
        envvar_prefix="DYNACONF",
        settings_files=[
            CONFIG_DIR / "settings.yaml",
            CONFIG_DIR / ".secrets.yaml",
            CONFIG_DIR / "production.yaml",
            CONFIG_DIR / "development.yaml",
        ],
        dotenv_path=CONFIG_DIR / ".env",
        environments=True,
        env_switcher="DYNACONF_ENV",
        # Generally don't want to load .env files in production
        load_dotenv={"when": {"env": {"is_in": ["development"]}}},
    )
    configure_settings(settings=settings)
    validate_settings(settings=settings)
    return settings


settings = load_settings()

if __name__ == "__main__":
    print(f"Current environment: {settings.current_env}")
    print(f"App name: {settings.app_name}")
    print(f"Version: {settings.version}")
    print(f"Current host: {settings.host.host_identifier}")
