import time
from itertools import product
from typing import Any

import pandas as pd
from tqdm.contrib.concurrent import process_map

from finbot.core.contracts.batch import BatchItemResult, BatchStatus, ErrorCategory
from finbot.services.backtesting.batch_registry import BatchRegistry
from finbot.services.backtesting.error_categorizer import categorize_error
from finbot.services.backtesting.run_backtest import run_backtest


def _get_starts_from_steps(
    latest_start_date: pd.Timestamp,
    earliest_end_date: pd.Timestamp,
    start_step: pd.Timedelta,
    duration: pd.Timedelta,
) -> list[pd.Timestamp]:
    starts: list[pd.Timestamp] = []
    cur_start = latest_start_date
    cur_end = cur_start + duration
    while cur_end < earliest_end_date:
        starts.append(cur_start)
        cur_start += start_step
        cur_end = cur_start + duration
    return starts


def _run_backtest_safely(task: tuple[int, int, tuple]) -> dict:
    """Run one batch task and capture success/error metadata."""
    item_id, attempt_count, comb = task
    start_time = time.perf_counter()

    try:
        result_df = run_backtest(comb)
        return {
            "item_id": item_id,
            "success": True,
            "result": result_df,
            "duration_seconds": time.perf_counter() - start_time,
            "attempt_count": attempt_count,
        }
    except Exception as exc:  # pragma: no cover - covered via monkeypatched tests
        return {
            "item_id": item_id,
            "success": False,
            "error_message": str(exc),
            "error_category": categorize_error(exc),
            "duration_seconds": time.perf_counter() - start_time,
            "attempt_count": attempt_count,
        }


def _is_retryable_failure(item: dict) -> bool:
    """Return True when a failed item should be retried."""
    if item.get("success", False):
        return False

    category = item.get("error_category")
    if category in {ErrorCategory.TIMEOUT, ErrorCategory.MEMORY_ERROR}:
        return True

    message = str(item.get("error_message", "")).lower()
    transient_keywords = (
        "timeout",
        "timed out",
        "connection",
        "network",
        "temporary",
        "resource",
        "busy",
        "unavailable",
    )
    return any(keyword in message for keyword in transient_keywords)


