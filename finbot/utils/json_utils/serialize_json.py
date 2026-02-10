from __future__ import annotations

import json
from typing import Any

import zstandard as zstd


def serialize_json(data: dict[str, Any] | list, compress: bool = True, compression_level: int = 3) -> bytes:
    """
    Serialize a dictionary into JSON. Compress if required.

    Args:
        data: The dictionary or list to serialize.
        compress: Whether to compress the JSON. Defaults to True.
        compression_level: The level of compression to use. Defaults to 3.

    Returns:
        The serialized (and possibly compressed) JSON data.
    """
    json_str = json.dumps(data)
    if compress:
        compressor = zstd.ZstdCompressor(level=compression_level)
        return compressor.compress(json_str.encode("utf-8"))
    return json_str.encode("utf-8")
