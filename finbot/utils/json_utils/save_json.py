from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from config import logger
from finbot.exceptions import InvalidExtensionError, SaveError
from finbot.utils.dict_utils.hash_dictionary import hash_dictionary
from finbot.utils.json_utils.serialize_json import serialize_json


def save_json(
    data: dict[str, Any] | list[Any],
    save_dir: Path | str,
    file_name: str | None = None,
    compress: bool = True,
    compression_level: int = 3,
) -> Path:
    """
    Saves the provided data as a JSON file, with optional compression.

    Args:
        data: The data (dictionary or list) to be saved in JSON format.
        save_dir: Directory to save the file.
        file_name: Optional. Custom name for the file.
        compress: Whether to compress the JSON file.
        compression_level: Compression level if compression is enabled.

    Returns:
        The path to the saved JSON file.

    Raises:
        FileNotFoundError: If the save_dir does not exist.
        InvalidExtensionError: If the file extension is not as expected.
        JsonSaveError: If there is an error in saving the JSON file.
    """
    save_dir = Path(save_dir)

    if not save_dir.exists():
        raise FileNotFoundError(f"Directory {save_dir} does not exist.")

    if not file_name:
        # Use a different method to generate a hash if data is a list
        md5_hash = hash_dictionary(data) if isinstance(data, dict) else hash(str(data))
        dt_str = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        extension = ".json.zst" if compress else ".json"
        file_name = f"{dt_str}_{md5_hash}{extension}"
    elif compress and not file_name.endswith(".json.zst"):
        raise InvalidExtensionError(
            "File name must end with .json.zst if using compression",
        )
    elif not compress and not file_name.endswith(".json"):
        raise InvalidExtensionError(
            "File name must end with .json if not using compression",
        )

    file_path = save_dir / file_name
    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        logger.info(f"Saving JSON to {file_path}...")
        write_data = serialize_json(data, compress, compression_level) if compress else json.dumps(data)
        write_mode = "wb" if compress else "w"
        enc = None if compress else "utf-8"
        with open(file_path, write_mode, encoding=enc) as f:
            f.write(write_data)
        logger.info(f"Successfully saved JSON to {file_path}.")
    except Exception as e:
        logger.error(f"Error saving JSON to {file_path}: {e}")
        raise SaveError(f"Error saving JSON: {e}") from e

    return file_path
