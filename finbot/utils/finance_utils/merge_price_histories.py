import pandas as pd

# Constants for readability and to avoid magic strings
FIX_POINT_START = "start"
FIX_POINT_END = "end"


def merge_price_histories(
    original_series: pd.Series,
    series_to_merge: pd.Series,
    fix_point: str = FIX_POINT_END,
) -> pd.Series:
    """
    Splice `series_to_merge` pd.Series into `original_series` pd.Series.
    Both series must be time-series indexed.

    Parameters:
    original_series (pd.Series): Original time-series data.
    series_to_merge (pd.Series): Time-series data to merge into the original series.
    fix_point (Literal["start", "end"]): Determines whether to align the start or end values of the series.

    Returns:
    pd.Series: Merged time-series data.
    """
    fix_point = fix_point.lower()

    if not isinstance(original_series, pd.Series) or not isinstance(series_to_merge, pd.Series):
        raise TypeError("Both 'original_series' and 'series_to_merge' must be pandas Series.")

    if not pd.api.types.is_datetime64_any_dtype(original_series.index) or not pd.api.types.is_datetime64_any_dtype(
        series_to_merge.index,
    ):
        raise ValueError("Both series must be time-series indexed.")

    orig_start, orig_end = original_series.index.min(), original_series.index.max()
    series_to_merge = series_to_merge.truncate(before=orig_start, after=orig_end)

    merge_start, merge_end = series_to_merge.index.min(), series_to_merge.index.max()

    orig_changes = original_series.pct_change()
    merge_in_changes = series_to_merge.pct_change()

    pre_merge = orig_changes[orig_changes.index < merge_start]
    post_merge = orig_changes[orig_changes.index > merge_end]

    merged_changes = pd.concat([pre_merge, merge_in_changes, post_merge])
    merged_changes.iloc[0] = 0

    merged_mults = merged_changes + 1
    merged_closes = merged_mults.cumprod() * (original_series.iloc[0] / merged_mults.cumprod().iloc[0])

    if fix_point == FIX_POINT_END:
        merged_closes *= original_series.iloc[-1] / merged_closes.iloc[-1]

    return merged_closes


if __name__ == "__main__":
    from finbot.utils.data_collection_utils.yfinance.get_history import get_history

    orig = get_history("^GSPC")["Adj Close"]
    merge_in = get_history("SPY")["Adj Close"]

    print(merge_in.corr(orig))
    merged = merge_price_histories(orig, merge_in)
    print(merge_in.corr(merged))
