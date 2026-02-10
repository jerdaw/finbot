from __future__ import annotations

from collections.abc import Callable

import pandas as pd


def apply_custom_validations(
    data: pd.DataFrame,
    validation_functions: dict[str, Callable[[pd.Series], pd.Series]],
) -> pd.DataFrame:
    """
    Apply custom validation functions to specified columns.
    """
    for column, func in validation_functions.items():
        data[column] = func(data[column])
    return data
