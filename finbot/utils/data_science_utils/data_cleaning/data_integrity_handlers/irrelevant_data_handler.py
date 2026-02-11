"""Remove irrelevant rows from DataFrames based on custom criteria.

Filters out rows that don't meet specified relevance criteria, either through
boolean masks or custom functions. Useful for removing out-of-scope data,
test records, or rows that don't satisfy analysis requirements.

Typical usage:
    ```python
    # Remove rows using boolean mask
    mask = df["status"] == "deleted"
    df_clean = remove_irrelevant_data(df, criteria=mask)


    # Remove rows using custom function
    def is_irrelevant(row):
        return row["age"] < 0 or row["age"] > 120


    df_clean = remove_irrelevant_data(df, criteria=is_irrelevant)

    # In-place modification
    remove_irrelevant_data(df, criteria=mask, inplace=True)
    ```

Criteria types:
    - **Boolean Series/mask**: Direct row selection
      - Example: df['column'] > threshold
      - Fastest method for simple conditions

    - **Callable function**: Row-wise evaluation
      - Takes row as input, returns bool (True = remove row)
      - Allows complex multi-column logic
      - More flexible but slower than masks

Features:
    - Two filtering methods (mask or function)
    - In-place or copy modification
    - Flexible criteria specification
    - Inverts mask automatically (~criteria)

Use cases:
    - Removing test/dummy records
    - Filtering out-of-scope observations
    - Data cleaning (invalid combinations)
    - Removing flagged/deleted records
    - Temporal filtering (dates outside range)

Example criteria functions:
    ```python
    # Remove rows with invalid combinations
    def invalid_combination(row):
        return row["quantity"] > 0 and row["price"] == 0


    # Remove rows outside date range
    def outside_range(row):
        return row["date"] < start_date or row["date"] > end_date


    # Remove rows with suspicious patterns
    def suspicious(row):
        return row["revenue"] > row["budget"] * 10
    ```

Best practices:
    - Use masks for simple single-column conditions (faster)
    - Use functions for complex multi-column logic
    - Document why data is considered irrelevant
    - Log number of removed rows for audit trail
    - Keep removed data separately for validation

Performance considerations:
    - Boolean masks are vectorized (faster)
    - Functions use apply (row-by-row, slower)
    - For large DataFrames, prefer masks when possible

Related modules: duplicates_handlers (remove duplicates),
identify_corrupted_data (find corrupted rows), custom_validations
(apply validation rules).
"""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd


def remove_irrelevant_data(
    df: pd.DataFrame,
    criteria: pd.Series | Callable,
    inplace: bool = False,
) -> pd.DataFrame | None:
    """
    Removes irrelevant data from the DataFrame based on provided criteria.

    Parameters:
    df (pd.DataFrame): The DataFrame to be processed.
    criteria (Union[pd.Series, Callable]): A boolean mask or a function that identifies irrelevant data.
    inplace (bool): If True, modify the DataFrame in place. Otherwise, return a new DataFrame.

    Returns:
    Union[pd.DataFrame, None]: Processed DataFrame if inplace is False, otherwise None.
    """
    if not inplace:
        df = df.copy()

    if isinstance(criteria, pd.Series):
        df = df[~criteria]
    elif callable(criteria):
        mask = df.apply(criteria, axis=1)
        df.drop(df[mask].index, inplace=True)

    if inplace:
        return None
    else:
        return df


# Example Usage
if __name__ == "__main__":
    # Example DataFrame
    data = {"A": [1, 2, 3], "B": [4, None, 6], "C": ["keep", "remove", "keep"]}
    df = pd.DataFrame(data)

    # Using a mask
    mask = df["C"] == "remove"
    print(
        "DataFrame after removing with mask:\n",
        remove_irrelevant_data(df, mask),
    )

    # Using a function
    def removal_criteria(row):
        return row["C"] == "remove"

    print(
        "DataFrame after removing with function:\n",
        remove_irrelevant_data(df, removal_criteria),
    )

    # Inplace modification
    remove_irrelevant_data(df, removal_criteria, inplace=True)
    print("DataFrame after inplace modification:\n", df)
