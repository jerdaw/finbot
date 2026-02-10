import pandas as pd

from constants.path_constants import DEMO_DATA_PATH

DEMO_DATA = pd.read_csv(DEMO_DATA_PATH, index_col=0, parse_dates=True)
