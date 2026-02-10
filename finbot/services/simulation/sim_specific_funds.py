import pandas as pd

from constants.path_constants import SIMULATIONS_DATA_DIR
from finbot.services.simulation.fund_simulator import fund_simulator
from finbot.services.simulation.is_sufficiently_updated import is_sufficiently_updated
from finbot.services.simulation.sim_specific_bond_indexes import sim_idcot1tr, sim_idcot7tr, sim_idcot20tr
from finbot.services.simulation.sim_specific_stock_indexes import sim_nd100tr, sim_sp500tr
from finbot.utils.data_collection_utils.yfinance.get_history import get_history
from finbot.utils.finance_utils.merge_price_histories import merge_price_histories


def _sim_fund(
    fund_name: str,
    underlying_func,
    leverage_mult: float,
    annual_er_pct: float,
    percent_daily_spread_cost: float,
    fund_swap_pct: float,
    additive_constant_default: float,
    underlying=None,
    libor_yield_df=None,
    save_sim: bool = True,
    force_update: bool = False,
    adj=None,
    overwrite_sim_with_fund: bool = True,
) -> pd.DataFrame:
    """Generic fund simulation helper to reduce repetition."""
    fund_path = SIMULATIONS_DATA_DIR / f"{fund_name}.parquet"
    if is_sufficiently_updated(fund_name) and not force_update:
        return pd.read_parquet(fund_path)

    fund = fund_simulator(
        price_df=underlying_func() if underlying is None else underlying,
        leverage_mult=leverage_mult,
        annual_er_pct=annual_er_pct,
        percent_daily_spread_cost=percent_daily_spread_cost,
        fund_swap_pct=fund_swap_pct,
        periods_per_year=252,
        multiplicative_constant=1,
        additive_constant=adj if adj is not None else additive_constant_default,
        libor_yield_df=libor_yield_df,
    )

    if overwrite_sim_with_fund:
        ticker = fund_name.split("_")[0]
        try:
            actual_close = get_history(ticker, adjust_price=True)["Close"]
            fund["Close"] = merge_price_histories(fund["Close"], actual_close, fix_point="end")
            fund["Close"] *= actual_close.iloc[-1] / fund.iloc[-1]["Close"]
        except Exception:
            pass  # Fund may not have actual data available

    if save_sim:
        fund.to_parquet(fund_path)
    return fund


