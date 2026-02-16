"""Data snapshot contracts for reproducible backtesting."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd


@dataclass(frozen=True, slots=True)
class DataSnapshot:
    """Immutable snapshot of market data for reproducibility.

    Attributes:
        snapshot_id: Content-addressable hash identifier
        symbols: Tuple of ticker symbols in snapshot
        start_date: Beginning of data range
        end_date: End of data range
        created_at: Timestamp when snapshot was created
        data_hash: Hash of actual data content for verification
        file_sizes: Mapping of symbol to file size in bytes
        total_rows: Total number of data rows across all symbols
    """

    snapshot_id: str
    symbols: tuple[str, ...]
    start_date: datetime
    end_date: datetime
    created_at: datetime
    data_hash: str
    file_sizes: dict[str, int] = field(default_factory=dict)
    total_rows: int = 0


def compute_snapshot_hash(
    symbols: list[str],
    data: dict[str, pd.DataFrame],
) -> str:
    """Compute content-addressable hash for snapshot.

    The hash is deterministic and based on:
    - Sorted list of symbols
    - Content hash of each DataFrame

    This ensures that identical data produces identical snapshot IDs,
    enabling automatic deduplication.

    Args:
        symbols: List of ticker symbols
        data: Dictionary mapping symbol to DataFrame

    Returns:
        Snapshot ID in format "snap-{hash[:16]}"

    Examples:
        >>> symbols = ["SPY", "TLT"]
        >>> data = {"SPY": spy_df, "TLT": tlt_df}
        >>> snapshot_id = compute_snapshot_hash(symbols, data)
        >>> snapshot_id.startswith("snap-")
        True
    """
    hasher = hashlib.sha256()

    # Hash sorted symbols for deterministic ordering
    hasher.update(json.dumps(sorted(symbols)).encode())

    # Hash each DataFrame content (sorted by symbol for consistency)
    for symbol in sorted(symbols):
        if symbol not in data:
            continue

        df = data[symbol]

        # Use pandas hash for consistent DataFrame hashing
        # Sum of hash values gives us a single integer representing content
        df_hash = pd.util.hash_pandas_object(df, index=True).sum()
        hasher.update(str(df_hash).encode())

    # Return shortened hash as snapshot ID
    return f"snap-{hasher.hexdigest()[:16]}"


def compute_data_content_hash(data: dict[str, pd.DataFrame]) -> str:
    """Compute hash of actual data content for verification.

    Similar to snapshot hash but focuses purely on data content,
    not symbols. Used for integrity verification.

    Args:
        data: Dictionary mapping symbol to DataFrame

    Returns:
        SHA-256 hash of data content
    """
    hasher = hashlib.sha256()

    for symbol in sorted(data.keys()):
        df = data[symbol]
        df_hash = pd.util.hash_pandas_object(df, index=True).sum()
        hasher.update(f"{symbol}:{df_hash}".encode())

    return hasher.hexdigest()
