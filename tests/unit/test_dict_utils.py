"""Comprehensive tests for finbot.utils.dict_utils.

Tests for dictionary hashing with different algorithms, order-independence,
and handling of special types.

Priority 7, Item P7.2: Increase test coverage to 60%+
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from finbot.utils.dict_utils.hash_dictionary import hash_dictionary


class TestHashDictionary:
    """Tests for hash_dictionary function."""

    def test_hash_simple_dict_md5(self):
        """Test hashing simple dictionary with MD5 (default)."""
        data = {"key": "value", "number": 42}
        result = hash_dictionary(data)

        assert isinstance(result, str)
        assert len(result) == 32  # MD5 produces 32-character hex

    def test_hash_simple_dict_sha256(self):
        """Test hashing with SHA256 algorithm."""
        data = {"key": "value", "number": 42}
        result = hash_dictionary(data, hash_algorithm="sha256")

        assert isinstance(result, str)
        assert len(result) == 64  # SHA256 produces 64-character hex

    def test_hash_simple_dict_sha512(self):
        """Test hashing with SHA512 algorithm."""
        data = {"key": "value"}
        result = hash_dictionary(data, hash_algorithm="sha512")

        assert isinstance(result, str)
        assert len(result) == 128  # SHA512 produces 128-character hex

    def test_hash_order_independence(self):
        """Test that hash is independent of key order."""
        dict1 = {"a": 1, "b": 2, "c": 3}
        dict2 = {"c": 3, "a": 1, "b": 2}
        dict3 = {"b": 2, "c": 3, "a": 1}

        hash1 = hash_dictionary(dict1)
        hash2 = hash_dictionary(dict2)
        hash3 = hash_dictionary(dict3)

        assert hash1 == hash2 == hash3

    def test_hash_deterministic(self):
        """Test that same dict produces same hash multiple times."""
        data = {"symbol": "SPY", "price": 450.25}
        hash1 = hash_dictionary(data)
        hash2 = hash_dictionary(data)
        hash3 = hash_dictionary(data)

        assert hash1 == hash2 == hash3

    def test_hash_different_content_different_hash(self):
        """Test that different content produces different hash."""
        dict1 = {"key": "value1"}
        dict2 = {"key": "value2"}

        hash1 = hash_dictionary(dict1)
        hash2 = hash_dictionary(dict2)

        assert hash1 != hash2

    def test_hash_nested_dict(self):
        """Test hashing of nested dictionary."""
        data = {
            "level1": {"level2": {"level3": "value"}, "array": [1, 2, 3]},
            "root": "value",
        }
        result = hash_dictionary(data)

        assert isinstance(result, str)
        assert len(result) == 32

    def test_hash_with_list_values(self):
        """Test hashing dict with list values."""
        data = {"prices": [100, 105, 110], "volumes": [1000, 2000, 3000]}
        result = hash_dictionary(data)

        assert isinstance(result, str)
        # Same structure, same hash
        result2 = hash_dictionary(data)
        assert result == result2

    def test_hash_with_null_values(self):
        """Test hashing dict with None values."""
        data = {"key1": "value", "key2": None, "key3": 42}
        result = hash_dictionary(data)

        assert isinstance(result, str)
        assert len(result) == 32

    def test_hash_with_boolean_values(self):
        """Test hashing dict with boolean values."""
        data = {"enabled": True, "disabled": False, "count": 0}
        result = hash_dictionary(data)

        assert isinstance(result, str)

    def test_hash_empty_dict(self):
        """Test hashing empty dictionary."""
        result = hash_dictionary({})

        assert isinstance(result, str)
        assert len(result) == 32

    def test_hash_with_datetime_objects(self):
        """Test hashing dict with datetime objects (uses default=str)."""
        data = {"timestamp": datetime(2026, 2, 17, 12, 0, 0), "value": 42}
        result = hash_dictionary(data)

        assert isinstance(result, str)
        assert len(result) == 32

    def test_hash_with_path_objects(self):
        """Test hashing dict with Path objects (uses default=str)."""
        data = {"file": Path("/data/prices.csv"), "size": 1024}
        result = hash_dictionary(data)

        assert isinstance(result, str)

    def test_hash_with_mixed_types(self):
        """Test hashing dict with mixed value types."""
        data = {
            "string": "value",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "null": None,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
        }
        result = hash_dictionary(data)

        assert isinstance(result, str)
        assert len(result) == 32

    def test_hash_consistency_different_algorithms(self):
        """Test that different algorithms produce different hashes."""
        data = {"key": "value"}

        md5_hash = hash_dictionary(data, hash_algorithm="md5")
        sha256_hash = hash_dictionary(data, hash_algorithm="sha256")

        assert md5_hash != sha256_hash
        assert len(md5_hash) == 32
        assert len(sha256_hash) == 64

    def test_hash_large_dict(self):
        """Test hashing large dictionary."""
        data = {f"key_{i}": f"value_{i}" for i in range(1000)}
        result = hash_dictionary(data)

        assert isinstance(result, str)
        assert len(result) == 32

    def test_hash_unicode_values(self):
        """Test hashing dict with unicode values."""
        data = {"emoji": "🎉", "chinese": "你好", "arabic": "مرحبا"}
        result = hash_dictionary(data)

        assert isinstance(result, str)

    def test_hash_special_characters(self):
        """Test hashing dict with special characters."""
        data = {
            "quotes": "double \" and single '",
            "newlines": "line1\nline2",
            "tabs": "col1\tcol2",
        }
        result = hash_dictionary(data)

        assert isinstance(result, str)

    def test_hash_numeric_precision(self):
        """Test that float precision affects hash."""
        dict1 = {"value": 1.0}
        dict2 = {"value": 1.0000000001}

        hash1 = hash_dictionary(dict1)
        hash2 = hash_dictionary(dict2)

        # Different floats should produce different hashes
        assert hash1 != hash2

    def test_hash_same_content_same_algorithm_same_hash(self):
        """Test consistency: same content + same algorithm = same hash."""
        data = {"symbol": "SPY", "price": 450.25, "volume": 1000000}

        # Hash 10 times
        hashes = [hash_dictionary(data) for _ in range(10)]

        # All should be identical
        assert len(set(hashes)) == 1


class TestHashDictionaryUseCases:
    """Tests for common use cases of hash_dictionary."""

    def test_use_case_cache_key(self):
        """Test using hash as cache key."""
        api_params = {"endpoint": "/prices", "symbol": "SPY", "days": 365}
        cache_key = hash_dictionary(api_params)

        # Simulate cache lookup
        assert isinstance(cache_key, str)
        assert len(cache_key) > 0

    def test_use_case_deduplication(self):
        """Test using hash for deduplication."""
        data_list = [
            {"symbol": "SPY", "price": 450},
            {"symbol": "QQQ", "price": 375},
            {"symbol": "SPY", "price": 450},  # Duplicate
            {"symbol": "TLT", "price": 95},
        ]

        seen_hashes = set()
        unique_count = 0

        for data_dict in data_list:
            hash_str = hash_dictionary(data_dict)
            if hash_str not in seen_hashes:
                seen_hashes.add(hash_str)
                unique_count += 1

        assert unique_count == 3  # 3 unique dicts (one duplicate)

    def test_use_case_change_detection(self):
        """Test using hash for change detection."""
        config_v1 = {"setting1": "value1", "setting2": 42}
        config_v2 = {"setting1": "value1", "setting2": 43}  # Changed

        hash_v1 = hash_dictionary(config_v1)
        hash_v2 = hash_dictionary(config_v2)

        assert hash_v1 != hash_v2  # Change detected

    def test_use_case_content_equality(self):
        """Test using hash to check content equality."""
        # Two dicts with same content but different order
        dict_a = {"z": 26, "a": 1, "m": 13}
        dict_b = {"a": 1, "m": 13, "z": 26}

        assert hash_dictionary(dict_a) == hash_dictionary(dict_b)

    def test_use_case_filename_generation(self):
        """Test using hash for auto-generated filenames."""
        data = {"symbol": "SPY", "date": "2026-02-17"}
        hash_str = hash_dictionary(data)
        filename = f"cache_{hash_str}.json"

        assert filename.startswith("cache_")
        assert filename.endswith(".json")
        assert len(filename) == 6 + 32 + 5  # "cache_" + hash + ".json" = 43
