import hashlib
from datetime import datetime
from pathlib import Path

import zstandard as zstd

from config import logger
from finbot.exceptions import InvalidExtensionError, SaveError


def save_text(
    text: str,
    save_dir: Path | str,
    file_name: str | None = None,
    compress: bool = True,
    compression_level: int = 3,
) -> Path:
    """
    Saves the provided text as a file, with optional compression.

    Args:
        text: The text to be saved.
        save_dir: Directory to save the file.
        file_name: Optional. Custom name for the file.
        compress: Whether to compress the file.
        compression_level: Compression level if compression is enabled.

    Returns:
        The path to the saved file.

    Raises:
        FileNotFoundError: If the save_dir does not exist.
        InvalidExtensionError: If the file extension is not as expected.
        SaveError: If there is an error in saving the file.
    """
    save_dir = Path(save_dir)

    if not save_dir.exists():
        raise FileNotFoundError(f"Directory {save_dir} does not exist.")

    if not file_name:
        md5_hash = hashlib.md5(text.encode("utf-8"), usedforsecurity=False).hexdigest()
        dt_str = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        extension = ".txt.zst" if compress else ".txt"
        file_name = f"{dt_str}_{md5_hash}{extension}"
    elif compress and not file_name.endswith(".txt.zst"):
        raise InvalidExtensionError(
            "File name must end with .txt.zst if using compression",
        )
    elif not compress and not file_name.endswith(".txt"):
        raise InvalidExtensionError(
            "File name must end with .txt if not using compression",
        )

    file_path = save_dir / file_name
    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        logger.info(f"Saving text to {file_path}...")
        if compress:
            compressor = zstd.ZstdCompressor(level=compression_level)
            compressed_text = compressor.compress(text.encode("utf-8"))
            with open(file_path, "wb") as f:
                f.write(compressed_text)
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
        logger.info(f"Successfully saved text to {file_path}.")
    except Exception as e:
        logger.error(f"Error saving text to {file_path}: {e}")
        raise SaveError(f"Error saving text: {e}") from e

    return file_path
