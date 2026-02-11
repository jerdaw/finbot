"""Input validation helpers for parameter checking and error handling.

Provides reusable validation functions for common parameter validation patterns:
literal values, numeric ranges, and type checking. Generates clear, consistent
error messages for invalid inputs.

Typical usage:
    ```python
    from finbot.utils.validation_utils.validation_helpers import (
        validate_literals,
        validate_num_in_range,
        validate_types,
    )


    def process_data(mode, threshold, data):
        # Validate mode is one of allowed values
        validate_literals(mode, "mode", ["simple", "advanced", "expert"])

        # Validate threshold is in range [0, 100]
        validate_num_in_range(threshold, "threshold", 0, 100, inclusive="both")

        # Validate data is list or tuple
        validate_types(data, "data", [list, tuple])

        # Now safe to proceed with validated inputs
        ...
    ```

Validation functions:

1. **validate_literals()**: Check value is in allowed set
   ```python
   validate_literals("daily", "frequency", ["daily", "weekly", "monthly"])
   # Raises ValueError if not in list
   ```

2. **validate_num_in_range()**: Check numeric value in range
   ```python
   # Closed interval [0, 100]
   validate_num_in_range(50, "percentage", 0, 100, inclusive="both")

   # Half-open interval [0, 100)
   validate_num_in_range(99, "value", 0, 100, inclusive="first")

   # Open interval (0, 1)
   validate_num_in_range(0.5, "probability", 0, 1, inclusive="none")
   ```

3. **validate_types()**: Check value is one of allowed types
   ```python
   validate_types([1, 2, 3], "data", [list, tuple])
   validate_types(42, "count", [int])
   validate_types("text", "input", [str, bytes])
   ```

Features:
    - Clear, consistent error messages
    - Parameter name in error message (better debugging)
    - Reusable across codebase
    - Type hints for IDE support
    - No return value (raises on invalid)

Inclusive parameter (validate_num_in_range):
    - "both": [min, max] - closed interval
    - "first": [min, max) - closed-open
    - "last": (min, max] - open-closed
    - "none": (min, max) - open interval

Use cases:
    - Function parameter validation
    - Configuration file validation
    - API input validation
    - Data preprocessing validation
    - Safety checks before operations

Example function with validation:
    ```python
    def calculate_metrics(data, method, percentile):
        # Type validation
        validate_types(data, "data", [list, tuple, pd.Series])

        # Literal validation
        validate_literals(method, "method", ["mean", "median", "mode"])

        # Range validation
        validate_num_in_range(percentile, "percentile", 0, 100, inclusive="both")

        # Now safe to proceed
        if method == "mean":
            return np.mean(data)
        # ...
    ```

Error message examples:
    ```python
    # validate_literals
    # ValueError: mode must be one of the following literals: ['simple', 'advanced', 'expert']

    # validate_num_in_range
    # ValueError: threshold must be in the range [0, 100]

    # validate_types
    # TypeError: data must be one of the types [<class 'list'>, <class 'tuple'>]
    ```

Why use validation helpers:
    - Consistent error messages across codebase
    - Reduce boilerplate validation code
    - Easier to maintain validation logic
    - Clear error messages help users/developers
    - Type hints improve IDE experience

Best practices:
    ```python
    # Validate early (fail fast)
    def process(value, mode):
        validate_literals(mode, "mode", ["fast", "accurate"])
        validate_num_in_range(value, "value", 0, 1)
        # Now safe to use value and mode


    # Group related validations
    def analyze_data(data, settings):
        # Type checks first
        validate_types(data, "data", [pd.DataFrame])
        validate_types(settings, "settings", [dict])

        # Then content checks
        validate_literals(settings["method"], "settings['method']", ["a", "b"])
    ```

Comparison with assertions:
    ```python
    # Assertion (disabled with -O flag, poor error message)
    assert mode in ["a", "b", "c"]

    # Validation helper (always runs, clear error message)
    validate_literals(mode, "mode", ["a", "b", "c"])
    # ValueError: mode must be one of the following literals: ['a', 'b', 'c']
    ```

Limitations:
    - Simple validation only (no regex, custom logic)
    - No automatic coercion (raises instead of converts)
    - English-only error messages
    - No warning mode (always raises)

Related modules: Used throughout finbot for parameter validation,
especially in data_science_utils and services modules.
"""

from typing import Any, Literal


def validate_literals(value: Any, parameter_name: str, literals: list[Any]) -> None:
    """
    Validates if a value matches one of the provided literals.

    Parameters:
        value: The value to check.
        parameter_name (str): Name of the parameter for error messages.
        literals (List[Any]): List of literals to check.

    Raises:
        ValueError: If the value does not match any of the provided literals.
    """
    if value not in literals:
        raise ValueError(f"{parameter_name} must be one of the following literals: {literals}")


def validate_num_in_range(
    value: int | float,
    parameter_name: str,
    min_value: int | float = float("-inf"),
    max_value: int | float = float("inf"),
    inclusive: Literal["first", "last", "both", "none"] = "both",
) -> None:
    """
    Validates if a value is a number within a range.

    Parameters:
        value (Union[int, float]): The value to check.
        parameter_name (str): Name of the parameter for error messages.
        min_value (Union[int, float]): The minimum value of the range.
        max_value (Union[int, float]): The maximum value of the range.
        inclusive (Literal["first", "last", "both", "none"]): Whether the range is inclusive or exclusive.

    Raises:
        ValueError: If the value is not within the specified range.
        ValueError: If the 'inclusive' parameter is invalid.
    """
    validate_literals(inclusive, "inclusive", ["first", "last", "both", "none"])
    if inclusive == "first":
        if not min_value <= value < max_value:
            raise ValueError(f"{parameter_name} must be in the range [{min_value}, {max_value})")
    elif inclusive == "last":
        if not min_value < value <= max_value:
            raise ValueError(f"{parameter_name} must be in the range ({min_value}, {max_value}]")
    elif inclusive == "both":
        if not min_value <= value <= max_value:
            raise ValueError(f"{parameter_name} must be in the range [{min_value}, {max_value}]")
    elif inclusive == "none":
        if not min_value < value < max_value:
            raise ValueError(f"{parameter_name} must be in the range ({min_value}, {max_value})")
    else:
        raise ValueError(f"Invalid inclusive value: {inclusive}")


def validate_types(value: Any, parameter_name: str, types: list[type]) -> None:
    """
    Validates if a value is of one of the specified types.

    Parameters:
        value: The value to check.
        parameter_name (str): Name of the parameter for error messages.
        types (List[type]): List of types to check.

    Raises:
        TypeError: If the value is not one of the specified types.
    """
    if not isinstance(value, tuple(types)):
        raise TypeError(f"{parameter_name} must be one of the types {types}")
