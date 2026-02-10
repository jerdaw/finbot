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
