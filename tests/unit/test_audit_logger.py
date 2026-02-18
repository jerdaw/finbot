"""Tests for audit logging functionality."""

from __future__ import annotations

import logging
import time

import pytest

from finbot.libs.audit.audit_logger import AuditLogger, _extract_safe_parameters, _safe_result_to_dict, audit_operation
from finbot.libs.audit.audit_schema import AuditLogEntry, OperationStatus, OperationType


class TestAuditLogEntry:
    """Tests for AuditLogEntry schema."""

    def test_default_creation(self):
        """Test creating an audit log entry with defaults."""
        entry = AuditLogEntry(
            operation="test_operation",
            operation_type=OperationType.BACKTEST,
        )

        assert entry.operation == "test_operation"
        assert entry.operation_type == OperationType.BACKTEST
        assert entry.status == OperationStatus.IN_PROGRESS
        assert entry.user == "system"
        assert entry.parameters == {}
        assert entry.result == {}
        assert entry.errors == []
        assert entry.duration_ms == 0.0

    def test_to_dict(self):
        """Test converting entry to dictionary."""
        entry = AuditLogEntry(
            operation="test_op",
            operation_type=OperationType.SIMULATION,
            parameters={"param1": "value1"},
            result={"metric1": 123},
        )

        result = entry.to_dict()

        assert result["audit_log"] is True
        assert result["operation"] == "test_op"
        assert result["operation_type"] == "simulation"
        assert result["status"] == "in_progress"
        assert result["parameters"] == {"param1": "value1"}
        assert result["result"] == {"metric1": 123}

    def test_sanitize_dict_removes_sensitive_keys(self):
        """Test that sensitive information is redacted."""
        data = {
            "api_key": "secret123",
            "password": "pass123",
            "token": "token123",
            "normal_key": "value",
        }

        sanitized = AuditLogEntry._sanitize_dict(data)

        assert sanitized["api_key"] == "***REDACTED***"
        assert sanitized["password"] == "***REDACTED***"
        assert sanitized["token"] == "***REDACTED***"
        assert sanitized["normal_key"] == "value"

    def test_sanitize_dict_nested(self):
        """Test sanitization of nested dictionaries."""
        data = {
            "outer": {
                "api_key": "secret",
                "safe_key": "value",
            },
            "normal": "data",
        }

        sanitized = AuditLogEntry._sanitize_dict(data)

        assert sanitized["outer"]["api_key"] == "***REDACTED***"
        assert sanitized["outer"]["safe_key"] == "value"
        assert sanitized["normal"] == "data"

    def test_update_status(self):
        """Test updating operation status."""
        entry = AuditLogEntry(
            operation="test",
            operation_type=OperationType.BACKTEST,
        )

        entry.update_status(OperationStatus.SUCCESS)
        assert entry.status == OperationStatus.SUCCESS

        entry.update_status(OperationStatus.FAILURE, errors=["Error 1", "Error 2"])
        assert entry.status == OperationStatus.FAILURE
        assert len(entry.errors) == 2

    def test_update_result(self):
        """Test updating operation result."""
        entry = AuditLogEntry(
            operation="test",
            operation_type=OperationType.BACKTEST,
        )

        entry.update_result({"metric1": 10})
        assert entry.result["metric1"] == 10

        entry.update_result({"metric2": 20})
        assert entry.result["metric1"] == 10
        assert entry.result["metric2"] == 20

    def test_set_duration(self):
        """Test setting operation duration."""
        entry = AuditLogEntry(
            operation="test",
            operation_type=OperationType.BACKTEST,
        )

        entry.set_duration(1234.56)
        assert entry.duration_ms == 1234.56


class TestAuditLogger:
    """Tests for AuditLogger class."""

    @pytest.fixture
    def logger(self):
        """Create a test logger."""
        logger = logging.getLogger("test_audit")
        logger.setLevel(logging.INFO)
        # Clear any existing handlers
        logger.handlers.clear()
        return logger

    @pytest.fixture
    def audit(self, logger):
        """Create AuditLogger instance."""
        return AuditLogger(logger)

    def test_log_operation_success(self, audit, logger, caplog):
        """Test successful operation logging."""
        with (
            caplog.at_level(logging.INFO),
            audit.log_operation(
                operation="test_operation",
                operation_type=OperationType.BACKTEST,
                parameters={"param1": "value1"},
            ) as entry,
        ):
            # Simulate work
            time.sleep(0.01)

        # Check that both start and completion were logged
        assert len(caplog.records) == 2
        assert "Starting backtest operation: test_operation" in caplog.records[0].message
        assert "Completed backtest operation: test_operation" in caplog.records[1].message

        # Check entry was marked successful
        assert entry.status == OperationStatus.SUCCESS
        assert entry.duration_ms > 0

    def test_log_operation_failure(self, audit, logger, caplog):
        """Test failed operation logging."""
        with (
            caplog.at_level(logging.INFO),
            pytest.raises(ValueError),
            audit.log_operation(
                operation="test_operation",
                operation_type=OperationType.SIMULATION,
            ) as _,
        ):
            raise ValueError("Test error")

        # Check that failure was logged
        assert len(caplog.records) == 2
        assert caplog.records[1].levelname == "ERROR"
        assert "Failed simulation operation" in caplog.records[1].message

    def test_log_operation_updates_result(self, audit, logger):
        """Test updating result during operation."""
        with audit.log_operation(
            operation="test_op",
            operation_type=OperationType.OPTIMIZATION,
        ) as entry:
            entry.update_result({"step1": "complete"})
            entry.update_result({"step2": "complete"})

        assert entry.result["step1"] == "complete"
        assert entry.result["step2"] == "complete"

    def test_log_event(self, audit, logger, caplog):
        """Test single event logging."""
        with caplog.at_level(logging.INFO):
            audit.log_event(
                operation="cache_hit",
                operation_type=OperationType.DATA_COLLECTION,
                status=OperationStatus.SUCCESS,
                parameters={"key": "test_key"},
                result={"cached": True},
            )

        assert len(caplog.records) == 1
        assert "data_collection operation: cache_hit - success" in caplog.records[0].message


