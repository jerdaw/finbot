from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config import logger
from finbot.exceptions import InvalidExtensionError
from finbot.utils.file_utils.is_valid_extension import is_valid_extension
from finbot.utils.json_utils.deserialize_json import deserialize_json


def load_json(
    file_path: Path | str,
    raise_exception: bool = True,
) -> dict[str, Any] | list[Any]:
    """
    Load a JSON file and return its contents as a dictionary or a list.

    Args:
        file_path: Path to the JSON file.
        raise_exception: If True, re-raises the exception after logging.

    Returns:
        A dictionary or a list containing the loaded JSON data.

    Raises:
        FileNotFoundError: If the specified file is not found.
        InvalidExtensionError: If the file extension is incorrect.
        json.JSONDecodeError: If the file content is not valid JSON.
    """
    file_path = Path(file_path)

    if not is_valid_extension(file_path, {".json", ".zst"}):
        raise InvalidExtensionError("File must end with .json or .zst")

    try:
        logger.info(f"Loading JSON data from {file_path}...")
        if file_path.suffix.lower() == ".json":
            with open(file_path, encoding="utf-8") as file:
                str_data = file.read()
            return json.loads(str_data)
        elif file_path.suffix.lower() == ".zst":
            with open(file_path, "rb") as file:
                bin_data = file.read()
            return deserialize_json(bin_data, compressed=file_path.suffix.lower() == ".zst")
        else:
            raise InvalidExtensionError(f"Invalid file extension: {file_path.suffix}")
    except FileNotFoundError as e:
        if raise_exception:
            logger.error(f"File not found {file_path}: {e}")
            raise
        logger.warning(f"File not found {file_path}: {e}")
        return {}
