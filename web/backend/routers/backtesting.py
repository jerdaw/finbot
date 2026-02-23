"""Backtesting router — wraps BacktestRunner service."""

from __future__ import annotations

from typing import Any

import backtrader as bt
import pandas as pd
from fastapi import APIRouter, HTTPException

from finbot.services.backtesting.backtest_runner import BacktestRunner
from finbot.services.backtesting.brokers.commission_schemes import CommInfo_NoCommission
from finbot.services.backtesting.strategies.dip_buy_sma import DipBuySMA
from finbot.services.backtesting.strategies.dip_buy_stdev import DipBuyStdev
from finbot.services.backtesting.strategies.dual_momentum import DualMomentum
from finbot.services.backtesting.strategies.macd_dual import MACDDual
from finbot.services.backtesting.strategies.macd_single import MACDSingle
from finbot.services.backtesting.strategies.no_rebalance import NoRebalance
from finbot.services.backtesting.strategies.rebalance import Rebalance
from finbot.services.backtesting.strategies.risk_parity import RiskParity
from finbot.services.backtesting.strategies.sma_crossover import SMACrossover
from finbot.services.backtesting.strategies.sma_crossover_double import SMACrossoverDouble
from finbot.services.backtesting.strategies.sma_crossover_triple import SMACrossoverTriple
from finbot.services.backtesting.strategies.sma_rebal_mix import SmaRebalMix
from finbot.utils.data_collection_utils.yfinance.get_history import get_history
from web.backend.schemas.backtesting import BacktestRequest, BacktestResponse, StrategyInfo, StrategyParam, TradeRecord
from web.backend.services.serializers import dataframe_to_records, stats_df_to_dict

router = APIRouter()

STRATEGIES: dict[str, Any] = {
    "NoRebalance": NoRebalance,
    "Rebalance": Rebalance,
    "SMACrossover": SMACrossover,
    "SMACrossoverDouble": SMACrossoverDouble,
    "SMACrossoverTriple": SMACrossoverTriple,
    "MACDSingle": MACDSingle,
    "MACDDual": MACDDual,
    "DipBuySMA": DipBuySMA,
    "DipBuyStdev": DipBuyStdev,
    "SmaRebalMix": SmaRebalMix,
    "DualMomentum": DualMomentum,
    "RiskParity": RiskParity,
}

STRATEGY_INFO: list[StrategyInfo] = [
    StrategyInfo(
        name="NoRebalance",
        description="Buy and hold without rebalancing",
        params=[],
    ),
    StrategyInfo(
        name="Rebalance",
        description="Periodic portfolio rebalancing at fixed intervals",
        params=[
            StrategyParam(name="rebal_interval", type="int", default=63, min=1, description="Days between rebalances"),
        ],
    ),
    StrategyInfo(
        name="SMACrossover",
        description="Single SMA crossover timing strategy",
        params=[
            StrategyParam(name="fast_ma", type="int", default=50, min=2, description="Fast moving average period"),
            StrategyParam(name="slow_ma", type="int", default=200, min=2, description="Slow moving average period"),
        ],
    ),
    StrategyInfo(
        name="SMACrossoverDouble",
        description="Double SMA crossover timing strategy",
        params=[
            StrategyParam(name="fast_ma", type="int", default=50, min=2, description="Fast moving average period"),
            StrategyParam(name="slow_ma", type="int", default=200, min=2, description="Slow moving average period"),
        ],
    ),
    StrategyInfo(
        name="SMACrossoverTriple",
        description="Triple SMA crossover with three moving averages",
        params=[
            StrategyParam(name="fast_ma", type="int", default=20, min=2, description="Fast moving average period"),
            StrategyParam(name="med_ma", type="int", default=50, min=2, description="Medium moving average period"),
            StrategyParam(name="slow_ma", type="int", default=200, min=2, description="Slow moving average period"),
        ],
    ),
    StrategyInfo(
        name="MACDSingle",
        description="MACD-based single signal strategy",
        params=[
            StrategyParam(name="fast_ma", type="int", default=12, min=2, description="Fast EMA period"),
            StrategyParam(name="slow_ma", type="int", default=26, min=2, description="Slow EMA period"),
            StrategyParam(name="signal_period", type="int", default=9, min=1, description="Signal line period"),
        ],
    ),
    StrategyInfo(
        name="MACDDual",
        description="MACD-based dual signal strategy",
        params=[
            StrategyParam(name="fast_ma", type="int", default=12, min=2, description="Fast EMA period"),
            StrategyParam(name="slow_ma", type="int", default=26, min=2, description="Slow EMA period"),
            StrategyParam(name="signal_period", type="int", default=9, min=1, description="Signal line period"),
        ],
    ),
    StrategyInfo(
        name="DipBuySMA",
        description="Buy dips identified by SMA deviation",
        params=[
            StrategyParam(name="fast_ma", type="int", default=20, min=2, description="Fast moving average period"),
            StrategyParam(name="med_ma", type="int", default=50, min=2, description="Medium moving average period"),
            StrategyParam(name="slow_ma", type="int", default=200, min=2, description="Slow moving average period"),
        ],
    ),
    StrategyInfo(
        name="DipBuyStdev",
        description="Buy dips identified by standard deviation quantiles",
        params=[
            StrategyParam(
                name="buy_quantile", type="float", default=0.1, min=0.0, description="Buy threshold quantile"
            ),
            StrategyParam(
                name="sell_quantile", type="float", default=1.0, min=0.0, description="Sell threshold quantile"
            ),
        ],
    ),
    StrategyInfo(
        name="SmaRebalMix",
        description="Combined SMA timing with portfolio rebalancing",
        params=[
            StrategyParam(name="fast_ma", type="int", default=20, min=2, description="Fast moving average period"),
            StrategyParam(name="med_ma", type="int", default=50, min=2, description="Medium moving average period"),
            StrategyParam(name="slow_ma", type="int", default=200, min=2, description="Slow moving average period"),
        ],
    ),
    StrategyInfo(
        name="DualMomentum",
        description="Dual momentum with absolute and relative strength, safe-asset fallback",
        params=[
            StrategyParam(name="lookback", type="int", default=252, min=21, description="Lookback period in days"),
            StrategyParam(
                name="rebal_interval", type="int", default=21, min=1, description="Rebalance interval in days"
            ),
        ],
        min_assets=2,
    ),
    StrategyInfo(
        name="RiskParity",
        description="Inverse-volatility weighted portfolio with periodic rebalancing",
        params=[
            StrategyParam(name="vol_window", type="int", default=63, min=10, description="Volatility lookback window"),
            StrategyParam(
                name="rebal_interval", type="int", default=21, min=1, description="Rebalance interval in days"
            ),
        ],
        min_assets=2,
    ),
]


