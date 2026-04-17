"""Backtesting router — wraps BacktestRunner service."""

from __future__ import annotations

from collections import defaultdict
from math import isclose
from typing import Any

import backtrader as bt
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

from finbot.core.contracts.regime import MarketRegime, RegimeConfig
from finbot.services.backtesting.backtest_runner import BacktestRunner
from finbot.services.backtesting.brokers.commission_schemes import CommInfo_NoCommission
from finbot.services.backtesting.regime import SimpleRegimeDetector, segment_by_regime
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
from finbot.services.portfolio_analytics.benchmark import compute_benchmark_comparison
from finbot.services.portfolio_analytics.rolling import compute_rolling_metrics
from finbot.utils.data_collection_utils.yfinance.get_history import get_history
from web.backend.schemas.backtesting import (
    BacktestBenchmarkStats,
    CashflowEventRecord,
    BacktestRegimePeriod,
    BacktestRegimeSummary,
    BacktestRequest,
    BacktestResponse,
    RebalanceEventRecord,
    ReturnTableRow,
    StrategyInfo,
    StrategyParam,
    TradeRecord,
    WithdrawalDurabilitySummary,
)
from web.backend.schemas.portfolio_analytics import RollingMetricsResponse
from web.backend.services.serializers import dataframe_to_records, sanitize_value, stats_df_to_dict

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

STRATEGY_INFO_BY_NAME = {info.name: info for info in STRATEGY_INFO}


