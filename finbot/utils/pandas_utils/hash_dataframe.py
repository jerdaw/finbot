"""Generate hash of DataFrame content for versioning and caching.

Creates cryptographic hash of DataFrame data for:
    - Content-based file naming (see save_dataframe.py)
    - Change detection (has data changed?)
    - Cache key generation
    - Data integrity verification

Row-by-row hashing approach ensures:
    - Consistency independent of chunk size
    - Handles various data types via stringify_df_value.py
    - Configurable hash algorithm (md5, sha256, etc.)

Used by save_dataframe.py to generate automatic file names based on content.

Typical usage:
    - Generate cache keys for expensive computations
    - Detect data changes without full comparison
    - Create content-addressed storage
    - Verify data integrity after transfer
"""

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
