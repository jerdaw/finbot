"""Drawdown calculation for time series data.

Calculates the percentage decline from peak to trough over a given time period.
Drawdown is a key risk metric measuring the largest peak-to-valley loss experienced.

Supports both cumulative maximum (window=1) and rolling window drawdowns.

Typical usage:
    - Measure portfolio risk and maximum loss potential
    - Compare risk-adjusted returns across strategies
    - Identify periods of sustained underperformance
"""

import pandas as pd


def get_drawdown(data: pd.DataFrame | pd.Series, window: int = 1) -> pd.DataFrame | pd.Series:
    """
    Calculate the drawdown of a pandas DataFrame or Series.

    Drawdown is the percentage loss from each point to its rolling maximum in the past.

    Parameters:
    data (DataFrame | Series): DataFrame or Series containing price data.
    window (int): The rolling window period for calculating the drawdown. Default is 1.

    Returns:
    DataFrame | Series: Series representing the drawdown.
    """
    if window < 1:
        raise ValueError("Window must be greater than 0.")

    if window == 1:
        cumulative_max = data.cummax()
        drawdown = (data - cumulative_max) / cumulative_max
    else:  # window > 1
        rolling_max = data.rolling(window, min_periods=1).max()
        drawdown = (data - rolling_max) / rolling_max

    return drawdown


# Example usage:
if __name__ == "__main__":
    from finbot.utils.data_collection_utils.yfinance.get_history import get_history  # Example data collection

    # Fetch example data
    gspc = get_history("^GSPC")
    data = gspc["Adj Close"]

    # Calculate drawdown for different scenarios
    for n in [1, round(252 / 2), 252]:
        res = get_drawdown(data=data, window=n)
        print(f"Drawdown with window {n}:\n{res.head()}")
