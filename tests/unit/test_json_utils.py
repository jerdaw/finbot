"""Comprehensive tests for finbot.utils.json_utils.

Tests for JSON serialization, deserialization, loading, and saving with and
without compression. Covers round-trip compatibility, error handling, and
edge cases.

Priority 7, Item P7.2: Increase test coverage to 60%+
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from finbot.exceptions import InvalidExtensionError
from finbot.utils.json_utils.deserialize_json import deserialize_json
from finbot.utils.json_utils.load_json import load_json
from finbot.utils.json_utils.save_json import save_json
from finbot.utils.json_utils.serialize_json import serialize_json


class TestSerializeJson:
    """Tests for serialize_json function."""

    def test_serialize_dict_uncompressed(self):
        """Test serializing dictionary without compression."""
        data = {"key": "value", "number": 42}
        result = serialize_json(data, compress=False)

        assert isinstance(result, bytes)
        assert result == json.dumps(data).encode("utf-8")

    def test_serialize_dict_compressed(self):
        """Test serializing dictionary with compression."""
        data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        result = serialize_json(data, compress=True)

        assert isinstance(result, bytes)
        # Compressed should be different from uncompressed
        uncompressed = json.dumps(data).encode("utf-8")
        assert result != uncompressed

    def test_serialize_list_uncompressed(self):
        """Test serializing list without compression."""
        data = [1, 2, 3, "four", {"five": 5}]
        result = serialize_json(data, compress=False)

        assert isinstance(result, bytes)
        assert result == json.dumps(data).encode("utf-8")

    def test_serialize_list_compressed(self):
        """Test serializing list with compression."""
        data = [1, 2, 3, "four", {"five": 5}]
        result = serialize_json(data, compress=True)

        assert isinstance(result, bytes)
        # Should be compressed
        uncompressed = json.dumps(data).encode("utf-8")
        assert result != uncompressed

    def test_serialize_compression_levels(self):
        """Test different compression levels."""
        data = {"key": "value" * 100}  # Repetitive data compresses well

        level1 = serialize_json(data, compress=True, compression_level=1)
        level3 = serialize_json(data, compress=True, compression_level=3)
        level9 = serialize_json(data, compress=True, compression_level=9)

        # All should be bytes
        assert all(isinstance(x, bytes) for x in [level1, level3, level9])

        # Higher levels should compress more (generally)
        # Note: Very small data might not follow this pattern
        assert len(level9) <= len(level1)

    def test_serialize_empty_dict(self):
        """Test serializing empty dictionary."""
        result = serialize_json({}, compress=False)
        assert result == b"{}"

    def test_serialize_empty_list(self):
        """Test serializing empty list."""
        result = serialize_json([], compress=False)
        assert result == b"[]"


class TestDeserializeJson:
    """Tests for deserialize_json function."""

    def test_deserialize_uncompressed_dict(self):
        """Test deserializing uncompressed dictionary."""
        data = {"key": "value", "number": 42}
        serialized = json.dumps(data).encode("utf-8")
        result = deserialize_json(serialized, compressed=False)

        assert result == data

    def test_deserialize_compressed_dict(self):
        """Test deserializing compressed dictionary."""
        data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        serialized = serialize_json(data, compress=True)
        result = deserialize_json(serialized, compressed=True)

        assert result == data

    def test_deserialize_auto_detect_compressed(self):
        """Test automatic detection of compressed data."""
        data = {"key": "value", "auto": "detect"}
        serialized = serialize_json(data, compress=True)
        result = deserialize_json(serialized)  # compressed=None (auto-detect)

        assert result == data

    def test_deserialize_auto_detect_uncompressed(self):
        """Test automatic detection of uncompressed data."""
        data = {"key": "value", "auto": "detect"}
        serialized = json.dumps(data).encode("utf-8")
        result = deserialize_json(serialized)  # compressed=None (auto-detect)

        assert result == data

    def test_deserialize_list_compressed(self):
        """Test deserializing compressed list."""
        data = [1, 2, 3, "four", {"five": 5}]
        serialized = serialize_json(data, compress=True)
        result = deserialize_json(serialized, compressed=True)

        assert result == data

    def test_deserialize_invalid_json_raises(self):
        """Test that invalid JSON raises RuntimeError."""
        invalid_data = b"not valid json"
        with pytest.raises(RuntimeError, match="Unable to determine"):
            deserialize_json(invalid_data)

    def test_round_trip_compressed(self):
        """Test round-trip serialize → deserialize with compression."""
        original = {"a": 1, "b": [2, 3, 4], "c": {"nested": True}}
        serialized = serialize_json(original, compress=True)
        recovered = deserialize_json(serialized, compressed=True)

        assert original == recovered

    def test_round_trip_uncompressed(self):
        """Test round-trip serialize → deserialize without compression."""
        original = {"a": 1, "b": [2, 3, 4], "c": {"nested": True}}
        serialized = serialize_json(original, compress=False)
        recovered = deserialize_json(serialized, compressed=False)

        assert original == recovered


class TestSaveJson:
    """Tests for save_json function."""

    def test_save_dict_uncompressed(self, tmp_path):
        """Test saving dictionary without compression."""
        data = {"key": "value", "number": 42}
        result_path = save_json(data, tmp_path, "test.json", compress=False)

        assert result_path.exists()
        assert result_path.suffix == ".json"
        with open(result_path, encoding="utf-8") as f:
            loaded = json.load(f)
        assert loaded == data

    def test_save_dict_compressed(self, tmp_path):
        """Test saving dictionary with compression."""
        data = {"key": "value", "number": 42}
        result_path = save_json(data, tmp_path, "test.json.zst", compress=True)

        assert result_path.exists()
        assert result_path.suffix == ".zst"
        # Verify file exists and is non-empty (small data may not compress smaller due to overhead)
        assert result_path.stat().st_size > 0

    def test_save_auto_filename_compressed(self, tmp_path):
        """Test auto-generated filename with compression."""
        data = {"auto": "filename", "test": True}
        result_path = save_json(data, tmp_path)  # compress=True by default

        assert result_path.exists()
        assert result_path.suffix == ".zst"
        # Filename should contain timestamp and hash
        assert "_" in result_path.stem
        assert len(result_path.stem) > 20  # timestamp_hash format

    def test_save_auto_filename_uncompressed(self, tmp_path):
        """Test auto-generated filename without compression."""
        data = {"auto": "filename", "test": True}
        result_path = save_json(data, tmp_path, compress=False)

        assert result_path.exists()
        assert result_path.suffix == ".json"
        assert "_" in result_path.stem

    def test_save_list_compressed(self, tmp_path):
        """Test saving list with compression."""
        data = [1, 2, 3, "four", {"five": 5}]
        result_path = save_json(data, tmp_path, "list.json.zst", compress=True)

        assert result_path.exists()
        loaded = load_json(result_path)
        assert loaded == data

    def test_save_creates_nested_directories(self, tmp_path):
        """Test that save creates parent directories."""
        # Create the base directory first (save_json checks dir exists)
        nested_dir = tmp_path / "nested" / "path"
        nested_dir.mkdir(parents=True, exist_ok=True)
        data = {"nested": True}
        # File path has additional nesting beyond save_dir
        result_path = save_json(data, nested_dir, "subdir/test.json", compress=False)

        assert result_path.exists()
        assert "subdir" in str(result_path)

    def test_save_dir_not_exists_raises(self):
        """Test that non-existent save_dir raises FileNotFoundError."""
        non_existent = Path("/nonexistent/directory")
        data = {"test": True}
        with pytest.raises(FileNotFoundError, match="does not exist"):
            save_json(data, non_existent, "test.json")

    def test_save_wrong_extension_compressed_raises(self, tmp_path):
        """Test that .json extension with compress=True raises error."""
        data = {"test": True}
        with pytest.raises(InvalidExtensionError, match=r"\.json\.zst"):
            save_json(data, tmp_path, "test.json", compress=True)

    def test_save_wrong_extension_uncompressed_raises(self, tmp_path):
        """Test that .json.zst extension with compress=False raises error."""
        data = {"test": True}
        with pytest.raises(InvalidExtensionError, match=r"must end with \.json"):
            save_json(data, tmp_path, "test.json.zst", compress=False)

    def test_save_compression_levels(self, tmp_path):
        """Test different compression levels."""
        data = {"key": "value" * 100}  # Repetitive data

        path1 = save_json(data, tmp_path, "level1.json.zst", compress=True, compression_level=1)
        path9 = save_json(data, tmp_path, "level9.json.zst", compress=True, compression_level=9)

        # Higher compression level should result in smaller file
        assert path9.stat().st_size <= path1.stat().st_size


class TestLoadJson:
    """Tests for load_json function."""

    def test_load_uncompressed_dict(self, tmp_path):
        """Test loading uncompressed JSON dictionary."""
        data = {"key": "value", "number": 42}
        file_path = tmp_path / "test.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        loaded = load_json(file_path)
        assert loaded == data

    def test_load_compressed_dict(self, tmp_path):
        """Test loading compressed JSON dictionary."""
        data = {"key": "value", "number": 42}
        file_path = save_json(data, tmp_path, "test.json.zst", compress=True)

        loaded = load_json(file_path)
        assert loaded == data

    def test_load_list(self, tmp_path):
        """Test loading JSON list."""
        data = [1, 2, 3, "four", {"five": 5}]
        file_path = tmp_path / "test.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        loaded = load_json(file_path)
        assert loaded == data

    def test_load_file_not_found_raises(self, tmp_path):
        """Test that loading non-existent file raises FileNotFoundError."""
        non_existent = tmp_path / "nonexistent.json"
        with pytest.raises(FileNotFoundError):
            load_json(non_existent)

    def test_load_file_not_found_no_raise(self, tmp_path):
        """Test that raise_exception=False returns empty dict."""
        non_existent = tmp_path / "nonexistent.json"
        result = load_json(non_existent, raise_exception=False)

        assert result == {}

    def test_load_invalid_extension_raises(self, tmp_path):
        """Test that invalid extension raises InvalidExtensionError."""
        bad_path = tmp_path / "test.txt"
        bad_path.touch()
        with pytest.raises(InvalidExtensionError, match=r"\.json or \.zst"):
            load_json(bad_path)

    def test_load_invalid_json_raises(self, tmp_path):
        """Test that invalid JSON content raises JSONDecodeError."""
        bad_file = tmp_path / "bad.json"
        with open(bad_file, "w", encoding="utf-8") as f:
            f.write("not valid json")

        with pytest.raises(json.JSONDecodeError):
            load_json(bad_file)


class TestRoundTrip:
    """Tests for round-trip save → load compatibility."""

    def test_round_trip_dict_compressed(self, tmp_path):
        """Test round-trip save → load with compression."""
        original = {"a": 1, "b": [2, 3, 4], "c": {"nested": True}}
        path = save_json(original, tmp_path, "test.json.zst", compress=True)
        loaded = load_json(path)

        assert loaded == original

    def test_round_trip_dict_uncompressed(self, tmp_path):
        """Test round-trip save → load without compression."""
        original = {"a": 1, "b": [2, 3, 4], "c": {"nested": True}}
        path = save_json(original, tmp_path, "test.json", compress=False)
        loaded = load_json(path)

        assert loaded == original

    def test_round_trip_list_compressed(self, tmp_path):
        """Test round-trip save → load list with compression."""
        original = [1, "two", {"three": 3}, [4, 5]]
        path = save_json(original, tmp_path, "test.json.zst", compress=True)
        loaded = load_json(path)

        assert loaded == original

    def test_round_trip_list_uncompressed(self, tmp_path):
        """Test round-trip save → load list without compression."""
        original = [1, "two", {"three": 3}, [4, 5]]
        path = save_json(original, tmp_path, "test.json", compress=False)
        loaded = load_json(path)

        assert loaded == original

    def test_round_trip_complex_nested_structure(self, tmp_path):
        """Test round-trip with deeply nested structure."""
        original = {
            "level1": {
                "level2": {
                    "level3": {
                        "data": [1, 2, 3],
                        "metadata": {"created": "2026-02-17", "version": "1.0"},
                    }
                },
                "array": [{"id": 1}, {"id": 2}],
            },
            "root_level": "value",
        }
        path = save_json(original, tmp_path, "nested.json.zst", compress=True)
        loaded = load_json(path)

        assert loaded == original

    def test_round_trip_auto_filename(self, tmp_path):
        """Test round-trip with auto-generated filename."""
        original = {"auto": "filename", "test": True}
        path = save_json(original, tmp_path)  # Auto filename, compressed
        loaded = load_json(path)

        assert loaded == original


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_empty_dict(self, tmp_path):
        """Test handling empty dictionary."""
        data = {}
        path = save_json(data, tmp_path, "empty.json", compress=False)
        loaded = load_json(path)

        assert loaded == data

    def test_empty_list(self, tmp_path):
        """Test handling empty list."""
        data = []
        path = save_json(data, tmp_path, "empty.json", compress=False)
        loaded = load_json(path)

        assert loaded == data

    def test_large_data_structure(self, tmp_path):
        """Test handling large data structure."""
        # 1000 items with nested structures
        data = {f"key_{i}": {"value": i, "nested": [i, i * 2, i * 3]} for i in range(1000)}
        path = save_json(data, tmp_path, "large.json.zst", compress=True)
        loaded = load_json(path)

        assert loaded == data
        assert len(loaded) == 1000

    def test_unicode_handling(self, tmp_path):
        """Test handling of unicode characters."""
        data = {"emoji": "🎉", "chinese": "你好", "arabic": "مرحبا"}
        path = save_json(data, tmp_path, "unicode.json", compress=False)
        loaded = load_json(path)

        assert loaded == data

    def test_special_characters(self, tmp_path):
        """Test handling of special characters."""
        data = {
            "quotes": "double \" and single '",
            "newlines": "line1\nline2",
            "tabs": "col1\tcol2",
        }
        path = save_json(data, tmp_path, "special.json", compress=False)
        loaded = load_json(path)

        assert loaded == data

    def test_numeric_edge_cases(self, tmp_path):
        """Test handling of numeric edge cases."""
        data = {
            "zero": 0,
            "negative": -42,
            "float": 3.14159,
            "scientific": 1.23e-10,
            "large": 999999999999,
        }
        path = save_json(data, tmp_path, "numbers.json", compress=False)
        loaded = load_json(path)

        assert loaded == data

    def test_boolean_and_null(self, tmp_path):
        """Test handling of boolean and null values."""
        data = {"true_val": True, "false_val": False, "null_val": None}
        path = save_json(data, tmp_path, "boolnull.json", compress=False)
        loaded = load_json(path)

        assert loaded == data
