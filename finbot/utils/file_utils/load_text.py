from __future__ import annotations

from pathlib import Path

import zstandard as zstd

from config import logger
from finbot.exceptions import InvalidExtensionError, LoadError


def load_text(file_path: Path | str, decompress: bool = True) -> str:
    """
    Loads text from a file, with optional decompression.

    Args:
        file_path: Path of the file to be loaded.
        decompress: Whether to decompress the file. Defaults to True.

    Returns:
        The loaded text.

    Raises:
        FileNotFoundError: If the file_path does not exist.
        InvalidExtensionError: If the file extension is not as expected for decompression.
        LoadError: If there is an error in loading the file.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File {file_path} does not exist.")

    if decompress and not file_path.suffix.endswith(".zst"):
        raise InvalidExtensionError(
            "File extension must be .zst for decompressed files",
        )

    try:
        logger.info(f"Loading text from {file_path}...")
        if decompress:
            with open(file_path, "rb") as f:
                decompressor = zstd.ZstdDecompressor()
                decompressed_text = decompressor.decompress(f.read())
            return decompressed_text.decode("utf-8")
        else:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        logger.error(f"Error loading text from {file_path}: {e}")
        raise LoadError(f"Error loading text: {e}") from e
