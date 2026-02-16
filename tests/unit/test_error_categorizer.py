"""Unit tests for error categorizer."""

from __future__ import annotations

from finbot.core.contracts.batch import ErrorCategory
from finbot.services.backtesting.error_categorizer import categorize_error


def test_categorize_value_error_as_parameter():
    """Test ValueError categorized as parameter error."""
    error = ValueError("Invalid parameter value")
    assert categorize_error(error) == ErrorCategory.PARAMETER_ERROR


def test_categorize_value_error_as_data():
    """Test ValueError with data keywords categorized as data error."""
    error = ValueError("Data is empty")
    assert categorize_error(error) == ErrorCategory.DATA_ERROR


def test_categorize_file_not_found():
    """Test FileNotFoundError categorized as data error."""
    error = FileNotFoundError("Data file not found")
    assert categorize_error(error) == ErrorCategory.DATA_ERROR


def test_categorize_key_error():
    """Test KeyError categorized as data error."""
    error = KeyError("symbol")
    assert categorize_error(error) == ErrorCategory.DATA_ERROR


def test_categorize_index_error():
    """Test IndexError categorized as data error."""
    error = IndexError("list index out of range")
    assert categorize_error(error) == ErrorCategory.DATA_ERROR


def test_categorize_memory_error():
    """Test MemoryError categorized as memory error."""
    error = MemoryError()
    assert categorize_error(error) == ErrorCategory.MEMORY_ERROR


def test_categorize_timeout_error():
    """Test TimeoutError categorized as timeout."""
    error = TimeoutError("Execution timeout")
    assert categorize_error(error) == ErrorCategory.TIMEOUT


def test_categorize_by_data_keywords():
    """Test categorization by data-related keywords."""
    errors = [
        RuntimeError("DataFrame is empty"),
        Exception("No data available"),
        RuntimeError("Missing column in data"),
        Exception("Insufficient data for backtest"),
    ]

    for error in errors:
        assert categorize_error(error) == ErrorCategory.DATA_ERROR


def test_categorize_by_parameter_keywords():
    """Test categorization by parameter-related keywords."""
    errors = [
        RuntimeError("Invalid configuration"),
        Exception("Parameter must be positive"),
        RuntimeError("Expected string, got int"),
        Exception("Argument cannot be None"),
    ]

    for error in errors:
        assert categorize_error(error) == ErrorCategory.PARAMETER_ERROR


def test_categorize_by_engine_keywords():
    """Test categorization by engine-related keywords."""
    errors = [
        RuntimeError("Cerebro engine failed"),
        Exception("Strategy initialization error"),
        RuntimeError("Broker error during execution"),
        AssertionError("Analyzer assertion failed"),
    ]

    for error in errors:
        assert categorize_error(error) == ErrorCategory.ENGINE_ERROR


def test_categorize_timeout_by_keyword():
    """Test timeout categorization by keyword in message."""
    error = RuntimeError("Operation timed out")
    assert categorize_error(error) == ErrorCategory.TIMEOUT


def test_categorize_memory_by_keyword():
    """Test memory error categorization by keyword in message."""
    error = RuntimeError("Out of memory")
    assert categorize_error(error) == ErrorCategory.MEMORY_ERROR


def test_categorize_unknown():
    """Test unknown categorization for unrecognized errors."""
    error = Exception("Some completely unrelated error")
    assert categorize_error(error) == ErrorCategory.UNKNOWN


def test_categorize_type_error_as_parameter():
    """Test TypeError categorized as parameter error."""
    error = TypeError("Expected int, got str")
    assert categorize_error(error) == ErrorCategory.PARAMETER_ERROR


def test_categorize_attribute_error_as_parameter():
    """Test AttributeError categorized as parameter error."""
    error = AttributeError("Object has no attribute 'name'")
    assert categorize_error(error) == ErrorCategory.PARAMETER_ERROR


def test_categorize_case_insensitive():
    """Test categorization is case-insensitive."""
    error1 = ValueError("DATA is missing")
    error2 = ValueError("data is missing")

    assert categorize_error(error1) == ErrorCategory.DATA_ERROR
    assert categorize_error(error2) == ErrorCategory.DATA_ERROR
