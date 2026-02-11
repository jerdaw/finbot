"""Convert any DataFrame value to consistent string representation.

Converts various data types to string representations for hashing and
comparison. Handles special cases like NaN values, complex types, and
nested structures.

Used by hash_dataframe.py to create consistent string representations
of DataFrame content for cryptographic hashing.

Features:
    - Handles NaN values (pandas and otherwise)
    - Consistent string formatting for numbers
    - Supports lists, dictionaries, and complex types
    - Deterministic output for hashing

Typical usage:
    - Prepare DataFrame values for hashing
    - Create string keys from mixed-type data
    - Normalize values for comparison
    - Generate consistent representations
"""

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
    if value is pd.NA or (isinstance(value, float | pd.Series) and pd.isna(value)):
        return "NaN"

    # For other types, use the string representation
    return str(value)
