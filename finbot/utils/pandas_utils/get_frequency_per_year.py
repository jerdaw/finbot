import pandas as pd

from constants.data_constants import DEMO_DATA


def get_frequency_per_interval(
    df: pd.DataFrame,
    interval: pd.DateOffset,
    method: str = "mode",
    sort_index: bool = True,
) -> None | float:
    if len(df) < 2:
        return None

    if method not in ["mean", "mode", "last"]:
        raise ValueError("`method` must be 'mean', 'mode', or 'last'.")

    if sort_index:
        df = df.sort_index()

    start, end = df.index.min(), df.index.max()

    # Prevent overflow by checking if start date plus interval is within bounds
    if start + interval > pd.Timestamp.max:
        raise OverflowError("Interval addition results in an out-of-bounds datetime.")

    interval_duration = (start + interval) - start

    if end - start < interval_duration:
        raise ValueError("DataFrame does not contain a full period of data.")

    if method == "last":
        return len(df.loc[end - interval_duration :])

    timedeltas = [
        len(df.loc[df.index[i] : df.index[i] + interval_duration])
        for i in range(len(df))
        if df.index[i] + interval_duration < end
    ]
    if method == "mean":
        return sum(timedeltas) / len(timedeltas)
    elif method == "mode":
        return pd.Series(timedeltas).mode()[0]
    else:
        raise ValueError("`method` must be 'mean', 'mode', or 'last'.")

    return None


if __name__ == "__main__":
    spy = DEMO_DATA

    offsets = [
        pd.DateOffset(years=1),
        pd.DateOffset(months=1),
        pd.DateOffset(weeks=1),
        pd.DateOffset(days=1),
        pd.DateOffset(hours=1),
        pd.DateOffset(minutes=1),
        pd.DateOffset(seconds=1),
    ]

    for offset in offsets:
        for method in "mean", "mode", "last":
            res = get_frequency_per_interval(df=spy, interval=offset, method=method)
            print(f"{offset} - {method}: {res}")
