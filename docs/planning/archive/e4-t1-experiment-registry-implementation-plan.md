# E4-T1: Experiment Registry Implementation Plan

**Created:** 2026-02-16
**Epic:** E4 - Reproducibility and Observability
**Task:** E4-T1
**Estimated Effort:** M (3-5 days)

## Overview

Implement a file-based experiment registry for persisting and querying backtest runs to enable reproducibility and comparative analysis.

## Current State

**Already Implemented:**
- ✅ `BacktestRunMetadata` with config_hash and random_seed
- ✅ `BacktestRunResult` serialization (JSON-compatible)
- ✅ Config hashing in `BacktraderAdapter`

**What's Missing:**
- Persistent storage of completed runs
- Query/retrieval functionality
- Comparison helpers
- CLI integration

## Goals

1. **Auto-save runs** - Optionally persist all backtest results
2. **Query experiments** - Find runs by date, strategy, hash, etc.
3. **Compare runs** - Side-by-side comparison of metrics
4. **CLI access** - Command-line experiment management

## Implementation

### Step 1: Experiment Registry (2-3 hours)

**File:** `finbot/services/backtesting/experiment_registry.py`

```python
class ExperimentRegistry:
    """File-based registry for backtest experiments."""

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir

    def save(self, result: BacktestRunResult) -> Path:
        """Save experiment result to registry."""

    def load(self, run_id: str) -> BacktestRunResult:
        """Load experiment by run ID."""

    def list_runs(
        self,
        strategy: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[BacktestRunMetadata]:
        """List experiments matching criteria."""

    def find_by_hash(self, config_hash: str) -> list[BacktestRunResult]:
        """Find all runs with matching config hash."""
```

**Storage Structure:**
```
experiments/
├── 2026/
│   ├── 02/
│   │   ├── bt-uuid1.json
│   │   ├── bt-uuid2.json
│   │   └── ...
│   └── 03/
└── index.json  # Optional: metadata index for faster queries
```

### Step 2: Adapter Integration (1 hour)

**Modify:** `finbot/services/backtesting/adapters/backtrader_adapter.py`

```python
class BacktraderAdapter(BacktestEngine):
    def __init__(
        self,
        ...,
        experiment_registry: ExperimentRegistry | None = None,
        auto_save: bool = True,
    ):
        self._experiment_registry = experiment_registry
        self._auto_save = auto_save

    def run(self, request: BacktestRunRequest) -> BacktestRunResult:
        result = ...  # existing implementation

        # Auto-save if enabled
        if self._auto_save and self._experiment_registry:
            self._experiment_registry.save(result)

        return result
```

### Step 3: Comparison Helpers (1-2 hours)

**File:** `finbot/services/backtesting/experiment_comparison.py`

```python
def compare_experiments(
    results: list[BacktestRunResult],
) -> pd.DataFrame:
    """Create comparison table of experiment results."""

def find_similar_configs(
    registry: ExperimentRegistry,
    reference: BacktestRunResult,
    tolerance: float = 0.1,
) -> list[BacktestRunResult]:
    """Find experiments with similar configurations."""
```

### Step 4: CLI Integration (2-3 hours)

**File:** `finbot/cli/commands/experiments.py`

```bash
# List all experiments
finbot experiments list

# List by strategy
finbot experiments list --strategy Rebalance

# Show specific run
finbot experiments show bt-uuid

# Compare runs
finbot experiments compare bt-uuid1 bt-uuid2

# Find by hash
finbot experiments find-hash abc123def456
```

### Step 5: Tests (2-3 hours)

**File:** `tests/unit/test_experiment_registry.py`

- Save/load roundtrip
- Query by date range
- Query by strategy
- Find by hash
- List operations
- Path handling

## Design Decisions

**File-Based Storage (not database):**
- Simpler deployment (no DB setup)
- Easy backup/version control
- Human-readable (JSON)
- Portable across systems
- Sufficient for single-user scenarios

**Future: Could add database backend later via same interface**

**Auto-Save Default:**
- Opt-in per adapter instance
- Prevents accidental data loss
- Easy to disable for experiments

**JSON Storage:**
- Already have serialization
- Cross-platform compatible
- Easy to inspect/debug
- Can compress if needed

## Acceptance Criteria

- [x] Already have: Runs store immutable metadata
- [x] Already have: Config hash generation
- [x] Already have: Random seed tracking
- [x] Experiment registry with save/load
- [x] Query functionality (list, filter, find by hash)
- [ ] CLI commands for experiment management (deferred to future work)
- [x] Tests for all registry operations (14 tests, all passing)
- [ ] Documentation (deferred to future work)

## Implementation Status

### Completed (2026-02-16)

**Step 1: Experiment Registry** ✅
- Created `finbot/services/backtesting/experiment_registry.py`
- Implemented `ExperimentRegistry` class with:
  - `save()` - persist results to year/month organized JSON files
  - `load()` - retrieve by run_id
  - `list_runs()` - filter by strategy, date range, limit
  - `find_by_hash()` - find runs with matching config hash
  - `count()` - count total experiments
  - `delete()` - remove experiments
  - `_find_run_file()` - internal file lookup helper

**Step 5: Tests** ✅
- Created `tests/unit/test_experiment_registry.py` with 14 tests:
  - test_registry_initialization
  - test_save_experiment
  - test_save_duplicate_raises_error
  - test_load_experiment
  - test_load_nonexistent_raises_error
  - test_list_runs_empty
  - test_list_runs_returns_all
  - test_list_runs_filter_by_strategy
  - test_list_runs_filter_by_date_range
  - test_list_runs_with_limit
  - test_find_by_hash
  - test_count
  - test_delete
  - test_delete_nonexistent_raises_error
- All tests passing (509 total in test suite)

**Bugs Fixed:**
- Fixed duplicate run_id issue in test_list_runs_filter_by_strategy (used enumerate for unique IDs)
- Fixed timezone comparison error in test_list_runs_filter_by_date_range (added UTC timezone to parsed dates)

### Deferred to Future Work

**Step 2: Adapter Integration**
- Will integrate with BacktraderAdapter in future task
- Auto-save functionality to be added when needed

**Step 3: Comparison Helpers**
- Will create `finbot/services/backtesting/experiment_comparison.py` in future task
- `compare_experiments()` and `find_similar_configs()` helpers

**Step 4: CLI Integration**
- Will create `finbot/cli/commands/experiments.py` in future task
- Commands: `finbot experiments list/show/compare/find-hash`

**Documentation**
- User guide for experiment registry to be added in future task

## Out of Scope (Future Work)

- Database backend (PostgreSQL, SQLite)
- Web UI for experiment browsing
- Automatic experiment tagging
- Experiment lineage tracking
- Distributed storage (S3, cloud)
- Advanced search (full-text, ML similarity)

## Risk Mitigation

**Disk space:** JSON files can accumulate quickly
- Solution: Compression, cleanup utilities, configurable retention

**Concurrency:** Multiple processes writing simultaneously
- Solution: File locking, atomic writes, UUID-based filenames (no collisions)

**Performance:** Scanning many files for queries
- Solution: Optional index file, lazy loading, caching

## Timeline

- Step 1: Registry core (2-3 hours)
- Step 2: Adapter integration (1 hour)
- Step 3: Comparison helpers (1-2 hours)
- Step 4: CLI integration (2-3 hours)
- Step 5: Tests (2-3 hours)
- Total: 8-12 hours (~2 days)