# S&P 500 Fund Simulations
def sim_spy(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    return _sim_fund(
        "SPY_sim",
        sim_sp500tr,
        1,
        0.0945 / 100,
        0,
        0,
        8.808908907942556e-07,
        underlying,
        libor_yield_df,
        save_sim,
        force_update,
        adj,
        overwrite_sim_with_fund,
    )


def sim_sso(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    return _sim_fund(
        "SSO_sim",
        sim_sp500tr,
        2,
        0.89 / 100,
        0.01 / 100,
        1.3 / 2,
        4.0651890220138234e-05,
        underlying,
        libor_yield_df,
        save_sim,
        force_update,
        adj,
        overwrite_sim_with_fund,
    )


def sim_upro(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    return _sim_fund(
        "UPRO_sim",
        sim_sp500tr,
        3,
        0.91 / 100,
        0.015 / 100,
        2.5 / 3,
        6.801033362864044e-05,
        underlying,
        libor_yield_df,
        save_sim,
        force_update,
        adj,
        overwrite_sim_with_fund,
    )


# Nasdaq 100 Fund Simulations
def sim_qqq(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    return _sim_fund(
        "QQQ_sim",
        sim_nd100tr,
        1,
        0.2 / 100,
        0,
        0,
        -2.4360845949314585e-06,
        underlying,
        libor_yield_df,
        save_sim,
        force_update,
        adj,
        overwrite_sim_with_fund,
    )


def sim_qld(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    return _sim_fund(
        "QLD_sim",
        sim_nd100tr,
        2,
        0.95 / 100,
        0.015 / 100,
        1.3 / 2,
        6.412501098908426e-05,
        underlying,
        libor_yield_df,
        save_sim,
        force_update,
        adj,
        overwrite_sim_with_fund,
    )


def sim_tqqq(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    return _sim_fund(
        "TQQQ_sim",
        sim_nd100tr,
        3,
        0.95 / 100,
        0.01 / 100,
        2.5 / 3,
        2.4468046610555124e-05,
        underlying,
        libor_yield_df,
        save_sim,
        force_update,
        adj,
        overwrite_sim_with_fund,
    )


# Long Term US Treasury Fund Simulations
def sim_tlt(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    return _sim_fund(
        "TLT_sim",
        sim_idcot20tr,
        1,
        0.15 / 100,
        0,
        0,
        3.5764777900282787e-06,
        underlying,
        libor_yield_df,
        save_sim,
        force_update,
        adj,
        overwrite_sim_with_fund,
    )


def sim_ubt(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    return _sim_fund(
        "UBT_sim",
        sim_idcot20tr,
        2,
        0.95 / 100,
        0.01 / 100,
        1.3 / 2,
        6.021317309256665e-05,
        underlying,
        libor_yield_df,
        save_sim,
        force_update,
        adj,
        overwrite_sim_with_fund,
    )


def sim_tmf(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    return _sim_fund(
        "TMF_sim",
        sim_idcot20tr,
        3,
        1.06 / 100,
        0.01 / 100,
        2.5 / 3,
        7.014463531693148e-05,
        underlying,
        libor_yield_df,
        save_sim,
        force_update,
        adj,
        overwrite_sim_with_fund,
    )


# Intermediate Term US Treasury Fund Simulations
def sim_ief(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    return _sim_fund(
        "IEF_sim",
        sim_idcot7tr,
        1,
        0.15 / 100,
        0,
        0,
        2.2816511415927623e-06,
        underlying,
        libor_yield_df,
        save_sim,
        force_update,
        adj,
        overwrite_sim_with_fund,
    )


def sim_ust(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    return _sim_fund(
        "UST_sim",
        sim_idcot7tr,
        2,
        0.95 / 100,
        0.01 / 100,
        1.3 / 2,
        6.456134479694582e-05,
        underlying,
        libor_yield_df,
        save_sim,
        force_update,
        adj,
        overwrite_sim_with_fund,
    )


def sim_tyd(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    return _sim_fund(
        "TYD_sim",
        sim_idcot7tr,
        3,
        1.07 / 100,
        0.01 / 100,
        2.5 / 3,
        9.993223451984391e-05,
        underlying,
        libor_yield_df,
        save_sim,
        force_update,
        adj,
        overwrite_sim_with_fund,
    )


# Short Term US Treasury Fund Simulations
def sim_shy(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    return _sim_fund(
        "SHY_sim",
        sim_idcot1tr,
        1,
        0.15 / 100,
        0,
        0,
        1.3278656100702214e-06,
        underlying,
        libor_yield_df,
        save_sim,
        force_update,
        adj,
        overwrite_sim_with_fund,
    )


def sim_2x_stt(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    return _sim_fund(
        "2x_stt_sim",
        sim_idcot1tr,
        2,
        0.95 / 100,
        0.01 / 100,
        1.3 / 2,
        6.456134479694582e-05,
        underlying,
        libor_yield_df,
        save_sim,
        force_update,
        adj,
        False,
    )


def sim_3x_stt(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    return _sim_fund(
        "3x_stt_sim",
        sim_idcot1tr,
        3,
        1.07 / 100,
        0.01 / 100,
        2.5 / 3,
        9.993223451984391e-05,
        underlying,
        libor_yield_df,
        save_sim,
        force_update,
        adj,
        False,
    )


def sim_ntsx(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    fund_name = "NTSX_sim"
    fund_path = SIMULATIONS_DATA_DIR / f"{fund_name}.parquet"
    if is_sufficiently_updated(fund_name) and not force_update:
        return pd.read_parquet(fund_path)

    spy_change = sim_spy()["Close"].pct_change() * 0.9
    tlt_change = sim_tlt()["Close"].pct_change() * 0.0
    ief_change = sim_ief()["Close"].pct_change() * 0.4
    shy_change = sim_shy()["Close"].pct_change() * 0.2

    merged = pd.DataFrame({"SPY": spy_change, "TLT": tlt_change, "IEF": ief_change, "SHY": shy_change}).interpolate()
    merged["Change"] = merged.sum(axis=1)
    merged["Change"] += -4.858471304152913e-05 if adj is None else adj
    merged["Change"] += 1
    merged["Close"] = merged["Change"].cumprod()
    merged["Change"] = merged["Close"].pct_change()
    fund = merged[["Close", "Change"]]

    if overwrite_sim_with_fund:
        try:
            actual_close = get_history("NTSX", adjust_price=True)["Close"]
            fund["Close"] = merge_price_histories(fund["Close"], actual_close, fix_point="end")
        except Exception:
            pass

    if save_sim:
        fund.to_parquet(fund_path)
    return fund
