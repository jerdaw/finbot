from __future__ import annotations

import pandas as pd
from sklearn.impute import IterativeImputer

from finbot.utils.data_science_utils.data_cleaning.missing_data_handlers._missing_data_utils import (
    _check_numeric,
    _validate_df_or_series,
)


def iterative_impute(data, inplace: bool = False, **kwargs):
    """
    Perform imputation on the given data using sklearn's IterativeImputer.

    Args:
        data (pd.DataFrame or pd.Series): The input data with missing values to be imputed.
        inplace (bool): Whether to perform the imputation in-place. Default is False.
        **kwargs: Additional keyword arguments to pass to sklearn's IterativeImputer.

    Returns:
        pd.DataFrame or pd.Series: The imputed data with missing values replaced.
    """
    _validate_df_or_series(data)
    _check_numeric(data)

    was_series = False
    if isinstance(data, pd.Series):
        data = data.to_frame()
        was_series = True

    imputer = IterativeImputer(**kwargs)
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
