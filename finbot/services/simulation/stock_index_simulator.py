import pandas as pd

from finbot.constants.path_constants import SIMULATIONS_DATA_DIR
from finbot.services.simulation.is_sufficiently_updated import is_sufficiently_updated
from finbot.utils.finance_utils.merge_price_histories import merge_price_histories


def stock_index_simulator(
    fund_name: str,
    underlying_closes: pd.Series,
    underlying_yields: pd.Series | None,
    overwrite_sim_with_index: bool = True,
    index_closes: pd.Series | None = None,
    save_index: bool = True,
    force_update: bool = True,
    additive_constant: float | None = None,
) -> pd.DataFrame:
    fund_path = SIMULATIONS_DATA_DIR / f"{fund_name}.parquet"
    if not force_update and is_sufficiently_updated(fund_name):
        return pd.read_parquet(fund_path)
    print(f"Building {fund_name} Stock Index Simulation...")

    underlying_changes = underlying_closes.pct_change()
    if additive_constant:
        underlying_changes += additive_constant
    sim_mults = underlying_changes + 1
    if isinstance(underlying_yields, pd.Series):
        assert len(underlying_closes) == len(underlying_yields)
        sim_mults += underlying_yields
    sim_closes = sim_mults.cumprod()
    sim_closes.iloc[0] = 1
    sim_df = pd.DataFrame({"Close": sim_closes, "Change": sim_closes.pct_change()})
    sim_df.index = underlying_changes.index

    if overwrite_sim_with_index and isinstance(index_closes, pd.Series):
        sim_df["Close"] = merge_price_histories(sim_df["Close"], index_closes, fix_point="end")

    sim_df["Change"] = sim_df["Close"].pct_change()

    if save_index:
        print(f"Saving {fund_name} to simulations db")
        sim_df.to_parquet(fund_path)

    return sim_df
