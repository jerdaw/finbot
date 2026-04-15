"""Unit tests for configuration system."""

from __future__ import annotations

import importlib

import pytest


class TestSettingsAccessors:
    """Tests for settings_accessors module."""

    def test_settings_accessors_exists(self):
        """Test that settings_accessors can be imported."""
        from finbot.config import settings_accessors

        assert settings_accessors is not None

    def test_settings_accessors_has_max_threads(self):
        """Test that settings_accessors has MAX_THREADS."""
        from finbot.config import settings_accessors

        assert hasattr(settings_accessors, "MAX_THREADS")
        assert isinstance(settings_accessors.MAX_THREADS, int)
        assert settings_accessors.MAX_THREADS > 0

    def test_get_max_threads_function(self):
        """Test that get_max_threads function works."""
        from finbot.config import settings_accessors

        max_threads = settings_accessors.get_max_threads()
        assert isinstance(max_threads, int)
        assert max_threads > 0


class TestDynaconfSettings:
    """Tests for Dynaconf settings."""

    def test_settings_current_env(self):
        """Test that settings has current_env."""
        from finbot.config import settings

        assert hasattr(settings, "current_env")
        assert settings.current_env in ["development", "production"]

    def test_settings_has_current_env(self):
        """Test that settings has current_env attribute."""
        from finbot.config import settings

        assert hasattr(settings, "current_env")


class TestLogger:
    """Tests for logger configuration."""

    def test_logger_exists(self):
        """Test that logger is configured."""
        from finbot.config import logger

        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "warning")

    def test_logger_basic_operations(self):
        """Test basic logger operations."""
        from finbot.config import logger

        # Should not raise
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")


class TestHostConfig:
    """Tests for lazy host info loading and config integration."""

    def test_get_current_host_info_is_cached(self):
        """Repeated accessor calls should return the same cached snapshot."""
        import finbot.constants.host_constants as host_constants

        host_constants.get_current_host_info.cache_clear()
        host_info = host_constants.get_current_host_info()
        cached_host_info = host_constants.get_current_host_info()

        assert host_info is cached_host_info

    def test_get_current_host_info_falls_back_when_probes_fail(self, monkeypatch: pytest.MonkeyPatch):
        """Host info access should not raise when all probe helpers fail."""
        import socket

        import finbot.constants.host_constants as host_constants

        host_constants.get_current_host_info.cache_clear()
        monkeypatch.setattr(socket, "gethostname", lambda: "")
        monkeypatch.setattr(socket, "gethostbyname", lambda hostname: (_ for _ in ()).throw(OSError("dns failed")))
        monkeypatch.setattr(host_constants.HostSystem, "get_cpu_name", staticmethod(lambda: "Unavailable"))
        monkeypatch.setattr(host_constants, "_safe_cpu_count", lambda *, logical: 0)
        monkeypatch.setattr(host_constants, "_safe_cpu_speed", lambda: 0.0)
        monkeypatch.setattr(host_constants, "_safe_memory_gb", lambda: 0.0)
        monkeypatch.setattr(host_constants, "_safe_disk_usage_gb", lambda field_name: 0.0)
        monkeypatch.setattr(host_constants.HostSystem, "get_active_network_interface", staticmethod(lambda: "None"))

        host_info = host_constants.get_current_host_info()

        assert host_info.hostname == "Unavailable"
        assert host_info.ip_address == "Unavailable"
        assert host_info.cpu_name == "Unavailable"
        assert host_info.cpu_cores == 0
        assert host_info.cpu_threads == 0
        assert host_info.cpu_speed == 0.0
        assert host_info.total_memory == 0.0
        assert host_info.disk_storage == 0.0
        assert host_info.available_storage == 0.0
        assert host_info.used_storage == 0.0
        assert host_info.network_interface == "None"

    def test_load_settings_succeeds_when_host_accessor_is_patched(self, monkeypatch: pytest.MonkeyPatch):
        """Settings load should succeed with a lazy host accessor in place."""
        import finbot.config.project_config as project_config
        import finbot.constants.host_constants as host_constants

        monkeypatch.setattr(
            host_constants,
            "get_current_host_info",
            lambda: host_constants.HostSystem(host_identifier="test-host-id"),
        )
        reloaded_project_config = importlib.reload(project_config)

        settings = reloaded_project_config.load_settings()

        assert settings.host.host_identifier == "test-host-id"


class TestAPIConstants:
    """Tests for API constants."""

    def test_get_alpha_vantage_headers_lazy_loading(self):
        """Test that get_alpha_vantage_rapi_headers is a function."""
        from finbot.constants.api_constants import get_alpha_vantage_rapi_headers

        assert callable(get_alpha_vantage_rapi_headers)

    def test_api_constants_module_exists(self):
        """Test that api_constants module can be imported."""
        import finbot.constants.api_constants

        assert finbot.constants.api_constants is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
