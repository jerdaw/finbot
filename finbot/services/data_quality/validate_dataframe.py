"""Validate DataFrame integrity after loading.

Provides lightweight validation checks for DataFrames loaded from
parquet files, catching common data quality issues like empty frames,
missing dates, duplicate indices, and unexpected column schemas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from finbot.config import logger


@dataclass
class ValidationResult:
    """Result of a DataFrame validation check."""

    file_path: Path
    is_valid: bool
    row_count: int
    col_count: int
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def validate_dataframe(  # noqa: C901 - Validation functions are inherently branchy
    df: pd.DataFrame,
    file_path: Path | str,
    min_rows: int = 1,
    expected_columns: list[str] | None = None,
    check_duplicates: bool = True,
    check_nulls: bool = False,
) -> ValidationResult:
    """Validate a DataFrame for common data quality issues.

    Args:
        df: DataFrame to validate.
        file_path: Source file path (for reporting).
        min_rows: Minimum expected row count.
        expected_columns: If provided, check these columns exist.
        check_duplicates: Check for duplicate index entries.
        check_nulls: Warn if any null values present.

    Returns:
        ValidationResult with errors and warnings.
    """
    file_path = Path(file_path)
    result = ValidationResult(
        file_path=file_path,
        is_valid=True,
        row_count=len(df),
        col_count=len(df.columns),
    )

    # Check empty
    if df.empty:
        result.errors.append("DataFrame is empty")
        result.is_valid = False
        return result

    # Check minimum rows
    if len(df) < min_rows:
        result.errors.append(f"Expected at least {min_rows} rows, got {len(df)}")
        result.is_valid = False

    # Check expected columns
    if expected_columns:
        missing = set(expected_columns) - set(df.columns)
        if missing:
            result.errors.append(f"Missing columns: {sorted(missing)}")
            result.is_valid = False

    # Check duplicate indices
    if check_duplicates and df.index.duplicated().any():
        dup_count = df.index.duplicated().sum()
        result.warnings.append(f"{dup_count} duplicate index entries")

    # Check nulls
    if check_nulls:
        null_counts = df.isnull().sum()
        null_cols = null_counts[null_counts > 0]
        if not null_cols.empty:
            result.warnings.append(f"Null values in {len(null_cols)} columns")

    # Log results
    if not result.is_valid:
        for err in result.errors:
            logger.warning(f"Validation error in {file_path.name}: {err}")
    for warn in result.warnings:
        logger.debug(f"Validation warning in {file_path.name}: {warn}")

    return result
