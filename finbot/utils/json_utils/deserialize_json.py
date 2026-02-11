"""Deserialize JSON bytes to Python data structures with automatic decompression.

Converts JSON bytes (optionally zstd-compressed) back to Python dictionaries
or lists. Features intelligent automatic compression detection when compressed
parameter is None.

Typical usage:
    ```python
    from finbot.utils.json_utils.deserialize_json import deserialize_json

    # Automatic compression detection (recommended)
    data_bytes = b"..."  # Could be compressed or uncompressed
    result = deserialize_json(data_bytes)  # Automatically detects and handles

    # Explicit compression specification
    compressed_bytes = serialize_json({"key": "value"}, compress=True)
    result = deserialize_json(compressed_bytes, compressed=True)

    # Explicit uncompressed
    json_bytes = b'{"key": "value"}'
    result = deserialize_json(json_bytes, compressed=False)
    ```

Automatic compression detection (compressed=None):
    1. Attempts zstd decompression first
    2. If decompression fails, treats as uncompressed
    3. If JSON parsing fails, raises RuntimeError
    4. Transparent handling - no need to track compression state

Compression parameter:
    - None (default): Automatic detection (try decompress, fallback to plain)
    - True: Explicitly decompress (raises if not compressed)
    - False: Explicitly treat as uncompressed JSON

Features:
    - Automatic compression detection
    - Handles both dict and list JSON structures
    - UTF-8 decoding
    - Clear error messages for invalid data
    - Thread-safe (no shared state)

Error handling:
    - json.JSONDecodeError: Invalid JSON after decompression
    - RuntimeError: Cannot determine compression status (both attempts failed)
    - zstd.ZstdError: Decompression error (explicit compressed=True only)

Use cases:
    - Loading cached API responses (unknown compression state)
    - Reading serialized data from storage
    - Network data reception
    - Paired with serialize_json for round-trip processing

Example workflows:
    ```python
    # Round-trip with compression
    from finbot.utils.json_utils import serialize_json, deserialize_json

    original = {"prices": [100, 105, 110], "symbol": "SPY"}
    serialized = serialize_json(original, compress=True)
    recovered = deserialize_json(serialized)  # Auto-detects compression
    assert original == recovered


    # Safe loading (handles both compressed and uncompressed)
    def load_data(bytes_data):
        try:
            return deserialize_json(bytes_data)  # Works either way
        except RuntimeError as e:
            logger.error(f"Invalid data: {e}")
            return None
    ```

Performance:
    - Decompression: Fast (~400 MB/s)
    - JSON parsing: Very fast (C-optimized json.loads)
    - Auto-detection overhead: Minimal (single try/except)

Why automatic detection:
    - Simplifies calling code (no need to track compression)
    - Safe for mixed sources (some compressed, some not)
    - Graceful fallback behavior
    - No performance penalty for uncompressed data

Limitations:
    - Auto-detection tries decompression first (slight overhead for uncompressed)
    - Ambiguous data (valid zstd AND valid JSON) will decompress
    - Not suitable for streaming (requires complete bytes)

Dependencies: zstandard (zstd), json

Related modules: serialize_json (inverse operation), load_json (deserialize
from file), save_json (serialize and save to file).
"""

from __future__ import annotations

import json
from typing import Any

import zstandard as zstd


def deserialize_json(data: bytes, compressed: bool | None = None) -> dict[str, Any] | list[Any]:
    """
    Deserialize JSON data from a byte string. Automatically handles zstd decompression if needed.

    Args:
        data: The JSON data to deserialize.
        compressed: Optional; specifies if the data is compressed. If None, the function will attempt to detect zstd compression.

    Returns:
        The deserialized JSON data as a dictionary or a list.

    Raises:
        json.JSONDecodeError: If the data is not valid JSON.
        RuntimeError: If unable to determine if the data is compressed or not.
    """
    if compressed is None:
        try:
            # Attempt to decompress assuming the data is compressed
            decompressor = zstd.ZstdDecompressor()
            decompressed_data = decompressor.decompress(data)
            return json.loads(decompressed_data.decode("utf-8"))
        except (zstd.ZstdError, json.JSONDecodeError):
            # If decompression fails or resulting data is not valid JSON,
            # assume the data was not compressed
            try:
                return json.loads(data.decode("utf-8"))
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    "Unable to determine if the data is compressed or not.",
                ) from e
    elif compressed:
        # Explicitly handle compressed data
        decompressor = zstd.ZstdDecompressor()
        decompressed_data = decompressor.decompress(data)
        return json.loads(decompressed_data.decode("utf-8"))
    else:
        # Handle non-compressed data
        return json.loads(data.decode("utf-8"))
