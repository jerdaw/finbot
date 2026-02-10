from __future__ import annotations

from typing import Any

import pandas as pd


def stringify_df_value(value: Any) -> str:
    """
    Convert a given value to its string representation.

    This function takes any input value and returns its string form. It is designed to handle various data types,
    including numbers, strings, booleans, lists, and dictionaries. Special handling is included for NaN values
    (from Pandas or otherwise), which are converted to the string "NaN".

    :param value: The value to be converted to a string. Can be of any type, including native Python types or
                  Pandas-specific types like NaN.
    :return: A string representation of the input value. For NaN values, the string "NaN" is returned.
    """
    # First, check if the value is None
    if value is None:
        return "None"

    # Check for NaN and NA values
    if value is pd.NA or (isinstance(value, float | pd.core.series.Series) and pd.isna(value)):
        return "NaN"

    # For other types, use the string representation
    return str(value)
