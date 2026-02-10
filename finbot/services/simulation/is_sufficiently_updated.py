import pandas as pd
from pandas._libs.tslibs.offsets import BDay

from constants.path_constants import SIMULATIONS_DATA_DIR


def is_sufficiently_updated(fund_name: str, max_bday_latency: int = 1) -> bool:
    fund_path = SIMULATIONS_DATA_DIR / f"{fund_name}.parquet"
    if not fund_path.is_file():
        return False
    mtime = pd.Timestamp.fromtimestamp(fund_path.stat().st_mtime)
    cur_ts = pd.Timestamp.now().normalize()
    return mtime >= (cur_ts - BDay(max_bday_latency))
