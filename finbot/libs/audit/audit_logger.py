"""Audit logger utilities for structured operation logging.

This module provides decorators, context managers, and utilities for
consistent audit logging across all Finbot operations.
"""

from __future__ import annotations

import functools
import logging
import time
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any

from finbot.libs.audit.audit_schema import AuditLogEntry, OperationStatus, OperationType


class AuditLogger:
    """Wrapper for logging audit events with structured schema.

    Examples:
        Using the context manager:
        >>> audit = AuditLogger(logger)
        >>> with audit.log_operation("run_backtest", OperationType.BACKTEST, parameters={"strategy": "rebalance"}):
        ...     # Operation code
        ...     pass

        Using the decorator:
        >>> @audit_operation(operation_type=OperationType.BACKTEST)
        >>> def run_backtest(**kwargs):
        ...     return {"total_return": 0.15}
    """

    def __init__(self, logger: logging.Logger):
        """Initialize audit logger.

        Args:
            logger: Python logger instance to use for audit logging
        """
        self.logger = logger

    @contextmanager
    def log_operation(
        self,
        operation: str,
        operation_type: OperationType,
        parameters: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
        user: str = "system",
    ):
        """Context manager for logging an operation.

        Args:
            operation: Name of the operation
            operation_type: Type of operation
            parameters: Operation parameters
            context: Additional context
            user: User identifier

        Yields:
            AuditLogEntry: Entry that can be updated during operation

        Example:
            >>> with audit.log_operation(
            ...     "simulate_fund", OperationType.SIMULATION, parameters={"fund": "UPRO", "years": 10}
            ... ):
            ...     result = simulate_fund(...)
        """
        entry = AuditLogEntry(
            operation=operation,
            operation_type=operation_type,
            parameters=parameters or {},
            context=context or {},
            user=user,
        )

        start_time = time.perf_counter()

        try:
            # Log operation start
            self.logger.info(
                f"Starting {operation_type.value} operation: {operation}",
                extra=entry.to_dict(),
            )

            yield entry

            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000
            entry.set_duration(duration_ms)

            # Update status if not already set
            if entry.status == OperationStatus.IN_PROGRESS:
                entry.update_status(OperationStatus.SUCCESS)

            # Log operation completion
            self.logger.info(
                f"Completed {operation_type.value} operation: {operation} ({duration_ms:.2f}ms) - {entry.status.value}",
                extra=entry.to_dict(),
            )

        except Exception as e:
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000
            entry.set_duration(duration_ms)

            # Update status to failure
            entry.update_status(OperationStatus.FAILURE, errors=[str(e)])

            # Log operation failure
            self.logger.error(
                f"Failed {operation_type.value} operation: {operation} ({duration_ms:.2f}ms) - {e!s}",
                extra=entry.to_dict(),
                exc_info=True,
            )

            # Re-raise the exception
            raise

    def log_event(
        self,
        operation: str,
        operation_type: OperationType,
        status: OperationStatus,
        parameters: dict[str, Any] | None = None,
        result: dict[str, Any] | None = None,
        errors: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ):
        """Log a single audit event (for operations not using context manager).

        Args:
            operation: Name of the operation
            operation_type: Type of operation
            status: Operation status
            parameters: Operation parameters
            result: Operation result
            errors: List of errors if any
            context: Additional context

        Example:
            >>> audit.log_event(
            ...     "data_fetch",
            ...     OperationType.DATA_COLLECTION,
            ...     OperationStatus.SUCCESS,
            ...     parameters={"source": "yfinance", "symbol": "SPY"},
            ...     result={"rows": 5000},
            ... )
        """
        entry = AuditLogEntry(
            operation=operation,
            operation_type=operation_type,
            status=status,
            parameters=parameters or {},
            result=result or {},
            errors=errors or [],
            context=context or {},
        )

        level = logging.INFO if status == OperationStatus.SUCCESS else logging.ERROR

        self.logger.log(
            level,
            f"{operation_type.value} operation: {operation} - {status.value}",
            extra=entry.to_dict(),
        )


def audit_operation(
    operation_type: OperationType,
    operation_name: str | None = None,
    include_return: bool = True,
    logger_name: str = "finbot",
):
    """Decorator for automatic audit logging of operations.

    Args:
        operation_type: Type of operation
        operation_name: Custom operation name (default: function name)
        include_return: Include return value in result (default: True)
        logger_name: Logger name to use (default: "finbot")

    Returns:
        Decorated function with audit logging

    Example:
        >>> @audit_operation(operation_type=OperationType.BACKTEST)
        >>> def run_backtest(strategy: str, **kwargs):
        ...     return {"total_return": 0.15}
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Lazy import to avoid circular dependency
            import logging

            # Get logger
            logger = logging.getLogger(logger_name)
            audit = AuditLogger(logger)

            # Determine operation name
            op_name = operation_name or func.__name__

            # Extract parameters (avoid logging large objects)
            parameters = _extract_safe_parameters(args, kwargs)

            # Log operation
            with audit.log_operation(op_name, operation_type, parameters=parameters) as entry:
                # Execute function
                result = func(*args, **kwargs)

                # Include return value in result if requested
                if include_return:
                    # Safely convert result to dict
                    result_dict = _safe_result_to_dict(result)
                    entry.update_result(result_dict)

                return result

        return wrapper

    return decorator


def _extract_safe_parameters(args: tuple, kwargs: dict[str, Any]) -> dict[str, Any]:
    """Extract safe parameters for logging.

    Args:
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Dictionary of safe parameters
    """
    parameters = {}

    # Add keyword arguments (safer than positional)
    for key, value in kwargs.items():
        if isinstance(value, str | int | float | bool | type(None)) or (
            isinstance(value, list | tuple) and all(isinstance(v, str | int | float) for v in value)
        ):
            parameters[key] = value
        else:
            # Log type instead of value for complex objects
            parameters[key] = f"<{type(value).__name__}>"

    # Add count of positional arguments
    if args:
        parameters["_positional_args_count"] = len(args)

    return parameters


def _safe_result_to_dict(result: Any) -> dict[str, Any]:
    """Safely convert result to dictionary for logging.

    Args:
        result: Function return value

    Returns:
        Dictionary representation of result
    """
    if result is None:
        return {"return_value": None}

    if isinstance(result, dict):
        return {"return_value": result}

    if isinstance(result, str | int | float | bool):
        return {"return_value": result}

    if isinstance(result, list | tuple):
        return {"return_value": result, "count": len(result)}

    # For objects, try to get a summary
    if hasattr(result, "__dict__"):
        return {"return_type": type(result).__name__, "summary": str(result)[:200]}

    return {"return_type": type(result).__name__}
