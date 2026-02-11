"""Tests for path_constants.

Verifies directory auto-creation, path correctness, and structural relationships
between the declared path constants.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from finbot.constants import path_constants


class TestRootDirectory:
    """Tests for ROOT_DIR and top-level paths."""

    def test_root_dir_exists(self):
        assert path_constants.ROOT_DIR.exists()
        assert path_constants.ROOT_DIR.is_dir()

    def test_root_dir_is_absolute(self):
        assert path_constants.ROOT_DIR.is_absolute()

    def test_root_dir_contains_pyproject(self):
        """ROOT_DIR should be the project root (contains pyproject.toml)."""
        assert (path_constants.ROOT_DIR / "pyproject.toml").exists()

    def test_finbot_dir_under_root(self):
        assert path_constants.FINBOT_DIR == path_constants.ROOT_DIR / "finbot"
        assert path_constants.FINBOT_DIR.exists()


class TestDirectoryAutoCreation:
    """Tests that _process_dir creates missing directories."""

    def test_process_dir_creates_directory(self, tmp_path):
        new_dir = tmp_path / "test_subdir" / "nested"
        result = path_constants._process_dir(new_dir)
        assert result.exists()
        assert result.is_dir()

    def test_process_dir_returns_resolved_path(self, tmp_path):
        new_dir = tmp_path / "test_dir"
        result = path_constants._process_dir(new_dir)
        assert result == new_dir.resolve()

    def test_process_dir_idempotent(self, tmp_path):
        new_dir = tmp_path / "idempotent_dir"
        result1 = path_constants._process_dir(new_dir)
        result2 = path_constants._process_dir(new_dir)
        assert result1 == result2


class TestSubdirectories:
    """Tests for subdirectory path constants."""

    @pytest.mark.parametrize(
        "dir_name",
        [
            "ASSETS_DIR",
            "BACKUPS_DIR",
            "DOCS_DIR",
            "LOGS_DIR",
            "NOTEBOOKS_DIR",
            "SCRIPTS_DIR",
            "TESTS_DIR",
        ],
    )
    def test_root_subdirs_exist(self, dir_name):
        dir_path = getattr(path_constants, dir_name)
        assert isinstance(dir_path, Path)
        assert dir_path.exists()
        assert dir_path.is_dir()

    @pytest.mark.parametrize(
        "dir_name",
        [
            "CONFIG_DIR",
            "CONSTANTS_DIR",
            "DATA_DIR",
            "SERVICES_DIR",
            "UTILS_DIR",
        ],
    )
    def test_finbot_subdirs_exist(self, dir_name):
        dir_path = getattr(path_constants, dir_name)
        assert isinstance(dir_path, Path)
        assert dir_path.exists()
        assert dir_path.is_dir()

    @pytest.mark.parametrize(
        "dir_name",
        [
            "ALPHA_VANTAGE_DATA_DIR",
            "BLS_DATA_DIR",
            "CUSTOM_DATA_DIR",
            "FRED_DATA_DIR",
            "GOOGLE_FINANCE_DATA_DIR",
            "MSCI_DATA_DIR",
            "MULTPL_DATA_DIR",
            "RESPONSES_DATA_DIR",
            "SHILLER_DATA_DIR",
            "YFINANCE_DATA_DIR",
            "SIMULATIONS_DATA_DIR",
            "BACKTESTS_DATA_DIR",
            "PRICE_HISTORIES_DATA_DIR",
            "LONGTERMTRENDS_DATA_DIR",
        ],
    )
    def test_data_subdirs_exist(self, dir_name):
        dir_path = getattr(path_constants, dir_name)
        assert isinstance(dir_path, Path)
        assert dir_path.exists()
        assert dir_path.is_dir()

    @pytest.mark.parametrize(
        "dir_name",
        [
            "FRED_RESPONSES_DATA_DIR",
            "ALPHA_VANTAGE_RESPONSES_DATA_DIR",
            "BLS_RESPONSES_DATA_DIR",
        ],
    )
    def test_response_subdirs_exist(self, dir_name):
        dir_path = getattr(path_constants, dir_name)
        assert isinstance(dir_path, Path)
        assert dir_path.exists()


class TestPathRelationships:
    """Tests for structural relationships between paths."""

    def test_data_dir_under_finbot(self):
        assert path_constants.DATA_DIR.parent == path_constants.FINBOT_DIR

    def test_simulations_under_data(self):
        assert path_constants.SIMULATIONS_DATA_DIR.parent == path_constants.DATA_DIR

    def test_backtests_under_data(self):
        assert path_constants.BACKTESTS_DATA_DIR.parent == path_constants.DATA_DIR

    def test_responses_under_data(self):
        assert path_constants.RESPONSES_DATA_DIR.parent == path_constants.DATA_DIR

    def test_fred_responses_under_responses(self):
        assert path_constants.FRED_RESPONSES_DATA_DIR.parent == path_constants.RESPONSES_DATA_DIR

    def test_config_under_finbot(self):
        assert path_constants.CONFIG_DIR.parent == path_constants.FINBOT_DIR

    def test_constants_under_finbot(self):
        assert path_constants.CONSTANTS_DIR.parent == path_constants.FINBOT_DIR

    def test_tracked_collections_under_constants(self):
        assert path_constants.TRACKED_COLLECTIONS_DIR.parent == path_constants.CONSTANTS_DIR

    def test_unit_tests_under_tests(self):
        assert path_constants.UNIT_TESTS_DIR.parent == path_constants.TESTS_DIR
