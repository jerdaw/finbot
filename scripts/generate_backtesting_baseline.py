"""Generate baseline metrics for golden backtesting strategies."""

from __future__ import annotations

from pathlib import Path
from time import perf_counter

import backtrader as bt
import pandas as pd

from finbot.services.backtesting.backtest_runner import BacktestRunner
from finbot.services.backtesting.brokers.fixed_commission_scheme import FixedCommissionScheme
from finbot.services.backtesting.strategies.dual_momentum import DualMomentum
from finbot.services.backtesting.strategies.no_rebalance import NoRebalance
from finbot.services.backtesting.strategies.risk_parity import RiskParity

START = pd.Timestamp("2010-01-04")
END = pd.Timestamp("2026-02-09")
INIT_CASH = 100_000.0
BASE_HISTORY_DIR = Path("finbot/data/yfinance_data/history")
OUTPUT_CSV = Path("docs/research/backtesting-baseline-results-2026-02-14.csv")


def _load_price_histories(symbols: list[str]) -> dict[str, pd.DataFrame]:
    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    histories: dict[str, pd.DataFrame] = {}
    for symbol in symbols:
        df = pd.read_parquet(BASE_HISTORY_DIR / f"{symbol}_history_1d.parquet")
        histories[symbol] = df[required_cols].copy()
    return histories


def _run_case(
    case_id: str,
    strategy: type[bt.Strategy],
    strat_kwargs: dict[str, object],
    symbols: list[str],
) -> dict[str, object]:
    runner = BacktestRunner(
        price_histories=_load_price_histories(symbols),
        start=START,
        end=END,
        duration=None,
        start_step=None,
        init_cash=INIT_CASH,
        strat=strategy,
        strat_kwargs=strat_kwargs,
        broker=bt.brokers.BackBroker,
        broker_kwargs={},
        broker_commission=FixedCommissionScheme,
        sizer=bt.sizers.AllInSizer,
        sizer_kwargs={},
        plot=False,
    )

    start_time = perf_counter()
    stats = runner.run_backtest()
    runtime_s = perf_counter() - start_time

    return {
        "case_id": case_id,
        "strategy": strategy.__name__,
        "symbols": ",".join(symbols),
        "rows": len(runner.get_value_history()),
        "runtime_s": runtime_s,
        "start_date": str(stats["Start Date"].iloc[0].date()),
        "end_date": str(stats["End Date"].iloc[0].date()),
        "starting_value": float(stats["Starting Value"].iloc[0]),
        "ending_value": float(stats["Ending Value"].iloc[0]),
        "roi": float(stats["ROI"].iloc[0]),
        "cagr": float(stats["CAGR"].iloc[0]),
        "sharpe": float(stats["Sharpe"].iloc[0]),
        "max_drawdown": float(stats["Max Drawdown"].iloc[0]),
        "mean_cash_utilization": float(stats["Mean Cash Utilization"].iloc[0]),
    }


def main() -> None:
    cases = [
        ("GS-01", NoRebalance, {"equity_proportions": [1.0]}, ["SPY"]),
        ("GS-02", DualMomentum, {"lookback": 252, "rebal_interval": 21}, ["SPY", "TLT"]),
        ("GS-03", RiskParity, {"vol_window": 63, "rebal_interval": 21}, ["SPY", "QQQ", "TLT"]),
    ]

    rows = [_run_case(case_id, strategy, kwargs, symbols) for case_id, strategy, kwargs, symbols in cases]
    result = pd.DataFrame(rows)
    result.to_csv(OUTPUT_CSV, index=False)

    print(result.to_string(index=False))
    print(f"Wrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
