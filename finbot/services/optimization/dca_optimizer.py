"""DCA (Dollar Cost Averaging) optimizer.

Runs a series of backtests throughout the duration of a security to optimize:
  1) The optimal ratio at which to DCA over time (e.g. 2x at start vs end)
  2) The optimal DCA period (e.g., 1 year, etc)
  3) The optimal purchase rate (e.g., daily, weekly, monthly, etc)
"""

import itertools

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from tqdm.contrib.concurrent import process_map

from config import logger
from constants.path_constants import BACKTESTS_DATA_DIR
from finbot.utils.finance_utils.get_cgr import get_cgr
from finbot.utils.finance_utils.get_pct_change import get_pct_change
from finbot.utils.finance_utils.get_risk_free_rate import get_risk_free_rate


def dca_optimizer(
    price_history: pd.Series,
    ticker: str | None = None,
    ratio_range: tuple = (1, 1.5, 2, 3, 5, 10),
    dca_durations: tuple = tuple(round(n) for n in (1, 5, 252 / 12, 252 / 4, 252 / 2, 252, 252 * 2, 252 * 3)),
    dca_steps: tuple = tuple(round(n) for n in (1, 5, 10, 252 / 12, 252 / 4)),
    trial_durations: tuple = tuple(round(n) for n in (252 * 3, 252 * 5)),
    starting_cash: float = 1000,
    start_step: int = 5,
    save_df: bool = True,
    analyze_results: bool = True,
) -> pd.DataFrame | tuple[pd.DataFrame, pd.DataFrame]:
    """Run DCA optimization across many parameter combinations.

    Parameters
    ----------
    price_history : pd.Series
        Series of "Adj Close" or "Close" float values.
    ticker : str, optional
        Ticker symbol for labeling output.
    ratio_range : tuple
        Ratios of amount to invest on first DCA day over last DCA day.
    dca_durations : tuple
        Number of periods to DCA over.
    dca_steps : tuple
        Number of periods between DCA purchases.
    trial_durations : tuple
        Total number of periods per trial.
    starting_cash : float
        Starting cash amount.
    start_step : int
        Periods to advance trial starting point between trials.
    save_df : bool
        Whether to save results to parquet.
    analyze_results : bool
        Whether to return analyzed results or raw DataFrame.
    """
    closes = (tuple(price_history),)
    starting_cash_list = [starting_cash]
    start_idxs = tuple(start_step * n for n in range((len(price_history) - max(trial_durations)) // start_step))

    combs_list = (start_idxs, ratio_range, dca_durations, dca_steps, trial_durations, closes, starting_cash_list)
    combs = tuple(itertools.product(*combs_list))
    n_combs = np.prod([len(v) for v in combs_list])

    data = process_map(_mp_helper, combs, total=n_combs, chunksize=1000, desc=f"Running DCA Optimizer - {ticker}")

    price_hist_idxs = price_history.index
    df = _convert_to_df(data, price_hist_idxs)
    if save_df:
        file_name = f"{ticker if ticker else str(pd.Timestamp.now())} - DCA Optimizer.parquet"
        df.to_parquet(BACKTESTS_DATA_DIR / file_name)

    if analyze_results:
        return analyze_results_helper(df)
    return df


def _mp_helper(comb):
    """Multiprocessing helper for a single DCA parameter combination."""
    start_idx, ratio, dca_duration, dca_step, trial_duration, closes, starting_cash = comb
    closes = closes[start_idx:]
    ratio_linspace = np.linspace(ratio, 1, round(dca_duration // dca_step))
    ratio_linspace /= ratio_linspace.sum()
    if ratio_linspace.size == 0:
        return None, None
    comb_res = _dca_single(
        starting_cash=starting_cash,
        ratio_linspace=ratio_linspace,
        trial_duration=trial_duration,
        dca_duration=dca_duration,
        dca_step=dca_step,
        closes=closes,
    )
    return (start_idx, ratio, dca_duration, dca_step, trial_duration), comb_res


def _dca_single(
    starting_cash: float,
    ratio_linspace: np.ndarray,
    trial_duration: int,
    dca_duration: int,
    dca_step: int,
    closes: tuple,
) -> tuple[float, float, float, float, float, float]:
    """Run a single DCA trial and return performance metrics."""
    cur_cash = starting_cash
    stock_owned = 0.0
    assert len(closes) >= trial_duration
    total_value = np.zeros(trial_duration)

    linspace_idx = 0
    for close_idx in range(trial_duration):
        cur_close = closes[close_idx]
        if close_idx % dca_step == 0 and close_idx < dca_duration and linspace_idx < len(ratio_linspace):
            funds_available = ratio_linspace[linspace_idx] * starting_cash
            linspace_idx += 1
            stock_owned += funds_available / cur_close
            cur_cash -= funds_available
            if stock_owned < 0 or round(cur_cash, 2) < 0:
                raise RuntimeError("Negative cash or stock during DCA trial")
        total_value[close_idx] = cur_close * stock_owned + cur_cash

    if round(cur_cash, 2) != 0:
        raise RuntimeError("Trial end cash is not $0.00")

    final_price = closes[trial_duration - 1]
    final_value = final_price * stock_owned + cur_cash
    pct_change = get_pct_change(starting_cash, final_value) * 100
    cagr = get_cgr(starting_cash, final_value, trial_duration / 252) * 100
    std = total_value.std()
    as_series = pd.Series(total_value)
    roll_max = as_series.rolling(252, min_periods=1).max()
    daily_drawdown = as_series / roll_max - 1.0
    max_drawdown = daily_drawdown.min() * 100 * -1

    # Fetch current risk-free rate (3-month T-bill), fallback to 2.0% if unavailable
    try:
        risk_free_rate_data = get_risk_free_rate(full_series=False)
        risk_free_rate = float(risk_free_rate_data["Data"]) if isinstance(risk_free_rate_data, pd.Series) else 2.0
    except Exception as e:
        logger.warning(f"Could not fetch risk-free rate: {e}. Using default 2.0%")
        risk_free_rate = 2.0

    sharpe = (cagr - risk_free_rate) / std

    return final_value, pct_change, cagr, max_drawdown, std, sharpe


def _convert_to_df(res: list, price_hist_idxs: pd.Index) -> pd.DataFrame:
    """Convert raw results list into a structured DataFrame."""
    as_dict = {
        "Trial Start": [],
        "Trial End": [],
        "Trial Duration": [],
        "DCA Duration": [],
        "DCA Ratio": [],
        "DCA Step": [],
        "Final Value": [],
        "Pct Change": [],
        "CAGR": [],
        "Max Drawdown": [],
        "STDev": [],
        "Sharpe": [],
    }
    for data in res:
        if None in data:
            continue
        as_dict["Trial Start"].append(price_hist_idxs[data[0][0]])
        as_dict["Trial End"].append(price_hist_idxs[round(data[0][0] + data[0][2] - 1)])
        as_dict["Trial Duration"].append(data[0][4])
        as_dict["DCA Duration"].append(data[0][2])
        as_dict["DCA Ratio"].append(data[0][1])
        as_dict["DCA Step"].append(data[0][3])
        as_dict["Final Value"].append(data[1][0])
        as_dict["Pct Change"].append(data[1][1])
        as_dict["CAGR"].append(data[1][2])
        as_dict["Max Drawdown"].append(data[1][3])
        as_dict["STDev"].append(data[1][4])
        as_dict["Sharpe"].append(data[1][5])

    return pd.DataFrame(as_dict).set_index("Trial Start")


def analyze_results_helper(
    results_df: pd.DataFrame,
    plot: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Analyze DCA optimization results by ratio and duration."""
    ratios = sorted(set(results_df["DCA Ratio"]))
    ratio_df = (
        pd.DataFrame(
            {
                "Ratio": ratios,
                "Ratio Sharpe Avg": [results_df[results_df["DCA Ratio"] == r]["Sharpe"].mean() for r in ratios],
                "Ratio CAGR Avg": [results_df[results_df["DCA Ratio"] == r]["CAGR"].mean() for r in ratios],
                "Ratio STDev Avg": [results_df[results_df["DCA Ratio"] == r]["STDev"].mean() for r in ratios],
                "Ratio Max Drawdown Avg": [
                    results_df[results_df["DCA Ratio"] == r]["Max Drawdown"].mean() for r in ratios
                ],
            }
        )
        .set_index("Ratio")
        .sort_index()
    )

    durations = sorted(set(results_df["DCA Duration"]))
    duration_df = (
        pd.DataFrame(
            {
                "Duration": durations,
                "Duration Sharpe Avg": [
                    results_df[results_df["DCA Duration"] == d]["Sharpe"].mean() for d in durations
                ],
                "Duration CAGR Avg": [results_df[results_df["DCA Duration"] == d]["CAGR"].mean() for d in durations],
                "Duration STDev Avg": [results_df[results_df["DCA Duration"] == d]["STDev"].mean() for d in durations],
                "Duration Max Drawdown Avg": [
                    results_df[results_df["DCA Duration"] == d]["Max Drawdown"].mean() for d in durations
                ],
            }
        )
        .set_index("Duration")
        .sort_index()
    )

    if plot:
        for name, df in (("Ratio", ratio_df), ("Duration", duration_df)):
            normalized_df = df.copy()
            for col in normalized_df.columns:
                normalized_df[col] /= normalized_df[col].min()
            normalized_df.plot()
            plt.title(f"DCA Optimization by {name}")
            plt.show()

    return ratio_df, duration_df
