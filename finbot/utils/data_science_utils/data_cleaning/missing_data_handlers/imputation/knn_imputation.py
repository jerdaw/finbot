from __future__ import annotations

import pandas as pd
from sklearn.impute import KNNImputer

from finbot.utils.data_science_utils.data_cleaning.missing_data_handlers._missing_data_utils import (
    _check_numeric,
    _validate_df_or_series,
)


def knn_imputation(data: pd.DataFrame | pd.Series, n_neighbors: int = 5, inplace: bool = False, **kwargs):
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
        return data.squeeze() if was_series else data
    else:
        imputed_result = pd.DataFrame(
            imputed_data,
            columns=data.columns,
            index=data.index,
        )
        return imputed_result.squeeze() if was_series else imputed_result
