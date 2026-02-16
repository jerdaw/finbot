"""Unit tests for data snapshot registry."""

from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
import pytest

from finbot.core.contracts.snapshot import compute_data_content_hash, compute_snapshot_hash
from finbot.services.backtesting.snapshot_registry import DataSnapshotRegistry


@pytest.fixture
def temp_registry(tmp_path):
    """Create temporary snapshot registry."""
    return DataSnapshotRegistry(tmp_path / "snapshots")


@pytest.fixture
def sample_data():
    """Create sample market data."""
    dates = pd.date_range("2020-01-01", periods=10, freq="D")

    spy_data = pd.DataFrame(
        {
            "Open": [300.0 + i for i in range(10)],
            "High": [305.0 + i for i in range(10)],
            "Low": [295.0 + i for i in range(10)],
            "Close": [302.0 + i for i in range(10)],
            "Volume": [1000000 + i * 10000 for i in range(10)],
        },
        index=dates,
    )

    tlt_data = pd.DataFrame(
        {
            "Open": [140.0 + i * 0.5 for i in range(10)],
            "High": [142.0 + i * 0.5 for i in range(10)],
            "Low": [138.0 + i * 0.5 for i in range(10)],
            "Close": [141.0 + i * 0.5 for i in range(10)],
            "Volume": [500000 + i * 5000 for i in range(10)],
        },
        index=dates,
    )

    return {"SPY": spy_data, "TLT": tlt_data}


def test_registry_initialization(tmp_path):
    """Test registry initializes and creates directories."""
    registry_path = tmp_path / "snapshots"
    assert not registry_path.exists()

    registry = DataSnapshotRegistry(registry_path)

    assert registry.storage_dir == registry_path
    assert registry_path.exists()
    assert (registry_path / "metadata").exists()
    assert (registry_path / "data").exists()


def test_compute_snapshot_hash_deterministic(sample_data):
    """Test snapshot hash is deterministic for same data."""
    symbols = ["SPY", "TLT"]

    hash1 = compute_snapshot_hash(symbols, sample_data)
    hash2 = compute_snapshot_hash(symbols, sample_data)

    assert hash1 == hash2
    assert hash1.startswith("snap-")


def test_compute_snapshot_hash_different_for_different_data(sample_data):
    """Test snapshot hash changes when data changes."""
    symbols = ["SPY", "TLT"]

    hash1 = compute_snapshot_hash(symbols, sample_data)

    # Modify data
    modified_data = sample_data.copy()
    modified_data["SPY"]["Close"] = modified_data["SPY"]["Close"] * 1.01

    hash2 = compute_snapshot_hash(symbols, modified_data)

    assert hash1 != hash2


def test_compute_snapshot_hash_symbol_order_independent(sample_data):
    """Test snapshot hash is same regardless of symbol order."""
    hash1 = compute_snapshot_hash(["SPY", "TLT"], sample_data)
    hash2 = compute_snapshot_hash(["TLT", "SPY"], sample_data)

    assert hash1 == hash2


def test_create_snapshot(temp_registry, sample_data):
    """Test creating snapshot saves data and metadata."""
    symbols = ["SPY", "TLT"]
    start = datetime(2020, 1, 1, tzinfo=UTC)
    end = datetime(2020, 1, 10, tzinfo=UTC)

    snapshot = temp_registry.create_snapshot(symbols, sample_data, start, end)

    # Check snapshot metadata
    assert snapshot.snapshot_id.startswith("snap-")
    assert set(snapshot.symbols) == set(symbols)
    assert snapshot.start_date == start
    assert snapshot.end_date == end
    assert snapshot.total_rows == 20  # 10 rows per symbol
    assert "SPY" in snapshot.file_sizes
    assert "TLT" in snapshot.file_sizes

    # Check files exist
    assert temp_registry.snapshot_exists(snapshot.snapshot_id)
    data_dir = temp_registry.data_dir / snapshot.snapshot_id
    assert (data_dir / "SPY.parquet").exists()
    assert (data_dir / "TLT.parquet").exists()
    assert (temp_registry.metadata_dir / f"{snapshot.snapshot_id}.json").exists()


def test_create_snapshot_deduplication(temp_registry, sample_data):
    """Test creating identical snapshots returns same snapshot ID."""
    symbols = ["SPY", "TLT"]
    start = datetime(2020, 1, 1, tzinfo=UTC)
    end = datetime(2020, 1, 10, tzinfo=UTC)

    snapshot1 = temp_registry.create_snapshot(symbols, sample_data, start, end)
    snapshot2 = temp_registry.create_snapshot(symbols, sample_data, start, end)

    # Should have same ID (deduplication)
    assert snapshot1.snapshot_id == snapshot2.snapshot_id

    # Should only have one set of files
    assert temp_registry.count() == 1


