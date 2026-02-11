"""Analyze missing data patterns in pandas DataFrames and Series.

Provides statistical analysis of missing values including counts, percentages,
and row-level completeness metrics. Helps identify data quality issues and
inform imputation strategy decisions.

Typical usage:
    ```python
    analysis, summary = analyze_missing_data_pattern(df, round_decimals=2)
    print(f"Rows with missing: {summary['rows_with_missing']}")
    print(f"Complete rows: {summary['complete_rows']}")
    print(analysis)  # Missing count and percentage per column
    ```

Analysis features:
    - Missing value counts per column
    - Missing value percentages (customizable rounding)
    - Row-level completeness statistics
    - Support for custom missing value indicators (e.g., 'N/A', '?')
    - Works with both DataFrames and Series

Use cases:
    - Data quality assessment before imputation
    - Identifying columns with excessive missing data
    - Deciding between deletion vs. imputation strategies
    - Reporting data completeness metrics
"""

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
