from collections.abc import Callable

import pandas as pd

from finbot.utils.data_science_utils.data_cleaning.outlier_handlers._outliers_utils import _apply_treatment_to_pandas


def _transform_outliers_logic(
    data: pd.Series,
    mask: pd.Series,
    transform_func: Callable[[pd.Series], pd.Series],
    **kwargs,
) -> pd.Series:
    raise NotImplementedError("This function hasn't yet been confirmed to work as intended.")
    return data.where(~mask, transform_func(data[mask]))


def transform_outliers(data: pd.DataFrame, transform_func: Callable[[pd.Series], pd.Series], **kwargs) -> pd.DataFrame:
    raise NotImplementedError("This function hasn't yet been confirmed to work as intended.")
    return _apply_treatment_to_pandas(
        data=data,
        method=_transform_outliers_logic,
        transform_func=transform_func,
        **kwargs,
    )
