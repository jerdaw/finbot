import pandas as pd

from finbot.utils.data_science_utils.data_cleaning.outlier_handlers._outliers_utils import _apply_treatment_to_pandas


def _cap_outliers_logic(**kwargs) -> pd.Series:
    raise NotImplementedError("This function hasn't yet been confirmed to work as intended.")
    """
    Cap outliers in the Series within the specified limits.
    """
    data = kwargs.get("data")
    limit = kwargs.get("limit")
    return data.where(~kwargs.get("mask"), data.clip(limit[0], limit[1]))


def cap_outliers(data: pd.DataFrame, limit: tuple[float, float]) -> pd.DataFrame:
    raise NotImplementedError("This function hasn't yet been confirmed to work as intended.")
    return _apply_treatment_to_pandas(
        data=data,
        method=_cap_outliers_logic,
        limit=limit,
    )
