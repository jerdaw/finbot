"""Extract recession date ranges from NBER data.

Convenience wrapper around get_us_gdp_cycle_dates that returns only the
recession periods as a list of (start_date, end_date) tuples.

Returns recession periods based on NBER definitions (default: USRECD).
For full cycle data including non-recession periods, use get_us_gdp_cycle_dates directly.

Typical usage:
    - Filter backtest data to recession-only periods
    - Compare strategy performance across recessions
    - Recession-specific risk analysis
"""

import pandas as pd

from finbot.utils.finance_utils.get_us_gdp_cycle_dates import get_us_gdp_cycle_dates


def get_us_gdp_recession_dates(df: pd.DataFrame | None = None) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    return get_us_gdp_cycle_dates(df)["recessions"]


if __name__ == "__main__":
    print(get_us_gdp_recession_dates())
