from __future__ import annotations

import pandas as pd

from finbot.utils.data_science_utils.data_cleaning.missing_data_handlers._missing_data_utils import (
    _check_numeric,
    _validate_df_or_series,
)


def analyze_missing_data_pattern(
    data: pd.DataFrame | pd.Series,
    round_decimals: int = 2,
    missing_values=None,
) -> tuple[pd.DataFrame | pd.Series, dict[str, int]]:
    """
    Analyzes the pattern of missing data in the DataFrame or Series.

    Args:
        data (pd.DataFrame | pd.Series): The DataFrame or Series to analyze.
        round_decimals (int): The number of decimal places to round the percentage values.
        missing_values: Additional values to consider as missing (e.g., ['N/A', '?']).

    Returns:
        tuple[pd.DataFrame | pd.Series, dict[str, int]]: A tuple containing:
            - A DataFrame or Series showing the count and percentage of missing values for each column/element.
            - A dictionary with the number of rows/elements containing missing values and the number of complete rows/elements.
    """
    _validate_df_or_series(data)
    _check_numeric(data, allow_mixed=True)

    if missing_values is not None:
        data = data.replace(missing_values, pd.NA)

    total_count = data.shape[0]
    missing_count = data.isnull().sum()
    missing_percentage = (missing_count / total_count * 100).round(round_decimals)

    if isinstance(data, pd.Series):
        rows_with_missing = total_count if missing_count > 0 else 0
    else:  # data is a DataFrame
        rows_with_missing = data.isnull().any(axis=1).sum()  # type: ignore

    complete_rows = total_count - rows_with_missing

    analysis = pd.DataFrame(
        {"missing_count": missing_count, "missing_percentage": missing_percentage},
    ).squeeze()  # squeeze to Series if input is Series

    summary = {
        "rows_with_missing": rows_with_missing,
        "complete_rows": complete_rows,
    }

    return analysis, summary
