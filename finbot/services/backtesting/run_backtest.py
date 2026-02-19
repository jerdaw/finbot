from __future__ import annotations

from typing import Any

import pandas as pd

from finbot.services.backtesting.backtest_runner import BacktestRunner


def run_backtest(*args: Any, **kwargs: Any) -> pd.DataFrame:
    # Adjust args/kwargs for tqdm process_map batch runner
    if not kwargs and len(args) == 1:
        kw_list = (
            "price_histories",
            "start",
            "end",
            "duration",
            "start_step",
            "init_cash",
            "strat",
            "strat_kwargs",
            "broker",
            "broker_kwargs",
            "broker_commission",
            "sizer",
            "sizer_kwargs",
            "plot",
        )
        kwargs = {kw_list[i]: args[0][i] for i in range(len(kw_list))}
        args = ()

    backtest_runner = BacktestRunner(*args, **kwargs)
    return backtest_runner.run_backtest()
