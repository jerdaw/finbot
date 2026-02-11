"""Tests for data quality and observability services."""

from pathlib import Path

import pandas as pd
import pytest


class TestDataSourceRegistry:
    """Tests for the data source registry."""

    def test_registry_import(self):
        from finbot.services.data_quality.data_source_registry import DATA_SOURCES

        assert DATA_SOURCES is not None
        assert len(DATA_SOURCES) > 0

    def test_data_source_fields(self):
        from finbot.services.data_quality.data_source_registry import DATA_SOURCES

        for source in DATA_SOURCES:
            assert source.name
            assert isinstance(source.directory, Path)
            assert source.pattern
            assert source.max_age_days > 0
            assert source.description

    def test_known_sources_present(self):
        from finbot.services.data_quality.data_source_registry import DATA_SOURCES

        names = {s.name for s in DATA_SOURCES}
        assert "Yahoo Finance" in names
        assert "FRED" in names
        assert "Simulations" in names


class TestCheckDataFreshness:
    """Tests for the freshness checker."""

    def test_check_all_freshness_returns_list(self):
        from finbot.services.data_quality.check_data_freshness import check_all_freshness

        results = check_all_freshness()
        assert isinstance(results, list)
        assert len(results) > 0

    def test_status_properties(self):
        from finbot.services.data_quality.check_data_freshness import check_all_freshness

        results = check_all_freshness()
        for status in results:
            # age_str should always return a string
            assert isinstance(status.age_str, str)
            # size_str should always return a string
            assert isinstance(status.size_str, str)
            # is_stale should be boolean
            assert isinstance(status.is_stale, bool)
            # file_count should be non-negative
            assert status.file_count >= 0

    def test_check_single_source(self):
        from finbot.services.data_quality.check_data_freshness import check_source_freshness
        from finbot.services.data_quality.data_source_registry import DATA_SOURCES

        status = check_source_freshness(DATA_SOURCES[0])
        assert status.source == DATA_SOURCES[0]
        assert status.file_count >= 0


class TestValidateDataFrame:
    """Tests for DataFrame validation."""

    def test_validate_empty_dataframe(self):
        from finbot.services.data_quality.validate_dataframe import validate_dataframe

        df = pd.DataFrame()
        result = validate_dataframe(df, "test.parquet")
        assert not result.is_valid
        assert any("empty" in e.lower() for e in result.errors)

    def test_validate_valid_dataframe(self):
        from finbot.services.data_quality.validate_dataframe import validate_dataframe

        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        result = validate_dataframe(df, "test.parquet")
        assert result.is_valid
        assert result.row_count == 3
        assert result.col_count == 2

    def test_validate_min_rows(self):
        from finbot.services.data_quality.validate_dataframe import validate_dataframe

        df = pd.DataFrame({"A": [1]})
        result = validate_dataframe(df, "test.parquet", min_rows=10)
        assert not result.is_valid
        assert any("10 rows" in e for e in result.errors)

    def test_validate_expected_columns(self):
        from finbot.services.data_quality.validate_dataframe import validate_dataframe

        df = pd.DataFrame({"A": [1], "B": [2]})
        result = validate_dataframe(df, "test.parquet", expected_columns=["A", "C"])
        assert not result.is_valid
        assert any("Missing columns" in e for e in result.errors)

    def test_validate_duplicate_index(self):
        from finbot.services.data_quality.validate_dataframe import validate_dataframe

        df = pd.DataFrame({"A": [1, 2, 3]}, index=[0, 0, 1])
        result = validate_dataframe(df, "test.parquet", check_duplicates=True)
        assert result.is_valid  # duplicates are warnings, not errors
        assert any("duplicate" in w.lower() for w in result.warnings)

    def test_validate_nulls(self):
        from finbot.services.data_quality.validate_dataframe import validate_dataframe

        df = pd.DataFrame({"A": [1, None, 3]})
        result = validate_dataframe(df, "test.parquet", check_nulls=True)
        assert result.is_valid  # nulls are warnings, not errors
        assert any("Null" in w for w in result.warnings)


class TestStatusCLI:
    """Tests for the status CLI command."""

    def test_status_command_import(self):
        from finbot.cli.commands.status import status

        assert status is not None
        assert callable(status)

    def test_status_registered_in_cli(self):
        from finbot.cli.main import cli

        command_names = list(cli.commands)
        assert "status" in command_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