def _filter_price_history(
    df: pd.DataFrame,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    filtered = df.copy()
    if start_date is not None:
        filtered = filtered[filtered.index >= pd.Timestamp(start_date)]
    if end_date is not None:
        filtered = filtered[filtered.index <= pd.Timestamp(end_date)]
    return filtered


def _load_close_series(
    ticker: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.Series:
    try:
        df = get_history(ticker.upper())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to load price data for {ticker}: {exc}") from exc

    if df is None or df.empty:
        raise HTTPException(status_code=400, detail=f"No price data available for {ticker}")

    series = _filter_price_history(df, start_date, end_date)["Close"]
    if series.empty:
        raise HTTPException(status_code=400, detail=f"Insufficient price data for {ticker} after filtering")

    return series.astype(float)


def _build_benchmark_response(
    *,
    value_history: pd.DataFrame,
    benchmark_ticker: str,
    start_date: str | None,
    end_date: str | None,
    risk_free_rate: float,
) -> tuple[BacktestBenchmarkStats, list[dict[str, Any]]]:
    if value_history is None or value_history.empty or "Value" not in value_history.columns:
        raise HTTPException(status_code=500, detail="Backtest did not produce a usable value history")

    portfolio_series = value_history["Value"].dropna().astype(float)
    if len(portfolio_series) < 30:
        raise HTTPException(status_code=400, detail="Insufficient backtest observations for benchmark comparison")

    benchmark_series = _load_close_series(benchmark_ticker, start_date, end_date)

    common_idx = portfolio_series.index.intersection(benchmark_series.index)
    if len(common_idx) < 30:
        raise HTTPException(status_code=400, detail="Insufficient overlapping data between portfolio and benchmark")

    aligned_portfolio = portfolio_series.loc[common_idx]
    aligned_benchmark = benchmark_series.loc[common_idx]
    portfolio_returns = aligned_portfolio.pct_change().dropna()
    benchmark_returns = aligned_benchmark.pct_change().dropna()

    common_return_idx = portfolio_returns.index.intersection(benchmark_returns.index)
    if len(common_return_idx) < 30:
        raise HTTPException(status_code=400, detail="Insufficient overlapping returns between portfolio and benchmark")

    portfolio_returns = portfolio_returns.loc[common_return_idx]
    benchmark_returns = benchmark_returns.loc[common_return_idx]

    result = compute_benchmark_comparison(
        portfolio_returns=portfolio_returns.values,
        benchmark_returns=benchmark_returns.values,
        risk_free_rate=risk_free_rate,
        benchmark_name=benchmark_ticker.upper(),
    )

    normalized_benchmark = aligned_benchmark / aligned_benchmark.iloc[0] * aligned_portfolio.iloc[0]
    benchmark_frame = pd.DataFrame({"Value": normalized_benchmark}, index=normalized_benchmark.index)

    return (
        BacktestBenchmarkStats(
            alpha=sanitize_value(result.alpha),
            beta=sanitize_value(result.beta),
            r_squared=sanitize_value(result.r_squared),
            tracking_error=sanitize_value(result.tracking_error),
            information_ratio=sanitize_value(result.information_ratio),
            up_capture=sanitize_value(result.up_capture),
            down_capture=sanitize_value(result.down_capture),
            benchmark_name=result.benchmark_name,
            n_observations=result.n_observations,
        ),
        dataframe_to_records(benchmark_frame),
    )


def _build_period_return_table(value_history: pd.DataFrame, freq: str) -> list[ReturnTableRow]:
    if value_history is None or value_history.empty or "Value" not in value_history.columns:
        return []

    value_series = value_history["Value"].dropna().astype(float)
    if value_series.empty:
        return []

    rows: list[ReturnTableRow] = []
    grouped = value_series.groupby(value_series.index.to_period(freq))
    for period, period_values in grouped:
        start_value = float(period_values.iloc[0])
        end_value = float(period_values.iloc[-1])
        return_pct = (end_value / start_value - 1.0) if start_value != 0 else None
        rows.append(
            ReturnTableRow(
                period=str(period),
                start_value=sanitize_value(start_value),
                end_value=sanitize_value(end_value),
                return_pct=sanitize_value(return_pct),
            )
        )

    return rows


def _validate_cashflow_inputs(req: BacktestRequest) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    recurring = [rule.model_dump(exclude_none=True) for rule in req.recurring_cashflows]
    one_time = [event.model_dump(exclude_none=True) for event in req.one_time_cashflows]

    for rule in recurring:
        if float(rule["amount"]) == 0:
            raise HTTPException(status_code=400, detail="Recurring cashflow amounts must be non-zero")
        start_date = pd.Timestamp(rule["start_date"]) if rule.get("start_date") is not None else None
        end_date = pd.Timestamp(rule["end_date"]) if rule.get("end_date") is not None else None
        if start_date is not None and end_date is not None and start_date > end_date:
            raise HTTPException(status_code=400, detail="Recurring cashflow start_date must be before end_date")

    for event in one_time:
        if float(event["amount"]) == 0:
            raise HTTPException(status_code=400, detail="One-time cashflow amounts must be non-zero")
        try:
            pd.Timestamp(event["date"])
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="One-time cashflow date is invalid") from exc

    if req.inflation_rate < 0 or req.inflation_rate > 1:
        raise HTTPException(status_code=400, detail="inflation_rate must be between 0 and 1")

    return recurring, one_time


def _sanitize_dynamic_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: sanitize_value(value) for key, value in record.items()} for record in records]


def _build_real_value_history(value_history: pd.DataFrame, inflation_rate: float) -> list[dict[str, Any]]:
    if inflation_rate <= 0 or value_history is None or value_history.empty or "Value" not in value_history.columns:
        return []

    base_frame = value_history[[column for column in ["Value", "Cash"] if column in value_history.columns]].dropna(
        subset=["Value"]
    )
    if base_frame.empty:
        return []

    start_date = base_frame.index[0]
    year_fractions = (base_frame.index - start_date).days / 365.25
    inflation_factors = np.power(1 + inflation_rate, year_fractions)

    real_frame = pd.DataFrame(index=base_frame.index)
    real_frame["Value"] = base_frame["Value"].astype(float) / inflation_factors
    if "Cash" in base_frame.columns:
        real_frame["Cash"] = base_frame["Cash"].astype(float) / inflation_factors

    return dataframe_to_records(real_frame)


