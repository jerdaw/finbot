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
