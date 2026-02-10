from __future__ import annotations

from pathlib import Path


def is_valid_extension(file_path: Path | str, valid_extensions: set) -> bool:
    """
    Check if a file's extension is in the allowed set.

    Args:
        file_path: The path of the file to check.
        valid_extensions: A set of allowed file extensions.

    Returns:
        True if the file's extension is in the set, False otherwise.
    """
    return Path(file_path).suffix.lower() in valid_extensions
