"""Find files matching flexible search criteria with time-based sorting.

Provides powerful file discovery by combining multiple search patterns
(starts_with, ends_with, contains, regex) with time-based sorting. Ideal
for finding the most recent log files, backups, or data files.

Typical usage:
    ```python
    from pathlib import Path

    # Find all CSV files modified today
    csvs = get_matching_files("/data", ends_with=".csv", time_sort="mtime")

    # Find log files starting with "error"
    error_logs = get_matching_files("/logs", starts_with="error", time_sort="ctime")

    # Find files containing "backup" in name
    backups = get_matching_files("/backups", contains="backup")

    # Complex pattern with regex
    data_files = get_matching_files("/data", regex_pattern=r"^data_\\d{8}\\.csv$")

    # Get most recent file matching criteria
    latest = get_latest_matching_file("/data", starts_with="report")
    ```

Search criteria (combine multiple):
    - **starts_with**: Filename must begin with string
    - **ends_with**: Filename must end with string (useful for extensions)
    - **contains**: String must appear anywhere in filename
    - **regex_pattern**: Full regex pattern for complex matching

Time sort options:
    - **mtime** (default): Modification time (most common)
    - **ctime**: Creation/change time (filesystem dependent)
    - **atime**: Access time (read time)

Returns files sorted oldest to newest by the specified time.

Features:
    - Flexible pattern matching (4 methods)
    - Time-based sorting with 3 options
    - Returns list of Path objects (sorted)
    - Comprehensive error handling with logging
    - Input validation for all parameters

Error handling:
    - FileNotFoundError: Directory doesn't exist
    - ValueError: No search criteria provided or invalid time_sort
    - re.error: Invalid regex pattern
    - All errors logged before raising

Use cases:
    - Finding most recent log/data files
    - Batch processing files matching pattern
    - Backup file discovery
    - Data pipeline file management
    - Cleanup operations (find old files)

Example patterns:
    ```python
    # Find all Python files
    get_matching_files(dir, ends_with=".py")

    # Find dated CSV files
    get_matching_files(dir, regex_pattern=r"data_\\d{8}\\.csv")

    # Find backup files from today
    get_matching_files(dir, contains="backup", time_sort="mtime")

    # Find files with specific prefix and suffix
    get_matching_files(dir, starts_with="report", ends_with=".pdf")
    ```

Performance:
    - Single directory scan with compiled regex
    - Efficient sorting with lambda key function
    - No recursive search (use glob pattern for subdirectories)

Related modules: get_latest_matching_file (convenience wrapper for most recent),
are_files_outdated (check if files need updating), backup_file (file backup).
"""

from __future__ import annotations

import fnmatch
import re
from collections.abc import Sequence
from pathlib import Path

from config import logger


def _sort_files_for_match(file_list: Sequence[Path], time_sort: str) -> list[Path]:
    """
    Sorts a list of file paths based on a specified time criteria.

    Parameters:
    - file_list (List[Path]): List of file paths.
    - time_sort (str): The time type to sort by ('ctime', 'mtime', or 'atime').

    Returns:
    - List[Path]: Sorted list of file paths.
    """
    valid_time_sorts = ["ctime", "mtime", "atime"]
    if time_sort not in valid_time_sorts:
        raise ValueError(
            f"Invalid time_sort value '{time_sort}'. Choose 'ctime', 'mtime', or 'atime'.",
        )
    return sorted(file_list, key=lambda f: getattr(f.stat(), f"st_{time_sort}"))


def _compile_search_pattern_for_match(
    starts_with: str | None,
    ends_with: str | None,
    contains: str | None,
    regex_pattern: str | None,
) -> re.Pattern:
    """
    Compiles a regex pattern based on provided search criteria.

    Parameters:
    - starts_with (str | None): The starting string of the file name to search for.
    - ends_with (str | None): The ending string of the file name to search for.
    - contains (str | None): A string that should be contained within the file name.
    - regex_pattern (str | None): A regex pattern to match file names.

    Returns:
    - re.Pattern: Compiled regex pattern.
    """
    if regex_pattern:
        return re.compile(regex_pattern)

    pattern = "*"
    if starts_with:
        pattern = f"{starts_with}{pattern}"
    if ends_with:
        pattern = f"{pattern}{ends_with}"
    if contains:
        pattern = pattern.replace("*", f"*{contains}*")
    return re.compile(fnmatch.translate(pattern))


def get_matching_files(
    save_dir: Path | str,
    starts_with: str | None = None,
    ends_with: str | None = None,
    contains: str | None = None,
    regex_pattern: str | None = None,
    time_sort: str = "mtime",
) -> list[Path]:
    """
    Finds files in the save_dir that match the given criteria or regex pattern and sorts them based on the specified time.
    The function handles specific exceptions for missing directories, invalid regex patterns, and incorrect sorting parameters.
    Errors are logged for better debugging and error tracking.

    Parameters:
    - save_dir (Path | str): The directory to search for the file.
    - starts_with (str | None): The starting string of the file name to search for.
    - ends_with (str | None): The ending string of the file name to search for.
    - contains (str | None): A string that should be contained within the file name.
    - regex_pattern (str | None): A regex pattern to match file names.
    - time_sort (str): The time type to sort by ('ctime', 'mtime', or 'atime').

    Returns:
    - List[Path]: List of Paths to the files sorted from oldest to newest based on the specified time.

    Raises:
    - FileNotFoundError: If the specified save_dir does not exist or is not a directory.
    - re.error: If the regex_pattern is invalid.
    - ValueError: If an invalid time_sort value is provided or if the necessary parameters are not given.
    """
    if not any([starts_with, ends_with, contains, regex_pattern]):
        raise ValueError(
            "At least one parameter (starts_with, ends_with, contains, regex_pattern) must be provided",
        )

    try:
        save_dir = Path(save_dir)
        if not save_dir.exists() or not save_dir.is_dir():
            raise FileNotFoundError(
                f"The directory {save_dir} does not exist or is not a directory.",
            )

        compiled_pattern = _compile_search_pattern_for_match(
            starts_with,
            ends_with,
            contains,
            regex_pattern,
        )
        file_list = [
            f
            for f in save_dir.glob(
                "*",
            )
            if compiled_pattern.match(f.name)
        ]
        return _sort_files_for_match(file_list, time_sort)

    except FileNotFoundError as e:
        logger.error(f"File not found error: {e}")
        raise
    except re.error as e:
        logger.error(f"Regex error: {e}")
        raise
    except ValueError as e:
        logger.error(f"Value error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
