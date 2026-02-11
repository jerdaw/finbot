"""Load JSON files with automatic decompression support.

Reads JSON files (both plain .json and compressed .json.zst) and returns
Python data structures. Features automatic format detection, optional error
handling, and comprehensive validation.

Typical usage:
    ```python
    from finbot.utils.json_utils.load_json import load_json

    # Load plain JSON file
    data = load_json("config.json")

    # Load compressed JSON file
    data = load_json("cache.json.zst")

    # Load with optional error handling (returns {} on not found)
    data = load_json("optional_config.json", raise_exception=False)
    if not data:
        print("Config not found, using defaults")

    # Full path
    from pathlib import Path

    data = load_json(Path("/data/prices/SPY.json.zst"))
    ```

Supported formats:
    - `.json` - Plain JSON files (UTF-8 encoded)
    - `.zst` - Zstandard-compressed JSON files
    - `.json.zst` - Also recognized (checks suffix, not full extension)

Features:
    - Automatic compression detection by extension
    - Extension validation (.json or .zst only)
    - Optional exception handling (return {} instead of raising)
    - Comprehensive logging (info on load, warning/error on failures)
    - Works with Path or str inputs
    - Returns dict or list (depends on JSON structure)

Error handling modes:
    - raise_exception=True (default): Raises all exceptions after logging
    - raise_exception=False: Returns empty dict on FileNotFoundError
      - Other exceptions still raise (JSONDecodeError, InvalidExtensionError)
      - Logs warning instead of error for file not found

Error types:
    - FileNotFoundError: File doesn't exist
    - InvalidExtensionError: Extension not .json or .zst
    - json.JSONDecodeError: Invalid JSON content
    - RuntimeError: From deserialize_json (compression issues)

Use cases:
    - Loading configuration files
    - Reading cached API responses
    - Loading application state
    - Processing compressed JSON archives
    - Optional configuration loading

Example workflows:
    ```python
    # Required configuration (raise on missing)
    config = load_json("config.json")  # Must exist

    # Optional configuration (default on missing)
    user_prefs = load_json("user_prefs.json", raise_exception=False)
    if not user_prefs:
        user_prefs = DEFAULT_PREFERENCES

    # Cached data with fallback
    cached = load_json("cache.json.zst", raise_exception=False)
    if not cached:
        print("Cache miss, fetching fresh data")
        cached = fetch_and_cache_data()

    # Round-trip with save_json
    from finbot.utils.json_utils import save_json, load_json

    original = {"prices": [100, 105, 110]}
    path = save_json(original, "/data", "prices.json.zst")
    loaded = load_json(path)
    assert original == loaded
    ```

Extension detection:
    - Uses Path.suffix to extract extension
    - .json → Plain JSON (json.loads)
    - .zst → Compressed JSON (deserialize_json with compressed=True)
    - Other → InvalidExtensionError

Performance:
    - Plain JSON: Very fast (C-optimized json.loads)
    - Compressed JSON: Fast decompression (~400 MB/s) + parsing
    - File I/O: Depends on storage (SSD vs HDD)
    - Overhead: <1ms for small files (<10KB)

Why support compression:
    - Reduces storage usage (50-80% typical)
    - Faster network transfers
    - Especially beneficial for large JSON files (API responses, data exports)
    - Transparent to calling code (just specify correct extension)

Best practices:
    ```python
    # Use Path for type safety
    from pathlib import Path

    path = Path("/data/file.json.zst")
    data = load_json(path)

    # Validate data structure after loading
    data = load_json("config.json")
    required_keys = ["api_key", "endpoint", "timeout"]
    if not all(k in data for k in required_keys):
        raise ValueError(f"Config missing required keys: {required_keys}")

    # Handle optional files gracefully
    cache = load_json("cache.json", raise_exception=False) or {}
    ```

Limitations:
    - Extension must match content (no auto-detection of compression)
    - Loads entire file into memory (not suitable for very large files)
    - No streaming support
    - No schema validation (returns raw JSON structure)

Dependencies: json, zstandard (via deserialize_json)

Related modules: save_json (corresponding save operation), deserialize_json
(underlying deserialization), is_valid_extension (extension validation),
load_text (text file loading).
"""

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
