from __future__ import annotations

from collections.abc import Callable

import pandas as pd


def custom_imputation(
    data: pd.DataFrame,
    strategies: dict[str, Callable[[pd.Series], pd.Series]],
    inplace: bool = False,
) -> pd.DataFrame:
    """
    Perform custom imputation based on specified strategies for each column.

    Args:
        data (pd.DataFrame): The DataFrame with missing values.
        strategies (Dict[str, Callable[[pd.Series], pd.Series]]): A dictionary where keys are column names and values are functions defining the imputation strategy.
        inplace (bool): Whether to perform the imputation in-place. Default is False.

    Returns:
        pd.DataFrame: The DataFrame with missing values imputed as per the custom strategies.

    Raises:
        KeyError: If a strategy is provided for a column not in the DataFrame.
    """
    if not inplace:
        data = data.copy()

    for col, strategy in strategies.items():
        if col not in data.columns:
            raise KeyError(f"Column '{col}' not found in the DataFrame.")
        try:
            data[col].fillna(strategy(data[col]), inplace=inplace)
        except Exception as e:
            print(f"Error applying strategy for column '{col}': {e}")

    return data
