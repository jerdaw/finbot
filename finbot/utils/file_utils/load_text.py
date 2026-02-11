"""Load text files with optional zstandard decompression.

Handles text file loading with support for zstandard (.zst) compressed files.
Provides consistent error handling and logging for both plain and compressed
text files.

Typical usage:
    ```python
    from finbot.utils.file_utils.load_text import load_text

    # Load plain text file
    content = load_text("data.txt", decompress=False)

    # Load compressed text file (default behavior)
    content = load_text("data.txt.zst")  # decompress=True by default

    # Load HTTP response cache
    cached_html = load_text("finbot/data/responses/page.html.zst")
    ```

Compression:
    - Uses zstandard compression (faster and better compression than gzip)
    - Compressed files must have `.zst` extension
    - Set decompress=False for plain text files
    - Decompression is automatic for .zst files

Features:
    - Automatic encoding handling (UTF-8)
    - Extension validation (ensures .zst for compressed files)
    - Comprehensive error handling with custom exceptions
    - Logging of load operations
    - Returns str (ready for processing)

Error handling:
    - FileNotFoundError: File doesn't exist
    - InvalidExtensionError: Missing .zst extension for compressed files
    - LoadError: Generic load failure (wraps underlying exceptions)
    - All errors logged before raising

Use cases:
    - Loading HTTP response caches (request_handler stores as .zst)
    - Reading configuration files
    - Loading log files or text data
    - Processing compressed text archives
    - Reading cached API responses

Paired with save_text():
    ```python
    # Save and load round-trip
    from finbot.utils.file_utils import save_text, load_text

    text = "Important data"
    path = save_text(text, "/data", "file.txt", compress=True)
    # Saves as file.txt.zst

    loaded = load_text(path)  # Auto-decompresses
    assert text == loaded
    ```

Compression benefits:
    - Reduces disk space usage (typically 50-80% compression)
    - Faster I/O for network storage (less data to transfer)
    - Especially effective for repetitive text (JSON, HTML, logs)

Performance:
    - Zstandard decompression is very fast (~400 MB/s)
    - Suitable for frequently accessed cached data
    - Minimal CPU overhead

Dependencies: zstandard (zstd)

Related modules: save_text (corresponding save operation), request_handler
(uses for HTTP response caching), finbot.utils.json_utils (structured data).
"""

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
