from __future__ import annotations

import pandas as pd
from sklearn.impute import MissingIndicator

from finbot.utils.data_science_utils.data_cleaning.missing_data_handlers._missing_data_utils import (
    _validate_df_or_series,
)


def add_missing_indicators(data, features="missing-only", **kwargs):
    """
    Adds binary indicators for missing values in the given data using sklearn's MissingIndicator.

    Args:
        data (pd.DataFrame or pd.Series): The input data with potential missing values.
        features (str): The features to which the indicator should be applied.
                        Default is "missing-only" which adds indicators only for columns with missing values.
        **kwargs: Additional keyword arguments to pass to sklearn's MissingIndicator.

    Returns:
        pd.DataFrame: The original data with additional columns representing missing value indicators.
    """
    _validate_df_or_series(data)

    was_series = False
    if isinstance(data, pd.Series):
        data = data.to_frame()
        was_series = True

    indicator = MissingIndicator(features=features, **kwargs)
    indicators = indicator.fit_transform(data)

    indicator_cols = [f"missing_{i}" for i in range(indicators.shape[1])]
    df_indicators = pd.DataFrame(
        indicators,
        columns=indicator_cols,
        index=data.index,
    )

    result = pd.concat([data, df_indicators], axis=1)
    return result.squeeze() if was_series else result
