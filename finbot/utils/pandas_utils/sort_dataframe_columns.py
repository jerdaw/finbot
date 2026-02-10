from __future__ import annotations

import pandas as pd


def sort_dataframe_multiindex(df, level=0, ascending=True, inplace=False):
    """
    Sorts the columns of a pandas DataFrame with MultiIndex columns, but only sorts the specified level.
    Other levels maintain their original order within each group of the sorted level.

    Parameters:
    df (pd.DataFrame): The DataFrame to sort.
    level (int or level name): Level of MultiIndex to sort by. Defaults to 0 (top level).
    ascending (bool): Sort in ascending order if True, else in descending order. Default is True.
    inplace (bool): If True, perform operation in-place and return None. Default is False.

    Returns:
    pd.DataFrame or None: A new DataFrame with sorted columns, or None if inplace is True.
    """
    if not isinstance(df.columns, pd.MultiIndex):
        raise ValueError(
            "The DataFrame must have MultiIndex columns to use this function.",
        )

    # Creating a sorting key that considers only the top level for sorting
    def sort_key(col):
        return col[level]

    # Sorting the top level while keeping the order of sub-levels
    sorted_columns = sorted(df.columns, key=sort_key, reverse=not ascending)

    # Reordering columns based on sorted top level while maintaining sub-level order
    new_columns_order = []
    for col in sorted_columns:
        if col[level] not in [c[level] for c in new_columns_order]:
            new_columns_order.extend(
                [c for c in df.columns if c[level] == col[level]],
            )

    df = (
        df.reindex(columns=new_columns_order, copy=False)
        if inplace
        else df.reindex(
            columns=new_columns_order,
        )
    )

    return None if inplace else df
