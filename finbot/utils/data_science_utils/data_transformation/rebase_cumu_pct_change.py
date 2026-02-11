"""Rebase time series data to cumulative percent change from starting value.

Normalizes time series to show percentage change from initial value or rebases
to a specified starting value. Useful for comparing multiple series with
different scales or creating indexed performance charts.

Typical usage:
    ```python
    # Rebase to 0 (shows cumulative percent change from start)
    df_rebased = rebase_cumu_pct_change(df, start_val=0)
    # If df starts at 100, ends at 150: result starts at 0, ends at 0.50 (50% gain)

    # Rebase to 100 (shows indexed performance)
    df_rebased = rebase_cumu_pct_change(df, start_val=100)
    # If df starts at 50, ends at 75: result starts at 100, ends at 150 (50% gain)

    # Compare multiple assets on same scale
    combined = pd.DataFrame(
        {
            "stock_a": rebase_cumu_pct_change(stock_a, start_val=100),
            "stock_b": rebase_cumu_pct_change(stock_b, start_val=100),
            "bond": rebase_cumu_pct_change(bond, start_val=100),
        }
    )
    ```

Rebasing formula:
    - start_val=0: `(value / first_value) - 1`
      - Converts to cumulative returns
      - First value becomes 0, subsequent values show % change

    - start_val≠0: `(value / first_value) * start_val`
      - Normalizes to specified starting value
      - Preserves relative changes while changing scale

Features:
    - Works with both DataFrames and Series
    - Preserves pandas index and structure
    - Simple one-line implementation
    - No fitting required (pure transformation)

Use cases:
    - Creating indexed performance charts (all start at 100)
    - Comparing assets with different price scales
    - Visualizing relative performance over time
    - Converting prices to returns
    - Normalizing backt data for analysis

Example use cases:
    ```python
    # Compare stocks at different price points
    aapl_rebased = rebase_cumu_pct_change(aapl_prices, start_val=100)  # $150 → 100
    goog_rebased = rebase_cumu_pct_change(goog_prices, start_val=100)  # $2500 → 100
    # Now both start at 100, easy to compare performance

    # Create cumulative returns chart
    returns = rebase_cumu_pct_change(prices, start_val=0)
    # Shows % gain/loss from starting point

    # Normalize portfolio values
    portfolio_norm = rebase_cumu_pct_change(portfolio_value, start_val=10000)
    # Shows growth assuming $10,000 initial investment
    ```

Best practices:
    - Use start_val=100 for intuitive percentage-based charts
    - Use start_val=0 when focusing on returns/changes
    - Rebase all series to same start_val for fair comparison
    - Consider implications of division by first value (first value should not be 0)

Limitations:
    - Assumes first value is non-zero (would cause division by zero)
    - Does not handle missing data at start
    - Single time point transformation (no rolling window)

Related modules: scalers_normalizers/* (more sophisticated normalization methods),
get_pct_change (simple percent change), get_cgr (compound growth rate).
"""

from __future__ import annotations

import pandas as pd


def rebase_cumu_pct_change(df: pd.DataFrame | pd.Series, start_val: float | int = 0) -> pd.DataFrame | pd.Series:
    """
    Rebase a cumulative percent change series to a specified starting value.

    Parameters:
        df (pd.DataFrame or pd.Series): Data to rebase.
        start_val (float or int): Value to rebase to.

    Returns:
        pd.DataFrame or pd.Series: Rebased data.
    """
    return (df / df.iloc[0] - 1) if start_val == 0 else (df / df.iloc[0] * start_val)


if __name__ == "__main__":
    from finbot.constants.data_constants import DEMO_DATA

    print(rebase_cumu_pct_change(DEMO_DATA["Close"]))
