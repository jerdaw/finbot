"""Bond ladder simulation loop — replaces numba @njit with plain Python."""
from __future__ import annotations

import numpy as np

from finbot.services.simulation.bond_ladder.build_yield_curve import build_yield_curve
from finbot.services.simulation.bond_ladder.ladder import BondLadder


def loop(
    ladder: BondLadder,
    yield_history_rows: list[tuple],
    max_periods: int,
    periods_per_year: int,
) -> dict:
    """
    Loop through each date/day of fund for simulation.

    Args:
        ladder: Initialized BondLadder instance.
        yield_history_rows: List of (timestamp, rates_dict) tuples.
        max_periods: Maximum maturity in periods.
        periods_per_year: Number of periods per year.

    Returns:
        dict mapping timestamps to NAV values.
    """
    closes: dict = {}

    for date, current_rates in yield_history_rows:
        yield_curve = build_yield_curve(current_rates, max_periods, periods_per_year)
        ladder, nav = iterate_fund(ladder, yield_curve, max_periods)
        closes[date] = nav

    return closes


def iterate_fund(
    ladder: BondLadder,
    yield_curve: np.ndarray,
    max_maturity: int,
) -> tuple[BondLadder, float]:
    """Perform single day operations of bond fund."""
    # Update remaining bond maturity/duration
    ladder.reduce_maturities()

    # Generate payments from currently held bonds
    ladder.generate_payments()

    # Sell bonds under minimum maturity
    sold_bonds = ladder.sell_bonds(yield_curve)

    # Only buy a new bond if we actually sold one
    if sold_bonds:
        ladder.buy_bond(yield_curve[max_maturity - 1], max_maturity)

    # Calculate NAV after sell/buy
    nav = ladder.get_nav(yield_curve)

    return ladder, nav