def backtest_batch(**kwargs: Any) -> pd.DataFrame:  # noqa: C901 - Complex parameter validation logic
    track_batch = kwargs.pop("track_batch", False)
    batch_registry = kwargs.pop("batch_registry", None)
    retry_failed = kwargs.pop("retry_failed", False)
    max_retry_attempts = kwargs.pop("max_retry_attempts", 1)
    retry_backoff_seconds = kwargs.pop("retry_backoff_seconds", 0.0)

    if track_batch and batch_registry is None:
        raise ValueError("track_batch=True requires batch_registry")
    if batch_registry is not None and not isinstance(batch_registry, BatchRegistry):
        raise TypeError("batch_registry must be a BatchRegistry instance")
    if max_retry_attempts < 1:
        raise ValueError("max_retry_attempts must be >= 1")
    if retry_backoff_seconds < 0:
        raise ValueError("retry_backoff_seconds must be >= 0")
    if retry_failed and not track_batch:
        raise ValueError("retry_failed=True requires track_batch=True")

    kwargs["plot"] = False
    for kw in kwargs:
        if not isinstance(kwargs[kw], tuple | list):
            kwargs[kw] = (kwargs[kw],)

    # Validate price_histories is not empty
    if not kwargs.get("price_histories") or len(kwargs["price_histories"]) == 0:
        raise ValueError("price_histories cannot be empty")

    # Validate that all price_histories have data
    for i, ph in enumerate(kwargs["price_histories"]):
        if not ph or len(ph) == 0:
            raise ValueError(f"price_histories[{i}] is empty")
        for key, hist in ph.items():
            if hist is None or len(hist) == 0:
                raise ValueError(f"price_histories[{i}]['{key}'] is empty")

    latest_start_date = max(h.index[0] for ph in kwargs["price_histories"] for h in ph.values())
    if None not in kwargs["start"]:
        latest_start_date = max(latest_start_date, max(kwargs["start"]))
    earliest_end_date = min(h.index[-1] for ph in kwargs["price_histories"] for h in ph.values())
    if None not in kwargs["end"]:
        earliest_end_date = max(earliest_end_date, max(kwargs["end"]))

    for i, ph in enumerate(kwargs["price_histories"]):
        for k, v in ph.items():
            kwargs["price_histories"][i][k] = v.truncate(before=latest_start_date, after=earliest_end_date)

    # Replace assert with explicit validation
    if len(kwargs["duration"]) != 1 or len(kwargs["start_step"]) != 1:
        raise ValueError(
            f"duration and start_step must have exactly 1 element each. "
            f"Got duration length: {len(kwargs['duration'])}, start_step length: {len(kwargs['start_step'])}"
        )
    start_step = kwargs["start_step"][0]
    duration = kwargs["duration"][0]
    if start_step is not None and duration is not None:
        starts = _get_starts_from_steps(latest_start_date, earliest_end_date, start_step, duration)
        kwargs["start"] = starts

    combs = tuple(product(*kwargs.values()))
    n_combs = len(combs)
    print(f"Running {n_combs} backtests...")

    if not track_batch:
        results = process_map(
            run_backtest, combs, total=n_combs, desc="Performing backtests", chunksize=1, smoothing=0.1
        )
        results = pd.concat(results, axis=0).reset_index(drop=True)
        return results

    assert batch_registry is not None
    configuration = {key: [str(value) for value in values] for key, values in kwargs.items()}
    batch = batch_registry.create_batch(total_items=n_combs, configuration=configuration)
    batch_registry.update_status(batch.batch_id, BatchStatus.RUNNING)

    task_inputs = tuple((item_id, 1, comb) for item_id, comb in enumerate(combs))
    execution_results = process_map(
        _run_backtest_safely,
        task_inputs,
        total=n_combs,
        desc="Performing backtests",
        chunksize=1,
        smoothing=0.1,
    )

    latest_results_by_item = {item["item_id"]: item for item in execution_results}

    if retry_failed and max_retry_attempts > 1:
        for attempt_count in range(2, max_retry_attempts + 1):
            retry_task_inputs = tuple(
                (item_id, attempt_count, combs[item_id])
                for item_id, item in sorted(latest_results_by_item.items())
                if _is_retryable_failure(item)
            )
            if not retry_task_inputs:
                break

            if retry_backoff_seconds > 0:
                time.sleep(retry_backoff_seconds)

            retry_results = process_map(
                _run_backtest_safely,
                retry_task_inputs,
                total=len(retry_task_inputs),
                desc=f"Retrying failed backtests (attempt {attempt_count})",
                chunksize=1,
                smoothing=0.1,
            )
            for item in retry_results:
                latest_results_by_item[item["item_id"]] = item

    successful_results: list[pd.DataFrame] = []
    for item in (latest_results_by_item[item_id] for item_id in sorted(latest_results_by_item)):
        batch_registry.add_item_result(
            batch.batch_id,
            BatchItemResult(
                item_id=item["item_id"],
                success=item["success"],
                run_id=None,
                error_message=item.get("error_message"),
                error_category=item.get("error_category"),
                duration_seconds=item["duration_seconds"],
                attempt_count=item.get("attempt_count", 1),
                final_attempt_success=item["success"],
            ),
        )
        if item["success"]:
            successful_results.append(item["result"])

    completed = batch_registry.complete_batch(batch.batch_id)
    if not successful_results:
        raise RuntimeError(
            f"All batch items failed (batch_id={completed.batch_id}, failed={completed.failed_items}/{completed.total_items})"
        )

    return pd.concat(successful_results, axis=0).reset_index(drop=True)
