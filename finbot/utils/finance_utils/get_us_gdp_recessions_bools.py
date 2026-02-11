"""US recession indicators from NBER via FRED.

Retrieves National Bureau of Economic Research (NBER) recession indicators from
the Federal Reserve Economic Data (FRED) database. Returns boolean time series
indicating whether the US economy was in recession for each period.

Multiple FRED symbols available with different definitions:
    - USRECD/USREC: Period following peak through trough (standard definition)
    - USRECDM/USRECM: Peak through trough (includes peak)
    - USRECDP/USRECP: Peak through period preceding trough
    - JHDUSRGDPBR: GDP-based recession indicator (quarterly)

Default (USRECD) uses daily/7-day data with standard NBER recession definition.

Typical usage:
    - Identify recession periods for backtesting strategies
    - Analyze asset performance during economic downturns
    - Regime-based analysis (bull market vs recession)
    - Economic cycle research
"""

import matplotlib.pyplot as plt
import pandas as pd

from finbot.utils.data_collection_utils.fred.get_fred_data import get_fred_data


def get_us_gdp_recessions_bools(fred_symbol: str = "USRECD") -> pd.DataFrame:
    """
    Some jargon for the below descriptions:
    - "peak": the highest point before decline begins
    - "period following the peak": the period/time immediately after the peak
    - "through": the entire duration of the recession (or other economic cycle) from peak through the start of recovery
    - "through the through": basically another way of saying "through"
    - "period preceding the through": the period immediately before the end of the recession/start of the recovery

    Some other potentially useful symbols:

    NBER based Recession Indicators for the United States from the Period following the Peak through the Trough:
        "USRECD",       # Daily, 7-Day
        "USREC",        # Monthly

    NBER based Recession Indicators for the United States from the Peak through the Trough:
        "USRECDM",      # Daily, 7-Day
        "USRECM",       # Monthly

    NBER based Recession Indicators for the United States from the Peak through the Period preceding the Trough:
        "USRECDP",      # Daily, 7-Day
        "USRECP",       # Monthly

    Dates of U.S. recessions as inferred by GDP-based recession indicator:
        "JHDUSRGDPBR"   # Quarterly

    More generally, see: https://fred.stlouisfed.org/categories/32262
    """

    fred_recession_dfs = get_fred_data(symbols=[fred_symbol])

    result = fred_recession_dfs.dropna(how="all").sort_index()
    assert isinstance(result, pd.DataFrame)
    return result


if __name__ == "__main__":
    boolean_recessions_df = get_us_gdp_recessions_bools()
    print(boolean_recessions_df)

    gdp_df = get_fred_data(symbols=["GDPC1"])
    gdp_df["GDPC1"] = gdp_df["GDPC1"] / gdp_df["GDPC1"].iloc[-1]

    # concatenate the dfs
    boolean_recessions_df = pd.concat([boolean_recessions_df, gdp_df], axis=1)
    boolean_recessions_df["GDPC1"] = boolean_recessions_df["GDPC1"].ffill()

    # Check if the DataFrame is not empty
    if not boolean_recessions_df.empty:
        plt.figure(figsize=(10, 6))  # Create a new figure with a specified size

        # Plot each series in the DataFrame on the same plot
        for column in boolean_recessions_df.columns:
            plt.plot(boolean_recessions_df.index, boolean_recessions_df[column], label=column)

        plt.title("US Recession Indicators Over Time")
        plt.xlabel("Date")
        plt.ylabel("Indicator Value")
        plt.legend()
        plt.show()
    else:
        print("Dataframe is empty.")