def _build_withdrawal_durability(
    *,
    value_history: pd.DataFrame,
    real_value_history: list[dict[str, Any]],
    cashflow_events: list[dict[str, Any]],
    inflation_rate: float,
) -> WithdrawalDurabilitySummary | None:
    if (not cashflow_events and inflation_rate <= 0) or value_history is None or value_history.empty:
        return None

    nominal_series = value_history["Value"].dropna().astype(float)
    if nominal_series.empty:
        return None

    real_series = None
    if real_value_history:
        real_frame = pd.DataFrame(real_value_history)
        if not real_frame.empty and "date" in real_frame.columns and "Value" in real_frame.columns:
            real_frame["date"] = pd.to_datetime(real_frame["date"])
            real_frame = real_frame.set_index("date")
            real_series = real_frame["Value"].dropna().astype(float)

    total_contributions = sum(float(event["amount"]) for event in cashflow_events if float(event["amount"]) > 0)
    total_withdrawals = sum(abs(float(event["amount"])) for event in cashflow_events if float(event["amount"]) < 0)
    depletion_points = nominal_series[nominal_series <= 0]
    depletion_date = depletion_points.index[0].isoformat() if not depletion_points.empty else None
    ending_real_value = float(real_series.iloc[-1]) if real_series is not None and not real_series.empty else None
    min_real_value = float(real_series.min()) if real_series is not None and not real_series.empty else None
    real_total_return = None
    if real_series is not None and not real_series.empty and float(real_series.iloc[0]) != 0:
        real_total_return = float(real_series.iloc[-1] / real_series.iloc[0] - 1.0)

    return WithdrawalDurabilitySummary(
        survived_to_end=depletion_date is None,
        depletion_date=depletion_date,
        ending_nominal_value=sanitize_value(float(nominal_series.iloc[-1])),
        ending_real_value=sanitize_value(ending_real_value),
        min_nominal_value=sanitize_value(float(nominal_series.min())),
        min_real_value=sanitize_value(min_real_value),
        total_contributions=total_contributions,
        total_withdrawals=total_withdrawals,
        net_cashflow=total_contributions - total_withdrawals,
        real_total_return=sanitize_value(real_total_return),
        inflation_rate=inflation_rate,
    )


def _build_rebalance_events(
    *,
    raw_trades: list[Any],
    value_history: pd.DataFrame,
    strategy_name: str,
) -> list[RebalanceEventRecord]:
    if not raw_trades:
        return []

    value_lookup = value_history[[column for column in ["Value", "Cash"] if column in value_history.columns]].copy()
    if not value_lookup.empty:
        value_lookup.index = pd.to_datetime(value_lookup.index).normalize()

    grouped: dict[pd.Timestamp, list[Any]] = defaultdict(list)
    for trade in raw_trades:
        timestamp = pd.Timestamp(getattr(trade, "timestamp", None))
        grouped[timestamp.normalize()].append(trade)

    rebalancing_strategies = {"Rebalance", "RiskParity", "RegimeAdaptive", "SmaRebalMix"}
    event_rows: list[RebalanceEventRecord] = []

    for index, trade_date in enumerate(sorted(grouped.keys())):
        trades = grouped[trade_date]
        symbols = sorted({str(getattr(trade, "symbol", "")) for trade in trades if getattr(trade, "symbol", "")})
        gross_trade_value = sum(abs(float(getattr(trade, "value", 0.0))) for trade in trades)
        net_trade_value = sum(float(getattr(trade, "size", 0.0)) * float(getattr(trade, "price", 0.0)) for trade in trades)

        event_type = "trade"
        if index == 0 and strategy_name in {"NoRebalance", "Rebalance"}:
            event_type = "initial_allocation"
        elif strategy_name in rebalancing_strategies or len(symbols) > 1:
            event_type = "rebalance"

        portfolio_value = None
        cash_after = None
        if trade_date in value_lookup.index:
            row = value_lookup.loc[trade_date]
            portfolio_value = sanitize_value(float(row["Value"])) if "Value" in row else None
            cash_after = sanitize_value(float(row["Cash"])) if "Cash" in row else None

        event_rows.append(
            RebalanceEventRecord(
                date=trade_date.isoformat(),
                event_type=event_type,
                trade_count=len(trades),
                symbols=symbols,
                gross_trade_value=sanitize_value(gross_trade_value),
                net_trade_value=sanitize_value(net_trade_value),
                portfolio_value=portfolio_value,
                cash_after=cash_after,
            )
        )

    return event_rows


