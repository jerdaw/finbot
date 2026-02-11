"""Extract non-recession date ranges from NBER data.

Convenience wrapper around get_us_gdp_cycle_dates that returns only the
non-recession (expansion) periods as a list of (start_date, end_date) tuples.

Returns expansion periods based on NBER definitions (default: USRECD).
Complements get_us_gdp_recession_dates.py for cycle-aware analysis.

Typical usage:
    - Analyze strategy performance during economic expansions
    - Compare risk/return in expansions vs recessions
    - Identify bull market patterns
"""

import pandas as pd

from finbot.utils.finance_utils.get_us_gdp_cycle_dates import get_us_gdp_cycle_dates


def get_us_gdp_non_recession_dates(df: pd.DataFrame | None = None):
    return get_us_gdp_cycle_dates(df)["non_recessions"]


if __name__ == "__main__":
    print(get_us_gdp_non_recession_dates())
