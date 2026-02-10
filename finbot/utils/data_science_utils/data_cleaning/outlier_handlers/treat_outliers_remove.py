import pandas as pd

from finbot.utils.data_science_utils.data_cleaning.outlier_handlers._outliers_utils import _apply_treatment_to_pandas


def _remove_outliers_logic(data: pd.Series, **kwargs) -> pd.Series:
    raise NotImplementedError("This function hasn't yet been confirmed to work as intended.")
    """
    Remove outliers from the Series.
    """
    return data[~kwargs.get("mask")]


def remove_outliers(data: pd.DataFrame, mask: pd.Series) -> pd.DataFrame:
    raise NotImplementedError("This function hasn't yet been confirmed to work as intended.")
    return _apply_treatment_to_pandas(
        data=data,
        method=_remove_outliers_logic,
        mask=mask,
    )
