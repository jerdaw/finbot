from typing import Literal

import pandas as pd


def get_periods_per_year(
    df: pd.DataFrame,
    method: Literal["mean", "mode", "last"] = "mode",
    sort_index: bool = True,
) -> int:
    if len(df) < 2:
        return 252  # Default to trading days

    if sort_index:
        df = df.sort_index()
    method = method.lower()

    offset = pd.DateOffset(months=12)
    timedelta = pd.Timestamp(2020, 1, 1) - pd.Timestamp(2019, 1, 1)

    start = df.index.min()
    end = df.index.max()
    assert end - start >= timedelta

    if method == "last":
        res = len(df.loc[end - offset :])
    elif method == "mean":
        timedeltas = pd.Series(
            [len(df.loc[df.index[i] : df.index[i] + offset]) for i in range(len(df)) if df.index[i] + offset < end]
        )
        res = timedeltas.mean()
    elif method == "mode":
        timedeltas = pd.Series(
            [len(df.loc[df.index[i] : df.index[i] + offset]) for i in range(len(df)) if df.index[i] + offset < end]
        )
        res = timedeltas.mode()[0]
    else:
        raise ValueError("`method` must be 'mean', 'mode', or 'last'.")

    return int(res)
