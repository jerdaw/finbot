import pandas as pd

from finbot.constants.path_constants import ASSETS_DIR

DEMO_DATA_PATH = ASSETS_DIR / "demo_data.csv"
DEMO_DATA = pd.read_csv(DEMO_DATA_PATH, index_col=0, parse_dates=True) if DEMO_DATA_PATH.exists() else pd.DataFrame()
