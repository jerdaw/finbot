import warnings

import pandas as pd

from finbot.services.simulation.stock_index_simulator import stock_index_simulator
from finbot.utils.data_collection_utils.google_finance.get_xndx import get_xndx
from finbot.utils.data_collection_utils.scrapers.shiller.get_shiller_data import get_shiller_data
from finbot.utils.data_collection_utils.yfinance.get_history import get_history


def sim_sp500tr(
    overwrite_sim_with_index: bool = True,
    save_db: bool = True,
    force_update: bool = False,
    adj: float | None = None,
) -> pd.DataFrame:
    fund_name = "SP500TR_sim"
    price_hist = get_history("^GSPC")
    close_col = "Adj Close" if "Adj Close" in price_hist.columns else "Close"
    underlying_closes = price_hist[close_col]
    underlying_yields = _get_yield_from_shiller(price_hist)["Yield"][price_hist.index] / 245.65
    index_closes = get_history("^SP500TR")["Close"] if overwrite_sim_with_index else None
    sim_df = stock_index_simulator(
        fund_name=fund_name,
        underlying_closes=underlying_closes,
        underlying_yields=underlying_yields,
        overwrite_sim_with_index=overwrite_sim_with_index,
        index_closes=index_closes,
        save_index=save_db,
        force_update=force_update,
        additive_constant=adj if adj is not None else 1.667141575198267e-07,
    )
    return sim_df


def sim_nd100tr(
    overwrite_sim_with_index: bool = True,
    save_db: bool = True,
    force_update: bool = False,
    adj: float | None = None,
) -> pd.DataFrame:
    fund_name = "ND100TR_sim"
    price_hist = get_history("^NDX")
    close_col = "Adj Close" if "Adj Close" in price_hist.columns else "Close"
    underlying_closes = price_hist[close_col]
    warnings.warn(
        "The Nasdaq 100 TR index simulator inaccurately uses a single fixed value for dividend yields", stacklevel=2
    )
    cur_d_yields = 0.015 / 252
    underlying_yields = pd.Series([cur_d_yields] * len(underlying_closes))
    underlying_yields.index = underlying_closes.index
    if overwrite_sim_with_index:
        nd100tr_index = get_xndx()
        nd100tr_index.index = nd100tr_index.index.normalize()
        index_closes = nd100tr_index["Close"]
    else:
        index_closes = None
    sim_df = stock_index_simulator(
        fund_name=fund_name,
        underlying_closes=underlying_closes,
        underlying_yields=underlying_yields,
        overwrite_sim_with_index=overwrite_sim_with_index,
        index_closes=index_closes,
        save_index=save_db,
        force_update=force_update,
        additive_constant=adj if adj is not None else -2.2418516294175528e-05,
    )
    return sim_df


def _get_yield_from_shiller(price_index: pd.DataFrame) -> pd.DataFrame:
    shiller_data = get_shiller_data()
    yields = []
    for _r_idx, row in shiller_data.iterrows():
        rd = row["Dividend D"]
        rp = row["S&P Comp. P"]
        yld = rd / rp
        yields.append(yld)
    yields_df = pd.DataFrame({"Yield": yields})
    yields_df.index = shiller_data.index
    yields_df = pd.concat([yields_df, price_index], axis=1, join="outer")
    yields_df = yields_df["Yield"].to_frame()
    yields_df = yields_df.interpolate()
    return yields_df
