import pandas as pd

from constants.path_constants import BACKTESTS_DATA_DIR
from finbot.services.backtesting.avg_stepped_results import avg_stepped_results


def print_and_save_backtest(file_name: str, results: pd.DataFrame, print_res: bool = True, save: bool = True):
    res = results.copy()
    res["File Name"] = [file_name for _ in range(len(res))]
    strat_col_idx = res.columns.to_list().index("Strategy")
    res = res[
        res.columns[: strat_col_idx + 1].to_list() + ["File Name"] + res.columns[strat_col_idx + 1 : -1].to_list()
    ]

    file_head = f"{pd.Timestamp.now()} - {file_name}"
    if save:
        res.to_parquet(BACKTESTS_DATA_DIR / f"{file_head} - Tests.parquet")
    res.sort_values("CAGR", ascending=False, inplace=True)
    if print_res:
        print(res.head(50).to_string())

    if len(set(res["Start Date"])) > 1:
        averaged = avg_stepped_results(res)
        if save:
            averaged.to_parquet(BACKTESTS_DATA_DIR / f"{file_head} - Averaged.parquet")
        averaged.sort_values("CAGR", ascending=False, inplace=True)
        if print_res:
            print()
            print(averaged.head(50).to_string())