def _build_rolling_metrics_response(
    *,
    value_history: pd.DataFrame,
    benchmark_ticker: str | None,
    start_date: str | None,
    end_date: str | None,
    risk_free_rate: float,
    default_window: int = 63,
) -> RollingMetricsResponse | None:
    if value_history is None or value_history.empty or "Value" not in value_history.columns:
        return None

    portfolio_series = value_history["Value"].dropna().astype(float)
    portfolio_returns = portfolio_series.pct_change().dropna()
    if len(portfolio_returns) < 30:
        return None

    benchmark_arr: np.ndarray | None = None
    rolling_index = portfolio_returns.index
    if benchmark_ticker is not None:
        try:
            benchmark_returns = _load_close_series(benchmark_ticker, start_date, end_date).pct_change().dropna()
        except HTTPException:
            return None
        common_idx = portfolio_returns.index.intersection(benchmark_returns.index)
        if len(common_idx) < 30:
            return None
        portfolio_returns = portfolio_returns.loc[common_idx]
        benchmark_arr = benchmark_returns.loc[common_idx].values
        rolling_index = common_idx

    effective_window = min(default_window, len(portfolio_returns))
    if effective_window < 2:
        return None

    try:
        result = compute_rolling_metrics(
            returns=portfolio_returns.values,
            window=effective_window,
            benchmark_returns=benchmark_arr,
            risk_free_rate=risk_free_rate,
            dates=[timestamp.isoformat() for timestamp in rolling_index],
        )
    except (ValueError, TypeError):
        return None

    sharpe_arr = np.array(result.sharpe, dtype=float)
    vol_arr = np.array(result.volatility, dtype=float)
    mean_sharpe = sanitize_value(float(np.nanmean(sharpe_arr)))
    mean_vol = sanitize_value(float(np.nanmean(vol_arr)))

    mean_beta: float | None = None
    beta_list: list[float | None] | None = None
    if result.beta is not None:
        beta_arr = np.array(result.beta, dtype=float)
        beta_list = [sanitize_value(value) for value in result.beta]
        mean_beta = sanitize_value(float(np.nanmean(beta_arr)))

    return RollingMetricsResponse(
        window=result.window,
        n_obs=result.n_obs,
        sharpe=[sanitize_value(value) for value in result.sharpe],
        volatility=[sanitize_value(value) for value in result.volatility],
        beta=beta_list,
        dates=list(result.dates),
        mean_sharpe=mean_sharpe,
        mean_vol=mean_vol,
        mean_beta=mean_beta,
    )


