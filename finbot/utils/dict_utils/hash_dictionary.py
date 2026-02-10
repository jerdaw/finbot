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
