"""Batch backtest run registry for observability and tracking."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from finbot.core.contracts.batch import BatchItemResult, BatchRun, BatchStatus, ErrorCategory


class BatchRegistry:
    """File-based registry for tracking batch backtest runs.

    Provides observability into batch execution status, errors, and performance.

    Storage structure:
        batches/
        ├── metadata/
        │   ├── batch-abc123.json  # Batch metadata + results
        │   └── batch-def456.json
        └── logs/
            └── (future: detailed logs)

    Attributes:
        storage_dir: Root directory for batch storage
        metadata_dir: Directory for batch metadata files
        logs_dir: Directory for batch logs
    """

    def __init__(self, storage_dir: Path | str):
        """Initialize batch registry.

        Args:
            storage_dir: Directory to store batch data
        """
        self.storage_dir = Path(storage_dir)
        self.metadata_dir = self.storage_dir / "metadata"
        self.logs_dir = self.storage_dir / "logs"

        # Create directories
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def create_batch(
        self,
        total_items: int,
        configuration: dict | None = None,
    ) -> BatchRun:
        """Create a new batch run.

        Args:
            total_items: Total number of backtests in batch
            configuration: Snapshot of batch parameters

        Returns:
            BatchRun initialized with PENDING status

        Raises:
            ValueError: If total_items is not positive
        """
        if total_items <= 0:
            raise ValueError(f"total_items must be positive, got {total_items}")

        # Generate batch ID
        batch_id = f"batch-{uuid.uuid4().hex[:16]}"

        # Create batch
        batch = BatchRun(
            batch_id=batch_id,
            created_at=datetime.now(UTC),
            status=BatchStatus.PENDING,
            total_items=total_items,
            configuration=configuration or {},
        )

        # Save metadata
        self._save_batch(batch)

        return batch

    def update_status(
        self,
        batch_id: str,
        status: BatchStatus,
    ) -> BatchRun:
        """Update batch status.

        Args:
            batch_id: Batch identifier
            status: New status

        Returns:
            Updated BatchRun

        Raises:
            FileNotFoundError: If batch not found
        """
        batch = self.get_batch(batch_id)

        # Update status and timestamps
        batch.status = status

        if status == BatchStatus.RUNNING and batch.started_at is None:
            batch.started_at = datetime.now(UTC)

        if batch.is_complete() and batch.completed_at is None:
            batch.completed_at = datetime.now(UTC)

        self._save_batch(batch)
        return batch

    def add_item_result(
        self,
        batch_id: str,
        result: BatchItemResult,
    ) -> BatchRun:
        """Add result for a single item in the batch.

        Args:
            batch_id: Batch identifier
            result: Result of individual backtest

        Returns:
            Updated BatchRun

        Raises:
            FileNotFoundError: If batch not found
        """
        batch = self.get_batch(batch_id)

        # Add result
        batch.item_results.append(result)

        # Update counters
        if result.success:
            batch.succeeded_items += 1
        else:
            batch.failed_items += 1

            # Update error summary
            if result.error_category:
                category = result.error_category.value
                batch.error_summary[category] = batch.error_summary.get(category, 0) + 1

        self._save_batch(batch)
        return batch

    def complete_batch(
        self,
        batch_id: str,
    ) -> BatchRun:
        """Mark batch as completed and compute final metrics.

        Determines final status based on success/failure counts:
        - COMPLETED: All items succeeded
        - PARTIAL: Some items failed
        - FAILED: All items failed

        Args:
            batch_id: Batch identifier

        Returns:
            Completed BatchRun with calculated metrics

        Raises:
            FileNotFoundError: If batch not found
        """
        batch = self.get_batch(batch_id)

        # Set completion time
        if batch.completed_at is None:
            batch.completed_at = datetime.now(UTC)

        # Calculate duration
        if batch.started_at:
            duration = (batch.completed_at - batch.started_at).total_seconds()
            batch.total_duration_seconds = duration

            # Calculate throughput
            if duration > 0:
                batch.items_per_second = batch.total_items / duration

        # Determine final status
        if batch.failed_items == 0:
            batch.status = BatchStatus.COMPLETED
        elif batch.succeeded_items == 0:
            batch.status = BatchStatus.FAILED
        else:
            batch.status = BatchStatus.PARTIAL

        self._save_batch(batch)
        return batch

    def get_batch(self, batch_id: str) -> BatchRun:
        """Get batch metadata and results.

        Args:
            batch_id: Batch identifier

        Returns:
            BatchRun with all data

        Raises:
            FileNotFoundError: If batch not found
        """
        metadata_path = self.metadata_dir / f"{batch_id}.json"

        if not metadata_path.exists():
            raise FileNotFoundError(f"Batch {batch_id} not found in registry")

        with metadata_path.open("r") as f:
            payload = json.load(f)

        return self._batch_from_dict(payload)

    def list_batches(
        self,
        status: BatchStatus | None = None,
        since: datetime | None = None,
        limit: int | None = None,
    ) -> list[BatchRun]:
        """List batch runs matching criteria.

        Args:
            status: Filter by status
            since: Filter to batches created on or after this date
            limit: Maximum number of results to return

        Returns:
            List of matching batches, sorted by created_at descending
        """
        # Collect all metadata files
        metadata_files = sorted(self.metadata_dir.glob("batch-*.json"), reverse=True)

        batches: list[BatchRun] = []

        for metadata_path in metadata_files:
            try:
                with metadata_path.open("r") as f:
                    payload = json.load(f)

                batch = self._batch_from_dict(payload)

                # Apply filters
                if status and batch.status != status:
                    continue

                if since and batch.created_at < since:
                    continue

                batches.append(batch)

                # Check limit
                if limit and len(batches) >= limit:
                    break

            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip malformed files
                continue

        return batches

    def get_failed_items(
        self,
        batch_id: str,
    ) -> list[BatchItemResult]:
        """Get all failed items for a batch.

        Args:
            batch_id: Batch identifier

        Returns:
            List of failed item results

        Raises:
            FileNotFoundError: If batch not found
        """
        batch = self.get_batch(batch_id)
        return [result for result in batch.item_results if not result.success]

    def get_error_summary(
        self,
        batch_id: str,
    ) -> dict[str, int]:
        """Get error category breakdown for a batch.

        Args:
            batch_id: Batch identifier

        Returns:
            Dictionary mapping error category to count

        Raises:
            FileNotFoundError: If batch not found
        """
        batch = self.get_batch(batch_id)
        return batch.error_summary

    def count(self) -> int:
        """Count total number of batches in registry.

        Returns:
            Total number of batches
        """
        return len(list(self.metadata_dir.glob("batch-*.json")))

    def batch_exists(self, batch_id: str) -> bool:
        """Check if batch exists.

        Args:
            batch_id: Batch identifier

        Returns:
            True if batch exists, False otherwise
        """
        metadata_path = self.metadata_dir / f"{batch_id}.json"
        return metadata_path.exists()

    def _save_batch(self, batch: BatchRun) -> None:
        """Save batch to storage.

        Args:
            batch: BatchRun to save
        """
        metadata_path = self.metadata_dir / f"{batch.batch_id}.json"
        payload = self._batch_to_dict(batch)

        with metadata_path.open("w") as f:
            json.dump(payload, f, indent=2)

    def _batch_to_dict(self, batch: BatchRun) -> dict:
        """Convert BatchRun to JSON-serializable dict.

        Args:
            batch: BatchRun object

        Returns:
            Dictionary representation
        """
        return {
            "batch_id": batch.batch_id,
            "created_at": batch.created_at.isoformat(),
            "status": batch.status.value,
            "total_items": batch.total_items,
            "started_at": batch.started_at.isoformat() if batch.started_at else None,
            "completed_at": batch.completed_at.isoformat() if batch.completed_at else None,
            "succeeded_items": batch.succeeded_items,
            "failed_items": batch.failed_items,
            "item_results": [self._item_result_to_dict(r) for r in batch.item_results],
            "error_summary": batch.error_summary,
            "configuration": batch.configuration,
            "total_duration_seconds": batch.total_duration_seconds,
            "items_per_second": batch.items_per_second,
        }

    def _batch_from_dict(self, payload: dict) -> BatchRun:
        """Convert dict to BatchRun object.

        Args:
            payload: Dictionary representation

        Returns:
            BatchRun object
        """
        return BatchRun(
            batch_id=payload["batch_id"],
            created_at=datetime.fromisoformat(payload["created_at"]),
            status=BatchStatus(payload["status"]),
            total_items=payload["total_items"],
            started_at=datetime.fromisoformat(payload["started_at"]) if payload.get("started_at") else None,
            completed_at=datetime.fromisoformat(payload["completed_at"]) if payload.get("completed_at") else None,
            succeeded_items=payload.get("succeeded_items", 0),
            failed_items=payload.get("failed_items", 0),
            item_results=[self._item_result_from_dict(r) for r in payload.get("item_results", [])],
            error_summary=payload.get("error_summary", {}),
            configuration=payload.get("configuration", {}),
            total_duration_seconds=payload.get("total_duration_seconds", 0.0),
            items_per_second=payload.get("items_per_second", 0.0),
        )

    def _item_result_to_dict(self, result: BatchItemResult) -> dict:
        """Convert BatchItemResult to dict.

        Args:
            result: BatchItemResult object

        Returns:
            Dictionary representation
        """
        return {
            "item_id": result.item_id,
            "success": result.success,
            "run_id": result.run_id,
            "error_message": result.error_message,
            "error_category": result.error_category.value if result.error_category else None,
            "duration_seconds": result.duration_seconds,
        }

    def _item_result_from_dict(self, payload: dict) -> BatchItemResult:
        """Convert dict to BatchItemResult.

        Args:
            payload: Dictionary representation

        Returns:
            BatchItemResult object
        """
        return BatchItemResult(
            item_id=payload["item_id"],
            success=payload["success"],
            run_id=payload.get("run_id"),
            error_message=payload.get("error_message"),
            error_category=ErrorCategory(payload["error_category"]) if payload.get("error_category") else None,
            duration_seconds=payload.get("duration_seconds", 0.0),
        )