@router.get("/strategies", response_model=list[StrategyInfo])
def list_strategies() -> list[StrategyInfo]:
    """List all available backtesting strategies with parameter definitions."""
    return STRATEGY_INFO


@router.post("/run", response_model=BacktestResponse)
def run_backtest(req: BacktestRequest) -> BacktestResponse:
    """Run a backtest with the given configuration."""
    if req.strategy not in STRATEGIES:
        raise HTTPException(status_code=400, detail=f"Unknown strategy: {req.strategy}")

    strat_cls = STRATEGIES[req.strategy]
    strat_kwargs = dict(req.strategy_params)

    # Add default proportions for NoRebalance / Rebalance
    if req.strategy == "NoRebalance" and "equity_proportions" not in strat_kwargs:
        strat_kwargs["equity_proportions"] = tuple(1.0 / len(req.tickers) for _ in req.tickers)
    elif req.strategy == "Rebalance" and "rebal_proportions" not in strat_kwargs:
        strat_kwargs["rebal_proportions"] = tuple(1.0 / len(req.tickers) for _ in req.tickers)

    # Load price data
    try:
        price_histories: dict[str, pd.DataFrame] = {}
        for t in req.tickers:
            price_histories[t.upper()] = get_history(t.upper())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load price data: {e}") from e

    # Run backtest
    try:
        start_ts = pd.Timestamp(req.start_date) if req.start_date else None
        end_ts = pd.Timestamp(req.end_date) if req.end_date else None

        runner = BacktestRunner(
            price_histories=price_histories,
            start=start_ts,
            end=end_ts,
            duration=None,
            start_step=None,
            init_cash=req.initial_cash,
            strat=strat_cls,
            strat_kwargs=strat_kwargs,
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=CommInfo_NoCommission,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )
        stats_df = runner.run_backtest()
        value_hist = runner.get_value_history()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {e}") from e

    # Serialize results
    stats = stats_df_to_dict(stats_df)
    vh_records = dataframe_to_records(value_hist)

    # Parse trades
    trades: list[TradeRecord] = []
    try:
        raw_trades = runner.get_trades()
        trades.extend(
            TradeRecord(
                date=str(getattr(t, "date", "")),
                ticker=str(getattr(t, "data_name", getattr(t, "ticker", ""))),
                action="buy" if getattr(t, "size", 0) > 0 else "sell",
                size=abs(float(getattr(t, "size", 0))),
                price=float(getattr(t, "price", 0)),
                value=float(getattr(t, "value", 0)),
            )
            for t in raw_trades
        )
    except Exception:
        pass  # Trades may not be available for all strategies

    return BacktestResponse(stats=stats, value_history=vh_records, trades=trades)
