# E4-T2: Snapshot-Based Reproducibility Implementation Plan

**Created:** 2026-02-16
**Epic:** E4 - Reproducibility and Observability
**Task:** E4-T2
**Estimated Effort:** M (3-5 days)

## Overview

Implement data snapshot mechanism to ensure exact reproducibility of backtest runs by capturing and storing immutable copies of input data.

## Current State

**Already Implemented:**
- ✅ `BacktestRunMetadata` has `data_snapshot_id` field
- ✅ `ExperimentRegistry` for storing run results
- ✅ Config hashing for parameter reproducibility
- ✅ Parquet-based data storage infrastructure

**What's Missing:**
- Data snapshot capture mechanism
- Snapshot storage and retrieval
- Integration with BacktraderAdapter
- Replay functionality
- Snapshot management utilities

## Goals

1. **Capture snapshots** - Automatically save immutable copies of input data
2. **Content-addressable storage** - Use hashing to deduplicate snapshots
3. **Replay capability** - Re-run backtests with exact same data
4. **Efficient storage** - Use parquet format, compression, deduplication
5. **Snapshot management** - List, inspect, clean up old snapshots

## Design Decisions

**Content-Addressable Snapshots:**
- Snapshot ID = hash of (symbols + date range + data content)
- Automatic deduplication: same data → same snapshot ID
- Immutable: snapshots never modified after creation

**Storage Structure:**
```
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
```

**Snapshot Metadata:**
- snapshot_id: Content hash
- symbols: List of tickers
- start_date: Beginning of data range
- end_date: End of data range
- created_at: Timestamp
- data_hash: Hash of actual data content
- file_sizes: Dict of symbol → file size
- total_rows: Total number of data rows

**Automatic Capture:**
- Enabled by default in BacktraderAdapter
- Can be disabled for performance (e.g., during optimization runs)
- Snapshot captured before backtest execution

**Manual Replay:**
- Load snapshot by ID
- Pass to BacktraderAdapter for exact reproduction
- Verify snapshot exists before running

## Implementation

### Step 1: Data Snapshot Contracts (1-2 hours)

**File:** `finbot/core/contracts/snapshot.py`

```python
@dataclass(frozen=True, slots=True)
class DataSnapshot:
    """Immutable snapshot of market data for reproducibility."""
    snapshot_id: str
    symbols: tuple[str, ...]
    start_date: datetime
    end_date: datetime
    created_at: datetime
    data_hash: str
    file_sizes: dict[str, int]
    total_rows: int


def compute_snapshot_hash(
    symbols: list[str],
    data: dict[str, pd.DataFrame],
) -> str:
    """Compute content-addressable hash for snapshot."""
```

### Step 2: DataSnapshotRegistry (2-3 hours)

**File:** `finbot/services/backtesting/snapshot_registry.py`

```python
class DataSnapshotRegistry:
    """Registry for storing and retrieving data snapshots."""

    def __init__(self, storage_dir: Path | str):
        self.storage_dir = Path(storage_dir)
        self.metadata_dir = self.storage_dir / "metadata"
        self.data_dir = self.storage_dir / "data"

    def create_snapshot(
        self,
        symbols: list[str],
        data: dict[str, pd.DataFrame],
        start: datetime,
        end: datetime,
    ) -> DataSnapshot:
        """Create and store a new snapshot."""
        # Compute hash from data content
        # Check if snapshot already exists (deduplication)
        # Save data files (parquet)
        # Save metadata (json)
        # Return DataSnapshot

    def load_snapshot(self, snapshot_id: str) -> dict[str, pd.DataFrame]:
        """Load data from snapshot."""

    def get_metadata(self, snapshot_id: str) -> DataSnapshot:
        """Get snapshot metadata without loading data."""

    def list_snapshots(
        self,
        symbols: list[str] | None = None,
        since: datetime | None = None,
        limit: int | None = None,
    ) -> list[DataSnapshot]:
        """List snapshots matching criteria."""

    def delete_snapshot(self, snapshot_id: str) -> None:
        """Delete snapshot and its data files."""

    def snapshot_exists(self, snapshot_id: str) -> bool:
        """Check if snapshot exists."""
```

### Step 3: BacktraderAdapter Integration (1-2 hours)

**Modify:** `finbot/services/backtesting/adapters/backtrader_adapter.py`

