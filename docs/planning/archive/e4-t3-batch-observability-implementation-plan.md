# E4-T3: Batch Observability Instrumentation Implementation Plan

**Created:** 2026-02-16
**Epic:** E4 - Reproducibility and Observability
**Task:** E4-T3
**Estimated Effort:** M (3-5 days)

## Overview

Implement comprehensive observability for batch backtesting operations to enable tracking, debugging, and analysis of large-scale backtest runs.

## Current State

**Already Implemented:**
- ✅ `backtest_batch()` function for parallel backtesting
- ✅ `ExperimentRegistry` for storing individual runs
- ✅ Multiprocessing with progress bar (tqdm)

**What's Missing:**
- Batch-level tracking (batch as a unit)
- Status taxonomy (pending/running/completed/failed/cancelled)
- Error tracking and categorization
- Retry mechanism
- Queryable batch history
- Performance metrics per batch

## Goals

1. **Batch tracking** - Treat batch runs as first-class entities
2. **Status visibility** - Real-time status of batch jobs
3. **Error taxonomy** - Categorize and track failures
4. **Retry support** - Automatic or manual retry of failed items
5. **Performance metrics** - Duration, throughput, resource usage
6. **Queryability** - Search and filter batch history

## Design Decisions

**Batch as Unit of Work:**
- Each batch run gets a unique batch_id
- Batch contains multiple individual backtest runs
- Batch has its own lifecycle (pending → running → completed/failed)

**Status Taxonomy:**
```python
class BatchStatus(StrEnum):
    PENDING = "pending"      # Created but not started
    RUNNING = "running"      # Currently executing
    COMPLETED = "completed"  # All items succeeded
    PARTIAL = "partial"      # Some items failed
    FAILED = "failed"        # All items failed or batch error
    CANCELLED = "cancelled"  # User cancelled
```

**Error Categories:**
```python
class ErrorCategory(StrEnum):
    DATA_ERROR = "data_error"          # Missing/invalid data
    PARAMETER_ERROR = "parameter_error" # Invalid parameters
    ENGINE_ERROR = "engine_error"       # Backtest engine failure
    TIMEOUT = "timeout"                 # Execution timeout
    MEMORY_ERROR = "memory_error"       # Out of memory
    UNKNOWN = "unknown"                 # Uncategorized
```

**Storage Structure:**
```
batches/
├── metadata/
│   ├── batch-abc123.json  # Batch metadata + results
│   └── batch-def456.json
└── logs/
    ├── batch-abc123.log   # Optional detailed logs
    └── batch-def456.log
```

**Batch Metadata:**
- batch_id: Unique identifier
- created_at: Creation timestamp
- started_at: Start timestamp
- completed_at: Completion timestamp
- status: Current status
- total_items: Total number of backtests
- succeeded_items: Number of successes
- failed_items: Number of failures
- error_summary: Dict of error category → count
- configuration: Parameters used
- performance: Duration, throughput

## Implementation

### Step 1: Batch Observability Contracts (1-2 hours)

**File:** `finbot/core/contracts/batch.py`

```python
from enum import StrEnum
from dataclasses import dataclass, field
from datetime import datetime


class BatchStatus(StrEnum):
    """Batch run lifecycle status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ErrorCategory(StrEnum):
    """Error categorization for failed backtests."""
    DATA_ERROR = "data_error"
    PARAMETER_ERROR = "parameter_error"
    ENGINE_ERROR = "engine_error"
    TIMEOUT = "timeout"
    MEMORY_ERROR = "memory_error"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class BatchItemResult:
    """Result of a single backtest within a batch."""
    item_id: int
    success: bool
    run_id: str | None = None  # If successful
    error_message: str | None = None
    error_category: ErrorCategory | None = None
    duration_seconds: float = 0.0


@dataclass
class BatchRun:
    """Batch backtest run metadata and results."""
    batch_id: str
    created_at: datetime
    status: BatchStatus
    total_items: int

    started_at: datetime | None = None
    completed_at: datetime | None = None

    succeeded_items: int = 0
    failed_items: int = 0

    item_results: list[BatchItemResult] = field(default_factory=list)
    error_summary: dict[str, int] = field(default_factory=dict)

    # Configuration snapshot
    configuration: dict = field(default_factory=dict)

    # Performance metrics
    total_duration_seconds: float = 0.0
    items_per_second: float = 0.0
```

### Step 2: BatchRegistry (2-3 hours)

**File:** `finbot/services/backtesting/batch_registry.py`

