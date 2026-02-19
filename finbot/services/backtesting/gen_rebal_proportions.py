from __future__ import annotations

from itertools import product

import numpy as np
from tqdm.contrib.concurrent import process_map


def gen_rebal_proportions(
    definition: float,
    n_stocks: int,
    n_groupings: int,
    custom_mins: list[float] | None = None,
    custom_maxs: list[float] | None = None,
) -> tuple[tuple[float, ...], ...]:
    if custom_mins is None:
        custom_mins = [0 for _ in range(round(n_stocks // n_groupings))]
    if custom_maxs is None:
        custom_maxs = [1 for _ in range(round(n_stocks // n_groupings))]

    round_to = round(np.ceil(np.log10(1 / definition)))

    ranges = []
    for i in range(round(n_stocks // n_groupings)):
        range_start = round(custom_mins[i], round_to)
        range_end = round(custom_maxs[i], round_to)
        linspace = []
        step = 1 / 10**round_to
        n = round(range_start - definition + step, round_to)
        while n <= range_end:
            if (
                round(n % definition, round_to) == 0 or n in (range_start, range_end)
            ) and range_start <= n <= range_end:
                linspace.append(n)
            n = round(n + step, round_to)
        ranges.append(list(linspace))

    start_prods = product(*ranges[: round(len(ranges) / 2)])
    end_prods = product(*ranges[round(len(ranges) / 2) :])
    n_prods = np.prod([len(r) for r in ranges])

    prods = product(start_prods, end_prods)
    results = tuple(
        n
        for n in process_map(
            _parse_prods,
            prods,
            total=n_prods,
            chunksize=max(1, round(n_prods / 200)),
            desc="Generating rebalance proportion options",
        )
        if n is not None
    )
    return results


def _parse_prods(prod: tuple[tuple[float, ...], tuple[float, ...]]) -> tuple[float, ...] | None:
    if round(sum(prod[0]) + sum(prod[1]), 2) == 1:
        return prod[0] + prod[1]
    return None
