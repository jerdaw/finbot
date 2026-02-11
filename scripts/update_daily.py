"""Daily data update pipeline.

Fetches latest price histories, index data, and FRED economic data,
then re-runs all simulation pipelines.
"""

import time
from time import perf_counter

from finbot.config import logger
from finbot.services.simulation.approximate_overnight_libor import approximate_overnight_libor
from finbot.services.simulation.sim_specific_bond_indexes import (
    sim_idcot1tr,
    sim_idcot7tr,
    sim_idcot20tr,
)
from finbot.services.simulation.sim_specific_funds import (
    sim_2x_stt,
    sim_3x_stt,
    sim_ief,
    sim_ntsx,
    sim_qld,
    sim_qqq,
    sim_shy,
    sim_spy,
    sim_sso,
    sim_tlt,
    sim_tmf,
    sim_tqqq,
    sim_tyd,
    sim_ubt,
    sim_upro,
    sim_ust,
)
from finbot.services.simulation.sim_specific_stock_indexes import sim_nd100tr, sim_sp500tr
from finbot.utils.data_collection_utils.fred.get_fred_data import get_fred_data
from finbot.utils.data_collection_utils.google_finance.get_idcot1tr import get_idcot1tr
from finbot.utils.data_collection_utils.google_finance.get_idcot7tr import get_idcot7tr
from finbot.utils.data_collection_utils.google_finance.get_idcot20tr import get_idcot20tr
from finbot.utils.data_collection_utils.google_finance.get_xndx import get_xndx
from finbot.utils.data_collection_utils.scrapers.shiller.get_shiller_ch26 import get_shiller_ch26
from finbot.utils.data_collection_utils.scrapers.shiller.get_shiller_ie_data import get_shiller_ie_data
from finbot.utils.data_collection_utils.yfinance.get_history import get_history


def _run_with_retry(func, name: str, max_retries: int = 2) -> None:
    """Run a function with retry logic. Logs errors instead of printing."""
    for attempt in range(1, max_retries + 1):
        try:
            t1 = perf_counter()
            func()
            t2 = perf_counter()
            logger.info(f"Completed {name} in {t2 - t1:.1f}s")
            return
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"{name} failed (attempt {attempt}/{max_retries}): {e}")
            else:
                logger.error(f"{name} failed after {max_retries} attempts: {e}")


def update_daily() -> None:
    """Run the full daily data update pipeline."""
    logger.info("Starting daily data update")
    t_start = perf_counter()

    steps = [
        (update_yf_price_histories, "YF Price Histories"),
        (update_gf_price_histories, "GF Price Histories"),
        (update_fred_data, "FRED Data"),
        (update_shiller_data, "Shiller Data"),
        (update_simulations, "Simulations"),
    ]

    for func, name in steps:
        _run_with_retry(func, name)

    t_end = perf_counter()
    logger.info(f"Daily update complete in {t_end - t_start:.1f}s")


def update_yf_price_histories() -> None:
    """Update tickers available on Yahoo Finance."""
    yahoo_tickers = sorted(
        {
            # S&P 500s
            "^GSPC",
            "SPY",
            "VOO",
            "IVV",
            "SSO",
            "UPRO",
            # Nasdaq 100s
            "^NDX",
            "QQQ",
            "QLD",
            "TQQQ",
            # VIX
            "UVXY",
            "VXX",
            "VIXY",
            # Bonds/Bills
            "TLT",
            "UBT",
            "TMF",
            "AGG",
            "BND",
            "IEF",
            "UST",
            "TYD",
            "SHY",
            # Other ETFs
            "VT",
            "VTI",
            "VWO",
            "VEA",
            "IEFA",
            "EFA",
            "VTV",
            "VUG",
            "IEMG",
            "IJR",
            "IWF",
            "IJH",
            "VIG",
            "GLD",
            "IWM",
            "IWD",
            "NTSX",
            # Specific Stocks
            "AAPL",
            "MSFT",
            "GOOG",
            "AMZN",
            "TSLA",
            "NVDA",
            "META",
            "GME",
            "AMD",
        }
    )
    get_history(yahoo_tickers, force_update=True)


def update_gf_price_histories() -> None:
    """Update tickers sourced from Google Finance/Sheets."""
    get_xndx(force_update=True)
    get_idcot20tr(force_update=True)
    get_idcot7tr(force_update=True)
    get_idcot1tr(force_update=True)


def update_fred_data() -> None:
    """Update FRED economic data series."""
    daily = sorted(
        {
            "SOFR",
            "DFF",
            "DTB4WK",
            "DTB3",
            "DTB6",
            "DTB1YR",
            "DGS1MO",
            "DGS3MO",
            "DGS6MO",
            "DGS1",
            "DGS2",
            "DGS3",
            "DGS5",
            "DGS7",
            "DGS10",
            "DGS20",
            "DGS30",
        }
    )
    weekly = sorted(
        {
            "WTB4WK",
            "WTB3MS",
            "WTB6MS",
            "WTB1YR",
            "WGS1MO",
            "WGS3MO",
            "WGS6MO",
            "WGS1YR",
            "WGS2YR",
            "WGS3YR",
            "WGS5YR",
            "WGS7YR",
            "WGS10YR",
            "WGS20YR",
            "WGS30YR",
        }
    )
    monthly = sorted(
        {
            "M1329AUSM193NNBR",
            "TB4WK",
            "TB3MS",
            "TB6MS",
            "TB1YR",
            "GS1M",
            "GS3M",
            "GS6M",
            "GS1",
            "GS2",
            "GS3",
            "GS5",
            "GS7",
            "GS10",
            "GS20",
            "GS30",
            "CPIAUCNS",
            "CPIAUCSL",
        }
    )

    for symbol_list in (daily, weekly, monthly):
        get_fred_data(symbol_list, force_update=True)
        time.sleep(0.5)


def update_shiller_data() -> None:
    """Update Shiller's online datasets."""
    get_shiller_ch26(force_update=True)
    get_shiller_ie_data(force_update=True)


def update_simulations() -> None:
    """Update all index and fund simulations."""
    # Approximate overnight LIBOR first (used by fund sims)
    approximate_overnight_libor()

    # Index sims before fund sims (fund sims depend on index sims)
    index_sims = (sim_sp500tr, sim_nd100tr, sim_idcot20tr, sim_idcot7tr, sim_idcot1tr)
    for sim in index_sims:
        sim(force_update=True)

    # Fund simulations
    fund_sims = (
        sim_spy,
        sim_sso,
        sim_upro,
        sim_qqq,
        sim_qld,
        sim_tqqq,
        sim_tlt,
        sim_ubt,
        sim_tmf,
        sim_ief,
        sim_ust,
        sim_tyd,
        sim_shy,
        sim_2x_stt,
        sim_3x_stt,
        sim_ntsx,
    )
    for sim in fund_sims:
        sim(force_update=True)


if __name__ == "__main__":
    update_daily()
