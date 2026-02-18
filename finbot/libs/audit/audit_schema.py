"""Audit log schema definitions for structured logging.

This module defines the standardized schema for audit logs to ensure
consistent logging across all operations in Finbot.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class OperationType(str, Enum):
    """Types of operations that can be audited."""

    BACKTEST = "backtest"
    SIMULATION = "simulation"
    DATA_COLLECTION = "data_collection"
    OPTIMIZATION = "optimization"
    CLI = "cli"
    HEALTH_ECONOMICS = "health_economics"
    EXECUTION = "execution"
    EXPERIMENT = "experiment"


class OperationStatus(str, Enum):
    """Status of an operation."""

    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    IN_PROGRESS = "in_progress"


@dataclass
class AuditLogEntry:
    """Standardized audit log entry schema.

    This schema ensures all critical operations are logged consistently
    with sufficient information for debugging, compliance, and audit trails.

    Attributes:
        operation: Name of the operation being performed
        operation_type: Category of operation
        timestamp: ISO 8601 timestamp of when operation started
        status: Outcome status of the operation
        parameters: Operation-specific input parameters (sanitized)
        result: Operation outcome details
        duration_ms: Operation duration in milliseconds
        user: User/system identifier (default: "system")
        context: Additional context (environment, version, etc.)
        errors: List of error messages if any
    """

    operation: str
    operation_type: OperationType
    timestamp: str = field(default_factory=lambda: datetime.now().astimezone().isoformat())
    status: OperationStatus = OperationStatus.IN_PROGRESS
    parameters: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    user: str = "system"
    context: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging extra fields.

        Returns:
            Dictionary representation suitable for logger.info(extra=...)
        """
        return {
            "audit_log": True,  # Flag to identify audit logs
            "operation": self.operation,
            "operation_type": self.operation_type.value,
            "audit_timestamp": self.timestamp,
            "status": self.status.value,
            "parameters": self._sanitize_dict(self.parameters),
            "result": self.result,
            "duration_ms": self.duration_ms,
            "user": self.user,
            "context": self.context,
            "errors": self.errors,
        }

    @staticmethod
    def _sanitize_dict(data: dict[str, Any]) -> dict[str, Any]:
        """Sanitize dictionary to remove sensitive information.

        Args:
            data: Dictionary to sanitize

        Returns:
            Sanitized dictionary with sensitive values masked
        """
        sensitive_keys = {"api_key", "password", "secret", "token", "credential", "auth"}
        sanitized = {}

        for key, value in data.items():
            key_lower = key.lower()
            # Check if key contains sensitive terms
            is_sensitive = any(term in key_lower for term in sensitive_keys)

            if is_sensitive:
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = AuditLogEntry._sanitize_dict(value)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                sanitized[key] = [AuditLogEntry._sanitize_dict(item) for item in value]
            else:
                sanitized[key] = value

        return sanitized

    def update_status(self, status: OperationStatus, errors: list[str] | None = None):
        """Update operation status.

        Args:
            status: New status
            errors: Optional list of error messages
        """
        self.status = status
        if errors:
            self.errors.extend(errors)

    def update_result(self, result: dict[str, Any]):
        """Update operation result.

        Args:
            result: Result dictionary to merge
        """
        self.result.update(result)

    def set_duration(self, duration_ms: float):
        """Set operation duration.

        Args:
            duration_ms: Duration in milliseconds
        """
        self.duration_ms = duration_ms
