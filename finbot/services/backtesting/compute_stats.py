from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import quantstats as qs


def compute_stats(
    value_history: pd.Series,
    cash_history: pd.Series,
    stocks: list[str] | None,
    strat: type | None,
    strat_kwargs: dict[str, Any],
    broker: type | None,
    broker_kwargs: dict[str, Any],
    broker_commission: type | None,
    sizer: type | None,
    sizer_kwargs: dict[str, Any],
    plot: bool = False,
) -> pd.DataFrame:
    qs.extend_pandas()

    stats: dict[str, Any] = {}

    # Backtest info
    stats["Start Date"] = value_history.index[0]
    stats["End Date"] = value_history.index[-1]
    stats["Duration"] = stats["End Date"] - stats["Start Date"]
    stats["Stocks"] = stocks if stocks else None
    stats["Strategy"] = str(strat).split(".")[-1][:-2] if strat else None
    for kw_name, kw_val in strat_kwargs.items():
        stats[f"{kw_name} (p)"] = str(kw_val)
    stats["Broker"] = str(broker).split(".")[-1][:-2] if broker else None
    for kw_name, kw_val in broker_kwargs.items():
        stats[f"{kw_name} (p)"] = str(kw_val)
    stats["Broker Commission"] = str(broker_commission).split(".")[-1][:-2] if broker_commission else None
    stats["Sizer"] = str(sizer).split(".")[-1][:-2] if sizer else None
    for kw_name, kw_val in sizer_kwargs.items():
        stats[f"{kw_name} (p)"] = str(kw_val)

    # Basic return stats
    stats["Starting Value"] = value_history.iloc[0]
    stats["Ending Value"] = value_history.iloc[-1]
    stats["ROI"] = (stats["Ending Value"] - stats["Starting Value"]) / stats["Starting Value"]
    stats["CAGR"] = value_history.cagr()  # quantstats extension method

    # Metric ratios
    stats["Sharpe"] = value_history.sharpe()  # quantstats extension method
    stats["Smart Sharpe"] = value_history.smart_sharpe()  # quantstats extension method
    stats["Smart Sortino/sqrt(2)"] = value_history.smart_sortino() / np.sqrt(2)  # quantstats extension method
    stats["Omega"] = None
    stats["Calmar"] = value_history.calmar()  # quantstats extension method
    stats["Common Sense Ratio"] = value_history.common_sense_ratio()  # quantstats extension method
    stats["Profit Factor"] = value_history.profit_factor()  # quantstats extension method
    stats["Kelly Criterion"] = value_history.kelly_criterion()  # quantstats extension method

    # Volatility & drawdown
    stats["Max Drawdown"] = value_history.max_drawdown()  # quantstats extension method
    stats["Annualized Volatility"] = value_history.volatility()  # quantstats extension method
    stats["Risk of Ruin"] = value_history.risk_of_ruin()  # quantstats extension method
    stats["Expected Shortfall (cVar)"] = value_history.expected_shortfall()  # quantstats extension method

    # Period stats
    stats["Best Day"] = value_history.best()  # quantstats extension method
    stats["Worst Day"] = value_history.worst()  # quantstats extension method
    stats["Win Days %"] = value_history.win_rate()  # quantstats extension method

    # Cash stats (vectorized)
    cash_utilizations = 1 - (cash_history / value_history)
    stats["Mean Cash Available"] = cash_history[1:].mean()
    stats["Mean Cash Utilization"] = cash_utilizations[1:].mean()

    df = pd.DataFrame({key: (value,) for key, value in stats.items()})

    if plot:
        qs.reports.html(value_history, title=f"{stocks} - {strat}", output=True)

    return df
