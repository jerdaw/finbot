"""Error categorization for batch backtest failures."""

from __future__ import annotations

from finbot.core.contracts.batch import ErrorCategory


def categorize_error(exception: Exception) -> ErrorCategory:  # noqa: C901
    """Categorize exception into error category.

    Uses exception type and message patterns to determine the most appropriate
    error category for tracking and analysis.

    Args:
        exception: The exception to categorize

    Returns:
        ErrorCategory representing the failure type

    Examples:
        >>> categorize_error(ValueError("Invalid parameter"))
        <ErrorCategory.PARAMETER_ERROR: 'parameter_error'>

        >>> categorize_error(FileNotFoundError("Data file missing"))
        <ErrorCategory.DATA_ERROR: 'data_error'>

        >>> categorize_error(MemoryError())
        <ErrorCategory.MEMORY_ERROR: 'memory_error'>
    """
    error_message = str(exception).lower()

    # Check exception type first
    if isinstance(exception, ValueError | TypeError | AttributeError):
        # Check if it's data-related or parameter-related
        if any(keyword in error_message for keyword in ["data", "empty", "missing", "insufficient"]):
            return ErrorCategory.DATA_ERROR
        return ErrorCategory.PARAMETER_ERROR

    if isinstance(exception, FileNotFoundError | KeyError | IndexError):
        return ErrorCategory.DATA_ERROR

    if isinstance(exception, MemoryError):
        return ErrorCategory.MEMORY_ERROR

    if isinstance(exception, TimeoutError):
        return ErrorCategory.TIMEOUT

    # Check error message patterns for data-related issues
    data_keywords = [
        "data",
        "dataframe",
        "empty",
        "missing",
        "insufficient",
        "no data",
        "file not found",
        "index",
        "column",
    ]
    if any(keyword in error_message for keyword in data_keywords):
        return ErrorCategory.DATA_ERROR

    # Check for parameter/configuration issues
    parameter_keywords = [
        "parameter",
        "config",
        "invalid",
        "argument",
        "expected",
        "must be",
        "should be",
        "cannot be",
    ]
    if any(keyword in error_message for keyword in parameter_keywords):
        return ErrorCategory.PARAMETER_ERROR

    # Check for engine/runtime errors
    engine_keywords = [
        "engine",
        "cerebro",
        "strategy",
        "broker",
        "analyzer",
        "runtime",
        "assertion",
    ]
    if any(keyword in error_message for keyword in engine_keywords):
        return ErrorCategory.ENGINE_ERROR

    # Check for timeout keywords
    if any(keyword in error_message for keyword in ["timeout", "time out", "timed out", "exceeded"]):
        return ErrorCategory.TIMEOUT

    # Check for memory keywords
    if any(keyword in error_message for keyword in ["memory", "allocation", "oom", "out of memory"]):
        return ErrorCategory.MEMORY_ERROR

    # Default to unknown if no pattern matches
    return ErrorCategory.UNKNOWN
