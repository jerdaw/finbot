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
