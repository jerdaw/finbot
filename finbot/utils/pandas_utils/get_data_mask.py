"""Create boolean masks from flexible criteria functions.

Generates boolean masks for pandas data structures using custom criteria
functions. Supports both single criteria (for Series) and column-specific
criteria (for DataFrames).

More flexible than simple comparison operators by allowing arbitrary
boolean functions. Optional vectorization for performance.

Related to remove_masked_data.py which applies masks to remove data.

Typical usage:
    - Identify outliers using custom logic
    - Flag data quality issues
    - Mark special conditions (gaps, anomalies)
    - Create complex filters not expressible as simple comparisons
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pandas as pd


def get_data_mask(
    data: pd.Series | pd.DataFrame,
    criteria: Callable[[Any], bool] | dict[str | None, Callable[[Any], bool]],
    use_vectorization: bool = False,
) -> pd.Series | pd.DataFrame:
    """
    Creates a mask for the data based on the given criteria, which can be a single function or a dictionary of functions.

    Parameters:
    data (Union[pd.Series, pd.DataFrame]): The DataFrame or Series to be masked.
    criteria (Union[Callable[[Any], bool], Dict[Union[str, None], Callable[[Any], bool]]]):
        Function or dictionary of functions to determine mask values.
    use_vectorization (bool): Determines if vectorized operations should be used.

    Returns:
    Union[pd.Series, pd.DataFrame]: A mask indicating where the criteria are met.
    """
    if isinstance(data, pd.Series):
        data = pd.DataFrame(data)

    if isinstance(data, pd.DataFrame):
        mask = pd.DataFrame(False, index=data.index, columns=data.columns)
        if isinstance(criteria, dict):
            for column, criteria_func in criteria.items():
                if column in data.columns:
                    mask[column] = (
                        data[column].apply(
                            criteria_func,
                        )
                        if not use_vectorization
                        else criteria_func(data[column])
                    )
        else:
            for column in data.columns:
                mask[column] = (
                    data[column].apply(
                        criteria,
                    )
                    if not use_vectorization
                    else criteria(data[column])
                )
        return mask
    else:
        raise TypeError(f"Expected data to be a DataFrame or Series, got {type(data)} instead.")