class TestAuditOperationDecorator:
    """Tests for @audit_operation decorator."""

    def test_decorator_basic(self, caplog):
        """Test decorator on simple function."""

        @audit_operation(operation_type=OperationType.SIMULATION)
        def test_function(x: int, y: int):
            return x + y

        with caplog.at_level(logging.INFO, logger="finbot"):
            result = test_function(5, 3)

        assert result == 8
        assert len(caplog.records) == 2  # Start + completion
        assert "Starting simulation operation: test_function" in caplog.records[0].message

    def test_decorator_with_custom_name(self, caplog):
        """Test decorator with custom operation name."""

        @audit_operation(
            operation_type=OperationType.BACKTEST,
            operation_name="custom_backtest",
        )
        def my_function():
            return {"result": 42}

        with caplog.at_level(logging.INFO, logger="finbot"):
            result = my_function()

        assert result["result"] == 42
        assert "custom_backtest" in caplog.records[0].message

    def test_decorator_handles_exceptions(self, caplog):
        """Test decorator handles exceptions properly."""

        @audit_operation(operation_type=OperationType.SIMULATION)
        def failing_function():
            raise RuntimeError("Test failure")

        with caplog.at_level(logging.INFO, logger="finbot"), pytest.raises(RuntimeError):
            failing_function()

        # Should have start + error logs
        assert len(caplog.records) == 2
        assert caplog.records[1].levelname == "ERROR"
        assert "Failed simulation operation" in caplog.records[1].message

    def test_decorator_includes_return_value(self, caplog):
        """Test decorator includes return value in result."""

        @audit_operation(operation_type=OperationType.OPTIMIZATION, include_return=True)
        def return_dict():
            return {"metric": 123}

        with caplog.at_level(logging.INFO, logger="finbot"):
            result = return_dict()

        assert result["metric"] == 123
        # Check that result was logged (in extra field)
        # Note: Can't easily verify extra fields in caplog, but function runs

    def test_decorator_without_return_value(self, caplog):
        """Test decorator without return value logging."""

        @audit_operation(operation_type=OperationType.CLI, include_return=False)
        def no_return_logged():
            return "some_result"

        with caplog.at_level(logging.INFO, logger="finbot"):
            result = no_return_logged()

        assert result == "some_result"


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_extract_safe_parameters_simple(self):
        from finbot.libs.audit.audit_logger import _extract_safe_parameters, _safe_result_to_dict  # noqa: F401

        """Test extracting safe parameters from kwargs."""
        kwargs = {
            "name": "test",
            "count": 42,
            "ratio": 0.5,
            "enabled": True,
        }

        params = _extract_safe_parameters((), kwargs)

        assert params == kwargs

    def test_extract_safe_parameters_complex_objects(self):
        """Test that complex objects are replaced with type names."""
        import pandas as pd

        kwargs = {
            "name": "test",
            "data": pd.DataFrame(),
        }

        params = _extract_safe_parameters((), kwargs)

        assert params["name"] == "test"
        assert params["data"] == "<DataFrame>"

    def test_extract_safe_parameters_with_args(self):
        """Test extracting parameters with positional args."""
        args = (1, 2, 3)
        kwargs = {"key": "value"}

        params = _extract_safe_parameters(args, kwargs)

        assert params["key"] == "value"
        assert params["_positional_args_count"] == 3

    def test_safe_result_to_dict_simple_types(self):
        """Test converting simple types to dict."""
        assert _safe_result_to_dict(None) == {"return_value": None}
        assert _safe_result_to_dict(42) == {"return_value": 42}
        assert _safe_result_to_dict("test") == {"return_value": "test"}
        assert _safe_result_to_dict(True) == {"return_value": True}

    def test_safe_result_to_dict_collections(self):
        """Test converting collections to dict."""
        result = _safe_result_to_dict([1, 2, 3])
        assert result["return_value"] == [1, 2, 3]
        assert result["count"] == 3

    def test_safe_result_to_dict_objects(self):
        """Test converting objects to dict."""

        class TestObject:
            def __str__(self):
                return "TestObject instance"

        obj = TestObject()
        result = _safe_result_to_dict(obj)

        assert result["return_type"] == "TestObject"
        assert "TestObject instance" in result["summary"]
