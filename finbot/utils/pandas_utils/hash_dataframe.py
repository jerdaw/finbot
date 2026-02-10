from __future__ import annotations

import hashlib

import pandas as pd

from finbot.utils.pandas_utils.stringify_df_value import stringify_df_value


def hash_dataframe(df: pd.DataFrame, hash_algorithm: str = "md5") -> str:
    """
    Hash a pandas DataFrame efficiently, independent of chunk size.

    :param df: DataFrame to be hashed.
    :param hash_algorithm: Hash algorithm to use ('md5', 'sha256', etc.). Defaults to md5.
    :return: Hexadecimal hash of the DataFrame.
    """
    hasher = hashlib.new(hash_algorithm)

    # Hash each row individually
    for _, row in df.iterrows():
        # Convert DataFrame row to a consistent string representation
        encoded_row = (
            row.apply(stringify_df_value)
            .to_string(
                header=False,
                index=False,
            )
            .encode()
        )
        hasher.update(encoded_row)

    return hasher.hexdigest()
