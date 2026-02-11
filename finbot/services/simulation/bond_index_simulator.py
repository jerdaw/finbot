import pandas as pd

from finbot.constants.path_constants import SIMULATIONS_DATA_DIR
from finbot.services.simulation.bond_ladder.bond_ladder_simulator import bond_ladder_simulator
from finbot.services.simulation.is_sufficiently_updated import is_sufficiently_updated
from finbot.utils.finance_utils.merge_price_histories import merge_price_histories


def bond_index_simulator(
    fund_name: str,
    min_maturity_years: int,
    max_maturity_years: int,
    overwrite_sim_with_index: bool = True,
    index_closes: pd.Series | None = None,
    save_index: bool = True,
    force_update: bool = False,
    additive_constant: float | None = None,
) -> pd.DataFrame:
    fund_path = SIMULATIONS_DATA_DIR / f"{fund_name}.parquet"
    if is_sufficiently_updated(fund_name) and not force_update:
        return pd.read_parquet(fund_path)
    print(f"Building {fund_name} Bond Index Simulation...")

    sim_df = bond_ladder_simulator(min_maturity_years, max_maturity_years)

    # Apply curve fitting
    mults = sim_df["Close"].pct_change() + 1
    if additive_constant:
        mults += additive_constant
    new_closes = mults.cumprod()
    new_closes.iloc[0] = 1
    sim_df["Close"] = new_closes

    # Overwrite simulated data with actual index data, where available
    if overwrite_sim_with_index and isinstance(index_closes, pd.Series):
        sim_df["Close"] = merge_price_histories(sim_df["Close"], index_closes, fix_point="end")

    sim_df["Change"] = sim_df["Close"].pct_change()

    if save_index:
        print(f"Saving {fund_name} to simulations db")
        sim_df.to_parquet(fund_path)

    return sim_df
