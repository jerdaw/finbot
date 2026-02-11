from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd

from finbot.config import logger
from finbot.constants.path_constants import SIMULATIONS_DATA_DIR
from finbot.services.simulation.fund_simulator import fund_simulator
from finbot.services.simulation.is_sufficiently_updated import is_sufficiently_updated
from finbot.services.simulation.sim_specific_bond_indexes import sim_idcot1tr, sim_idcot7tr, sim_idcot20tr
from finbot.services.simulation.sim_specific_stock_indexes import sim_nd100tr, sim_sp500tr
from finbot.utils.data_collection_utils.yfinance.get_history import get_history
from finbot.utils.finance_utils.merge_price_histories import merge_price_histories

# Additive constants for curve fitting (empirically determined)
# These constants adjust simulated returns to better match actual fund performance
ADDITIVE_CONSTANT_SPY = 8.808908907942556e-07
ADDITIVE_CONSTANT_QQQ = -2.4360845949314585e-06
ADDITIVE_CONSTANT_TLT = 3.5764777900282787e-06
ADDITIVE_CONSTANT_IEF = 2.2816511415927623e-06
ADDITIVE_CONSTANT_SHY = 1.3278656100702214e-06


@dataclass
class FundConfig:
    """Configuration for fund simulation parameters.

    Attributes:
        ticker: Fund ticker symbol (e.g., "SPY", "UPRO")
        name: Internal simulation name (e.g., "SPY_sim")
        underlying_func: Function that returns the underlying index price history
        leverage_mult: Leverage multiplier (1.0 = unleveraged, 2.0 = 2x, 3.0 = 3x)
        annual_er_pct: Annual expense ratio as a decimal (e.g., 0.0945/100 for 0.0945%)
        percent_daily_spread_cost: Daily spread cost as a decimal (e.g., 0.01/100 for 0.01%)
        fund_swap_pct: Fund swap percentage (typically leverage_ratio * 1.3 / leverage_mult)
        additive_constant: Empirically determined constant to match actual fund performance
        overwrite_sim_with_fund: Whether to overwrite simulation with actual fund data
    """

    ticker: str
    name: str
    underlying_func: Callable
    leverage_mult: float
    annual_er_pct: float
    percent_daily_spread_cost: float = 0.0
    fund_swap_pct: float = 0.0
    additive_constant: float = 0.0
    overwrite_sim_with_fund: bool = True


# Registry mapping ticker symbols to fund configurations
FUND_CONFIGS: dict[str, FundConfig] = {
    # S&P 500 Funds
    "SPY": FundConfig("SPY", "SPY_sim", sim_sp500tr, 1.0, 0.0945 / 100, 0.0, 0.0, ADDITIVE_CONSTANT_SPY),
    "SSO": FundConfig("SSO", "SSO_sim", sim_sp500tr, 2.0, 0.89 / 100, 0.01 / 100, 1.3 / 2, 4.0651890220138234e-05),
    "UPRO": FundConfig("UPRO", "UPRO_sim", sim_sp500tr, 3.0, 0.91 / 100, 0.015 / 100, 2.5 / 3, 6.801033362864044e-05),
    # Nasdaq-100 Funds
    "QQQ": FundConfig("QQQ", "QQQ_sim", sim_nd100tr, 1.0, 0.2 / 100, 0.0, 0.0, ADDITIVE_CONSTANT_QQQ),
    "QLD": FundConfig("QLD", "QLD_sim", sim_nd100tr, 2.0, 0.95 / 100, 0.015 / 100, 1.3 / 2, 6.412501098908426e-05),
    "TQQQ": FundConfig("TQQQ", "TQQQ_sim", sim_nd100tr, 3.0, 0.95 / 100, 0.01 / 100, 2.5 / 3, 2.4468046610555124e-05),
    # Long-Term US Treasury Funds (20Y)
    "TLT": FundConfig("TLT", "TLT_sim", sim_idcot20tr, 1.0, 0.15 / 100, 0.0, 0.0, ADDITIVE_CONSTANT_TLT),
    "UBT": FundConfig("UBT", "UBT_sim", sim_idcot20tr, 2.0, 0.95 / 100, 0.01 / 100, 1.3 / 2, 6.021317309256665e-05),
    "TMF": FundConfig("TMF", "TMF_sim", sim_idcot20tr, 3.0, 1.06 / 100, 0.01 / 100, 2.5 / 3, 7.014463531693148e-05),
    # Intermediate-Term US Treasury Funds (7-10Y)
    "IEF": FundConfig("IEF", "IEF_sim", sim_idcot7tr, 1.0, 0.15 / 100, 0.0, 0.0, ADDITIVE_CONSTANT_IEF),
    "UST": FundConfig("UST", "UST_sim", sim_idcot7tr, 2.0, 0.95 / 100, 0.01 / 100, 1.3 / 2, 6.456134479694582e-05),
    "TYD": FundConfig("TYD", "TYD_sim", sim_idcot7tr, 3.0, 1.07 / 100, 0.01 / 100, 2.5 / 3, 9.993223451984391e-05),
    # Short-Term US Treasury Funds (1-3Y)
    "SHY": FundConfig("SHY", "SHY_sim", sim_idcot1tr, 1.0, 0.15 / 100, 0.0, 0.0, ADDITIVE_CONSTANT_SHY),
    "2X_STT": FundConfig(
        "2X_STT", "2x_stt_sim", sim_idcot1tr, 2.0, 0.95 / 100, 0.01 / 100, 1.3 / 2, 6.456134479694582e-05, False
    ),
    "3X_STT": FundConfig(
        "3X_STT", "3x_stt_sim", sim_idcot1tr, 3.0, 1.07 / 100, 0.01 / 100, 2.5 / 3, 9.993223451984391e-05, False
    ),
}


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
            actual_close = get_history(ticker)["Close"]
            fund["Close"] = merge_price_histories(fund["Close"], actual_close, fix_point="end")
            fund["Close"] *= actual_close.iloc[-1] / fund.iloc[-1]["Close"]
        except (FileNotFoundError, KeyError, ValueError, IndexError) as e:
            logger.warning(f"Could not overwrite {fund_name} simulation with actual fund data for ticker {ticker}: {e}")

    if save_sim:
        fund.to_parquet(fund_path)
    return fund


