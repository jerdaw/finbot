"""Unit tests for snapshot management utilities."""

from __future__ import annotations

from unittest.mock import MagicMock

from finbot.services.backtesting.snapshot_utils import (
    cleanup_orphaned_snapshots,
    get_snapshot_stats,
)


def _make_snapshot(
    snapshot_id: str, symbols: list[str] | None = None, file_sizes: dict | None = None, total_rows: int = 100
):
    snap = MagicMock()
    snap.snapshot_id = snapshot_id
    snap.symbols = symbols or ["SPY"]
    snap.file_sizes = file_sizes or {"SPY.parquet": 1024}
    snap.total_rows = total_rows
    return snap


def _make_experiment(data_snapshot_id: str | None):
    exp = MagicMock()
    exp.data_snapshot_id = data_snapshot_id
    return exp


class TestCleanupOrphanedSnapshots:
    """Tests for cleanup_orphaned_snapshots()."""

    def test_dry_run_returns_orphan_ids(self):
        snap_reg = MagicMock()
        snap_reg.list_snapshots.return_value = [
            _make_snapshot("snap-1"),
            _make_snapshot("snap-2"),
        ]
        exp_reg = MagicMock()
        exp_reg.list_runs.return_value = [_make_experiment("snap-1")]

        orphans = cleanup_orphaned_snapshots(snap_reg, exp_reg, dry_run=True)
        assert orphans == ["snap-2"]
        snap_reg.delete_snapshot.assert_not_called()

    def test_dry_run_false_deletes(self):
        snap_reg = MagicMock()
        snap_reg.list_snapshots.return_value = [_make_snapshot("snap-orphan")]
        exp_reg = MagicMock()
        exp_reg.list_runs.return_value = []

        orphans = cleanup_orphaned_snapshots(snap_reg, exp_reg, dry_run=False)
        assert orphans == ["snap-orphan"]
        snap_reg.delete_snapshot.assert_called_once_with("snap-orphan")

    def test_no_orphans(self):
        snap_reg = MagicMock()
        snap_reg.list_snapshots.return_value = [_make_snapshot("snap-1")]
        exp_reg = MagicMock()
        exp_reg.list_runs.return_value = [_make_experiment("snap-1")]

        orphans = cleanup_orphaned_snapshots(snap_reg, exp_reg)
        assert orphans == []

    def test_all_orphaned(self):
        snap_reg = MagicMock()
        snap_reg.list_snapshots.return_value = [
            _make_snapshot("a"),
            _make_snapshot("b"),
        ]
        exp_reg = MagicMock()
        exp_reg.list_runs.return_value = []

        orphans = cleanup_orphaned_snapshots(snap_reg, exp_reg)
        assert set(orphans) == {"a", "b"}


class TestGetSnapshotStats:
    """Tests for get_snapshot_stats()."""

    def test_empty_registry(self):
        snap_reg = MagicMock()
        snap_reg.list_snapshots.return_value = []
        stats = get_snapshot_stats(snap_reg)
        assert stats["total_snapshots"] == 0
        assert stats["total_size_bytes"] == 0
        assert stats["largest_snapshot"] is None

    def test_single_snapshot(self):
        snap_reg = MagicMock()
        snap_reg.list_snapshots.return_value = [
            _make_snapshot(
                "snap-1", symbols=["SPY", "TLT"], file_sizes={"SPY.parquet": 2048, "TLT.parquet": 1024}, total_rows=500
            ),
        ]
        stats = get_snapshot_stats(snap_reg)
        assert stats["total_snapshots"] == 1
        assert stats["total_size_bytes"] == 3072
        assert stats["total_rows"] == 500
        assert stats["by_symbol"]["SPY"] == 1
        assert stats["by_symbol"]["TLT"] == 1
        assert stats["largest_snapshot"] == "snap-1"

    def test_multiple_snapshots_tracks_largest(self):
        snap_reg = MagicMock()
        snap_reg.list_snapshots.return_value = [
            _make_snapshot("small", file_sizes={"a.parquet": 100}, total_rows=10),
            _make_snapshot("big", file_sizes={"b.parquet": 9999}, total_rows=1000),
        ]
        stats = get_snapshot_stats(snap_reg)
        assert stats["largest_snapshot"] == "big"
        assert stats["largest_size_bytes"] == 9999
        assert stats["total_snapshots"] == 2

    def test_size_mb_calculated(self):
        snap_reg = MagicMock()
        snap_reg.list_snapshots.return_value = [
            _make_snapshot("snap-1", file_sizes={"a.parquet": 1048576}, total_rows=100),
        ]
        stats = get_snapshot_stats(snap_reg)
        assert stats["total_size_mb"] == 1.0
