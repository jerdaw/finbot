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