def simulate_fund(
    ticker: str,
    underlying=None,
    libor_yield_df=None,
    save_sim: bool = True,
    force_update: bool = False,
    adj=None,
    overwrite_sim_with_fund: bool | None = None,
) -> pd.DataFrame:
    """Simulate any fund by ticker using configuration registry.

    This is the new recommended way to simulate funds. It uses a data-driven
    configuration approach that's easier to maintain and extend.

    Parameters:
        ticker: Fund ticker symbol (e.g., "SPY", "UPRO", "TQQQ")
        underlying: Pre-computed underlying index price history (optional)
        libor_yield_df: LIBOR yield data for swap cost calculation (optional)
        save_sim: Whether to save simulation to disk (default: True)
        force_update: Force regeneration even if cached version exists (default: False)
        adj: Override additive constant (default: use config value)
        overwrite_sim_with_fund: Override config setting for actual data merge

    Returns:
        DataFrame with simulated fund price history (columns: "Close", "Change")

    Raises:
        ValueError: If ticker is not in FUND_CONFIGS registry

    Example:
        >>> spy_sim = simulate_fund("SPY")
        >>> upro_sim = simulate_fund("UPRO", force_update=True)
    """
    ticker_upper = ticker.upper()
    if ticker_upper not in FUND_CONFIGS:
        available = ", ".join(sorted(FUND_CONFIGS.keys()))
        raise ValueError(f"Unknown fund ticker: {ticker}. Available funds: {available}")

    config = FUND_CONFIGS[ticker_upper]

    # Use config's overwrite setting unless explicitly overridden
    overwrite = config.overwrite_sim_with_fund if overwrite_sim_with_fund is None else overwrite_sim_with_fund

    return _sim_fund(
        config.name,
        config.underlying_func,
        config.leverage_mult,
        config.annual_er_pct,
        config.percent_daily_spread_cost,
        config.fund_swap_pct,
        config.additive_constant,
        underlying,
        libor_yield_df,
        save_sim,
        force_update,
        adj,
        overwrite,
    )


