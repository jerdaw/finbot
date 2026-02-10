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
