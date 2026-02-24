"""Simple statistical imputation using sklearn's SimpleImputer.

Fills missing values using basic statistical measures (mean, median, mode, or
constant values). Wraps sklearn.impute.SimpleImputer with pandas-friendly
interface and extended functionality.

Typical usage:
    ```python
    # Fill with column means
    df_filled = simple_averaging(df, strategy="mean")

    # Fill with median values
    df_filled = simple_averaging(df, strategy="median")

    # Fill with constant value
    df_filled = simple_averaging(df, strategy="constant", fill_value=0)

    # Most frequent value (mode) imputation
    df_filled = simple_averaging(df, strategy="most_frequent")
    ```

Imputation strategies:
    - 'mean': Replace missing values with column mean
    - 'median': Replace missing values with column median
    - 'most_frequent': Replace with mode (most common value)
    - 'constant': Replace with user-specified constant value

Features:
    - Column-wise imputation for DataFrames
    - Automatic numeric column detection
    - Optional dropping of leading NaN values (dropna_start)
    - In-place or copy modification
    - Preserves pandas index and column names

Use cases:
    - Quick data cleaning when sophisticated methods not needed
    - Baseline imputation for comparison with advanced methods
    - Preprocessing step before machine learning

Dependencies: scikit-learn (sklearn.impute.SimpleImputer)

For more sophisticated imputation, see: mice_imputation, knn_imputation,
iterative_imputation modules.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.impute import SimpleImputer

from finbot.utils.data_science_utils.data_cleaning.missing_data_handlers._missing_data_utils import (
    _validate_df_or_series,
)


def simple_averaging(
    data: pd.DataFrame | pd.Series,
    strategy: str = "mean",
    fill_value: Any | None = None,
    dropna_start: bool = True,
    inplace: bool = False,
    **kwargs: object,
) -> pd.DataFrame | pd.Series:
    """
    Fill missing values using sklearn's SimpleImputer with extended functionality.

    Parameters:
        data (Union[pd.DataFrame, pd.Series]): The DataFrame or Series to be filled.
        strategy (str): The imputation strategy. Options: 'mean', 'median', 'most_frequent', 'constant'.
        fill_value (Optional[Any]): When strategy == 'constant', fill_value is used to replace missing data.
        dropna_start (bool): Whether to drop rows with missing values at the start.
        inplace (bool): Whether to modify the input data in-place.
        **kwargs: Additional keyword arguments to pass to sklearn's SimpleImputer.

    Returns:
        Union[pd.DataFrame, pd.Series]: DataFrame or Series with missing values filled.
    """
    _validate_df_or_series(data)

    if not inplace:
        data = data.copy()

    imputer = SimpleImputer(strategy=strategy, fill_value=fill_value, **kwargs)
    if isinstance(data, pd.DataFrame):
        for col in data.columns:
            if data[col].dtype.kind in "biufc":
                data[col] = imputer.fit_transform(data[[col]]).ravel()
    elif isinstance(data, pd.Series):
        data = pd.Series(
            imputer.fit_transform(
                data.to_frame(),
            ).ravel(),
            index=data.index,
        )

    if dropna_start:
        data.dropna(inplace=True)

    return data