def _build_regime_response(
    *,
    price_histories: dict[str, pd.DataFrame],
    value_history: pd.DataFrame,
    primary_ticker: str,
    benchmark_ticker: str | None,
    start_date: str | None,
    end_date: str | None,
) -> tuple[str | None, list[BacktestRegimeSummary], list[BacktestRegimePeriod]]:
    if value_history is None or value_history.empty or "Value" not in value_history.columns:
        return None, [], []

    reference_ticker = benchmark_ticker or primary_ticker
    market_df = price_histories.get(reference_ticker)
    if market_df is None:
        try:
            market_df = get_history(reference_ticker)
        except Exception:
            return reference_ticker, [], []

    if market_df is None or market_df.empty:
        return reference_ticker, [], []

    filtered_market_df = _filter_price_history(market_df, start_date, end_date)
    if filtered_market_df.empty:
        return reference_ticker, [], []

    equity_curve = value_history["Value"].dropna().astype(float).sort_index()
    if len(equity_curve) < 2:
        return reference_ticker, [], []

    detector = SimpleRegimeDetector()
    config = RegimeConfig()
    try:
        periods = detector.detect(filtered_market_df, config)
        if not periods:
            return reference_ticker, [], []

        regime_metrics = segment_by_regime(
            None,
            filtered_market_df,
            detector=detector,
            config=config,
            equity_curve=equity_curve,
        )
    except ValueError:
        return reference_ticker, [], []

    summary_rows = [
        BacktestRegimeSummary(
            regime=regime.value,
            count_periods=regime_metrics[regime].count_periods,
            total_days=regime_metrics[regime].total_days,
            cagr=sanitize_value(regime_metrics[regime].metrics.get("cagr")),
            volatility=sanitize_value(regime_metrics[regime].metrics.get("volatility")),
            sharpe=sanitize_value(regime_metrics[regime].metrics.get("sharpe")),
            total_return=sanitize_value(regime_metrics[regime].metrics.get("total_return")),
        )
        for regime in MarketRegime
    ]

    period_rows: list[BacktestRegimePeriod] = []
    for period in periods:
        slice_ = equity_curve[(equity_curve.index >= period.start) & (equity_curve.index <= period.end)]
        daily_returns = slice_.pct_change().dropna()
        portfolio_return = None
        portfolio_volatility = None
        if len(slice_) >= 2:
            portfolio_return = float(slice_.iloc[-1] / slice_.iloc[0] - 1.0)
        if len(daily_returns) >= 2:
            portfolio_volatility = float(daily_returns.std(ddof=1) * (252**0.5))

        period_rows.append(
            BacktestRegimePeriod(
                regime=period.regime.value,
                start=period.start.isoformat(),
                end=period.end.isoformat(),
                days=int((period.end - period.start).days) + 1,
                market_return=sanitize_value(period.market_return),
                market_volatility=sanitize_value(period.market_volatility),
                portfolio_return=sanitize_value(portfolio_return),
                portfolio_volatility=sanitize_value(portfolio_volatility),
            )
        )

    return reference_ticker, summary_rows, period_rows


def _validate_tickers(tickers: list[str]) -> list[str]:
    cleaned_tickers = [ticker.strip().upper() for ticker in tickers]
    if any(not ticker for ticker in cleaned_tickers):
        raise HTTPException(status_code=400, detail="Tickers must not be empty")
    if len(set(cleaned_tickers)) != len(cleaned_tickers):
        raise HTTPException(status_code=400, detail="Tickers must be unique")
    return cleaned_tickers


def _validate_allocation_weights(
    proportions: Any,
    *,
    ticker_count: int,
    field_name: str,
) -> list[float]:
    if not isinstance(proportions, (list, tuple)):
        raise HTTPException(status_code=400, detail=f"{field_name} must be a list of weights")

    try:
        weights = [float(value) for value in proportions]
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"{field_name} must contain numeric weights") from exc

    if len(weights) != ticker_count:
        raise HTTPException(status_code=400, detail=f"{field_name} length must match ticker count")
    if any(weight <= 0 for weight in weights):
        raise HTTPException(status_code=400, detail=f"{field_name} weights must be greater than 0")
    if not isclose(sum(weights), 1.0, rel_tol=1e-6, abs_tol=1e-6):
        raise HTTPException(status_code=400, detail=f"{field_name} weights must sum to 1.0")

    return weights


