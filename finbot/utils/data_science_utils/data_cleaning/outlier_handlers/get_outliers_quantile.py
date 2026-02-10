from __future__ import annotations

import pandas as pd

from finbot.utils.data_science_utils.data_cleaning.outlier_handlers._outliers_utils import _apply_detection_to_pandas
from finbot.utils.pandas_utils.remove_masked_data import remove_masked_data


def _quantile_detection_logic(data: pd.Series, **kwargs) -> pd.Series | None:
    q1 = data.quantile(kwargs["lower_quantile"])
    q3 = data.quantile(kwargs["upper_quantile"])
    iqr = q3 - q1
    lower_bound = q1 - kwargs["iqr_multiplier"] * iqr
    upper_bound = q3 + kwargs["iqr_multiplier"] * iqr
    mask = ~((data >= lower_bound) & (data <= upper_bound))
    if kwargs["remove"]:
        return remove_masked_data(data=data, mask=mask, inplace=kwargs["inplace"])
    return mask


def get_outliers_quantile(
    data: pd.DataFrame | pd.Series,
    lower_quantile: float = 0.25,
    upper_quantile: float = 0.75,
    iqr_multiplier: float = 1.5,
    remove: bool = False,
    inplace: bool = False,
) -> pd.DataFrame | pd.Series:
    """
    Detects and optionally removes outliers from a pandas Series using quantile-based method.

    Parameters:
        data (pd.DataFrame | pd.Series): The input data.
        lower_quantile (float, optional): The lower quantile threshold. Defaults to 0.25.
        upper_quantile (float, optional): The upper quantile threshold. Defaults to 0.75.
        iqr_multiplier (float, optional): The multiplier to calculate the interquartile range. Defaults to 1.5.
        remove (bool, optional): Whether to remove the outliers from the data. Defaults to False.
        inplace (bool, optional): Whether to modify the input data in-place. Defaults to False.

    Returns:
        pd.Series: The input data with outliers removed if `remove=True`, otherwise the input data as-is.
    """
    return _apply_detection_to_pandas(
        data=data,
        method=_quantile_detection_logic,
        lower_quantile=lower_quantile,
        upper_quantile=upper_quantile,
        iqr_multiplier=iqr_multiplier,
        remove=remove,
        inplace=inplace,
    )
