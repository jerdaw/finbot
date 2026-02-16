"""Data snapshot registry for reproducible backtesting."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from finbot.core.contracts.snapshot import DataSnapshot, compute_data_content_hash, compute_snapshot_hash


class DataSnapshotRegistry:
    """File-based registry for market data snapshots.

    Stores immutable snapshots of market data to enable exact reproducibility
    of backtest runs. Uses content-addressable storage for automatic deduplication.

    Storage structure:
        snapshots/
        ├── metadata/
        │   ├── snap-abc123.json  # Snapshot metadata
        │   └── snap-def456.json
        └── data/
            ├── snap-abc123/
            │   ├── SPY.parquet
            │   └── TLT.parquet
            └── snap-def456/
                └── QQQ.parquet

    Attributes:
        storage_dir: Root directory for snapshot storage
        metadata_dir: Directory for snapshot metadata files
        data_dir: Directory for snapshot data files
    """

    def __init__(self, storage_dir: Path | str):
        """Initialize snapshot registry.

        Args:
            storage_dir: Directory to store snapshots
        """
        self.storage_dir = Path(storage_dir)
        self.metadata_dir = self.storage_dir / "metadata"
        self.data_dir = self.storage_dir / "data"

        # Create directories
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def create_snapshot(
        self,
        symbols: list[str],
        data: dict[str, pd.DataFrame],
        start: datetime,
        end: datetime,
    ) -> DataSnapshot:
        """Create and store a new snapshot.

        If a snapshot with identical content already exists (same hash),
        returns the existing snapshot without creating a duplicate.

        Args:
            symbols: List of ticker symbols
            data: Dictionary mapping symbol to DataFrame
            start: Start date of data range
            end: End date of data range

        Returns:
            DataSnapshot metadata object

        Raises:
            ValueError: If symbols list is empty or data is missing symbols
        """
        if not symbols:
            raise ValueError("Symbols list cannot be empty")

        # Validate data contains all symbols
        missing = set(symbols) - set(data.keys())
        if missing:
            raise ValueError(f"Data missing for symbols: {missing}")

        # Compute content-addressable hash
        snapshot_id = compute_snapshot_hash(symbols, data)

        # Check if snapshot already exists (deduplication)
        if self.snapshot_exists(snapshot_id):
            return self.get_metadata(snapshot_id)

        # Create snapshot directory
        snapshot_data_dir = self.data_dir / snapshot_id
        snapshot_data_dir.mkdir(parents=True, exist_ok=True)

        # Save data files
        file_sizes: dict[str, int] = {}
        total_rows = 0

        for symbol in symbols:
            df = data[symbol]
            filepath = snapshot_data_dir / f"{symbol}.parquet"
            df.to_parquet(filepath, compression="snappy")

            file_sizes[symbol] = filepath.stat().st_size
            total_rows += len(df)

        # Compute data content hash for verification
        data_hash = compute_data_content_hash(data)

        # Create metadata
        snapshot = DataSnapshot(
            snapshot_id=snapshot_id,
            symbols=tuple(sorted(symbols)),
            start_date=start,
            end_date=end,
            created_at=datetime.now(UTC),
            data_hash=data_hash,
            file_sizes=file_sizes,
            total_rows=total_rows,
        )

        # Save metadata
        metadata_path = self.metadata_dir / f"{snapshot_id}.json"
        with metadata_path.open("w") as f:
            json.dump(self._snapshot_to_dict(snapshot), f, indent=2)

        return snapshot

    def load_snapshot(self, snapshot_id: str) -> dict[str, pd.DataFrame]:
        """Load data from snapshot.

        Args:
            snapshot_id: Snapshot identifier

        Returns:
            Dictionary mapping symbol to DataFrame

        Raises:
            FileNotFoundError: If snapshot not found
        """
        if not self.snapshot_exists(snapshot_id):
            raise FileNotFoundError(f"Snapshot {snapshot_id} not found in registry")

        # Get metadata to know which symbols to load
        metadata = self.get_metadata(snapshot_id)

        # Load data files
        snapshot_data_dir = self.data_dir / snapshot_id
        data: dict[str, pd.DataFrame] = {}

        for symbol in metadata.symbols:
            filepath = snapshot_data_dir / f"{symbol}.parquet"
            data[symbol] = pd.read_parquet(filepath)

        return data

    def get_metadata(self, snapshot_id: str) -> DataSnapshot:
        """Get snapshot metadata without loading data.

        Args:
            snapshot_id: Snapshot identifier

        Returns:
            DataSnapshot metadata object

        Raises:
            FileNotFoundError: If snapshot not found
        """
        metadata_path = self.metadata_dir / f"{snapshot_id}.json"

        if not metadata_path.exists():
            raise FileNotFoundError(f"Snapshot {snapshot_id} not found in registry")

        with metadata_path.open("r") as f:
            payload = json.load(f)

        return self._snapshot_from_dict(payload)

    def list_snapshots(
        self,
        symbols: list[str] | None = None,
        since: datetime | None = None,
        limit: int | None = None,
    ) -> list[DataSnapshot]:
        """List snapshots matching criteria.

        Args:
            symbols: Filter by symbols (matches if snapshot contains all these symbols)
            since: Filter to snapshots created on or after this date
            limit: Maximum number of results to return

        Returns:
            List of matching snapshot metadata, sorted by created_at descending
        """
        # Collect all metadata files
        metadata_files = sorted(self.metadata_dir.glob("snap-*.json"), reverse=True)

        snapshots: list[DataSnapshot] = []

        for metadata_path in metadata_files:
            try:
                with metadata_path.open("r") as f:
                    payload = json.load(f)

                snapshot = self._snapshot_from_dict(payload)

                # Apply filters
                if since and snapshot.created_at < since:
                    continue

                # Check if snapshot contains all requested symbols
                if symbols and not all(sym in snapshot.symbols for sym in symbols):
                    continue

                snapshots.append(snapshot)

                # Check limit
                if limit and len(snapshots) >= limit:
                    break

            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip malformed files
                continue

        return snapshots

    def delete_snapshot(self, snapshot_id: str) -> None:
        """Delete snapshot and its data files.

        Args:
            snapshot_id: Snapshot identifier

        Raises:
            FileNotFoundError: If snapshot not found
        """
        if not self.snapshot_exists(snapshot_id):
            raise FileNotFoundError(f"Snapshot {snapshot_id} not found in registry")

        # Delete data directory
        snapshot_data_dir = self.data_dir / snapshot_id
        if snapshot_data_dir.exists():
            for file in snapshot_data_dir.glob("*.parquet"):
                file.unlink()
            snapshot_data_dir.rmdir()

        # Delete metadata file
        metadata_path = self.metadata_dir / f"{snapshot_id}.json"
        if metadata_path.exists():
            metadata_path.unlink()

    def snapshot_exists(self, snapshot_id: str) -> bool:
        """Check if snapshot exists.

        Args:
            snapshot_id: Snapshot identifier

        Returns:
            True if snapshot exists, False otherwise
        """
        metadata_path = self.metadata_dir / f"{snapshot_id}.json"
        return metadata_path.exists()

    def count(self) -> int:
        """Count total number of snapshots in registry.

        Returns:
            Total number of snapshots
        """
        return len(list(self.metadata_dir.glob("snap-*.json")))

    def _snapshot_to_dict(self, snapshot: DataSnapshot) -> dict:
        """Convert DataSnapshot to JSON-serializable dict.

        Args:
            snapshot: DataSnapshot object

        Returns:
            Dictionary representation
        """
        return {
            "snapshot_id": snapshot.snapshot_id,
            "symbols": list(snapshot.symbols),
            "start_date": snapshot.start_date.isoformat(),
            "end_date": snapshot.end_date.isoformat(),
            "created_at": snapshot.created_at.isoformat(),
            "data_hash": snapshot.data_hash,
            "file_sizes": snapshot.file_sizes,
            "total_rows": snapshot.total_rows,
        }

    def _snapshot_from_dict(self, payload: dict) -> DataSnapshot:
        """Convert dict to DataSnapshot object.

        Args:
            payload: Dictionary representation

        Returns:
            DataSnapshot object
        """
        return DataSnapshot(
            snapshot_id=payload["snapshot_id"],
            symbols=tuple(payload["symbols"]),
            start_date=datetime.fromisoformat(payload["start_date"]),
            end_date=datetime.fromisoformat(payload["end_date"]),
            created_at=datetime.fromisoformat(payload["created_at"]),
            data_hash=payload["data_hash"],
            file_sizes=payload.get("file_sizes", {}),
            total_rows=payload.get("total_rows", 0),
        )
