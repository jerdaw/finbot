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
