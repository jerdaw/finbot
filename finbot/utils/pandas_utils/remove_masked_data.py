"""Remove data points based on boolean mask.

Applies boolean masks to remove unwanted data points from pandas Series.
Complements get_data_mask.py which creates the masks.

Typical usage:
    - Remove outliers identified by mask
    - Filter out invalid data points
    - Clean time series by removing gaps
    - Apply complex filtering criteria
"""

from __future__ import annotations

import pandas as pd


def remove_masked_data(data: pd.Series, mask: pd.Series, inplace: bool = False) -> pd.Series | None:
    """
    Removes data in a series based on a provided mask.

    Args:
        data (pd.Series): The data series from which to remove data.
        mask (pd.Series): Boolean Series where True indicates data points to be removed.
        inplace (bool): If True, performs operation in place and returns None. Defaults to False.

    Returns:
        pd.Series or None: Series with data removed according to the mask, or None if operation is performed inplace.
    """
    if inplace:
        data.drop(index=data[mask].index, inplace=True)
        return None
    else:
        return data[~mask]
