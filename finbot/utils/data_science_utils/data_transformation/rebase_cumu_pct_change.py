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
    from constants.data_constants import DEMO_DATA

    print(rebase_cumu_pct_change(DEMO_DATA["Close"]))
