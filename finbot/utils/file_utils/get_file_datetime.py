"""Retrieve file timestamps as datetime objects.

Converts filesystem timestamps (creation, modification, access times) into
Python datetime objects for easy comparison and analysis. Essential for
time-based file operations and staleness checking.

Typical usage:
    ```python
    from finbot.utils.file_utils.get_file_datetime import get_file_datetime

    # Get modification time
    mod_time = get_file_datetime("data.csv", "mtime")
    print(f"Last modified: {mod_time}")

    # Get creation time
    create_time = get_file_datetime("file.txt", "ctime")

    # Get last access time
    access_time = get_file_datetime("log.txt", "atime")

    # Check if file modified in last hour
    from datetime import datetime, timedelta

    mod_time = get_file_datetime("data.csv", "mtime")
    if datetime.now() - mod_time < timedelta(hours=1):
        print("Recently modified")
    ```

Time types:
    - **mtime** (Modification time): When file content last changed
      - Most commonly used for "file age" checks
      - Updates when file is written to
      - Best for: staleness checks, cache invalidation, backup decisions

    - **ctime** (Change/Creation time): When file metadata changed
      - On Unix: when metadata (permissions, ownership) or content changed
      - On Windows: file creation time
      - Platform-dependent behavior
      - Best for: metadata tracking, forensics

    - **atime** (Access time): When file was last read
      - Updates when file is opened for reading
      - May be disabled on some filesystems (noatime mount option)
      - Often unreliable or disabled for performance
      - Best for: access pattern analysis (when available)

Features:
    - Returns datetime object (timezone-naive, local time)
    - Input validation (file existence, valid time_type)
    - Clear error messages for invalid inputs
    - Works with Path or str inputs

Error handling:
    - FileNotFoundError: File doesn't exist
    - ValueError: Invalid time_type (not ctime/mtime/atime)

Use cases:
    - File staleness checking (is_file_outdated uses this)
    - Determining if files need re-processing
    - Cache invalidation logic
    - Backup scheduling
    - Data freshness validation
    - Log rotation decisions

Common patterns:
    ```python
    # Check if file is older than threshold
    mod_time = get_file_datetime("data.csv", "mtime")
    threshold = datetime(2025, 1, 1)
    if mod_time < threshold:
        print("File is outdated")

    # Compare two files by modification time
    time1 = get_file_datetime("file1.txt", "mtime")
    time2 = get_file_datetime("file2.txt", "mtime")
    if time1 > time2:
        print("file1.txt is newer")

    # Get age in days
    mod_time = get_file_datetime("data.csv", "mtime")
    age_days = (datetime.now() - mod_time).days
    ```

Limitations:
    - Returns timezone-naive datetime (local time)
    - atime may be unreliable (noatime mount option)
    - ctime behavior differs between Unix/Windows
    - Precision varies by filesystem (typically 1 second)

Related modules: is_file_outdated (uses this for staleness checks),
are_files_outdated (batch checking), get_matching_files (sorts by time).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


def get_file_datetime(file_path: Path | str, time_type: str) -> datetime:
    """
    Retrieves the specified time information of the file and returns it as a datetime object.

    Parameters:
    - file_path (Path): The path to the file.
    - time_type (str): The type of time to retrieve ('ctime', 'mtime', or 'atime').

    Returns:
    - datetime: The specified time of the file as a datetime object.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    valid_time_types = ["ctime", "mtime", "atime"]
    if time_type not in valid_time_types:
        raise ValueError(f"Invalid time_type. Choose from {valid_time_types}.")

    file_time = getattr(file_path.stat(), f"st_{time_type}")
    return datetime.fromtimestamp(file_time)
