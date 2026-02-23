"""Tests for structured audit logging utilities."""

from __future__ import annotations

import logging
import os

import pytest

# Ensure Dynaconf environment resolves during logger/config imports.
os.environ.setdefault("DYNACONF_ENV", "development")

import finbot.config  # noqa: F401
from finbot.libs.logger.audit import (
    AuditOutcome,
    audit_operation,
    emit_audit_event,
    generate_trace_id,
    get_trace_id,
    hash_parameters,
    set_trace_id,
)


def test_generate_trace_id_has_expected_shape() -> None:
    trace_id = generate_trace_id()
    assert isinstance(trace_id, str)
    assert len(trace_id) == 32


def test_get_trace_id_generates_when_missing() -> None:
    set_trace_id(None)
    trace_id = get_trace_id()
    assert len(trace_id) == 32


def test_parameter_hash_redacts_sensitive_values() -> None:
    hash1 = hash_parameters({"api_key": "secret-a", "operation": "simulate"})
    hash2 = hash_parameters({"api_key": "secret-b", "operation": "simulate"})
    assert hash1 == hash2


def test_emit_audit_event_logs_structured_fields(caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("test.audit.emit")
    set_trace_id("trace-emit-1")

    with caplog.at_level(logging.INFO):
        event = emit_audit_event(
            logger,
            operation="status",
            component="cli.status",
            outcome=AuditOutcome.SUCCESS,
            duration_ms=15,
            parameters={"stale_only": True},
        )

    assert event.trace_id == "trace-emit-1"
    assert event.operation == "status"
    assert event.component == "cli.status"
    assert event.duration_ms == 15

    audit_records = [r for r in caplog.records if r.message == "audit_event"]
    assert len(audit_records) >= 1
    record = audit_records[-1]
    assert record.trace_id == "trace-emit-1"
    assert record.operation == "status"
    assert record.component == "cli.status"
    assert record.outcome == "success"


def test_audit_operation_success_logs_success(caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("test.audit.context.success")
    set_trace_id("trace-success-1")

    with (
        caplog.at_level(logging.INFO),
        audit_operation(
            logger,
            operation="simulate",
            component="cli.simulate",
            parameters={"fund": "SPY"},
        ),
    ):
        pass

    audit_records = [r for r in caplog.records if r.message == "audit_event"]
    assert audit_records
    assert audit_records[-1].outcome == "success"


def test_audit_operation_failure_logs_failure(caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("test.audit.context.failure")
    set_trace_id("trace-failure-1")

    with (
        caplog.at_level(logging.INFO),
        pytest.raises(ValueError),
        audit_operation(
            logger,
            operation="optimize",
            component="cli.optimize",
            parameters={"asset": "SPY"},
        ),
    ):
        raise ValueError("forced failure")

    audit_records = [r for r in caplog.records if r.message == "audit_event"]
    assert audit_records
    assert audit_records[-1].outcome == "failure"
    assert audit_records[-1].error_type == "ValueError"
