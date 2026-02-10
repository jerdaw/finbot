from __future__ import annotations

import pandas as pd

from finbot.utils.data_science_utils.data_cleaning.missing_data_handlers._missing_data_utils import (
    _validate_df_or_series,
    _validate_parameters,
)


def directional_imputation(
    data: pd.DataFrame | pd.Series,
    method: str = "ffill",
    dropna_start: bool = True,
    inplace: bool = False,
) -> pd.DataFrame | pd.Series:
    """
    Fill missing values using directional methods ('ffill' or 'bfill').

    Parameters:
        data (Union[pd.DataFrame, pd.Series]): The DataFrame or Series to be filled.
        method (str): The method used to fill missing values. Options: 'ffill', 'bfill'.
        dropna_start (bool): Whether to drop rows with missing values at the start.
        inplace (bool): Whether to modify the input data in-place.

    Returns:
        Union[pd.DataFrame, pd.Series]: DataFrame or Series with missing values filled.
    """
    valid_methods = {"ffill", "bfill"}
    _validate_parameters(method, valid_methods, "Invalid parameters or method for directional_imputation")
    if not inplace:
        data = data.copy()
    _validate_df_or_series(data)

    if method == "ffill":
        data.ffill(inplace=True)
    elif method == "bfill":
        data.bfill(inplace=True)

    if dropna_start:
        data.dropna(inplace=True)

    return data