```python
class BatchRegistry:
    """Registry for tracking batch backtest runs."""

    def __init__(self, storage_dir: Path | str):
        self.storage_dir = Path(storage_dir)
        self.metadata_dir = self.storage_dir / "metadata"
        self.logs_dir = self.storage_dir / "logs"

    def create_batch(
        self,
        total_items: int,
        configuration: dict,
    ) -> BatchRun:
        """Create a new batch run."""
        # Generate batch_id
        # Initialize BatchRun with PENDING status
        # Save metadata
        # Return BatchRun

    def update_status(
        self,
        batch_id: str,
        status: BatchStatus,
    ) -> None:
        """Update batch status."""

    def add_item_result(
        self,
        batch_id: str,
        result: BatchItemResult,
    ) -> None:
        """Add result for a single item."""
        # Load batch
        # Add result
        # Update counters
        # Update error_summary
        # Save

    def complete_batch(
        self,
        batch_id: str,
    ) -> BatchRun:
        """Mark batch as completed and compute final metrics."""
        # Calculate duration
        # Calculate throughput
        # Determine final status (completed/partial/failed)
        # Save and return

    def get_batch(self, batch_id: str) -> BatchRun:
        """Get batch metadata and results."""

    def list_batches(
        self,
        status: BatchStatus | None = None,
        since: datetime | None = None,
        limit: int | None = None,
    ) -> list[BatchRun]:
        """List batch runs matching criteria."""

    def get_failed_items(
        self,
        batch_id: str,
    ) -> list[BatchItemResult]:
        """Get all failed items for a batch."""

    def get_error_summary(
        self,
        batch_id: str,
    ) -> dict[str, int]:
        """Get error category breakdown."""
```

### Step 3: Error Categorization Helper (1 hour)

**File:** `finbot/services/backtesting/error_categorizer.py`

```python
def categorize_error(exception: Exception) -> ErrorCategory:
    """Categorize exception into error category.

    Uses exception type and message to determine category.
    """
    # Check exception type
    # Check error message patterns
    # Return appropriate ErrorCategory
```

### Step 4: Integration with Batch Runner (2-3 hours)

**Modify:** `finbot/services/backtesting/backtest_batch.py`

Add optional batch tracking:

```python
def backtest_batch(
    *,
    batch_registry: BatchRegistry | None = None,
    track_batch: bool = True,
    **kwargs
):
    # Create batch if tracking enabled
    if track_batch and batch_registry:
        batch = batch_registry.create_batch(
            total_items=n_combs,
            configuration=kwargs,
        )
        batch_registry.update_status(batch.batch_id, BatchStatus.RUNNING)

    # Run backtests with error handling per item
    # Track results
    # Update batch registry

    # Complete batch
    if track_batch and batch_registry:
        batch_registry.complete_batch(batch.batch_id)
```

### Step 5: Tests (2-3 hours)

**File:** `tests/unit/test_batch_registry.py`

- Batch creation and initialization
- Status transitions
- Item result tracking
- Error categorization
- List and filter operations
- Completion metrics calculation

**File:** `tests/unit/test_error_categorizer.py`

- Error category inference from exception types
- Error message pattern matching

### Step 6: Utilities (1 hour)

**File:** `finbot/services/backtesting/batch_utils.py`

```python
def retry_failed_items(
    batch_registry: BatchRegistry,
    batch_id: str,
    max_retries: int = 3,
) -> BatchRun:
    """Retry all failed items from a batch."""

def get_batch_statistics(
    batch_registry: BatchRegistry,
    since: datetime | None = None,
) -> dict:
    """Get aggregated statistics across batches."""
```

## Acceptance Criteria

- [x] Batch observability contracts (BatchRun, BatchStatus, ErrorCategory, BatchItemResult) ✅
- [x] BatchRegistry with create/update/list/query operations ✅
- [x] Error categorization from exceptions ✅
- [x] Tests for batch tracking (23 tests, all passing) ✅
- [x] Tests for error categorization (16 tests, all passing) ✅
- [ ] Integration with existing backtest_batch (optional tracking) - Deferred
- [ ] Documentation - Deferred

**Core Infrastructure Complete:** The batch observability infrastructure is fully functional
and can be used immediately for manual batch tracking. Integration with the existing
batch runner deferred to maintain backward compatibility and enable focused testing.

## Out of Scope (Future Work)

- Real-time status updates (websocket/SSE)
- Web UI for batch monitoring
- Distributed batch execution
- Resource usage tracking (CPU, memory)
- Advanced retry strategies (exponential backoff)
- Batch scheduling and queueing

## Risk Mitigation

**Performance overhead:** Tracking adds overhead to batch runs
- Solution: Make tracking optional, lightweight updates

**Storage growth:** Batch metadata can accumulate
- Solution: Cleanup utilities, configurable retention

**Error categorization accuracy:** May misclassify errors
- Solution: Conservative defaults (UNKNOWN), allow manual override

## Timeline

- Step 1: Contracts (1-2 hours)
- Step 2: BatchRegistry (2-3 hours)
- Step 3: Error categorization (1 hour)
- Step 4: Integration (2-3 hours)
- Step 5: Tests (2-3 hours)
- Step 6: Utilities (1 hour)
- Total: 9-14 hours (~1.5-2.5 days)

## Implementation Status

### Completed (2026-02-16)

