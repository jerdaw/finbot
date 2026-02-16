"""Utilities for data snapshot management."""

from __future__ import annotations

from finbot.services.backtesting.experiment_registry import ExperimentRegistry
from finbot.services.backtesting.snapshot_registry import DataSnapshotRegistry


def cleanup_orphaned_snapshots(
    snapshot_registry: DataSnapshotRegistry,
    experiment_registry: ExperimentRegistry,
    *,
    dry_run: bool = True,
) -> list[str]:
    """Delete snapshots not referenced by any experiment.

    Args:
        snapshot_registry: Snapshot registry to clean up
        experiment_registry: Experiment registry to check references
        dry_run: If True, only list snapshots that would be deleted (default)

    Returns:
        List of snapshot IDs that were (or would be) deleted
    """
    # Get all snapshots
    all_snapshots = snapshot_registry.list_snapshots()

    # Get all experiments and collect referenced snapshot IDs
    all_experiments = experiment_registry.list_runs()
    referenced_snapshot_ids = {exp.data_snapshot_id for exp in all_experiments if exp.data_snapshot_id}

    # Find orphaned snapshots
    orphaned_ids: list[str] = []

    for snapshot in all_snapshots:
        if snapshot.snapshot_id not in referenced_snapshot_ids:
            orphaned_ids.append(snapshot.snapshot_id)

            if not dry_run:
                snapshot_registry.delete_snapshot(snapshot.snapshot_id)

    return orphaned_ids


def get_snapshot_stats(snapshot_registry: DataSnapshotRegistry) -> dict:
    """Get statistics about snapshot storage.

    Args:
        snapshot_registry: Snapshot registry to analyze

    Returns:
        Dictionary containing:
        - total_snapshots: Number of snapshots
        - total_size_bytes: Total storage used in bytes
        - total_size_mb: Total storage used in MB
        - total_rows: Total number of data rows
        - by_symbol: Dict mapping symbol to count of snapshots containing it
        - largest_snapshot: ID of largest snapshot by file size
        - largest_size_bytes: Size of largest snapshot
    """
    snapshots = snapshot_registry.list_snapshots()

    if not snapshots:
        return {
            "total_snapshots": 0,
            "total_size_bytes": 0,
            "total_size_mb": 0.0,
            "total_rows": 0,
            "by_symbol": {},
            "largest_snapshot": None,
            "largest_size_bytes": 0,
        }

    total_size = 0
    total_rows = 0
    symbol_counts: dict[str, int] = {}
    largest_snapshot = None
    largest_size = 0

    for snapshot in snapshots:
        # Sum file sizes
        snapshot_size = sum(snapshot.file_sizes.values())
        total_size += snapshot_size
        total_rows += snapshot.total_rows

        # Track largest
        if snapshot_size > largest_size:
            largest_size = snapshot_size
            largest_snapshot = snapshot.snapshot_id

        # Count symbols
        for symbol in snapshot.symbols:
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1

    return {
        "total_snapshots": len(snapshots),
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "total_rows": total_rows,
        "by_symbol": symbol_counts,
        "largest_snapshot": largest_snapshot,
        "largest_size_bytes": largest_size,
    }
