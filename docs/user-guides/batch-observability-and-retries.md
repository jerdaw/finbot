# Batch Observability and Retries

This guide covers opt-in batch tracking and retry behavior in `backtest_batch`.

## Batch Tracking

Enable tracking by passing `track_batch=True` and a `BatchRegistry` instance.

```python
from pathlib import Path

from finbot.services.backtesting.backtest_batch import backtest_batch
from finbot.services.backtesting.batch_registry import BatchRegistry

registry = BatchRegistry(Path("finbot/data/backtests/batches"))

result_df = backtest_batch(
    track_batch=True,
    batch_registry=registry,
    # ... regular batch args ...
)
```

## Retry Controls

Retries are optional and only active when tracking is enabled.

```python
result_df = backtest_batch(
    track_batch=True,
    batch_registry=registry,
    retry_failed=True,
    max_retry_attempts=2,
    retry_backoff_seconds=0.1,
    # ... regular batch args ...
)
```

## Retry Policy

- Retries are attempted for transient failures:
  - `ErrorCategory.TIMEOUT`
  - `ErrorCategory.MEMORY_ERROR`
  - errors with transient keywords (`network`, `connection`, `timeout`, `resource`, `temporary`, etc.)
- Deterministic failures (for example, bad parameters/data shape) are not retried.

## Recorded Metadata

Each item now persists:

- `attempt_count`: final attempt number for that item.
- `final_attempt_success`: final result boolean.

## Failure Semantics

- If all items fail after retries, `backtest_batch` raises `RuntimeError`.
- Partial success returns concatenated successful results and records failures in the batch registry.

## Notes

- Defaults are conservative (`retry_failed=False`, `max_retry_attempts=1`).
- Existing non-tracked behavior is unchanged.
