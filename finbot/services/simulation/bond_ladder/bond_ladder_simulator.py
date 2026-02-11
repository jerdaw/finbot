"""Bond ladder simulator — replaces numba typed.Dict/List with plain Python."""

from __future__ import annotations

import pandas as pd

from constants.path_constants import SIMULATIONS_DATA_DIR
from finbot.services.simulation.bond_ladder.build_yield_curve import build_yield_curve
from finbot.services.simulation.bond_ladder.get_yield_history import get_yield_history
from finbot.services.simulation.bond_ladder.ladder import make_annual_ladder
from finbot.services.simulation.bond_ladder.loop import loop
from finbot.utils.finance_utils.get_periods_per_year import get_periods_per_year


def bond_ladder_simulator(
    min_maturity_years: int,
    max_maturity_years: int,
    yield_history: pd.DataFrame | None = None,
    save_db: bool = True,
) -> pd.DataFrame:
    """
    Simulate a bond ladder fund.

    Sources:
    https://www.bogleheads.org/forum/viewtopic.php?f=10&t=179425
    https://github.com/hoostus/prime-harvesting/blob/master/Bond%20Fund%20Simulator.ipynb
    """
    print("Getting yield_history for bond fund/index simulator...")
    if yield_history is None:
        yield_history = get_yield_history()

    print(f"Simulating {min_maturity_years}-{max_maturity_years} bond ladder fund...")
    periods_per_year = get_periods_per_year(yield_history)
    first_yh_row = yield_history.iloc[0]

    # Bootstrap initial rates
    bootstrap_rates = pd.DataFrame([first_yh_row for _ in range(periods_per_year - 1)])
    yield_history_concat = pd.concat((bootstrap_rates, yield_history), axis=0)

    min_periods = min_maturity_years * periods_per_year
    max_periods = max_maturity_years * periods_per_year

    # Convert first row to dict for build_yield_curve
    first_rates_dict = first_yh_row.to_dict()
    initial_yields = build_yield_curve(first_rates_dict, max_periods, periods_per_year)
    ladder = make_annual_ladder(max_periods, min_periods, initial_yields, periods_per_year)

    # Convert yield history to list of (timestamp, rates_dict) tuples
    yield_history_rows = [(idx, row.to_dict()) for idx, row in yield_history_concat.iterrows()]

    sim_closes = loop(ladder, yield_history_rows, max_periods, periods_per_year)

    fund_indexes = list(sim_closes.keys())
    fund_closes = pd.Series(list(sim_closes.values()))
    fund_closes *= 1 / fund_closes.iloc[0]  # Scale fund to start at 1
    fund_changes = fund_closes.pct_change()

    fund = pd.DataFrame({"Close": fund_closes.values, "Change": fund_changes.values})
    assert len(fund) == len(fund_closes) == len(fund_indexes) == len(yield_history)
    fund.index = fund_indexes

    if save_db:
        _save_fund_to_db(fund)

    return fund


def _save_fund_to_db(df: pd.DataFrame) -> None:
    file_name = "ltt_bond_index_simulation.parquet"
    print(f"Saving {file_name} to simulations db")
    df.to_parquet(SIMULATIONS_DATA_DIR / file_name)