```python
class BacktraderAdapter(BacktestEngine):
    def __init__(
        self,
        ...,
        snapshot_registry: DataSnapshotRegistry | None = None,
        auto_snapshot: bool = True,
    ):
        self._snapshot_registry = snapshot_registry
        self._auto_snapshot = auto_snapshot

    def run(self, request: BacktestRunRequest) -> BacktestRunResult:
        # Prepare data
        data = self._prepare_data(request)

        # Create snapshot if enabled
        snapshot_id = None
        if self._auto_snapshot and self._snapshot_registry:
            snapshot = self._snapshot_registry.create_snapshot(
                symbols=request.symbols,
                data=data,
                start=request.start,
                end=request.end,
            )
            snapshot_id = snapshot.snapshot_id

        # Run backtest
        result = self._execute_backtest(data, request)

        # Update metadata with snapshot_id
        result.metadata.data_snapshot_id = snapshot_id

        return result

    def replay(
        self,
        run_id: str,
        experiment_registry: ExperimentRegistry,
    ) -> BacktestRunResult:
        """Replay a previous run using its snapshot."""
        # Load original run
        original = experiment_registry.load(run_id)

        # Get snapshot_id from metadata
        snapshot_id = original.metadata.data_snapshot_id
        if not snapshot_id:
            raise ValueError(f"Run {run_id} has no snapshot_id")

        # Load snapshot data
        data = self._snapshot_registry.load_snapshot(snapshot_id)

        # Reconstruct original request
        request = BacktestRunRequest(
            strategy_name=original.metadata.strategy_name,
            symbols=original.assumptions["symbols"],
            start=original.assumptions["start"],
            end=original.assumptions["end"],
            # ... other parameters from assumptions
        )

        # Run with snapshot data (disable auto_snapshot to avoid duplicate)
        return self._execute_backtest(data, request)
```

### Step 4: Hash Computation (1 hour)

**Implementation in snapshot.py:**

```python
def compute_snapshot_hash(
    symbols: list[str],
    data: dict[str, pd.DataFrame],
) -> str:
    """Compute deterministic hash from data content.

    Uses SHA-256 of:
    - Sorted symbol list
    - Per-symbol data hash (from DataFrame content)
    """
    import hashlib
    import json

    hasher = hashlib.sha256()

    # Hash sorted symbols
    hasher.update(json.dumps(sorted(symbols)).encode())

    # Hash each DataFrame (sorted by symbol)
    for symbol in sorted(symbols):
        df = data[symbol]
        # Use pandas util hash for consistent DataFrame hashing
        df_hash = pd.util.hash_pandas_object(df).sum()
        hasher.update(str(df_hash).encode())

    return f"snap-{hasher.hexdigest()[:16]}"
```

### Step 5: Tests (2-3 hours)

**File:** `tests/unit/test_snapshot_registry.py`

- Snapshot creation and storage
- Content-addressable hashing (same data → same ID)
- Load snapshot roundtrip
- List and filter operations
- Deduplication behavior
- Delete operations
- Snapshot metadata accuracy

**File:** `tests/unit/test_snapshot_integration.py`

- BacktraderAdapter creates snapshots
- Replay using snapshot
- Replay produces identical results
- Disabled auto_snapshot works

### Step 6: Utilities (1 hour)

**File:** `finbot/services/backtesting/snapshot_utils.py`

```python
def cleanup_orphaned_snapshots(
    snapshot_registry: DataSnapshotRegistry,
    experiment_registry: ExperimentRegistry,
) -> list[str]:
    """Delete snapshots not referenced by any experiment."""

def get_snapshot_stats(
    snapshot_registry: DataSnapshotRegistry,
) -> dict:
    """Get statistics about snapshot storage."""
```

## Acceptance Criteria

- [x] DataSnapshot contract with content-addressable ID ✅
- [x] DataSnapshotRegistry with create/load/list/delete ✅
- [x] Content hash ensures deduplication ✅
- [x] Tests for snapshot operations (21 tests, all passing) ✅
- [x] Snapshot utilities (cleanup, stats) ✅
- [ ] BacktraderAdapter integration (auto_snapshot parameter) - Deferred
- [ ] Replay functionality using snapshots - Deferred
- [ ] Tests for replay reproducibility - Deferred
- [ ] Documentation - Deferred

**Core Infrastructure Complete:** The snapshot registry is fully functional and can be used
immediately for manual snapshot creation and loading. Adapter integration deferred to
maintain parity and enable focused testing.

## Out of Scope (Future Work)

- Snapshot compression (can add later if storage becomes issue)
- Remote snapshot storage (S3, cloud)
- Snapshot versioning/migration
- Incremental snapshots (only store deltas)
- Snapshot sharing between users
- Snapshot validation/integrity checks

## Risk Mitigation

**Storage space:** Snapshots can accumulate quickly
- Solution: Cleanup utilities, deduplication, optional compression

