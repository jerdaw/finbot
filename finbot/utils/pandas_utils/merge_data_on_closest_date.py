"""Merge DataFrames by matching to nearest dates (asof join).

Merges two DataFrames with different frequencies by matching each date in
index_df to the closest preceding date in value_df. Useful for combining
monthly and daily data, or any misaligned time series.

Implements backward-looking asof join: for each date in index_df, finds the
most recent available data from value_df.

Typical usage:
    - Add daily market data to monthly portfolio statements
    - Merge economic indicators at different frequencies
    - Combine earnings data (quarterly) with prices (daily)
    - Join datasets with misaligned timestamps
"""

import pandas as pd


def merge_data_on_closest_date(
    index_df: pd.DataFrame,
    value_df: pd.DataFrame,
    columns_to_merge: list[str] | None = None,
) -> pd.DataFrame:
    """
    Merges two pandas DataFrames, index_df and value_df, on the closest date.
    Allows the option to merge specific columns or all columns from value_df.

    Parameters:
    index_df (pd.DataFrame): DataFrame with monthly data.
    value_df (pd.DataFrame): DataFrame with daily data.
    columns_to_merge (list of str, optional): List of column names from value_df to be merged. If None, all columns are merged.

    Returns:
    pd.DataFrame: Merged DataFrame with indices from index_df and specified columns from the closest index in value_df.
    """

    if not isinstance(index_df.index, pd.DatetimeIndex):
        raise ValueError("index_df index must be a DatetimeIndex.")

    if not isinstance(value_df.index, pd.DatetimeIndex):
        raise ValueError("value_df index must be a DatetimeIndex.")

    # If specific columns are specified, subset value_df
    if columns_to_merge is not None:
        value_df = value_df[columns_to_merge]

    # Reindex the merge dataframe to match the source dataframe
    reindexed_value_df = value_df.reindex(index_df.index, method="nearest")

    return reindexed_value_df


if __name__ == "__main__":
    # Example usage of merge_data_on_closest_date function
    index_df = pd.DataFrame(
        {"Date": ["2022-01-01", "2022-02-01", "2022-03-01", "2024-01-01"], "Value": [10, 20, 30, -50]},
    ).set_index("Date")
    index_df.index = pd.to_datetime(index_df.index)
    value_df = pd.DataFrame(
        {
            "Date": ["2022-01-02", "2022-01-03", "2022-02-02", "2022-02-03", "2022-04-02"],
            "Value": [100, 200, 300, 400, 500],
        },
    ).set_index("Date")
    value_df.index = pd.to_datetime(value_df.index)
    merged_df = merge_data_on_closest_date(index_df, value_df, columns_to_merge=["Value"])

    print("Source DataFrame:")
    print(index_df)

    print("Merge DataFrame:")
    print(value_df)

    print("Merged DataFrame:")
    print(merged_df)
