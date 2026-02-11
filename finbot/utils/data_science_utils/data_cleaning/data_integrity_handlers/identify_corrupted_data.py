"""Identify corrupted data using custom corruption detection criteria.

Wrapper around get_data_mask that identifies corrupted or invalid data based
on user-defined corruption criteria. Useful for detecting data quality issues,
malformed values, or entries that violate business rules.

Typical usage:
    ```python
    # Define corruption criteria for different columns
    criteria = {
        "age": lambda x: x < 0 or x > 120,  # Invalid age
        "price": lambda x: x < 0,  # Negative price
        "email": lambda x: "@" not in str(x),  # Invalid email
        None: lambda x: pd.isna(x),  # Generic NaN check
    }

    # Identify corrupted data (returns boolean mask)
    corrupted_mask = identify_corrupted_data(df, corruption_criteria=criteria)

    # Use mask to remove corrupted rows
    df_clean = df[~corrupted_mask.any(axis=1)]

    # Or to view corrupted data
    corrupted_rows = df[corrupted_mask.any(axis=1)]
    ```

Corruption criteria format:
    - Dict mapping column names to validation functions
    - Key: column name (or None for all columns)
    - Value: Callable that returns True if value is corrupted

Vectorization:
    - use_vectorization=True: Faster for simple operations (vectorized)
    - use_vectorization=False: Required for complex logic (apply)
    - Auto-detection available in get_data_mask

Features:
    - Flexible corruption criteria via callables
    - Column-specific or global validation rules
    - Returns boolean mask for further processing
    - Logging of vectorization status
    - Works with both Series and DataFrames

Use cases:
    - Data quality assessment
    - Identifying malformed entries
    - Detecting out-of-range values
    - Finding business rule violations
    - Locating incomplete records
    - Corruption reporting before cleaning

Example corruption criteria:
    ```python
    # Financial data validation
    criteria = {
        "revenue": lambda x: x < 0,  # Revenue can't be negative
        "margin": lambda x: not (0 <= x <= 1),  # Margin must be 0-1
        "date": lambda x: pd.to_datetime(x, errors="coerce") is pd.NaT,
    }

    # String format validation
    criteria = {
        "email": lambda x: not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", str(x)),
        "phone": lambda x: len(str(x).replace("-", "")) != 10,
        "zipcode": lambda x: len(str(x)) != 5,
    }

    # Cross-field validation (using None key)
    criteria = {None: lambda df: df["end_date"] < df["start_date"]}
    ```

Performance:
    - Vectorization preferred for simple comparisons
    - Use apply (use_vectorization=False) for complex logic
    - Consider data size when choosing approach

Related modules: custom_validations (apply transformations),
irrelevant_data_handler (remove corrupted rows), type_and_format_consistency
(type validation).

Dependencies: get_data_mask from pandas_utils
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pandas as pd

from config import logger
from finbot.utils.pandas_utils.get_data_mask import get_data_mask


def identify_corrupted_data(
    data: pd.Series | pd.DataFrame,
    corruption_criteria: dict[str | None, Callable[[Any], bool]],
    use_vectorization: bool = False,
) -> pd.Series | pd.DataFrame:
    """
    This function is a thin wrapper around get_data_mask that identifies corrupted data based on the given criteria.

    Parameters:
    data (Union[pd.Series, pd.DataFrame]): The DataFrame or Series to be checked for corruption.
    corruption_criteria (Dict[Union[str, None], Callable[[Any], bool]]): Criteria for identifying corrupted data.
    use_vectorization (Optional[bool]): If True, forces the use of vectorized operations. If False, uses 'apply'.
        If None, auto-detects the best approach.

    Returns:
    Union[pd.Series, pd.DataFrame]: A boolean mask indicating corrupted data.
    """
    logger.info(
        "Vectorization is %s for this operation.",
        "enabled" if use_vectorization else "disabled",
    )
    return get_data_mask(data, corruption_criteria, use_vectorization)
