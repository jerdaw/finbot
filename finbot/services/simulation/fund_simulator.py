import numpy as np
import pandas as pd

from finbot.config import logger
from finbot.services.simulation.approximate_overnight_libor import approximate_overnight_libor


def fund_simulator(
    price_df: pd.DataFrame,
    leverage_mult: float = 1,
    annual_er_pct: float = 0.5 / 100,
    percent_daily_spread_cost: float = 0,
    fund_swap_pct: float = 0,
    periods_per_year: int = 250,
    multiplicative_constant: float = 1,
    additive_constant: float = 0,
    libor_yield_df: pd.DataFrame | pd.Series | None = None,
) -> pd.DataFrame:
    """
    Returns a pd.DataFrame fund simulation with "Close" and percent "Change" values.

    Args:
        price_df: DataFrame with Timestamp index and "Close" or "Adj Close" column.
        leverage_mult: Leverage multiplier applied to underlying daily pct change.
        annual_er_pct: Annual expense ratio (decimal form).
        percent_daily_spread_cost: Spread cost (decimal form) on the current fund date.
        fund_swap_pct: Fraction of fund allocated to swap contracts.
        periods_per_year: Number of compounding periods per year.
        multiplicative_constant: Multiplicative curve fitting constant (1 = no effect).
        additive_constant: Additive curve fitting constant (0 = no effect).
        libor_yield_df: DataFrame/Series with Timestamp index and "Yield" column.

    Returns:
        DataFrame with simulated "Close" and percent "Change" values.
    """
    # Data validation
    if (
        libor_yield_df is not None
        and hasattr(libor_yield_df, "index")
        and libor_yield_df.index.dtype.name != "datetime64[ns]"
    ):
        raise ValueError(
            f"libor_yield_df must be indexed with dates of dtype datetime64[ns], not {libor_yield_df.index.dtype.name}"
        )
    if price_df.index.dtype.name != "datetime64[ns]":
        raise ValueError(
            f"price_df must be indexed with dates of dtype datetime64[ns], not {price_df.index.dtype.name}"
        )
    casefold_cols = [n.casefold() for n in price_df.columns]
    if "close" not in casefold_cols and "adj close" not in casefold_cols:
        raise ValueError("price_df must contain 'Close' column or 'Adj Close' column")

    # Get/generate approximate overnight lending rate
    if libor_yield_df is None:
        libor_yield_df = approximate_overnight_libor()
    # Ensure a "Yield" column or Series
    if isinstance(libor_yield_df, pd.Series):
        libor_yield_df = (
            libor_yield_df.to_frame(name="Yield") if libor_yield_df.name != "Yield" else libor_yield_df.to_frame()
        )

    # Ensure all dates in price_df are also in libor_yield_df
    if not set(price_df.index).issubset(set(libor_yield_df.index)):
        libor_yield_df = pd.concat([libor_yield_df, price_df], axis=1, join="outer")
        libor_yield_df = pd.DataFrame(libor_yield_df["Yield"]).interpolate().bfill()

    logger.info("Building fund simulation...")
    # Get the close column to use ("Adj Close" has priority)
    close_col = "Adj Close" if "Adj Close" in price_df.columns else "Close"
    underlying_changes = price_df[close_col].pct_change().to_numpy()
    underlying_changes[0] = 0
    period_libor_yield_percents = libor_yield_df.loc[price_df.index, "Yield"].to_numpy() / 100

    # Vectorized computation replacing numba @jit loop
    changes = _compute_sim_changes(
        underlying_changes=underlying_changes,
        period_libor_yield_percents=period_libor_yield_percents,
        leverage_mult=leverage_mult,
        annual_er_pct=annual_er_pct,
        percent_daily_spread_cost=percent_daily_spread_cost,
        fund_swap_pct=fund_swap_pct,
        periods_per_year=periods_per_year,
        multiplicative_constant=multiplicative_constant,
        additive_constant=additive_constant,
    )

    # Compute close values
    mults = changes + 1
    closes = mults.cumprod()

    # Check for zero value event
    zero_value_indexes = np.where(closes <= 0)[0]
    if len(zero_value_indexes):
        zero_idx = zero_value_indexes[0]
        closes = np.concatenate((closes[:zero_idx], np.zeros(len(closes[zero_idx:]))))

    # Construct and return final df
    fund_df = pd.DataFrame({"Close": closes, "Change": changes})
    fund_df.index = price_df.index
    return fund_df


def _compute_sim_changes(
    underlying_changes: np.ndarray,
    period_libor_yield_percents: np.ndarray,
    leverage_mult: float,
    annual_er_pct: float,
    percent_daily_spread_cost: float,
    fund_swap_pct: float,
    periods_per_year: float,
    multiplicative_constant: float = 1,
    additive_constant: float = 0,
) -> np.ndarray:
    """
    Vectorized computation of daily percent changes for the simulated fund.

    Replaces the original numba @jit loop with numpy broadcasting.
    The equation per period:
        (underlying_change * leverage_mult - daily_expenses) * mult_constant + add_constant
    Where daily_expenses =
        (annual_er / periods_per_year) + (libor / periods_per_year * (leverage - 1)) + (spread * swap_pct)
    """
    er_cost = annual_er_pct / periods_per_year
    spread_cost = percent_daily_spread_cost * fund_swap_pct
    libor_costs = (period_libor_yield_percents / periods_per_year) * (leverage_mult - 1)
    daily_pct_expenses = er_cost + libor_costs + spread_cost
    base_changes = underlying_changes * leverage_mult - daily_pct_expenses
    changes = base_changes * multiplicative_constant + additive_constant
    return changes