- [x] Step 1: Batch observability contracts ✅
  - Created `finbot/core/contracts/batch.py`
  - BatchStatus enum (PENDING/RUNNING/COMPLETED/PARTIAL/FAILED/CANCELLED)
  - ErrorCategory enum (DATA_ERROR/PARAMETER_ERROR/ENGINE_ERROR/TIMEOUT/MEMORY_ERROR/UNKNOWN)
  - BatchItemResult dataclass for individual backtest results
  - BatchRun dataclass for batch metadata and aggregated results
  - Helper methods: is_complete(), success_rate(), failure_rate()

- [x] Step 2: BatchRegistry ✅
  - Created `finbot/services/backtesting/batch_registry.py`
  - create_batch() - Initialize new batch run
  - update_status() - Update batch status with automatic timestamps
  - add_item_result() - Track individual backtest results
  - complete_batch() - Finalize batch with metrics calculation
  - get_batch() - Retrieve batch metadata
  - list_batches() - Query with filters (status, date, limit)
  - get_failed_items() - Get all failed backtests
  - get_error_summary() - Error category breakdown
  - count(), batch_exists() - Helper methods
  - JSON serialization/deserialization

- [x] Step 3: Error categorization ✅
  - Created `finbot/services/backtesting/error_categorizer.py`
  - categorize_error() function with intelligent pattern matching
  - Exception type detection (ValueError, FileNotFoundError, MemoryError, etc.)
  - Error message keyword matching for data/parameter/engine/timeout/memory errors
  - Case-insensitive categorization
  - Conservative fallback to UNKNOWN for ambiguous cases

- [x] Step 5: Tests ✅
  - Created `tests/unit/test_batch_registry.py` (23 tests)
    - Registry initialization
    - Batch creation and validation
    - Status transitions with timestamps
    - Item result tracking (success/failure)
    - Error summary aggregation
    - Batch completion with metrics
    - Filtering and querying
    - Success/failure rate calculations
  - Created `tests/unit/test_error_categorizer.py` (16 tests)
    - Exception type categorization
    - Keyword-based categorization
    - Case-insensitive matching
    - All error categories covered
  - All 39 tests passing
  - 569 tests total (up from 530)

### Deferred (Future Work)

- [ ] Step 4: Integration with batch runner
  - Requires careful integration with existing backtest_batch function
  - Should add optional tracking without breaking existing usage
  - Will add batch_registry parameter and error handling per item

- [ ] Step 6: Utilities
  - retry_failed_items() for automatic retry
  - get_batch_statistics() for aggregate analysis
  - Can be added when needed

**Reason for deferral:** The core observability infrastructure is complete and tested.
Integration with the existing batch runner should be done carefully to:
1. Maintain backward compatibility
2. Add comprehensive integration tests
3. Validate performance impact
4. Ensure error handling doesn't interfere with existing workflows

The batch registry can be used immediately for manual batch tracking.

## Usage Without Integration

The batch registry can be used standalone to track any batch operation:

```python
from finbot.services.backtesting.batch_registry import BatchRegistry
from finbot.core.contracts.batch import BatchItemResult, BatchStatus, ErrorCategory
from finbot.services.backtesting.error_categorizer import categorize_error

# Initialize registry
registry = BatchRegistry("data/batches")

# Create batch
batch = registry.create_batch(
    total_items=10,
    configuration={"strategy": "Rebalance", "symbols": ["SPY", "TLT"]},
)

# Start execution
registry.update_status(batch.batch_id, BatchStatus.RUNNING)

# Track each item
for i in range(10):
    try:
        # Run backtest...
        result = run_backtest(...)
        registry.add_item_result(
            batch.batch_id,
            BatchItemResult(
                item_id=i,
                success=True,
                run_id=result.metadata.run_id,
                duration_seconds=1.5,
            ),
        )
    except Exception as e:
        registry.add_item_result(
            batch.batch_id,
            BatchItemResult(
                item_id=i,
                success=False,
                error_message=str(e),
                error_category=categorize_error(e),
            ),
        )

# Complete batch
final_batch = registry.complete_batch(batch.batch_id)
print(f"Success rate: {final_batch.success_rate():.1%}")
print(f"Throughput: {final_batch.items_per_second:.1f} items/sec")
```

## Next Steps for Full Integration

1. **Modify backtest_batch function** (Step 4)
   - Add optional batch_registry parameter
   - Add optional track_batch parameter (default False for backward compat)
   - Wrap each backtest in try/except for error tracking
   - Update batch registry with results

2. **Add integration tests**
   - Test batch tracking during actual batch runs
   - Test error categorization with real backtest failures
   - Performance benchmarks

3. **Add retry utilities** (Step 6)
   - Implement retry_failed_items()
   - Add configuration for retry strategy
   - Test retry behavior

4. **Documentation**
   - User guide for batch observability
   - Examples of using batch registry
   - Best practices for error handling