def test_create_snapshot_empty_symbols(temp_registry, sample_data):
    """Test creating snapshot with empty symbols raises error."""
    with pytest.raises(ValueError, match="Symbols list cannot be empty"):
        temp_registry.create_snapshot([], sample_data, datetime.now(UTC), datetime.now(UTC))


def test_create_snapshot_missing_data(temp_registry, sample_data):
    """Test creating snapshot with missing data raises error."""
    symbols = ["SPY", "TLT", "QQQ"]  # QQQ not in sample_data

    with pytest.raises(ValueError, match="Data missing for symbols"):
        temp_registry.create_snapshot(symbols, sample_data, datetime.now(UTC), datetime.now(UTC))


def test_load_snapshot(temp_registry, sample_data):
    """Test loading snapshot returns correct data."""
    symbols = ["SPY", "TLT"]
    start = datetime(2020, 1, 1, tzinfo=UTC)
    end = datetime(2020, 1, 10, tzinfo=UTC)

    # Create snapshot
    snapshot = temp_registry.create_snapshot(symbols, sample_data, start, end)

    # Load it back
    loaded_data = temp_registry.load_snapshot(snapshot.snapshot_id)

    # Verify data matches (check_freq=False because parquet doesn't preserve freq)
    assert set(loaded_data.keys()) == set(symbols)
    pd.testing.assert_frame_equal(loaded_data["SPY"], sample_data["SPY"], check_freq=False)
    pd.testing.assert_frame_equal(loaded_data["TLT"], sample_data["TLT"], check_freq=False)


def test_load_nonexistent_snapshot(temp_registry):
    """Test loading nonexistent snapshot raises error."""
    with pytest.raises(FileNotFoundError, match="not found in registry"):
        temp_registry.load_snapshot("snap-nonexistent")


def test_get_metadata(temp_registry, sample_data):
    """Test getting metadata without loading data."""
    symbols = ["SPY", "TLT"]
    start = datetime(2020, 1, 1, tzinfo=UTC)
    end = datetime(2020, 1, 10, tzinfo=UTC)

    # Create snapshot
    original = temp_registry.create_snapshot(symbols, sample_data, start, end)

    # Get metadata
    metadata = temp_registry.get_metadata(original.snapshot_id)

    # Verify metadata matches
    assert metadata.snapshot_id == original.snapshot_id
    assert metadata.symbols == original.symbols
    assert metadata.start_date == original.start_date
    assert metadata.end_date == original.end_date
    assert metadata.data_hash == original.data_hash


def test_list_snapshots_empty(temp_registry):
    """Test listing snapshots when registry is empty."""
    snapshots = temp_registry.list_snapshots()
    assert snapshots == []


def test_list_snapshots_returns_all(temp_registry, sample_data):
    """Test listing snapshots returns all snapshots."""
    # Create multiple snapshots
    for i in range(3):
        symbols = ["SPY"]
        start = datetime(2020, 1, 1 + i, tzinfo=UTC)
        end = datetime(2020, 1, 10 + i, tzinfo=UTC)

        # Modify data slightly to get different hashes
        modified_data = {"SPY": sample_data["SPY"] * (1 + i * 0.01)}
        temp_registry.create_snapshot(symbols, modified_data, start, end)

    snapshots = temp_registry.list_snapshots()
    assert len(snapshots) == 3


def test_list_snapshots_filter_by_symbols(temp_registry, sample_data):
    """Test filtering snapshots by symbols."""
    # Create snapshots with different symbols
    temp_registry.create_snapshot(
        ["SPY"],
        {"SPY": sample_data["SPY"]},
        datetime(2020, 1, 1, tzinfo=UTC),
        datetime(2020, 1, 10, tzinfo=UTC),
    )
    temp_registry.create_snapshot(
        ["SPY", "TLT"],
        sample_data,
        datetime(2020, 1, 1, tzinfo=UTC),
        datetime(2020, 1, 10, tzinfo=UTC),
    )

    # Filter by SPY only - should return both
    spy_snapshots = temp_registry.list_snapshots(symbols=["SPY"])
    assert len(spy_snapshots) == 2

    # Filter by SPY and TLT - should return only the one with both
    both_snapshots = temp_registry.list_snapshots(symbols=["SPY", "TLT"])
    assert len(both_snapshots) == 1
    assert set(both_snapshots[0].symbols) == {"SPY", "TLT"}


