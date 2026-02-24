"""K-Nearest Neighbors (KNN) imputation for missing values.

Fills missing values using the weighted mean of K-nearest neighbors. This
method leverages the similarity structure in the data to produce more
accurate imputations than simple statistical methods.

Typical usage:
    ```python
    # KNN imputation with 5 neighbors (default)
    df_filled = knn_imputation(df, n_neighbors=5)

    # Use more neighbors for smoother imputation
    df_filled = knn_imputation(df, n_neighbors=10)

    # In-place imputation
    knn_imputation(df, n_neighbors=3, inplace=True)
    ```

How KNN imputation works:
    1. For each missing value, find K nearest neighbors based on complete features
    2. Compute weighted average of neighbors' values (inverse distance weighting)
    3. Fill missing value with computed average
    4. Handle both univariate and multivariate missing patterns

Parameters:
    - n_neighbors: Number of neighbors to use (default: 5)
    - Additional sklearn.impute.KNNImputer parameters via **kwargs

Features:
    - Preserves correlation structure in data
    - Works with both DataFrames and Series
    - Handles multivariate missing patterns
    - In-place or copy modification
    - Automatic Series to DataFrame conversion

Use cases:
    - Missing data with strong feature correlations
    - Multivariate missing patterns (MAR assumption)
    - When simple statistical methods are inadequate
    - Time series with irregular missing patterns

Trade-offs:
    - More computationally expensive than simple methods
    - Requires sufficient complete rows to find neighbors
    - Performance depends on distance metric choice
    - Works best with normalized/scaled features

Dependencies: scikit-learn (sklearn.impute.KNNImputer)

Related modules: mice_imputation, iterative_imputation (more sophisticated
alternatives), simple_imputation (faster but less accurate).
"""

from __future__ import annotations

import pandas as pd
from sklearn.impute import KNNImputer

from finbot.utils.data_science_utils.data_cleaning.missing_data_handlers._missing_data_utils import (
    _check_numeric,
    _validate_df_or_series,
)


def knn_imputation(
    data: pd.DataFrame | pd.Series, n_neighbors: int = 5, inplace: bool = False, **kwargs: object
) -> pd.DataFrame | pd.Series:
    """
    Perform K-nearest neighbors (KNN) imputation on the given data using sklearn's KNNImputer.

    KNN imputation is a technique used to fill in missing values in a dataset by using the values of its nearest neighbors.
    It works by finding the K nearest neighbors of each missing value and then imputing values based on these neighbors.

    Args:
        data (pd.DataFrame or pd.Series): The input data with missing values to be imputed.
        n_neighbors (int): The number of neighbors to consider for imputation. Default is 5.
        inplace (bool): Whether to perform the imputation in-place. Default is False.
        **kwargs: Additional keyword arguments to pass to sklearn's KNNImputer.

    Returns:
        pd.DataFrame or pd.Series: The imputed data with missing values replaced by KNN imputation.
    """
    _validate_df_or_series(data)
    _check_numeric(data)

    was_series = False
    if isinstance(data, pd.Series):
        data = data.to_frame()
        was_series = True

    imputer = KNNImputer(n_neighbors=n_neighbors, **kwargs)
    imputed_data = imputer.fit_transform(data)

    if inplace:
        data.loc[:, :] = imputed_data
        return data.squeeze() if was_series else data  # type: ignore[return-value]
    else:
        imputed_result = pd.DataFrame(
            imputed_data,
            columns=data.columns,
            index=data.index,
        )
        return imputed_result.squeeze() if was_series else imputed_result  # type: ignore[return-value]
