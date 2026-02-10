from __future__ import annotations

import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

from finbot.utils.data_science_utils.data_cleaning.missing_data_handlers._missing_data_utils import (
    _check_numeric,
    _validate_df_or_series,
    _validate_parameters,
)


def seasonal_decomposition_imputation(
    data: pd.DataFrame,
    model: str = "additive",
    freq: int | None = None,
    inplace: bool = False,
) -> pd.DataFrame:
    """
    Perform seasonal decomposition imputation on the given data.

    Seasonal decomposition imputation is a technique used to fill missing values in time series data by decomposing the series into its trend, seasonal, and residual components. The missing values in each component are then filled using forward fill and backward fill methods. Finally, the imputed data is reconstructed by combining the imputed components based on the specified model.

    Parameters:
        data (pd.DataFrame): The input data to be imputed.
        model (str): The type of seasonal decomposition model to use. Options: 'additive', 'multiplicative'.
        freq (int | None): The frequency of the data. Default is None.
        inplace (bool): Whether to perform the imputation in-place. Default is False.

    Returns:
        pd.DataFrame: The imputed data.

    Raises:
        TypeError: If not all columns in the DataFrame are numeric.
    """
    valid_models = {"additive", "multiplicative"}
    _validate_parameters(
        model,
        valid_models,
        "Invalid model for seasonal decomposition. Valid options are 'additive' and 'multiplicative'.",
    )

    if freq is not None and not isinstance(freq, int):
        raise ValueError("Frequency must be a positive integer.")

    if not inplace:
        data = data.copy()
    _validate_df_or_series(data)
    _check_numeric(data)

    decomposed = seasonal_decompose(data, model=model, period=freq)
    trend = decomposed.trend.fillna(method="ffill").fillna(method="bfill")
    seasonal = decomposed.seasonal.fillna(
        method="ffill",
    ).fillna(method="bfill")
    residual = decomposed.resid.fillna(method="ffill").fillna(method="bfill")

    data = trend + seasonal + residual if model == "additive" else trend * seasonal * residual

    return data
