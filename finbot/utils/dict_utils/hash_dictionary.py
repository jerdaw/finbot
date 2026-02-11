"""Generate consistent, deterministic hashes of Python dictionaries.

Creates hash strings from dictionaries using consistent key ordering and
JSON serialization. Useful for content-based cache keys, deduplication,
and change detection.

Typical usage:
    ```python
    from finbot.utils.dict_utils.hash_dictionary import hash_dictionary

    # Basic usage with MD5 (default)
    data = {"symbol": "SPY", "price": 450.25, "volume": 1000000}
    hash_str = hash_dictionary(data)
    # Result: "a1b2c3d4e5f6..."

    # Different algorithm
    hash_str = hash_dictionary(data, hash_algorithm="sha256")
    # Result: longer hash string

    # Same content → same hash (order-independent)
    dict1 = {"a": 1, "b": 2, "c": 3}
    dict2 = {"c": 3, "a": 1, "b": 2}
    assert hash_dictionary(dict1) == hash_dictionary(dict2)

    # Use for cache keys
    cache_key = hash_dictionary(api_params)
    if cache_key in cache:
        return cache[cache_key]
    ```

How it works:
    1. Serialize dict to JSON with sorted keys (json.dumps)
    2. Encode JSON string to bytes (UTF-8)
    3. Hash bytes using specified algorithm
    4. Return hexadecimal digest

Key ordering:
    - Uses json.dumps(sort_keys=True)
    - Ensures consistent hash for same content
    - Order-independent: {"a":1, "b":2} == {"b":2, "a":1}

Default parameter handling:
    - Uses default=str for non-serializable objects
    - Converts objects to string representation
    - Allows hashing of complex types (datetime, Path, etc.)

Supported hash algorithms:
    - "md5" (default): Fast, 32-character hex (128-bit)
    - "sha1": 40-character hex (160-bit)
    - "sha256": 64-character hex (256-bit)
    - "sha512": 128-character hex (512-bit)
    - Any algorithm supported by hashlib

Features:
    - Order-independent (sorted keys)
    - Deterministic (same dict → same hash)
    - Handles nested structures
    - Configurable algorithm
    - Graceful handling of non-JSON types (via default=str)

Use cases:
    - Content-based cache keys
    - Deduplication detection
    - Change tracking (compare hashes)
    - Auto-generated filenames (see save_json)
    - Data integrity verification

Example: Content-based caching:
    ```python
    def fetch_data(params):
        cache_key = hash_dictionary(params)
        cache_file = f"/cache/{cache_key}.json"

        if os.path.exists(cache_file):
            return load_json(cache_file)

        data = expensive_api_call(params)
        save_json(data, "/cache", f"{cache_key}.json")
        return data
    ```

Example: Change detection:
    ```python
    old_config = load_json("config.json")
    old_hash = hash_dictionary(old_config)

    # ... time passes ...

    new_config = load_json("config.json")
    new_hash = hash_dictionary(new_config)

    if old_hash != new_hash:
        print("Configuration changed, reloading...")
        reload_application()
    ```

Example: Deduplication:
    ```python
    seen_hashes = set()
    unique_dicts = []

    for data_dict in all_data:
        hash_str = hash_dictionary(data_dict)
        if hash_str not in seen_hashes:
            seen_hashes.add(hash_str)
            unique_dicts.append(data_dict)
    ```

Hash algorithm selection:
    - MD5: Fast, good for cache keys, not cryptographically secure
    - SHA256: Slower, cryptographically secure, good for integrity
    - SHA512: Slowest, highest security, overkill for most uses

Performance:
    - MD5: Very fast (~100 MB/s for JSON serialization bottleneck)
    - SHA256: Fast (~50 MB/s)
    - JSON serialization is the bottleneck (not hashing)
    - Overhead negligible for small dicts (<1ms)

Why MD5 default:
    - Fast enough for cache keys
    - Short hash strings (32 chars)
    - No security requirements for cache keys
    - Widely supported

Limitations:
    - Dict must be JSON-serializable (or have default=str fallback)
    - Float precision may cause hash mismatches
    - Large dicts incur serialization overhead
    - Not suitable for cryptographic purposes (use SHA256+)

Handling special types:
    ```python
    # Datetime objects
    from datetime import datetime

    data = {"timestamp": datetime.now()}
    hash_str = hash_dictionary(data)  # Converts datetime to string

    # Path objects
    from pathlib import Path

    data = {"file": Path("/data/file.csv")}
    hash_str = hash_dictionary(data)  # Converts Path to string


    # Custom objects (implement __str__)
    class MyObj:
        def __str__(self):
            return "my_obj_representation"


    data = {"obj": MyObj()}
    hash_str = hash_dictionary(data)  # Uses __str__()
    ```

Best practices:
    - Use MD5 for cache keys (fast, short)
    - Use SHA256 for integrity checking (secure)
    - Normalize floats if precision matters
    - Document hash algorithm choice
    - Test hash consistency across Python versions

Security note:
    MD5 is not cryptographically secure. Do not use for:
    - Password hashing
    - Digital signatures
    - Security-critical integrity checks
    Use SHA256 or SHA512 for security purposes.

Dependencies: hashlib (stdlib), json (stdlib)

Related modules: save_json (uses for auto-generated filenames), request_handler
(could use for cache keys).
"""

from __future__ import annotations

import hashlib
import json


def hash_dictionary(dct: dict, hash_algorithm: str = "md5") -> str:
    """
    Hash a Python dictionary in a memory and time-efficient manner.

    Args:
        dct: Dictionary to be hashed.
        hash_algorithm: Hash algorithm to use ('md5', 'sha256', etc.).

    Returns:
        str: The hash of the dictionary.
    """
    hasher = hashlib.new(hash_algorithm)
    # Create a consistently ordered string representation of the dictionary
    ordered_dct_str = json.dumps(
        dct,
        sort_keys=True,
        default=str,
    ).encode("utf-8")
    hasher.update(ordered_dct_str)
    return hasher.hexdigest()
