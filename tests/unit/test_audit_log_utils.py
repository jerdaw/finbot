"""Tests for audit log query utilities."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from finbot.utils.audit_log_utils import AuditLogQuery, AuditLogReader, AuditLogSummary


@pytest.fixture
def temp_log_file(tmp_path: Path) -> Path:
    """Create temporary log file with sample audit logs."""
    log_file = tmp_path / "finbot.log.jsonl"

    # Create sample audit log entries
    entries = [
        {
            "timestamp": "2024-02-17T10:00:00+00:00",
            "level": "INFO",
            "message": "Completed backtest",
            "audit_log": True,
            "operation": "run_backtest",
            "operation_type": "backtest",
            "audit_timestamp": "2024-02-17T10:00:00+00:00",
            "status": "success",
            "parameters": {"symbols": ["SPY"], "strategy": "Rebalance"},
            "result": {"total_return_pct": 15.4},
            "duration_ms": 1234.5,
            "user": "system",
            "context": {},
            "errors": [],
        },
        {
            "timestamp": "2024-02-17T11:00:00+00:00",
            "level": "ERROR",
            "message": "Failed simulation",
            "audit_log": True,
            "operation": "fund_simulator",
            "operation_type": "simulation",
            "audit_timestamp": "2024-02-17T11:00:00+00:00",
            "status": "failure",
            "parameters": {"fund": "UPRO"},
            "result": {},
            "duration_ms": 567.8,
            "user": "system",
            "context": {},
            "errors": ["Data not available"],
        },
        {
            "timestamp": "2024-02-17T12:00:00+00:00",
            "level": "INFO",
            "message": "Completed data fetch",
            "audit_log": True,
            "operation": "fetch_prices",
            "operation_type": "data_collection",
            "audit_timestamp": "2024-02-17T12:00:00+00:00",
            "status": "success",
            "parameters": {"symbol": "SPY"},
            "result": {"rows": 5000},
            "duration_ms": 2345.6,
            "user": "system",
            "context": {},
            "errors": [],
        },
        # Non-audit log entry (should be filtered out)
        {
            "timestamp": "2024-02-17T13:00:00+00:00",
            "level": "INFO",
            "message": "Regular log entry",
        },
    ]

    # Write to file
    with open(log_file, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    return log_file


class TestAuditLogQuery:
    """Tests for AuditLogQuery class."""

    def test_default_query(self):
        """Test creating query with defaults."""
        query = AuditLogQuery()

        assert query.operation_type is None
        assert query.operation is None
        assert query.status is None
        assert query.has_errors is False

    def test_query_with_filters(self):
        """Test creating query with filters."""
        query = AuditLogQuery(
            operation_type="backtest",
            status="failure",
            start_time="2024-01-01",
        )

        assert query.operation_type == "backtest"
        assert query.status == "failure"
        assert query.start_time == "2024-01-01"


class TestAuditLogReader:
    """Tests for AuditLogReader class."""

    def test_reader_initialization(self, temp_log_file: Path):
        """Test creating reader."""
        reader = AuditLogReader(log_dir=temp_log_file.parent)
        assert reader.log_file == temp_log_file

    def test_reader_file_not_found(self, tmp_path: Path):
        """Test error when log file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            AuditLogReader(log_dir=tmp_path)

    def test_read_all(self, temp_log_file: Path):
        """Test reading all audit log entries."""
        reader = AuditLogReader(log_dir=temp_log_file.parent)
        entries = reader.read_all()

        # Should read 3 audit log entries (4th is not audit log)
        assert len(entries) == 3
        assert all(entry.get("audit_log") for entry in entries)

    def test_query_by_operation_type(self, temp_log_file: Path):
        """Test querying by operation type."""
        reader = AuditLogReader(log_dir=temp_log_file.parent)

        backtests = reader.query(operation_type="backtest")
        assert len(backtests) == 1
        assert backtests[0]["operation"] == "run_backtest"

        simulations = reader.query(operation_type="simulation")
        assert len(simulations) == 1
        assert simulations[0]["operation"] == "fund_simulator"

    def test_query_by_status(self, temp_log_file: Path):
        """Test querying by status."""
        reader = AuditLogReader(log_dir=temp_log_file.parent)

        successful = reader.query(status="success")
        assert len(successful) == 2

        failed = reader.query(status="failure")
        assert len(failed) == 1
        assert failed[0]["operation"] == "fund_simulator"

    def test_query_by_operation_name(self, temp_log_file: Path):
        """Test querying by operation name."""
        reader = AuditLogReader(log_dir=temp_log_file.parent)

        results = reader.query(operation="run_backtest")
        assert len(results) == 1
        assert results[0]["operation_type"] == "backtest"

    def test_query_by_time_range(self, temp_log_file: Path):
        """Test querying by time range."""
        reader = AuditLogReader(log_dir=temp_log_file.parent)

        # Query for entries after 10:30
        results = reader.query(start_time="2024-02-17T10:30:00+00:00")
        assert len(results) == 2

        # Query for entries before 11:30
        results = reader.query(end_time="2024-02-17T11:30:00+00:00")
        assert len(results) == 2

        # Query for specific time window
        results = reader.query(
            start_time="2024-02-17T10:30:00+00:00",
            end_time="2024-02-17T11:30:00+00:00",
        )
        assert len(results) == 1
        assert results[0]["operation"] == "fund_simulator"

    def test_query_by_duration(self, temp_log_file: Path):
        """Test querying by duration."""
        reader = AuditLogReader(log_dir=temp_log_file.parent)

        # Operations faster than 1000ms
        fast = reader.query(max_duration_ms=1000)
        assert len(fast) == 1
        assert fast[0]["operation"] == "fund_simulator"

        # Operations slower than 1000ms
        slow = reader.query(min_duration_ms=1000)
        assert len(slow) == 2

    def test_query_with_errors(self, temp_log_file: Path):
        """Test querying for entries with errors."""
        reader = AuditLogReader(log_dir=temp_log_file.parent)

        with_errors = reader.query(has_errors=True)
        assert len(with_errors) == 1
        assert with_errors[0]["status"] == "failure"
        assert len(with_errors[0]["errors"]) > 0

    def test_query_combined_filters(self, temp_log_file: Path):
        """Test querying with multiple filters."""
        reader = AuditLogReader(log_dir=temp_log_file.parent)

        # Successful backtests only
        results = reader.query(
            operation_type="backtest",
            status="success",
        )
        assert len(results) == 1

        # Failed operations with errors
        results = reader.query(
            status="failure",
            has_errors=True,
        )
        assert len(results) == 1

    def test_generate_summary_all(self, temp_log_file: Path):
        """Test generating summary for all entries."""
        reader = AuditLogReader(log_dir=temp_log_file.parent)
        summary = reader.generate_summary()

        assert summary.total_operations == 3
        assert summary.successful_operations == 2
        assert summary.failed_operations == 1
        assert summary.partial_operations == 0
        assert summary.avg_duration_ms > 0
        assert "backtest" in summary.operations_by_type
        assert "simulation" in summary.operations_by_type
        assert "success" in summary.operations_by_status
        assert "failure" in summary.operations_by_status

    def test_generate_summary_filtered(self, temp_log_file: Path):
        """Test generating summary with filters."""
        reader = AuditLogReader(log_dir=temp_log_file.parent)

        # Summary for backtests only
        summary = reader.generate_summary(operation_type="backtest")
        assert summary.total_operations == 1
        assert summary.successful_operations == 1
        assert summary.failed_operations == 0

        # Summary for failed operations
        summary = reader.generate_summary(status="failure")
        assert summary.total_operations == 1
        assert summary.failed_operations == 1
        assert len(summary.error_messages) > 0

    def test_to_dataframe(self, temp_log_file: Path):
        """Test converting to DataFrame."""
        reader = AuditLogReader(log_dir=temp_log_file.parent)
        df = reader.to_dataframe()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert "timestamp" in df.columns
        assert "operation" in df.columns
        assert "operation_type" in df.columns
        assert "status" in df.columns
        assert "duration_ms" in df.columns
        assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])

    def test_to_dataframe_filtered(self, temp_log_file: Path):
        """Test converting filtered results to DataFrame."""
        reader = AuditLogReader(log_dir=temp_log_file.parent)
        df = reader.to_dataframe(operation_type="backtest")

        assert len(df) == 1
        assert df.iloc[0]["operation"] == "run_backtest"

    def test_export_to_csv(self, temp_log_file: Path, tmp_path: Path):
        """Test exporting to CSV."""
        reader = AuditLogReader(log_dir=temp_log_file.parent)
        output_file = tmp_path / "audit_logs.csv"

        reader.export_to_csv(output_file)

        assert output_file.exists()

        # Read back and verify
        df = pd.read_csv(output_file)
        assert len(df) == 3
        assert "operation" in df.columns

    def test_export_to_parquet(self, temp_log_file: Path, tmp_path: Path):
        """Test exporting to parquet."""
        reader = AuditLogReader(log_dir=temp_log_file.parent)
        output_file = tmp_path / "audit_logs.parquet"

        reader.export_to_parquet(output_file)

        assert output_file.exists()

        # Read back and verify
        df = pd.read_parquet(output_file)
        assert len(df) == 3
        assert "operation" in df.columns


class TestAuditLogSummary:
    """Tests for AuditLogSummary class."""

    def test_summary_defaults(self):
        """Test creating summary with defaults."""
        summary = AuditLogSummary()

        assert summary.total_operations == 0
        assert summary.successful_operations == 0
        assert summary.failed_operations == 0
        assert summary.partial_operations == 0
        assert summary.avg_duration_ms == 0.0
        assert summary.operations_by_type == {}
        assert summary.operations_by_status == {}
        assert summary.error_messages == []
