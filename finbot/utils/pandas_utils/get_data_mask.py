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
