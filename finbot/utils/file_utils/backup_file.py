from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path

from config import logger
from constants.path_constants import BACKUPS_DIR, ROOT_DIR


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
