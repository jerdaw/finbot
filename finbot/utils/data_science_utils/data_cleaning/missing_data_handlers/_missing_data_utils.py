from __future__ import annotations

import pandas as pd

from finbot.exceptions import DataTypeError


def _validate_df_or_series(data: pd.DataFrame | pd.Series) -> None:
    """
    Validates that the given data is a Pandas DataFrame or Series.

    Args:
        data (Union[pd.DataFrame, pd.Series]): The data to be validated.

    Raises:
        TypeError: If the data is not a Pandas DataFrame or Series.
    """
    if not isinstance(data, pd.DataFrame) and not isinstance(data, pd.Series):
        raise TypeError("Input data must be a Pandas DataFrame or Series.")
    if data.empty:
        raise ValueError("Input data is empty.")


def _validate_parameters(method: str, valid_options: set, error_message: str) -> None:
    """
    Validates the given method against a list of valid options.

    Args:
        method (str): The method to be validated.
        valid_options (set): A set of valid options.
        error_message (str): The error message to be raised if the method is not valid.

    Raises:
        ValueError: If the method is not in the set of valid options.
    """
    if method not in valid_options:
        raise ValueError(
            f"Invalid parameter '{method}' method. Valid options are: {', '.join(valid_options)}. {error_message}",
        )


def _check_numeric(data: pd.DataFrame | pd.Series, allow_mixed: bool = False) -> None:
    """
    Check if the columns in the given data are numeric.

    Parameters:
        data (Union[pd.DataFrame, pd.Series]): The data to be checked.
        allow_mixed (bool, optional): Whether to allow mixed data types in the columns. Defaults to False.

    Raises:
        DataTypeError: If the data contains non-numeric columns.

    Returns:
        None
    """
    if allow_mixed:
        if not any(dtype.kind in "biufc" for dtype in (list(data.dtypes) if len(data.dtypes) > 1 else [data.dtypes])):  # type: ignore
            raise DataTypeError("At least one column must be numeric.")
    else:
        if not all(dtype.kind in "biufc" for dtype in (list(data.dtypes) if len(data.dtypes) > 1 else [data.dtypes])):  # type: ignore
            raise DataTypeError("All columns must be numeric.")