def test_list_snapshots_filter_by_date(temp_registry, sample_data):
    """Test filtering snapshots by creation date."""
    # Create snapshots at different times
    early = datetime(2020, 1, 1, tzinfo=UTC)

    # Create one snapshot
    snap1 = temp_registry.create_snapshot(
        ["SPY"],
        {"SPY": sample_data["SPY"]},
        datetime(2020, 1, 1, tzinfo=UTC),
        datetime(2020, 1, 10, tzinfo=UTC),
    )

    # Modify data to get different snapshot
    modified_data = {"SPY": sample_data["SPY"] * 1.01}
    temp_registry.create_snapshot(
        ["SPY"],
        modified_data,
        datetime(2020, 2, 1, tzinfo=UTC),
        datetime(2020, 2, 10, tzinfo=UTC),
    )

    # Filter by date - get all created after early time
    all_snapshots = temp_registry.list_snapshots(since=early)
    assert len(all_snapshots) == 2

    # Filter to only recent ones
    recent = temp_registry.list_snapshots(since=snap1.created_at)
    assert len(recent) >= 1  # At least snap1, possibly snap2 depending on timing


def test_list_snapshots_with_limit(temp_registry, sample_data):
    """Test limiting number of results."""
    # Create 5 snapshots
    for i in range(5):
        modified_data = {"SPY": sample_data["SPY"] * (1 + i * 0.01)}
        temp_registry.create_snapshot(
            ["SPY"],
            modified_data,
            datetime(2020, 1, 1, tzinfo=UTC),
            datetime(2020, 1, 10, tzinfo=UTC),
        )

    # Limit to 3
    snapshots = temp_registry.list_snapshots(limit=3)
    assert len(snapshots) == 3


def test_delete_snapshot(temp_registry, sample_data):
    """Test deleting snapshot removes files."""
    symbols = ["SPY", "TLT"]
    snapshot = temp_registry.create_snapshot(
        symbols,
        sample_data,
        datetime(2020, 1, 1, tzinfo=UTC),
        datetime(2020, 1, 10, tzinfo=UTC),
    )

    assert temp_registry.count() == 1
    assert temp_registry.snapshot_exists(snapshot.snapshot_id)

    # Delete
    temp_registry.delete_snapshot(snapshot.snapshot_id)

    assert temp_registry.count() == 0
    assert not temp_registry.snapshot_exists(snapshot.snapshot_id)

    # Should not be loadable
    with pytest.raises(FileNotFoundError):
        temp_registry.load_snapshot(snapshot.snapshot_id)


def test_delete_nonexistent_snapshot(temp_registry):
    """Test deleting nonexistent snapshot raises error."""
    with pytest.raises(FileNotFoundError, match="not found in registry"):
        temp_registry.delete_snapshot("snap-nonexistent")


def test_count(temp_registry, sample_data):
    """Test counting snapshots."""
    assert temp_registry.count() == 0

    # Add some snapshots
    for i in range(3):
        modified_data = {"SPY": sample_data["SPY"] * (1 + i * 0.01)}
        temp_registry.create_snapshot(
            ["SPY"],
            modified_data,
            datetime(2020, 1, 1, tzinfo=UTC),
            datetime(2020, 1, 10, tzinfo=UTC),
        )

    assert temp_registry.count() == 3


def test_snapshot_exists(temp_registry, sample_data):
    """Test checking if snapshot exists."""
    assert not temp_registry.snapshot_exists("snap-nonexistent")

    snapshot = temp_registry.create_snapshot(
        ["SPY"],
        {"SPY": sample_data["SPY"]},
        datetime(2020, 1, 1, tzinfo=UTC),
        datetime(2020, 1, 10, tzinfo=UTC),
    )

    assert temp_registry.snapshot_exists(snapshot.snapshot_id)


def test_data_content_hash():
    """Test data content hash computation."""
    dates = pd.date_range("2020-01-01", periods=5, freq="D")

    data1 = {
        "SPY": pd.DataFrame({"Close": [100, 101, 102, 103, 104]}, index=dates),
    }

    data2 = {
        "SPY": pd.DataFrame({"Close": [100, 101, 102, 103, 104]}, index=dates),
    }

    data3 = {
        "SPY": pd.DataFrame({"Close": [100, 101, 102, 103, 105]}, index=dates),  # Different
    }

    # Same data should have same hash
    hash1 = compute_data_content_hash(data1)
    hash2 = compute_data_content_hash(data2)
    assert hash1 == hash2

    # Different data should have different hash
    hash3 = compute_data_content_hash(data3)
    assert hash1 != hash3
