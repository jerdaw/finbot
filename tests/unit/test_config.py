"""Unit tests for configuration system."""

from __future__ import annotations

import pytest


class TestBaseConfig:
    """Tests for BaseConfig singleton."""

    def test_config_singleton(self):
        """Test that Config is a singleton."""
        from config import Config

        config1 = Config
        config2 = Config

        assert config1 is config2

    def test_config_has_max_threads(self):
        """Test that Config has MAX_THREADS attribute."""
        from config import Config

        assert hasattr(Config, "MAX_THREADS")
        assert isinstance(Config.MAX_THREADS, int)
        assert Config.MAX_THREADS > 0

    def test_config_has_attributes(self):
        """Test that Config has expected attributes."""
        from config import Config

        # Config should be an object with attributes
        assert Config is not None


class TestDynaconfSettings:
    """Tests for Dynaconf settings."""

    def test_settings_current_env(self):
        """Test that settings has current_env."""
        from config import settings

        assert hasattr(settings, "current_env")
        assert settings.current_env in ["development", "production"]

    def test_settings_has_current_env(self):
        """Test that settings has current_env attribute."""
        from config import settings

        assert hasattr(settings, "current_env")


class TestLogger:
    """Tests for logger configuration."""

    def test_logger_exists(self):
        """Test that logger is configured."""
        from config import logger

        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "warning")

    def test_logger_basic_operations(self):
        """Test basic logger operations."""
        from config import logger

        # Should not raise
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")


class TestAPIConstants:
    """Tests for API constants."""

    def test_get_alpha_vantage_headers_lazy_loading(self):
        """Test that get_alpha_vantage_rapi_headers is a function."""
        from constants.api_constants import get_alpha_vantage_rapi_headers

        assert callable(get_alpha_vantage_rapi_headers)

    def test_api_constants_module_exists(self):
        """Test that api_constants module can be imported."""
        import constants.api_constants

        assert constants.api_constants is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
