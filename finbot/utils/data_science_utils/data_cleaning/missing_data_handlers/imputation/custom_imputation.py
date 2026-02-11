"""Custom column-specific imputation strategies via user-defined functions.

Allows applying different imputation strategies to different columns using
custom functions. Provides maximum flexibility when different columns require
different imputation logic based on domain knowledge or data characteristics.

Typical usage:
    ```python
    # Define custom strategies for specific columns
    strategies = {
        "age": lambda s: s.fillna(s.median()),
        "income": lambda s: s.fillna(s.mean()),
        "category": lambda s: s.fillna(s.mode()[0]),
        "score": lambda s: s.interpolate(method="linear"),
    }

    # Apply custom strategies
    df_filled = custom_imputation(df, strategies=strategies)

    # In-place modification
    custom_imputation(df, strategies=strategies, inplace=True)
    ```

Strategy function signature:
    - Input: pd.Series (column with missing values)
    - Output: pd.Series (column with filled values)
    - Function should handle NaN values appropriately

Features:
    - Column-specific imputation logic
    - Maximum flexibility via user-defined functions
    - Supports any pandas filling method
    - Error handling per column with informative messages
    - In-place or copy modification
    - Only affects columns specified in strategies dict

Use cases:
    - Different columns need different imputation methods
    - Domain-specific knowledge informs filling strategy
    - Complex imputation logic not available in standard methods
    - Combining multiple imputation techniques in single call

Example strategies:
    - Time-based: lambda s: s.interpolate(method='time')
    - Conditional: lambda s: s.fillna(0 if s.name == 'quantity' else s.mean())
    - Lagged: lambda s: s.fillna(s.shift(1))
    - Rolling window: lambda s: s.fillna(s.rolling(5, min_periods=1).mean())

Error handling:
    - KeyError raised if strategy specified for non-existent column
    - Individual column errors caught and printed (does not halt execution)
    - Allows partial imputation if some strategies fail

Best practices:
    - Test strategies on sample data before full dataset
    - Use lambda functions for simple strategies
    - Define named functions for complex logic (better error messages)
    - Combine with analyze_missing_data_pattern() to inform strategy choice

Related modules: simple_imputation (single strategy for all columns),
fill_methods (predefined strategies), functional_imputation (interpolation).
"""

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
