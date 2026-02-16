"""Unit tests for batch registry."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from finbot.core.contracts.batch import BatchItemResult, BatchStatus, ErrorCategory
from finbot.services.backtesting.batch_registry import BatchRegistry


@pytest.fixture
def temp_registry(tmp_path):
    """Create temporary batch registry."""
    return BatchRegistry(tmp_path / "batches")


def test_registry_initialization(tmp_path):
    """Test registry initializes and creates directories."""
    registry_path = tmp_path / "batches"
    assert not registry_path.exists()

    registry = BatchRegistry(registry_path)

    assert registry.storage_dir == registry_path
    assert registry_path.exists()
    assert (registry_path / "metadata").exists()
    assert (registry_path / "logs").exists()


def test_create_batch(temp_registry):
    """Test creating batch initializes correctly."""
    batch = temp_registry.create_batch(total_items=10, configuration={"strategy": "test"})

    assert batch.batch_id.startswith("batch-")
    assert batch.status == BatchStatus.PENDING
    assert batch.total_items == 10
    assert batch.succeeded_items == 0
    assert batch.failed_items == 0
    assert batch.configuration == {"strategy": "test"}
    assert temp_registry.batch_exists(batch.batch_id)


def test_create_batch_invalid_total_items(temp_registry):
    """Test creating batch with invalid total_items raises error."""
    with pytest.raises(ValueError, match="must be positive"):
        temp_registry.create_batch(total_items=0)


def test_update_status(temp_registry):
    """Test updating batch status."""
    batch = temp_registry.create_batch(total_items=5)

    # Update to running
    batch = temp_registry.update_status(batch.batch_id, BatchStatus.RUNNING)
    assert batch.status == BatchStatus.RUNNING
    assert batch.started_at is not None

    # Update to completed
    batch = temp_registry.update_status(batch.batch_id, BatchStatus.COMPLETED)
    assert batch.status == BatchStatus.COMPLETED
    assert batch.completed_at is not None


def test_add_item_result_success(temp_registry):
    """Test adding successful item result."""
    batch = temp_registry.create_batch(total_items=3)

    result = BatchItemResult(
        item_id=0,
        success=True,
        run_id="bt-test-001",
        duration_seconds=1.5,
    )

    batch = temp_registry.add_item_result(batch.batch_id, result)

    assert batch.succeeded_items == 1
    assert batch.failed_items == 0
    assert len(batch.item_results) == 1
    assert batch.item_results[0].run_id == "bt-test-001"


def test_add_item_result_failure(temp_registry):
    """Test adding failed item result."""
    batch = temp_registry.create_batch(total_items=3)

    result = BatchItemResult(
        item_id=0,
        success=False,
        error_message="Data missing",
        error_category=ErrorCategory.DATA_ERROR,
        duration_seconds=0.5,
    )

    batch = temp_registry.add_item_result(batch.batch_id, result)

    assert batch.succeeded_items == 0
    assert batch.failed_items == 1
    assert len(batch.item_results) == 1
    assert batch.error_summary[ErrorCategory.DATA_ERROR.value] == 1


def test_add_multiple_item_results(temp_registry):
    """Test adding multiple item results updates counters."""
    batch = temp_registry.create_batch(total_items=5)

    # Add 3 successes
    for i in range(3):
        temp_registry.add_item_result(
            batch.batch_id,
            BatchItemResult(item_id=i, success=True, run_id=f"bt-{i}"),
        )

    # Add 2 failures (different categories)
    temp_registry.add_item_result(
        batch.batch_id,
        BatchItemResult(
            item_id=3,
            success=False,
            error_category=ErrorCategory.DATA_ERROR,
        ),
    )
    temp_registry.add_item_result(
        batch.batch_id,
        BatchItemResult(
            item_id=4,
            success=False,
            error_category=ErrorCategory.PARAMETER_ERROR,
        ),
    )

    batch = temp_registry.get_batch(batch.batch_id)

    assert batch.succeeded_items == 3
    assert batch.failed_items == 2
    assert len(batch.item_results) == 5
    assert batch.error_summary[ErrorCategory.DATA_ERROR.value] == 1
    assert batch.error_summary[ErrorCategory.PARAMETER_ERROR.value] == 1


def test_complete_batch_all_success(temp_registry):
    """Test completing batch with all successes."""
    batch = temp_registry.create_batch(total_items=3)
    temp_registry.update_status(batch.batch_id, BatchStatus.RUNNING)

    # Add all successes
    for i in range(3):
        temp_registry.add_item_result(
            batch.batch_id,
            BatchItemResult(item_id=i, success=True, run_id=f"bt-{i}"),
        )

    batch = temp_registry.complete_batch(batch.batch_id)

    assert batch.status == BatchStatus.COMPLETED
    assert batch.completed_at is not None
    assert batch.total_duration_seconds > 0
    assert batch.items_per_second > 0
    assert batch.success_rate() == 1.0


def test_complete_batch_all_failures(temp_registry):
    """Test completing batch with all failures."""
    batch = temp_registry.create_batch(total_items=3)
    temp_registry.update_status(batch.batch_id, BatchStatus.RUNNING)

    # Add all failures
    for i in range(3):
        temp_registry.add_item_result(
            batch.batch_id,
            BatchItemResult(
                item_id=i,
                success=False,
                error_category=ErrorCategory.ENGINE_ERROR,
            ),
        )

    batch = temp_registry.complete_batch(batch.batch_id)

    assert batch.status == BatchStatus.FAILED
    assert batch.failure_rate() == 1.0


def test_complete_batch_partial(temp_registry):
    """Test completing batch with mixed results."""
    batch = temp_registry.create_batch(total_items=4)
    temp_registry.update_status(batch.batch_id, BatchStatus.RUNNING)

    # Add 2 successes and 2 failures
    temp_registry.add_item_result(
        batch.batch_id,
        BatchItemResult(item_id=0, success=True, run_id="bt-0"),
    )
    temp_registry.add_item_result(
        batch.batch_id,
        BatchItemResult(item_id=1, success=False, error_category=ErrorCategory.DATA_ERROR),
    )
    temp_registry.add_item_result(
        batch.batch_id,
        BatchItemResult(item_id=2, success=True, run_id="bt-2"),
    )
    temp_registry.add_item_result(
        batch.batch_id,
        BatchItemResult(item_id=3, success=False, error_category=ErrorCategory.TIMEOUT),
    )

    batch = temp_registry.complete_batch(batch.batch_id)

    assert batch.status == BatchStatus.PARTIAL
    assert batch.success_rate() == 0.5
    assert batch.failure_rate() == 0.5


def test_get_batch(temp_registry):
    """Test retrieving batch."""
    original = temp_registry.create_batch(total_items=5)
    retrieved = temp_registry.get_batch(original.batch_id)

    assert retrieved.batch_id == original.batch_id
    assert retrieved.total_items == original.total_items
    assert retrieved.status == original.status


def test_get_nonexistent_batch(temp_registry):
    """Test retrieving nonexistent batch raises error."""
    with pytest.raises(FileNotFoundError, match="not found in registry"):
        temp_registry.get_batch("batch-nonexistent")


def test_list_batches_empty(temp_registry):
    """Test listing batches when registry is empty."""
    batches = temp_registry.list_batches()
    assert batches == []


def test_list_batches_returns_all(temp_registry):
    """Test listing batches returns all batches."""
    # Create 3 batches
    for i in range(3):
        temp_registry.create_batch(total_items=i + 1)

    batches = temp_registry.list_batches()
    assert len(batches) == 3


def test_list_batches_filter_by_status(temp_registry):
    """Test filtering batches by status."""
    # Create batches with different statuses
    batch1 = temp_registry.create_batch(total_items=1)
    batch2 = temp_registry.create_batch(total_items=1)
    batch3 = temp_registry.create_batch(total_items=1)

    temp_registry.update_status(batch2.batch_id, BatchStatus.RUNNING)
    temp_registry.update_status(batch3.batch_id, BatchStatus.COMPLETED)

    # Filter by PENDING
    pending = temp_registry.list_batches(status=BatchStatus.PENDING)
    assert len(pending) == 1
    assert pending[0].batch_id == batch1.batch_id

    # Filter by RUNNING
    running = temp_registry.list_batches(status=BatchStatus.RUNNING)
    assert len(running) == 1
    assert running[0].batch_id == batch2.batch_id


def test_list_batches_filter_by_date(temp_registry):
    """Test filtering batches by creation date."""
    temp_registry.create_batch(total_items=1)

    # Create cutoff time
    cutoff = datetime.now(UTC)

    # This batch should be after cutoff (or very close)
    temp_registry.create_batch(total_items=1)

    # Get all batches
    all_batches = temp_registry.list_batches()
    assert len(all_batches) == 2

    # Filter by cutoff should get at least recent batch
    recent = temp_registry.list_batches(since=cutoff)
    assert len(recent) >= 1


def test_list_batches_with_limit(temp_registry):
    """Test limiting number of results."""
    # Create 5 batches
    for i in range(5):
        temp_registry.create_batch(total_items=i + 1)

    # Limit to 3
    batches = temp_registry.list_batches(limit=3)
    assert len(batches) == 3


def test_get_failed_items(temp_registry):
    """Test retrieving failed items."""
    batch = temp_registry.create_batch(total_items=4)

    # Add mixed results
    temp_registry.add_item_result(
        batch.batch_id,
        BatchItemResult(item_id=0, success=True, run_id="bt-0"),
    )
    temp_registry.add_item_result(
        batch.batch_id,
        BatchItemResult(item_id=1, success=False, error_category=ErrorCategory.DATA_ERROR),
    )
    temp_registry.add_item_result(
        batch.batch_id,
        BatchItemResult(item_id=2, success=True, run_id="bt-2"),
    )
    temp_registry.add_item_result(
        batch.batch_id,
        BatchItemResult(item_id=3, success=False, error_category=ErrorCategory.TIMEOUT),
    )

    failed = temp_registry.get_failed_items(batch.batch_id)

    assert len(failed) == 2
    assert all(not item.success for item in failed)
    assert failed[0].item_id == 1
    assert failed[1].item_id == 3


def test_get_error_summary(temp_registry):
    """Test retrieving error summary."""
    batch = temp_registry.create_batch(total_items=5)

    # Add failures with different categories
    temp_registry.add_item_result(
        batch.batch_id,
        BatchItemResult(item_id=0, success=False, error_category=ErrorCategory.DATA_ERROR),
    )
    temp_registry.add_item_result(
        batch.batch_id,
        BatchItemResult(item_id=1, success=False, error_category=ErrorCategory.DATA_ERROR),
    )
    temp_registry.add_item_result(
        batch.batch_id,
        BatchItemResult(item_id=2, success=False, error_category=ErrorCategory.PARAMETER_ERROR),
    )

    summary = temp_registry.get_error_summary(batch.batch_id)

    assert summary[ErrorCategory.DATA_ERROR.value] == 2
    assert summary[ErrorCategory.PARAMETER_ERROR.value] == 1


def test_count(temp_registry):
    """Test counting batches."""
    assert temp_registry.count() == 0

    # Add some batches
    for i in range(3):
        temp_registry.create_batch(total_items=i + 1)

    assert temp_registry.count() == 3


def test_batch_exists(temp_registry):
    """Test checking if batch exists."""
    assert not temp_registry.batch_exists("batch-nonexistent")

    batch = temp_registry.create_batch(total_items=5)
    assert temp_registry.batch_exists(batch.batch_id)


def test_batch_is_complete(temp_registry):
    """Test is_complete method."""
    batch = temp_registry.create_batch(total_items=1)

    assert not batch.is_complete()  # PENDING

    batch = temp_registry.update_status(batch.batch_id, BatchStatus.RUNNING)
    assert not batch.is_complete()  # RUNNING

    batch = temp_registry.update_status(batch.batch_id, BatchStatus.COMPLETED)
    assert batch.is_complete()  # COMPLETED


def test_batch_success_rate(temp_registry):
    """Test success rate calculation."""
    batch = temp_registry.create_batch(total_items=4)

    # Add 3 successes and 1 failure
    for i in range(3):
        temp_registry.add_item_result(
            batch.batch_id,
            BatchItemResult(item_id=i, success=True, run_id=f"bt-{i}"),
        )
    temp_registry.add_item_result(
        batch.batch_id,
        BatchItemResult(item_id=3, success=False, error_category=ErrorCategory.DATA_ERROR),
    )

    batch = temp_registry.get_batch(batch.batch_id)
    assert batch.success_rate() == 0.75
    assert batch.failure_rate() == 0.25
