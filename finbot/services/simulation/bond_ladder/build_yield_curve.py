"""Build yield curve — replaces numba @njit with plain numpy."""
from __future__ import annotations

import numpy as np


def build_yield_curve(raw_rates: dict[str, float], yield_curve_size: int, periods_per_year: int) -> np.ndarray:
    """Splice different raw rates together to build a yield curve."""
    ordered_rates_names = [
        "DGS1",
        "DGS2",
        "DGS3",
        "DGS5",
        "DGS7",
        "DGS10",
        "DGS20",
        "DGS30",
        "GS1",
        "One-Year Interest Rate",
        "Long Interest Rate GS10",
        "GS2",
        "GS3",
        "GS5",
        "GS7",
        "GS10",
        "GS20",
        "GS30",
        "TB4WK",
        "CD1M",
        "TB3MS",
        "M1329AUSM193NNBR",
        "TB6MS",
    ]
    ordered_rates = [raw_rates.get(name, np.nan) for name in ordered_rates_names]
    ordered_rate_maturities = [
        n * periods_per_year - 1
        for n in (
            1,
            2,
            3,
            5,
            7,
            10,
            20,
            30,
            1,
            1,
            10,
            2,
            3,
            5,
            7,
            10,
            20,
            30,
            round(4 / 52),
            round(1 / 12),
            round(3 / 12),
            round(3 / 12),
            round(6 / 12),
        )
    ]

    assert len(ordered_rates) == len(ordered_rate_maturities)

    yield_curve = _splice_rates(yield_curve_size, ordered_rates, ordered_rate_maturities)
    return yield_curve


def _splice_rates(
    yield_curve_size: int,
    ordered_rates: list[float],
    ordered_rate_maturities: list[int],
) -> np.ndarray:
    yield_curve = np.full(yield_curve_size, np.nan)
    for i in range(len(ordered_rates)):
        rate = ordered_rates[i]
        rate_maturity_idx = ordered_rate_maturities[i]
        if not np.isnan(rate) and rate_maturity_idx < yield_curve_size and np.isnan(yield_curve[rate_maturity_idx]):
            yield_curve[rate_maturity_idx] = rate

    # Interpolate NaN gaps (replaces numba np_interpolate_array)
    nans = np.isnan(yield_curve)
    if nans.any() and not nans.all():
        x = np.arange(len(yield_curve))
        yield_curve[nans] = np.interp(x[nans], x[~nans], yield_curve[~nans])

    yield_curve /= 100  # Convert from form 3.71 to .0371
    return yield_curve
