"""Batch backtesting observability contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class BatchStatus(StrEnum):
    """Batch run lifecycle status.

    Status transitions:
        PENDING → RUNNING → COMPLETED (all succeeded)
        PENDING → RUNNING → PARTIAL (some failed)
        PENDING → RUNNING → FAILED (all failed or batch error)
        PENDING → CANCELLED (user cancelled before running)
        RUNNING → CANCELLED (user cancelled during execution)
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ErrorCategory(StrEnum):
    """Error categorization for failed backtests.

    Used to group and analyze failure patterns across batch runs.
    """

    DATA_ERROR = "data_error"  # Missing, invalid, or insufficient data
    PARAMETER_ERROR = "parameter_error"  # Invalid configuration or parameters
    ENGINE_ERROR = "engine_error"  # Backtest engine internal error
    TIMEOUT = "timeout"  # Execution exceeded time limit
    MEMORY_ERROR = "memory_error"  # Out of memory or resource exhaustion
    UNKNOWN = "unknown"  # Uncategorized or unexpected error


@dataclass(frozen=True, slots=True)
class BatchItemResult:
    """Result of a single backtest within a batch.

    Attributes:
        item_id: Sequential ID within batch (0-indexed)
        success: Whether backtest completed successfully
        run_id: BacktestRunResult run_id if successful
        error_message: Error description if failed
        error_category: Categorized error type if failed
        duration_seconds: Execution time for this item
        attempt_count: Number of execution attempts for this item
        final_attempt_success: Whether final attempt succeeded
    """

    item_id: int
    success: bool
    run_id: str | None = None
    error_message: str | None = None
    error_category: ErrorCategory | None = None
    duration_seconds: float = 0.0
    attempt_count: int = 1
    final_attempt_success: bool | None = None


@dataclass
class BatchRun:
    """Batch backtest run metadata and results.

    Tracks a collection of related backtest runs as a single unit,
    providing visibility into batch execution status, errors, and performance.

    Attributes:
        batch_id: Unique identifier for this batch
        created_at: When batch was created
        status: Current lifecycle status
        total_items: Total number of backtests in batch
        started_at: When batch execution started
        completed_at: When batch execution finished
        succeeded_items: Count of successful backtests
        failed_items: Count of failed backtests
        item_results: Results for each individual backtest
        error_summary: Count by error category
        configuration: Snapshot of batch parameters
        total_duration_seconds: Total execution time
        items_per_second: Throughput (items/sec)
    """

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

    configuration: dict = field(default_factory=dict)

    total_duration_seconds: float = 0.0
    items_per_second: float = 0.0

    def is_complete(self) -> bool:
        """Check if batch has finished executing."""
        return self.status in (
            BatchStatus.COMPLETED,
            BatchStatus.PARTIAL,
            BatchStatus.FAILED,
            BatchStatus.CANCELLED,
        )

    def success_rate(self) -> float:
        """Calculate success rate (0.0 to 1.0)."""
        if self.total_items == 0:
            return 0.0
        return self.succeeded_items / self.total_items

    def failure_rate(self) -> float:
        """Calculate failure rate (0.0 to 1.0)."""
        if self.total_items == 0:
            return 0.0
        return self.failed_items / self.total_items
