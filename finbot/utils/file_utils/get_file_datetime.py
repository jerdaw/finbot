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
