from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from config import Config, logger
from finbot.utils.file_utils.backup_file import backup_file
from finbot.utils.pandas_utils.hash_dataframe import hash_dataframe

MAX_THREADS = Config.MAX_THREADS


def _construct_file_path(
    file_path: Path | str | None,
    save_dir: Path | str | None,
    file_name: Path | str | None,
    df: pd.DataFrame | pd.Series,
) -> Path:
    """
    Constructs and validates the full file path from the given file_path, save_dir, and file_name.

    Args:
        file_path (Path | str | None): Full file path to save the file.
        save_dir (Path | str | None): Directory to save the file.
        file_name (str | None): Custom name for the file.
        df (pd.DataFrame | pd.Series): The DataFrame or Series to be saved.

    Returns:
        Path: The constructed file path.

    Raises:
        ValueError: If the inputs are invalid or inconsistent.
    """
    if file_path is not None:
        file_path = Path(file_path)
    elif save_dir is not None:
        save_dir = Path(save_dir)
        if file_name is None:
            data_hash = hash_dataframe(pd.DataFrame(df))
            dt_str = datetime.now().strftime("%Y%m%d_%H%M%S%f")
            file_name = f"{dt_str}_{data_hash}.parquet"
        if not str(file_name).endswith(".parquet"):
            raise ValueError("file_name must end with '.parquet'")
        file_name = Path(file_name)
        if file_name.is_absolute():
            raise ValueError("file_name must not be an absolute path")
        file_path = save_dir / file_name
    else:
        raise ValueError("Either file_path or save_dir must be provided")

    if not file_path.name.endswith(".parquet"):
        raise ValueError("the final file path must end with '.parquet'")

    return file_path


def _is_suitable_key_column(column: pd.Series) -> bool:
    """
    Determine if a pandas Series is suitable as a key column for _df_save_safety_check.

    Args:
        column: pandas Series representing a DataFrame column.

    Returns:
        bool: True if the column is suitable as a key column for _df_save_safety_check, False otherwise.
    """
    try:
        # A column is suitable if it has a high proportion of unique values
        # and does not contain unhashable types.
        return len(column.unique()) / len(column) > 0.9
    except TypeError:
        # Occurs if the column contains unhashable types
        return False


def _df_save_safety_check(
    df: pd.DataFrame | pd.Series,
    file_path: Path | str,
    key_columns: list[str] | None = None,
) -> bool:
    """
    Check a pandas DataFrame for consistency with an existing file. Uses provided key columns, or automatically detects them if not provided. Issues warnings if inconsistencies are found.

    Note: For logging, the function performs all check types even if one check fails.

    Args:
        df: DataFrame or Series to be checked.
        file_path: Full file path of the existing file.
        key_columns: Optional list of key columns to check for data consistency. Automatically detected if not provided.

    Returns:
        bool: True if all checks pass, False otherwise.
    """
    df = pd.DataFrame(df)  # Otherwise accessing columns is a pain

    file_path = Path(file_path)
    if not isinstance(df, pd.DataFrame | pd.Series):
        raise ValueError("df must be a pandas DataFrame or Series")

    all_checks_passed = True

    # Check if the file exists
    if file_path.exists():
        # Read the existing file
        existing_df = pd.read_parquet(file_path)

        # Automatically detect key columns if not provided
        if key_columns is None:
            key_columns = [col for col in df.columns if _is_suitable_key_column(df[col])]

        # Check for row count consistency
        if len(df) < len(existing_df):
            logger.warning(
                f"The new DataFrame at has {len(existing_df) - len(df)} fewer rows than the existing file at {file_path}",
            )
            all_checks_passed = False

        # Check for key column consistency
        for key_column in key_columns:
            if key_column in df.columns and key_column in existing_df.columns:
                if not df[key_column].isin(existing_df[key_column]).all():
                    logger.warning(
                        f"Key column {key_column} values in the new DataFrame do not match the existing file.",
                    )
                    all_checks_passed = False
                    break
            else:
                logger.warning(
                    f"Key column {key_column} is missing in the new DataFrame or the existing file.",
                )
                all_checks_passed = False
                break

        # Check for data type consistency
        if not df.dtypes.equals(existing_df.dtypes):
            logger.warning(
                "Data types of the new DataFrame do not match the existing file.",
            )
            all_checks_passed = False

        # Check for column presence
        if not all(column in df.columns for column in existing_df.columns):
            logger.warning(
                "Not all columns in the existing file are present in the new DataFrame.",
            )
            all_checks_passed = False

    return all_checks_passed


def save_dataframe(
    df: pd.DataFrame | pd.Series,
    file_path: Path | str | None = None,
    save_dir: Path | str | None = None,
    file_name: str | None = None,
    compression: str = "zstd",
    smart_backup: bool = True,
) -> Path:
    """
    Save a pandas DataFrame or Series to a file using parquet.

    Args:
        df: Pandas DataFrame or Series to be saved.
        file_path: Optional. Full file path to save the file. Overrides save_dir and file_name.
        save_dir: Directory to save the file.
        file_name: Optional. Custom name for the file ending with '.parquet'. If not provided, a name is generated based on data hash.
        compression: The compression method for the Parquet file.
        smart_backup: Makes a backup of any existing save_dir/file_name if df fails _df_save_safety_check

    Raises:
        ValueError: If the provided file name does not end with '.parquet'.
        OSError: If there is an error during file saving.
    """

    # Use the helper function to construct and validate the file path
    file_path = _construct_file_path(
        file_path=file_path,
        save_dir=save_dir,
        file_name=file_name,
        df=df,
    )
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if smart_backup and not _df_save_safety_check(df=df, file_path=file_path):
        backup_file(file_path)

    try:
        logger.info(f"Saving DataFrame to {file_path}...")
        if isinstance(df, pd.Series):
            df = df.to_frame()
        df.to_parquet(path=file_path, compression=compression)  # type: ignore
        logger.info(f"Successfully saved DataFrame to {file_path}")
    except OSError as e:
        logger.error(f"Error saving DataFrame to {file_path}: {e}")
        raise

    return file_path