# S&P 500 Fund Simulations
def sim_spy(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    """Simulate SPY (S&P 500 ETF, 1x leverage).

    Deprecated: Use simulate_fund("SPY", ...) instead.
    """
    return simulate_fund("SPY", underlying, libor_yield_df, save_sim, force_update, adj, overwrite_sim_with_fund)


def sim_sso(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    """Simulate SSO (ProShares Ultra S&P500, 2x leverage).

    Deprecated: Use simulate_fund("SSO", ...) instead.
    """
    return simulate_fund("SSO", underlying, libor_yield_df, save_sim, force_update, adj, overwrite_sim_with_fund)


def sim_upro(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    """Simulate UPRO (ProShares UltraPro S&P500, 3x leverage).

    Deprecated: Use simulate_fund("UPRO", ...) instead.
    """
    return simulate_fund("UPRO", underlying, libor_yield_df, save_sim, force_update, adj, overwrite_sim_with_fund)


# Nasdaq 100 Fund Simulations
def sim_qqq(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    """Simulate QQQ (Invesco QQQ Trust, 1x Nasdaq-100).

    Deprecated: Use simulate_fund("QQQ", ...) instead.
    """
    return simulate_fund("QQQ", underlying, libor_yield_df, save_sim, force_update, adj, overwrite_sim_with_fund)


def sim_qld(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    """Simulate QLD (ProShares Ultra QQQ, 2x Nasdaq-100 leverage).

    Deprecated: Use simulate_fund("QLD", ...) instead.
    """
    return simulate_fund("QLD", underlying, libor_yield_df, save_sim, force_update, adj, overwrite_sim_with_fund)


def sim_tqqq(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    """Simulate TQQQ (ProShares UltraPro QQQ, 3x Nasdaq-100 leverage).

    Deprecated: Use simulate_fund("TQQQ", ...) instead.
    """
    return simulate_fund("TQQQ", underlying, libor_yield_df, save_sim, force_update, adj, overwrite_sim_with_fund)


# Long Term US Treasury Fund Simulations
def sim_tlt(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    """Simulate TLT (iShares 20+ Year Treasury Bond ETF, 1x).

    Deprecated: Use simulate_fund("TLT", ...) instead.
    """
    return simulate_fund("TLT", underlying, libor_yield_df, save_sim, force_update, adj, overwrite_sim_with_fund)


def sim_ubt(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    """Simulate UBT (ProShares Ultra 20+ Year Treasury, 2x leverage).

    Deprecated: Use simulate_fund("UBT", ...) instead.
    """
    return simulate_fund("UBT", underlying, libor_yield_df, save_sim, force_update, adj, overwrite_sim_with_fund)


def sim_tmf(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    """Simulate TMF (Direxion Daily 20+ Year Treasury Bull 3x, 3x leverage).

    Deprecated: Use simulate_fund("TMF", ...) instead.
    """
    return simulate_fund("TMF", underlying, libor_yield_df, save_sim, force_update, adj, overwrite_sim_with_fund)


# Intermediate Term US Treasury Fund Simulations
def sim_ief(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    """Simulate IEF (iShares 7-10 Year Treasury Bond ETF, 1x).

    Deprecated: Use simulate_fund("IEF", ...) instead.
    """
    return simulate_fund("IEF", underlying, libor_yield_df, save_sim, force_update, adj, overwrite_sim_with_fund)


def sim_ust(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    """Simulate UST (ProShares Ultra 7-10 Year Treasury, 2x leverage).

    Deprecated: Use simulate_fund("UST", ...) instead.
    """
    return simulate_fund("UST", underlying, libor_yield_df, save_sim, force_update, adj, overwrite_sim_with_fund)


def sim_tyd(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    """Simulate TYD (Direxion Daily 7-10 Year Treasury Bull 3x, 3x leverage).

    Deprecated: Use simulate_fund("TYD", ...) instead.
    """
    return simulate_fund("TYD", underlying, libor_yield_df, save_sim, force_update, adj, overwrite_sim_with_fund)


# Short Term US Treasury Fund Simulations
def sim_shy(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    """Simulate SHY (iShares 1-3 Year Treasury Bond ETF, 1x).

    Deprecated: Use simulate_fund("SHY", ...) instead.
    """
    return simulate_fund("SHY", underlying, libor_yield_df, save_sim, force_update, adj, overwrite_sim_with_fund)


def sim_2x_stt(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    """Simulate hypothetical 2x short-term Treasury fund.

    Deprecated: Use simulate_fund("2X_STT", ...) instead.
    """
    return simulate_fund("2X_STT", underlying, libor_yield_df, save_sim, force_update, adj, overwrite_sim_with_fund)


def sim_3x_stt(
    underlying=None, libor_yield_df=None, save_sim=True, force_update=False, adj=None, overwrite_sim_with_fund=True
):
    """Simulate hypothetical 3x short-term Treasury fund.

    Deprecated: Use simulate_fund("3X_STT", ...) instead.
    """
    return simulate_fund("3X_STT", underlying, libor_yield_df, save_sim, force_update, adj, overwrite_sim_with_fund)


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
            actual_close = get_history("NTSX")["Close"]
            fund["Close"] = merge_price_histories(fund["Close"], actual_close, fix_point="end")
        except (FileNotFoundError, KeyError, ValueError, IndexError) as e:
            logger.warning(f"Could not overwrite NTSX simulation with actual fund data: {e}")

    if save_sim:
        fund.to_parquet(fund_path)
    return fund
