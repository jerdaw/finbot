import pandas as pd

from finbot.utils.finance_utils.get_us_gdp_cycle_dates import get_us_gdp_cycle_dates


def get_us_gdp_recession_dates(df: pd.DataFrame | None = None):
    return get_us_gdp_cycle_dates(df)["recessions"]


if __name__ == "__main__":
    print(get_us_gdp_recession_dates())
