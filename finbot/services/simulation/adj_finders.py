import numpy as np
import pandas as pd


def get_best_corr_iterative(
    sim_closes: pd.Series,
    actual_closes: pd.Series,
    start: float | None = None,
    stop: float | None = None,
    n_steps: int = 10000,
) -> tuple[float, float]:
    sim_changes = sim_closes.pct_change()
    sim_changes.iloc[0] = 0

    if start is None:
        start = -abs(sim_changes.mean())
    if stop is None:
        stop = abs(sim_changes.mean())

    best_corr = -float("inf")
    best_adj = 0.0

    for adj in np.linspace(start, stop, n_steps):
        adj_mults = sim_changes + (adj + 1)
        adj_closes = adj_mults.cumprod()
        adj_closes.iloc[0] = 1
        adj_corr = adj_closes.corr(actual_closes)
        if adj_corr > best_corr:
            best_corr = adj_corr
            best_adj = adj

    return best_adj, best_corr


def get_best_corr_search(
    sim_closes: pd.Series,
    actual_closes: pd.Series,
    start: float | None = None,
    stop: float | None = None,
    max_depth: int = 100,
    n_parts: int = 4,
) -> tuple[float, float]:
    if start is None:
        start = -abs(sim_closes.pct_change().mean())
    if stop is None:
        stop = abs(sim_closes.pct_change().mean())

    orig_start = start
    orig_stop = stop
    overall_best_corr = -float("inf")
    overall_best_adj = 0.0

    for _cur_depth in range(max_depth):
        parts = np.linspace(start, stop, n_parts)
        if len(parts) < n_parts:
            break

        best_adj, best_corr = get_best_corr_iterative(sim_closes, actual_closes, start, stop, n_parts)
        best_part_idx = np.where(parts == best_adj)[0][0]
        if best_part_idx == 0:
            stop = max(orig_start, min(orig_stop, parts[1]))
        elif best_part_idx == 1:
            stop = max(orig_start, min(orig_stop, parts[2]))
        elif best_part_idx == 2:
            start = max(orig_start, min(orig_stop, parts[1]))
        elif best_part_idx == 3:
            start = max(orig_start, min(orig_stop, parts[2]))

        if best_corr > overall_best_corr:
            overall_best_corr = best_corr
            overall_best_adj = best_adj

    return overall_best_adj, overall_best_corr