def _validate_request(req: BacktestRequest, strat_kwargs: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    cleaned_tickers = _validate_tickers(req.tickers)
    strategy_info = STRATEGY_INFO_BY_NAME[req.strategy]

    if len(cleaned_tickers) < strategy_info.min_assets:
        raise HTTPException(
            status_code=400,
            detail=f"{req.strategy} requires at least {strategy_info.min_assets} assets",
        )

    if req.strategy == "DualMomentum" and len(cleaned_tickers) != 2:
        raise HTTPException(status_code=400, detail="DualMomentum requires exactly 2 assets")

    if req.benchmark_ticker is not None and not req.benchmark_ticker.strip():
        raise HTTPException(status_code=400, detail="benchmark_ticker must not be empty")

    recurring_cashflows, one_time_cashflows = _validate_cashflow_inputs(req)
    if recurring_cashflows:
        strat_kwargs["recurring_cashflows"] = recurring_cashflows
    if one_time_cashflows:
        strat_kwargs["one_time_cashflows"] = one_time_cashflows

    if req.strategy == "NoRebalance":
        strat_kwargs["equity_proportions"] = _validate_allocation_weights(
            strat_kwargs["equity_proportions"],
            ticker_count=len(cleaned_tickers),
            field_name="equity_proportions",
        )
    elif req.strategy == "Rebalance":
        strat_kwargs["rebal_proportions"] = _validate_allocation_weights(
            strat_kwargs["rebal_proportions"],
            ticker_count=len(cleaned_tickers),
            field_name="rebal_proportions",
        )

    return cleaned_tickers, strat_kwargs


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

    cleaned_tickers, strat_kwargs = _validate_request(req, strat_kwargs)

    # Load price data
    try:
        price_histories: dict[str, pd.DataFrame] = {}
        for ticker in cleaned_tickers:
            price_histories[ticker] = get_history(ticker)
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
    monthly_returns = _build_period_return_table(value_hist, "M")
    annual_returns = _build_period_return_table(value_hist, "Y")
    benchmark_stats: BacktestBenchmarkStats | None = None
    benchmark_value_history: list[dict[str, Any]] = []
    rolling_metrics = _build_rolling_metrics_response(
        value_history=value_hist,
        benchmark_ticker=req.benchmark_ticker.strip().upper() if req.benchmark_ticker is not None else None,
        start_date=req.start_date,
        end_date=req.end_date,
        risk_free_rate=req.risk_free_rate,
    )
    regime_reference_ticker, regime_summary, regime_periods = _build_regime_response(
        price_histories=price_histories,
        value_history=value_hist,
        primary_ticker=cleaned_tickers[0],
        benchmark_ticker=req.benchmark_ticker.strip().upper() if req.benchmark_ticker is not None else None,
        start_date=req.start_date,
        end_date=req.end_date,
    )

    if req.benchmark_ticker is not None:
        benchmark_stats, benchmark_value_history = _build_benchmark_response(
            value_history=value_hist,
            benchmark_ticker=req.benchmark_ticker.strip().upper(),
            start_date=req.start_date,
            end_date=req.end_date,
            risk_free_rate=req.risk_free_rate,
        )

    # Parse trades
    trades: list[TradeRecord] = []
    raw_trades: list[Any] = []
    try:
        raw_trades = runner.get_trades()
        trades.extend(
            TradeRecord(
                date=str(getattr(t, "timestamp", getattr(t, "date", ""))),
                ticker=str(getattr(t, "symbol", getattr(t, "data_name", getattr(t, "ticker", "")))),
                action="buy" if getattr(t, "size", 0) > 0 else "sell",
                size=abs(float(getattr(t, "size", 0))),
                price=float(getattr(t, "price", 0)),
                value=float(getattr(t, "value", 0)),
            )
            for t in raw_trades
        )
    except Exception:
        pass  # Trades may not be available for all strategies

    cashflow_events_raw = runner.get_cashflow_events()
    cashflow_events = [CashflowEventRecord(**event) for event in cashflow_events_raw]
    real_value_history = _build_real_value_history(value_hist, req.inflation_rate)
    withdrawal_durability = _build_withdrawal_durability(
        value_history=value_hist,
        real_value_history=real_value_history,
        cashflow_events=cashflow_events_raw,
        inflation_rate=req.inflation_rate,
    )
    allocation_history = _sanitize_dynamic_records(runner.get_allocation_history())
    rebalance_events = _build_rebalance_events(
        raw_trades=raw_trades,
        value_history=value_hist,
        strategy_name=req.strategy,
    )

    return BacktestResponse(
        stats=stats,
        value_history=vh_records,
        trades=trades,
        benchmark_stats=benchmark_stats,
        benchmark_value_history=benchmark_value_history,
        rolling_metrics=rolling_metrics,
        regime_reference_ticker=regime_reference_ticker,
        regime_summary=regime_summary,
        regime_periods=regime_periods,
        cashflow_events=cashflow_events,
        real_value_history=real_value_history,
        withdrawal_durability=withdrawal_durability,
        allocation_history=allocation_history,
        rebalance_events=rebalance_events,
        monthly_returns=monthly_returns,
        annual_returns=annual_returns,
    )
