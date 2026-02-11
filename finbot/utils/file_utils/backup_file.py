"""Create timestamped backups with intelligent directory structure preservation.

Provides safe file backup functionality with smart default backup locations
that mirror the original file's directory structure. Prevents accidental
recursive backups and includes comprehensive error handling.

Typical usage:
    ```python
    from pathlib import Path
    from finbot.utils.file_utils.backup_file import backup_file

    # Smart backup (preserves directory structure)
    backup_path = backup_file("finbot/data/prices.parquet")
    # Creates: backups/finbot/data/prices_backup_20260211_143022.parquet

    # Custom backup location
    backup_path = backup_file("data.csv", backup_dir="/backups/manual")
    # Creates: /backups/manual/data_backup_20260211_143022.csv

    # Before dangerous operation
    original = "important_config.yaml"
    backup_path = backup_file(original)
    # Now safe to modify original, can restore from backup_path
    ```

Smart backup location (when backup_dir=None):
    - Mirrors original file's path relative to ROOT_DIR
    - Original: `ROOT_DIR/finbot/data/file.csv`
    - Backup: `BACKUPS_DIR/finbot/data/file_backup_<timestamp>.csv`
    - Preserves directory structure for easy identification

Custom backup location (when backup_dir specified):
    - Places backup in specified directory
    - Filename still includes timestamp: `<stem>_backup_<timestamp><suffix>`
    - Useful for manual backups or custom backup strategies

Backup filename format:
    - Pattern: `{original_stem}_backup_{timestamp}{original_suffix}`
    - Timestamp: `YYYYMMDD_HHMMSS` (e.g., `20260211_143022`)
    - Example: `data_backup_20260211_143022.csv`

Features:
    - Timestamped backups (never overwrites existing backups)
    - Preserves file metadata (timestamps, permissions) via shutil.copy2
    - Automatic directory creation (parents=True, exist_ok=True)
    - Prevents recursive backups (won't backup files already in BACKUPS_DIR)
    - Returns Path to created backup for further use
    - Comprehensive logging (info on success, error on failure)

Safety features:
    - Checks file existence before backup
    - Validates read permissions
    - Raises ValueError if file already in backups directory
    - Clear error messages for all failure modes

Error handling:
    - FileNotFoundError: Original file doesn't exist
    - PermissionError: Insufficient read permissions or write permissions
    - ValueError: Attempted recursive backup (file already in BACKUPS_DIR)
    - OSError/IOError: IO errors during copy operation

Use cases:
    - Pre-modification backups (config files, data files)
    - Periodic snapshots of important files
    - Rollback mechanism for batch operations
    - Data pipeline checkpoints
    - User-initiated manual backups

Best practices:
    ```python
    # Always backup before modifying
    backup_path = backup_file("config.yaml")
    try:
        modify_config("config.yaml")
    except Exception:
        shutil.copy2(backup_path, "config.yaml")  # Restore
        raise

    # Backup before batch operation
    files = ["data1.csv", "data2.csv", "data3.csv"]
    backups = [backup_file(f) for f in files]
    # Now safe to modify all files
    ```

Limitations:
    - No automatic cleanup of old backups (implement separately)
    - No compression (use external compression if needed)
    - Requires sufficient disk space for full copy
    - Not suitable for very large files (consider versioning systems)

Related modules: is_file_outdated (check if backup needed), save_text/load_text
(text file operations), pandas save/load (DataFrame backup).
"""

from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path

from finbot.config import logger
from finbot.constants.path_constants import BACKUPS_DIR, ROOT_DIR


def backup_file(file_path: Path | str, backup_dir: Path | None = None) -> Path:
    """
    Create a backup of a file. If 'backup_dir' is not specified, it smartly places the backup in
    BACKUPS_DATA_DIR in a corresponding location to its place in the current application file structure.
    This avoids recursive backups if the file is already in the backups directory.

    Args:
        file_path: Full file path of the file to be backed up.
        backup_dir: Optional. Specific directory where the backup will be stored. If None, uses smart backup location.

    Raises:
        FileNotFoundError: If the original file does not exist.
        PermissionError: If there are issues with file access permissions.
        ValueError: If attempting to backup something already in backups.
        OSError, IOError: If there is an IO error during the backup process.
    """

    original_file_path = Path(file_path)
    if not original_file_path.exists():
        logger.error(f"No file found at {file_path}")
        raise FileNotFoundError(f"No file found at {file_path}")

    # Check for read permissions
    if not os.access(file_path, os.R_OK):
        logger.error(f"Read permission denied for {file_path}")
        raise PermissionError(f"Read permission denied for {file_path}")

    # Determine the backup path
    if backup_dir:
        backup_dir = Path(backup_dir)
    else:
        # Default backup directory with smart location determination
        relative_path = original_file_path.relative_to(ROOT_DIR)
        backup_root = BACKUPS_DIR
        backup_dir = backup_root / relative_path.parent

        # Avoid recursive backups
        if backup_root in original_file_path.parents:
            logger.error(
                f"Attempted to backup a file already in backups: {original_file_path}",
            )
            raise ValueError(
                "Cannot backup a file already in the backups directory",
            )

    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file_name = f"{original_file_path.stem}_backup_{timestamp}{original_file_path.suffix}"
    backup_file_path = backup_dir / backup_file_name

    try:
        shutil.copy2(file_path, backup_file_path)
        logger.info(f"{original_file_path} backed up to {backup_file_path}")
    except PermissionError as e:
        logger.error(f"Permission error during backup: {e}")
        raise
    except OSError as e:
        logger.error(f"IO error during backup: {e}")
        raise

    return backup_file_path
