from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256
from logging import Logger
from time import perf_counter
from typing import Any
from uuid import uuid4

_trace_id_ctx: ContextVar[str | None] = ContextVar("trace_id", default=None)

_SENSITIVE_KEY_FRAGMENTS = {
    "password",
    "token",
    "secret",
    "api_key",
    "apikey",
    "credential",
    "auth",
    "private_key",
}


class AuditOutcome(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"


@dataclass(frozen=True)
class AuditEvent:
    operation: str
    component: str
    outcome: AuditOutcome
    duration_ms: int
    trace_id: str
    parameters_hash: str
    error_type: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def generate_trace_id() -> str:
    return uuid4().hex


def set_trace_id(trace_id: str | None) -> None:
    _trace_id_ctx.set(trace_id)


def get_trace_id() -> str:
    current = _trace_id_ctx.get()
    if current:
        return current
    generated = generate_trace_id()
    _trace_id_ctx.set(generated)
    return generated


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(fragment in lowered for fragment in _SENSITIVE_KEY_FRAGMENTS)


def sanitize_parameters(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, val in value.items():
            if _is_sensitive_key(str(key)):
                sanitized[str(key)] = "[REDACTED]"
            else:
                sanitized[str(key)] = sanitize_parameters(val)
        return sanitized
    if isinstance(value, list):
        return [sanitize_parameters(item) for item in value]
    if isinstance(value, tuple):
        return tuple(sanitize_parameters(item) for item in value)
    if isinstance(value, str | int | float | bool) or value is None:
        return value
    return str(value)


def hash_parameters(parameters: dict[str, Any] | None) -> str:
    if not parameters:
        return sha256(b"{}").hexdigest()
    sanitized = sanitize_parameters(parameters)
    payload = json.dumps(sanitized, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(payload.encode("utf-8")).hexdigest()


def emit_audit_event(
    logger: Logger,
    *,
    operation: str,
    component: str,
    outcome: AuditOutcome,
    duration_ms: int,
    parameters: dict[str, Any] | None = None,
    error_type: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    trace_id = get_trace_id()
    parameters_hash = hash_parameters(parameters)
    event = AuditEvent(
        operation=operation,
        component=component,
        outcome=outcome,
        duration_ms=duration_ms,
        trace_id=trace_id,
        parameters_hash=parameters_hash,
        error_type=error_type,
        metadata=metadata or {},
    )
    logger.info(
        "audit_event",
        extra={
            "trace_id": event.trace_id,
            "operation": event.operation,
            "component": event.component,
            "outcome": event.outcome.value,
            "duration_ms": event.duration_ms,
            "parameters_hash": event.parameters_hash,
            "error_type": event.error_type,
            "audit_metadata": event.metadata,
        },
    )
    return event


@contextmanager
def audit_operation(
    logger: Logger,
    *,
    operation: str,
    component: str,
    parameters: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Iterator[None]:
    start = perf_counter()
    try:
        yield
    except Exception as exc:
        duration_ms = int((perf_counter() - start) * 1000)
        emit_audit_event(
            logger,
            operation=operation,
            component=component,
            outcome=AuditOutcome.FAILURE,
            duration_ms=duration_ms,
            parameters=parameters,
            error_type=type(exc).__name__,
            metadata=metadata,
        )
        raise
    else:
        duration_ms = int((perf_counter() - start) * 1000)
        emit_audit_event(
            logger,
            operation=operation,
            component=component,
            outcome=AuditOutcome.SUCCESS,
            duration_ms=duration_ms,
            parameters=parameters,
            metadata=metadata,
        )
