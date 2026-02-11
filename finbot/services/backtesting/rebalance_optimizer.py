from itertools import product

import pandas as pd
from tqdm.contrib.concurrent import process_map

from finbot.services.backtesting.avg_stepped_results import avg_stepped_results
from finbot.services.backtesting.run_backtest import run_backtest


def rebalance_optimizer(**kwargs):
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

    n_stocks = len(kwargs["price_histories"][0])
    step = round(0.01, 2)
    best_ratios = [round(1 / step) for _ in range(n_stocks)]

    kwargs_copy = kwargs.copy()
    for iteration in range(1000):
        cur_step = max(step / 10, 0.93**iteration)
        cur_test_props = []
        for i in range(n_stocks):
            cur_ratios = best_ratios.copy()
            cur_ratios[i] += round(sum(best_ratios) * cur_step)
            cur_ratios = [n / round(sum(cur_ratios)) for n in cur_ratios]
            cur_test_props.append(cur_ratios)

        kwargs_copy["strat_kwargs"] = [
            {"rebal_proportions": props, "rebal_interval": kwargs_copy["strat_kwargs"][0]["rebal_interval"]}
            for props in cur_test_props
        ]
        combs = tuple(product(*kwargs_copy.values()))
        results = process_map(run_backtest, combs, disable=False)
        results = pd.concat(results, axis=0).reset_index(drop=True)
        if len(set(results["Start Date"])) > 1:
            results = avg_stepped_results(results)
        results.sort_values("CAGR", ascending=False, inplace=True)
        best = results.iloc[0]["rebal_proportions (p)"]
        best_idx = next(i for i in range(n_stocks) if str(cur_test_props[i]) == best)
        best_ratios[best_idx] += round(sum(best_ratios) * cur_step)
    return results
