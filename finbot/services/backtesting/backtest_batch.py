import time
from itertools import product

import pandas as pd
from tqdm.contrib.concurrent import process_map

from finbot.core.contracts.batch import BatchItemResult, BatchStatus
from finbot.services.backtesting.batch_registry import BatchRegistry
from finbot.services.backtesting.error_categorizer import categorize_error
from finbot.services.backtesting.run_backtest import run_backtest


def _get_starts_from_steps(latest_start_date, earliest_end_date, start_step, duration):
    starts = []
    cur_start = latest_start_date
    cur_end = cur_start + duration
    while cur_end < earliest_end_date:
        starts.append(cur_start)
        cur_start += start_step
        cur_end = cur_start + duration
    return starts


def _run_backtest_safely(task: tuple[int, tuple]) -> dict:
    """Run one batch task and capture success/error metadata."""
    item_id, comb = task
    start_time = time.perf_counter()

    try:
        result_df = run_backtest(comb)
        return {
            "item_id": item_id,
            "success": True,
            "result": result_df,
            "duration_seconds": time.perf_counter() - start_time,
        }
    except Exception as exc:  # pragma: no cover - covered via monkeypatched tests
        return {
            "item_id": item_id,
            "success": False,
            "error_message": str(exc),
            "error_category": categorize_error(exc),
            "duration_seconds": time.perf_counter() - start_time,
        }


def backtest_batch(**kwargs):  # noqa: C901 - Complex parameter validation logic
    track_batch = kwargs.pop("track_batch", False)
    batch_registry = kwargs.pop("batch_registry", None)

    if track_batch and batch_registry is None:
        raise ValueError("track_batch=True requires batch_registry")
    if batch_registry is not None and not isinstance(batch_registry, BatchRegistry):
        raise TypeError("batch_registry must be a BatchRegistry instance")

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

    task_inputs = tuple(enumerate(combs))
    execution_results = process_map(
        _run_backtest_safely,
        task_inputs,
        total=n_combs,
        desc="Performing backtests",
        chunksize=1,
        smoothing=0.1,
    )

    successful_results: list[pd.DataFrame] = []
    for item in execution_results:
        batch_registry.add_item_result(
            batch.batch_id,
            BatchItemResult(
                item_id=item["item_id"],
                success=item["success"],
                run_id=None,
                error_message=item.get("error_message"),
                error_category=item.get("error_category"),
                duration_seconds=item["duration_seconds"],
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
