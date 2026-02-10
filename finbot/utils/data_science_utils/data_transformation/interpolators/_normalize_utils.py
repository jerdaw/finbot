from __future__ import annotations

import pandas as pd


def _handle_missing_values(df: pd.DataFrame, fillna_option: str | float | int) -> pd.DataFrame:
    """
    Handles missing values in the DataFrame based on the specified option.

    Parameters:
        df (pandas.DataFrame): The DataFrame to handle missing values.
        fillna_option (str or numeric): The option to fill missing values.
            Valid options are 'ffill', 'bfill', 'ffill then bfill', 'bfill then ffill',
            'interpolate', or a numeric value.

    Returns:
        pandas.DataFrame: The DataFrame with missing values handled.
    """
    if fillna_option == "ffill":
        df.ffill(inplace=True)
    elif fillna_option == "bfill":
        df.bfill(inplace=True)
    elif fillna_option == "ffillbfill":
        df.ffill(inplace=True)
        df.bfill(inplace=True)
    elif fillna_option == "bfillffill":
        df.bfill(inplace=True)
        df.ffill(inplace=True)
    elif fillna_option == "interpolate":
        df.interpolate(inplace=True)
    elif isinstance(fillna_option, int | float):
        df.fillna(fillna_option, inplace=True)
    else:
        raise ValueError(
            "Invalid fillna_option. Valid options are 'ffill', 'bfill', 'ffillbfill', 'bfillfill', 'interpolate', or a numeric value.",
        )
    return df
