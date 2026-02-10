import pandas as pd

DEFAULT_WINDOWS = (2, 3, 5, 10, 30, 50, 100, 200, 300)
DEFAULT_QUANTILES = (0, 0.1, 0.25, 0.5, 0.75, 0.9, 1)


def get_series_quantiles(
    series: pd.Series,
    quantiles: tuple[int | float, ...] = DEFAULT_QUANTILES,
) -> dict[str, float]:
    return {str(n): series.quantile(q=n) for n in quantiles}


def get_series_ma(series: pd.Series, ma_ranges: tuple[int, ...] = DEFAULT_WINDOWS) -> dict[str, float]:
    return {str(n): series.rolling(n).mean()[-1] for n in ma_ranges}


def get_series_cma(series: pd.Series, cma_ranges: tuple[int, ...] = DEFAULT_WINDOWS) -> dict[str, float]:
    return {str(n): series.expanding(min_periods=n).mean()[-1] for n in cma_ranges}


def get_series_ema(series: pd.Series, ema_ranges: tuple[int, ...] = DEFAULT_WINDOWS) -> dict[str, float]:
    return {str(n): series.ewm(span=n, adjust=False).mean()[-1] for n in ema_ranges}
