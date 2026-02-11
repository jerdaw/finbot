"""Find the most recent file matching search criteria.

Convenience wrapper around get_matching_files() that returns only the most
recent file. Ideal for finding the latest log, backup, or data file without
processing the entire list.

Typical usage:
    ```python
    from finbot.utils.file_utils import get_latest_matching_file

    # Get most recent CSV file
    latest_csv = get_latest_matching_file("/data", ends_with=".csv")

    # Get most recent error log
    latest_error = get_latest_matching_file("/logs", starts_with="error")

    # Get most recent backup
    latest_backup = get_latest_matching_file("/backups", contains="backup", time_sort="mtime")

    # Get latest file matching regex pattern
    latest_report = get_latest_matching_file("/reports", regex_pattern=r"report_\\d{8}\\.pdf")

    # Handle case where no files found
    latest = get_latest_matching_file("/data", starts_with="prefix")
    if latest:
        process_file(latest)
    else:
        print("No matching files found")
    ```

Parameters:
    - save_dir: Directory to search in
    - **kwargs: Passed to get_matching_files()
      - starts_with: Filename prefix
      - ends_with: Filename suffix (e.g., ".csv")
      - contains: Substring in filename
      - regex_pattern: Full regex pattern
      - time_sort: "mtime" (default), "ctime", or "atime"

Returns:
    - Path to most recent matching file
    - None if no files match criteria

Features:
    - Returns single Path (not list)
    - None if no matches (safe to check truthiness)
    - Leverages get_matching_files() for pattern matching
    - Sorted by specified time (defaults to mtime)

Use cases:
    - Loading most recent data file
    - Finding latest log for analysis
    - Getting newest backup before operation
    - Retrieving latest report for processing
    - Cache lookup (most recent cached response)

Common patterns:
    ```python
    # Process latest CSV or raise error
    latest = get_latest_matching_file("/data", ends_with=".csv")
    if not latest:
        raise FileNotFoundError("No CSV files found in /data")
    df = pd.read_csv(latest)

    # Get latest file with fallback
    latest = get_latest_matching_file("/data", starts_with="report")
    file_to_use = latest if latest else default_file

    # Check if latest file is recent enough
    latest = get_latest_matching_file("/data", ends_with=".csv")
    if latest:
        mod_time = get_file_datetime(latest, "mtime")
        if datetime.now() - mod_time < timedelta(hours=24):
            # File is fresh, use it
            pass
    ```

Performance:
    - Scans entire directory (not optimized for "stop at first")
    - Use get_matching_files() if you need all files
    - For large directories, consider time_sort="mtime" (most common)

Why use this instead of get_matching_files():
    - Cleaner code when you only need the latest
    - Returns None instead of empty list (more Pythonic)
    - No need to check list length or index

Comparison:
    ```python
    # Using get_matching_files (verbose)
    files = get_matching_files(dir, ends_with=".csv")
    latest = files[-1] if files else None

    # Using get_latest_matching_file (clean)
    latest = get_latest_matching_file(dir, ends_with=".csv")
    ```

Related modules: get_matching_files (underlying implementation), is_file_outdated
(check if file needs updating), get_file_datetime (extract file times).
"""

from __future__ import annotations

from pathlib import Path

from finbot.utils.file_utils.get_matching_files import get_matching_files


def get_latest_matching_file(save_dir: Path | str, **kwargs) -> Path | None:
    """
    Gets the most recent file in the save_dir that matches the given criteria.

    Parameters:
    - save_dir (Path | str): The directory to search for the file.
    - **kwargs: Parameters to be passed to the get_matching_files function.

    Returns:
    - Path or None: Path to the most recent file matching the criteria or None if no file is found.
    """
    save_dir = Path(save_dir)
    matching_files = get_matching_files(save_dir, **kwargs)
    if matching_files:
        # The last file in the sorted list is the most recent
        return matching_files[-1]
    return None
