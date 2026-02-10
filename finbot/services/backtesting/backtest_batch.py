from itertools import product

import pandas as pd
from tqdm.contrib.concurrent import process_map

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


def backtest_batch(**kwargs):
    kwargs["plot"] = False
    for kw in kwargs:
        if not isinstance(kwargs[kw], tuple | list):
            kwargs[kw] = (kwargs[kw],)

    latest_start_date = max(h.index[0] for ph in kwargs["price_histories"] for h in ph.values())
    if None not in kwargs["start"]:
        latest_start_date = max(latest_start_date, max(kwargs["start"]))
    earliest_end_date = min(h.index[-1] for ph in kwargs["price_histories"] for h in ph.values())
    if None not in kwargs["end"]:
        earliest_end_date = max(earliest_end_date, max(kwargs["end"]))

    for i, ph in enumerate(kwargs["price_histories"]):
        for k, v in ph.items():
            kwargs["price_histories"][i][k] = v.truncate(before=latest_start_date, after=earliest_end_date)

    assert len(kwargs["duration"]) == 1 and len(kwargs["start_step"]) == 1
    start_step = kwargs["start_step"][0]
    duration = kwargs["duration"][0]
    if start_step is not None and duration is not None:
        starts = _get_starts_from_steps(latest_start_date, earliest_end_date, start_step, duration)
        kwargs["start"] = starts

    combs = tuple(product(*kwargs.values()))
    n_combs = len(combs)
    print(f"Running {n_combs} backtests...")

    results = process_map(run_backtest, combs, total=n_combs, desc="Performing backtests", chunksize=1, smoothing=0.1)
    results = pd.concat(results, axis=0).reset_index(drop=True)
    return results
