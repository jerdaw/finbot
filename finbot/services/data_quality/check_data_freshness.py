"""Check freshness of all registered data sources.

Scans data directories for parquet files, reports the most recent
modification time, file count, and staleness status for each source.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from finbot.services.data_quality.data_source_registry import DATA_SOURCES, DataSource


@dataclass
class DataSourceStatus:
    """Freshness status for a single data source."""

    source: DataSource
    file_count: int
    oldest_file: datetime | None
    newest_file: datetime | None
    total_size_bytes: int

    @property
    def is_stale(self) -> bool:
        if self.newest_file is None:
            return True
        age_days = (datetime.now() - self.newest_file).total_seconds() / 86400
        return age_days > self.source.max_age_days

    @property
    def age_str(self) -> str:
        if self.newest_file is None:
            return "no data"
        delta = datetime.now() - self.newest_file
        days = delta.days
        hours = delta.seconds // 3600
        if days > 0:
            return f"{days}d {hours}h ago"
        if hours > 0:
            return f"{hours}h ago"
        minutes = delta.seconds // 60
        return f"{minutes}m ago"

    @property
    def size_str(self) -> str:
        if self.total_size_bytes == 0:
            return "0 B"
        units = ["B", "KB", "MB", "GB"]
        size = float(self.total_size_bytes)
        for unit in units:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


def _scan_directory(directory: Path, pattern: str) -> tuple[list[Path], int]:
    """Return matching files and total size in bytes."""
    if not directory.exists():
        return [], 0
    files = sorted(directory.glob(pattern))
    total_size = sum(f.stat().st_size for f in files)
    return files, total_size


def check_source_freshness(source: DataSource) -> DataSourceStatus:
    """Check freshness of a single data source."""
    files, total_size = _scan_directory(source.directory, source.pattern)

    if not files:
        return DataSourceStatus(
            source=source,
            file_count=0,
            oldest_file=None,
            newest_file=None,
            total_size_bytes=0,
        )

    mtimes = [datetime.fromtimestamp(f.stat().st_mtime) for f in files]
    return DataSourceStatus(
        source=source,
        file_count=len(files),
        oldest_file=min(mtimes),
        newest_file=max(mtimes),
        total_size_bytes=total_size,
    )


def check_all_freshness() -> list[DataSourceStatus]:
    """Check freshness of all registered data sources."""
    return [check_source_freshness(source) for source in DATA_SOURCES]
