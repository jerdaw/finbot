from __future__ import annotations

import pandas as pd
from sklearn.impute import IterativeImputer

from finbot.utils.data_science_utils.data_cleaning.missing_data_handlers._missing_data_utils import (
    _check_numeric,
    _validate_df_or_series,
)


def mice_imputation(data: pd.DataFrame, max_iter: int = 10, inplace: bool = False) -> pd.DataFrame:
    """
    Perform Multiple Imputation by Chained Equations (MICE) on the given data.

    Args:
        data (pd.DataFrame): The input data with missing values.
        max_iter (int): Maximum number of imputation iterations. Default is 10.
        inplace (bool): Whether to perform the imputation in-place. Default is False.

    Returns:
        pd.DataFrame: The imputed data with missing values replaced by MICE.

    Raises:
        TypeError: If the data is not a DataFrame.
    """
    if not inplace:
        data = data.copy()
    _validate_df_or_series(data)
    _check_numeric(data)

    if not 1 <= max_iter <= 100:
        raise ValueError(
            "Maximum number of iterations must be between 1 and 100.",
        )
    elif max_iter > 10:
        print("WARNING: Maximum number of iterations greater than 10 may take a (very) long time to run.")

    imputer = IterativeImputer(max_iter=max_iter)
    imputed_data = imputer.fit_transform(data)
    data.loc[:, :] = imputed_data

    return data
