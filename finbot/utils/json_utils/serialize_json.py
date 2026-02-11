"""Serialize Python data structures to JSON bytes with optional compression.

Converts dictionaries and lists to JSON format as bytes, with optional zstandard
compression for efficient storage and transmission. Part of the json_utils suite
for structured data handling.

Typical usage:
    ```python
    from finbot.utils.json_utils.serialize_json import serialize_json

    # Serialize with compression (default)
    data = {"symbol": "SPY", "price": 450.25, "volume": 1000000}
    compressed_bytes = serialize_json(data)
    # Result: zstd-compressed JSON bytes

    # Serialize without compression
    uncompressed_bytes = serialize_json(data, compress=False)
    # Result: UTF-8 encoded JSON bytes

    # Custom compression level (higher = more compression, slower)
    highly_compressed = serialize_json(data, compression_level=9)
    ```

Compression:
    - Uses zstandard (zstd) compression algorithm
    - Default compression level: 3 (balanced)
    - Compression levels: 1 (fast) to 22 (maximum)
    - Typical compression ratio: 50-80% size reduction

Compression levels:
    - Level 1: Fastest, ~40% reduction
    - Level 3: Default, ~50-60% reduction (recommended)
    - Level 9: High compression, ~70-80% reduction
    - Level 22: Maximum, ~80-85% reduction (very slow)

Features:
    - Accepts dict or list as input
    - Returns bytes (ready for file/network I/O)
    - Automatic UTF-8 encoding
    - Optional compression with configurable level
    - Deterministic output (same data → same bytes)

Use cases:
    - Serializing API responses for caching
    - Preparing data for network transmission
    - Storing structured data in binary format
    - Reducing storage size for large JSON objects
    - Paired with deserialize_json for round-trip serialization

Round-trip example:
    ```python
    from finbot.utils.json_utils import serialize_json, deserialize_json

    original = {"a": 1, "b": [2, 3, 4], "c": {"nested": True}}
    serialized = serialize_json(original, compress=True)
    deserialized = deserialize_json(serialized, compressed=True)
    assert original == deserialized
    ```

Performance:
    - Serialization: Very fast (pure Python json.dumps)
    - Compression: Fast (~400 MB/s for level 3)
    - Combined overhead: Typically <1ms for small objects (<10KB)

Why zstandard:
    - Faster than gzip with better compression
    - Industry standard (used by Facebook, Linux kernel, HTTP/2)
    - Excellent for repetitive JSON (API responses, config files)

Dependencies: zstandard (zstd)

Related modules: deserialize_json (inverse operation), save_json (serialize
and save to file), request_handler (uses for response caching).
"""

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