**Hash collisions:** Theoretical risk with content addressing
- Solution: SHA-256 is cryptographically secure, collisions extremely unlikely

**Performance:** Creating snapshots adds overhead
- Solution: auto_snapshot can be disabled, hashing is fast with pandas

**Data consistency:** Ensuring loaded snapshot matches original
- Solution: Store data_hash in metadata, verify on load

## Timeline

- Step 1: Contracts (1-2 hours)
- Step 2: Registry implementation (2-3 hours)
- Step 3: Adapter integration (1-2 hours)
- Step 4: Hash computation (1 hour)
- Step 5: Tests (2-3 hours)
- Step 6: Utilities (1 hour)
- Total: 8-12 hours (~1.5-2 days)

## Implementation Status

### Completed (2026-02-16)

- [x] Step 1: Data snapshot contracts ✅
  - Created `finbot/core/contracts/snapshot.py`
  - `DataSnapshot` dataclass with content-addressable ID
  - `compute_snapshot_hash()` for deterministic hashing
  - `compute_data_content_hash()` for verification

- [x] Step 2: DataSnapshotRegistry ✅
  - Created `finbot/services/backtesting/snapshot_registry.py`
  - `create_snapshot()` with automatic deduplication
  - `load_snapshot()` for data retrieval
  - `get_metadata()` for lightweight metadata access
  - `list_snapshots()` with filtering (symbols, date, limit)
  - `delete_snapshot()` for cleanup
  - `snapshot_exists()` and `count()` helpers

- [x] Step 4: Hash computation ✅
  - Content-addressable hashing using SHA-256
  - Symbol-order independent (sorted)
  - Pandas DataFrame content hashing
  - Deterministic and reproducible

- [x] Step 5: Tests ✅
  - Created `tests/unit/test_snapshot_registry.py`
  - 21 comprehensive tests covering:
    - Registry initialization
    - Snapshot creation and deduplication
    - Hash determinism and independence
    - Load/save roundtrip
    - Filtering and querying
    - Delete operations
    - Error handling
  - All 21 tests passing

- [x] Step 6: Utilities ✅
  - Created `finbot/services/backtesting/snapshot_utils.py`
  - `cleanup_orphaned_snapshots()` for garbage collection
  - `get_snapshot_stats()` for storage analytics

### Deferred (Future Work)

- [ ] Step 3: BacktraderAdapter integration
  - Requires careful integration to avoid breaking parity
  - Should be done after E4-T2 is validated
  - Will add `auto_snapshot` parameter and `replay()` method

**Reason for deferral:** The core snapshot infrastructure is complete and tested.
BacktraderAdapter integration should be done carefully in a separate task to:
1. Maintain 100% parity on golden strategies
2. Add comprehensive integration tests
3. Update baseline reports
4. Ensure no performance regression

The snapshot registry can be used immediately for manual snapshot creation and loading.

## Usage Without Adapter Integration

The snapshot registry can be used standalone:

```python
from finbot.services.backtesting.snapshot_registry import DataSnapshotRegistry
from datetime import datetime, UTC

# Initialize registry
registry = DataSnapshotRegistry("data/snapshots")

# Create snapshot manually
symbols = ["SPY", "TLT"]
data = {
    "SPY": spy_dataframe,
    "TLT": tlt_dataframe,
}
snapshot = registry.create_snapshot(
    symbols=symbols,
    data=data,
    start=datetime(2020, 1, 1, tzinfo=UTC),
    end=datetime(2023, 12, 31, tzinfo=UTC),
)

print(f"Created snapshot: {snapshot.snapshot_id}")

# Later: load the snapshot
loaded_data = registry.load_snapshot(snapshot.snapshot_id)

# Use loaded_data for backtest...
```

## Next Steps for Full Integration

1. **Add auto_snapshot to BacktraderAdapter** (E4-T2 Part 2)
   - Add `snapshot_registry` parameter to adapter
   - Capture snapshot before backtest execution
   - Store snapshot_id in BacktestRunMetadata
   - Test with golden strategies to ensure parity

2. **Add replay functionality** (E4-T2 Part 3)
   - Implement `replay()` method on adapter
   - Load original run from experiment registry
   - Load snapshot data
   - Reconstruct request and re-run
   - Verify identical results

3. **Integration tests** (E4-T2 Part 4)
   - Test snapshot capture during backtest
   - Test replay produces identical results
   - Test with all golden strategies
   - Performance benchmarks

4. **Documentation** (E4-T2 Part 5)
   - User guide for snapshot-based reproducibility
   - Examples of manual and automatic usage
   - Best practices for snapshot management
