import pandas as pd

from constants.path_constants import FRED_DATA_DIR, LONGTERMTRENDS_DATA_DIR, SIMULATIONS_DATA_DIR
from finbot.utils.data_collection_utils.fred.get_fred_data import get_fred_data
from finbot.utils.data_collection_utils.yfinance.get_history import get_history


def get_yields() -> pd.DataFrame:
    gspc = get_history("^GSPC")["Close"].to_frame().rename(columns={"Close": "GSPC"})
    fred_data = get_fred_data(["SOFR", "DFF", "TB3MS"])
    sofr = fred_data["SOFR"].dropna()
    dff = fred_data["DFF"].dropna()
    tb3ms = fred_data["TB3MS"].dropna()

    # Try loading supplementary yield data if available
    usdontd156n_path = FRED_DATA_DIR / "USDONTD156N.parquet"
    usdontd156n = pd.read_parquet(usdontd156n_path) if usdontd156n_path.is_file() else pd.DataFrame()

    longtermtrends_path = LONGTERMTRENDS_DATA_DIR / "constant-maturity-treasuries.parquet"
    if longtermtrends_path.is_file():
        proprietary_data = pd.read_parquet(longtermtrends_path)["US01Y Yield"]
    else:
        proprietary_data = pd.Series(dtype=float)

    dfs = [sofr, dff, tb3ms, gspc]
    if not usdontd156n.empty:
        dfs.insert(3, usdontd156n)
    if not proprietary_data.empty:
        dfs.insert(-1, proprietary_data)

    yield_history = pd.concat(dfs, axis=1, join="outer")
    yield_history = yield_history.drop(labels="GSPC", axis=1)
    return yield_history


def approximate_overnight_libor(save: bool = True) -> pd.Series:
    yield_history = get_yields()

    # Build composite yield series from best available data
    add_order = ["SOFR", "USDONTD156N", "DFF", "TB3MS", "US01Y Yield"]
    # Only use columns that actually exist
    available = [col for col in add_order if col in yield_history.columns]

    if not available:
        raise ValueError("No yield data available to approximate overnight LIBOR")

    libor_hist = yield_history[available[0]].copy()
    libor_hist.name = "Yield"
    for h in available[1:]:
        libor_hist = libor_hist.fillna(yield_history[h])
    libor_hist = libor_hist.interpolate()
    libor_hist = libor_hist.bfill()

    if save:
        libor_hist.to_frame().to_parquet(SIMULATIONS_DATA_DIR / "overnight_libor_sim.parquet")
    return libor_hist
