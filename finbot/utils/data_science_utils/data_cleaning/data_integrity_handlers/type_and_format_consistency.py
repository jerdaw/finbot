"""Standardize data types, formats, and column names for consistency.

Provides utilities for enforcing type consistency, standardizing string formats,
validating data ranges, and normalizing column names. Essential for data
quality and ensuring downstream operations don't fail due to type mismatches.

Typical usage:
    ```python
    # Standardize column types
    column_types = {"age": int, "price": float, "name": str}
    df = standardize_types(df, column_types)

    # Standardize string columns (lowercase + strip)
    df = standardize_string_formats(df, columns=["name", "email"], case="lower")

    # Validate numeric ranges
    ranges = {"age": (0, 120), "rating": (1, 5)}
    df = validate_data_ranges(df, column_ranges=ranges)

    # Standardize column names (lowercase, underscores)
    df = standardize_column_names(df)
    # "First Name" → "first_name"
    ```

Module functions:

1. **standardize_types()**:
   - Enforces specified data types for columns
   - Coerces non-convertible numeric values to NaN
   - Handles conversion errors gracefully
   - Returns copy of DataFrame with corrected types

2. **standardize_string_formats()**:
   - Converts strings to lowercase or uppercase
   - Strips leading/trailing whitespace
   - Ensures consistent text formatting

3. **validate_data_ranges()**:
   - Filters rows where values fall outside allowed ranges
   - Supports tuple ranges (min, max) for continuous data
   - Supports list ranges for categorical data
   - **WARNING**: Removes non-conforming rows (data loss)

4. **standardize_column_names()**:
   - Converts column names to lowercase
   - Replaces spaces with underscores
   - Creates programming-friendly column names

Features:
    - Type coercion with error handling
    - String normalization utilities
    - Range validation
    - Column name standardization
    - Safe type conversion (coerce to NaN on failure)

Use cases:
    - Data cleaning after import (CSV, Excel)
    - Ensuring type consistency before analysis
    - Standardizing text data (emails, names, categories)
    - Column name normalization for SQL/API compatibility
    - Removing out-of-range values

Type standardization examples:
    ```python
    # Mixed type columns
    column_types = {"user_id": int, "created_at": "datetime64[ns]", "is_active": bool, "balance": float}
    df = standardize_types(df, column_types)
    ```

String standardization examples:
    ```python
    # Email normalization
    df = standardize_string_formats(df, columns=["email"], case="lower")

    # Name formatting
    df = standardize_string_formats(df, columns=["name"], case="title")
    ```

Range validation examples:
    ```python
    # Numeric ranges
    ranges = {
        "age": (0, 120),  # Age between 0 and 120
        "temperature": (-50, 50),  # Temperature in Celsius
        "rating": [1, 2, 3, 4, 5],  # Only specific values allowed
    }
    df = validate_data_ranges(df, column_ranges=ranges)
    ```

Column name standardization:
    ```python
    # Before: "First Name", "Email Address", "User ID"
    df = standardize_column_names(df)
    # After: "first_name", "email_address", "user_id"
    ```

Best practices:
    - Standardize types early in data pipeline
    - Document expected types for each column
    - Check for data loss after validate_data_ranges
    - Use standardize_column_names before SQL operations
    - Consider impact of lowercase/uppercase on data meaning

Limitations:
    - validate_data_ranges **removes** non-conforming rows (not just flagging)
    - Type conversion failures result in NaN (may need imputation)
    - No support for complex type validations (use custom_validations)

**TODO**: Review if validate_data_ranges overlaps with outlier capping
functionality (see inline TODO comment).

Related modules: custom_validations (custom transformations),
identify_corrupted_data (detect type issues), duplicates_handlers
(remove duplicates).
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd


def standardize_types(data: pd.DataFrame, column_types: dict[str, type]) -> pd.DataFrame:
    """
    Ensures type consistency for specified columns in a DataFrame.

    Parameters:
    data (pd.DataFrame): The DataFrame to process.
    column_types (Dict[str, type]): A dictionary specifying the desired type for each column.

    Returns:
    pd.DataFrame: A DataFrame with types corrected as specified.
    """
    corrected_data = data.copy()
    for column, dtype in column_types.items():
        if column in corrected_data.columns:
            try:
                corrected_data[column] = corrected_data[column].astype(dtype)
            except ValueError:
                # Coerce non-convertible values to NaN for numeric types
                if dtype in [int, float, np.number]:
                    corrected_data[column] = pd.to_numeric(
                        corrected_data[column],
                        errors="coerce",
                    )
                else:
                    # Leave as is for non-numeric types, or implement additional logic
                    pass
    return corrected_data


def standardize_string_formats(data: pd.DataFrame, columns: Sequence[str], case: str = "lower") -> pd.DataFrame:
    """
    Standardize string formats in specified columns.
    """
    for col in columns:
        if case == "lower":
            data.loc[:, col] = data[col].str.lower()
        elif case == "upper":
            data.loc[:, col] = data[col].str.upper()
        data.loc[:, col] = data[col].str.strip()
    return data


def validate_data_ranges(data: pd.DataFrame, column_ranges: dict[str, tuple | list]) -> pd.DataFrame:
    """
    Validate that data in specified columns falls within defined ranges.
    TODO: Check if this is needed given the outlier imputation functino that squished outliers into a certain range.
    """
    for column, valid_range in column_ranges.items():
        if isinstance(valid_range, tuple):
            data = data[(data[column] >= valid_range[0]) & (data[column] <= valid_range[1])]
        elif isinstance(valid_range, list):
            data = data[data[column].isin(valid_range)]
    return data


def standardize_column_names(data: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names by replacing spaces with underscores and ensuring lowercase.
    """
    data.columns = pd.Index([col.lower().replace(" ", "_") for col in data.columns])
    return data
