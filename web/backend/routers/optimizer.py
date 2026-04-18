"""Optimizer router for DCA, Pareto, and efficient frontier research workflows."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import backtrader as bt
import pandas as pd
from fastapi import APIRouter, HTTPException

from finbot.core.contracts.models import BacktestRunMetadata, BacktestRunResult
from finbot.core.contracts.serialization import build_backtest_run_result_from_stats
from finbot.services.backtesting.backtest_runner import BacktestRunner
from finbot.services.backtesting.brokers.commission_schemes import CommInfo_NoCommission
from finbot.services.optimization import compute_efficient_frontier, compute_pareto_front
from finbot.services.optimization.dca_optimizer import analyze_results_helper, dca_optimizer
from finbot.utils.data_collection_utils.yfinance.get_history import get_history
from web.backend.routers.backtesting import STRATEGIES, STRATEGY_INFO_BY_NAME
from web.backend.schemas.optimizer import (
    DCAOptimizerRequest,
    DCAOptimizerResponse,
    EfficientFrontierAssetStatResponse,
    EfficientFrontierPortfolioResponse,
    EfficientFrontierRequest,
    EfficientFrontierResponse,
    ParetoOptimizerRequest,
    ParetoOptimizerResponse,
    ParetoPointResponse,
)
from web.backend.services.serializers import dataframe_to_records, sanitize_value

router = APIRouter()


def _filter_history(df: pd.DataFrame, start_date: str | None, end_date: str | None) -> pd.DataFrame:
    filtered = df.copy()
    if start_date is not None:
        filtered = filtered[filtered.index >= pd.Timestamp(start_date)]
    if end_date is not None:
        filtered = filtered[filtered.index <= pd.Timestamp(end_date)]
    if filtered.empty:
        raise ValueError("Insufficient price data after filtering")
    return filtered


def _load_histories(tickers: list[str], start_date: str | None, end_date: str | None) -> dict[str, pd.DataFrame]:
    histories: dict[str, pd.DataFrame] = {}
    for ticker in tickers:
        histories[ticker] = _filter_history(get_history(ticker), start_date, end_date)
    return histories


def _default_strategy_params(strategy_name: str, tickers: list[str]) -> tuple[list[str], dict[str, object], str | None]:
    info = STRATEGY_INFO_BY_NAME.get(strategy_name)
    if info is None:
        return [], {}, f"Unknown strategy: {strategy_name}"

    tickers_used = list(tickers)
    if strategy_name == "DualMomentum":
        if len(tickers) != 2:
            return [], {}, "DualMomentum requires exactly 2 tickers"
    elif strategy_name == "RiskParity":
        if len(tickers) < 2:
            return [], {}, "RiskParity requires at least 2 tickers"
    elif strategy_name in {"NoRebalance", "Rebalance"}:
        tickers_used = list(tickers)
    else:
        tickers_used = [tickers[0]]

    params = {param.name: param.default for param in info.params}
    if strategy_name == "NoRebalance":
        params["equity_proportions"] = [1.0 / len(tickers_used) for _ in tickers_used]
    elif strategy_name == "Rebalance":
        params["rebal_proportions"] = [1.0 / len(tickers_used) for _ in tickers_used]

    return tickers_used, params, None


def _run_strategy(
    *,
    strategy_name: str,
    tickers_used: list[str],
    params: dict[str, object],
    histories: dict[str, pd.DataFrame],
    start_date: str | None,
    end_date: str | None,
    initial_cash: float,
) -> BacktestRunResult:
    runner = BacktestRunner(
        price_histories={ticker: histories[ticker].copy() for ticker in tickers_used},
        start=pd.Timestamp(start_date) if start_date else None,
        end=pd.Timestamp(end_date) if end_date else None,
        duration=None,
        start_step=None,
        init_cash=initial_cash,
        strat=STRATEGIES[strategy_name],
        strat_kwargs=dict(params),
        broker=bt.brokers.BackBroker,
        broker_kwargs={},
        broker_commission=CommInfo_NoCommission,
        sizer=bt.sizers.AllInSizer,
        sizer_kwargs={},
        plot=False,
    )
    stats_df = runner.run_backtest()
    metadata = BacktestRunMetadata(
        run_id=f"pareto-{uuid4()}",
        engine_name="backtrader",
        engine_version=str(getattr(bt, "__version__", "unknown")),
        strategy_name=strategy_name,
        created_at=datetime.now(UTC),
        config_hash=f"pareto::{strategy_name}::{','.join(tickers_used)}",
        data_snapshot_id="web-local-histories",
    )
    result = build_backtest_run_result_from_stats(
        stats_df=stats_df,
        metadata=metadata,
        assumptions={
            "tickers": tickers_used,
            "parameters": params,
            "start": start_date,
            "end": end_date,
            "initial_cash": initial_cash,
            "source": "web-pareto",
        },
    )
    if result.metrics.get("max_drawdown", 0.0) < 0:
        return BacktestRunResult(
            metadata=result.metadata,
            metrics={
                **result.metrics,
                "max_drawdown": abs(result.metrics["max_drawdown"]),
            },
            schema_version=result.schema_version,
            assumptions=result.assumptions,
            artifacts=result.artifacts,
            warnings=result.warnings,
            costs=result.costs,
        )
    return result


def _portfolio_to_response(portfolio) -> EfficientFrontierPortfolioResponse:
    return EfficientFrontierPortfolioResponse(
        expected_return=portfolio.expected_return,
        volatility=portfolio.volatility,
        sharpe_ratio=portfolio.sharpe_ratio,
        weights=portfolio.weights,
    )


def _build_pareto_point(
    result: BacktestRunResult, *, objective_a: str, objective_b: str, is_front: bool
) -> ParetoPointResponse:
    metrics = {key: sanitize_value(value) for key, value in result.metrics.items()}
    return ParetoPointResponse(
        strategy_name=result.metadata.strategy_name,
        tickers_used=list(result.assumptions.get("tickers", [])),
        params=dict(result.assumptions.get("parameters", {})),
        metrics=metrics,
        objective_a=float(result.metrics[objective_a]),
        objective_b=float(result.metrics[objective_b]),
        is_pareto_optimal=is_front,
    )


@router.post("/run", response_model=DCAOptimizerResponse)
def run_optimizer(req: DCAOptimizerRequest) -> DCAOptimizerResponse:
    """Run DCA optimizer grid search."""
    try:
        price_df = get_history(req.ticker.upper())
        price_series = price_df["Close"] if "Close" in price_df.columns else price_df["Adj Close"]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load price data for {req.ticker}: {e}") from e

    try:
        raw_results = dca_optimizer(
            price_history=price_series,
            ticker=req.ticker.upper(),
            ratio_range=tuple(req.ratio_range),
            dca_durations=tuple(req.dca_durations),
            dca_steps=tuple(req.dca_steps),
            trial_durations=tuple(req.trial_durations),
            starting_cash=req.starting_cash,
            start_step=req.start_step,
            save_df=False,
            analyze_results=False,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimizer failed: {e}") from e

    try:
        ratio_df, duration_df = analyze_results_helper(raw_results, plot=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Result analysis failed: {e}") from e

    return DCAOptimizerResponse(
        by_ratio=dataframe_to_records(ratio_df.reset_index()),
        by_duration=dataframe_to_records(duration_df.reset_index()),
        raw_results=dataframe_to_records(raw_results.head(500)),
    )


@router.post("/pareto/run", response_model=ParetoOptimizerResponse)
def run_pareto_optimizer(req: ParetoOptimizerRequest) -> ParetoOptimizerResponse:
    """Run a canonical strategy sweep and surface the Pareto-optimal frontier."""
    cleaned_tickers = [ticker.strip().upper() for ticker in req.tickers if ticker.strip()]
    if not cleaned_tickers:
        raise HTTPException(status_code=400, detail="At least one ticker is required")
    if len(set(cleaned_tickers)) != len(cleaned_tickers):
        raise HTTPException(status_code=400, detail="Tickers must be unique")

    warnings: list[str] = []
    try:
        histories = _load_histories(cleaned_tickers, req.start_date, req.end_date)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to load price data: {exc}") from exc

    results: list[BacktestRunResult] = []
    for strategy_name in req.strategies:
        tickers_used, params, warning = _default_strategy_params(strategy_name, cleaned_tickers)
        if warning is not None:
            warnings.append(f"{strategy_name}: {warning}")
            continue

        try:
            results.append(
                _run_strategy(
                    strategy_name=strategy_name,
                    tickers_used=tickers_used,
                    params=params,
                    histories=histories,
                    start_date=req.start_date,
                    end_date=req.end_date,
                    initial_cash=req.initial_cash,
                )
            )
        except Exception as exc:
            warnings.append(f"{strategy_name}: {exc}")

    if not results:
        raise HTTPException(
            status_code=400, detail="No compatible strategies could be evaluated for the selected assets"
        )

    try:
        pareto = compute_pareto_front(
            results,
            objective_a=req.objective_a,
            objective_b=req.objective_b,
            maximize_a=req.maximize_a,
            maximize_b=req.maximize_b,
        )
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    front_names = {point.strategy_name for point in pareto.pareto_front}
    all_points = [
        _build_pareto_point(
            result,
            objective_a=req.objective_a,
            objective_b=req.objective_b,
            is_front=result.metadata.strategy_name in front_names,
        )
        for result in results
    ]
    pareto_front = [point for point in all_points if point.is_pareto_optimal]
    dominated_points = [point for point in all_points if not point.is_pareto_optimal]

    return ParetoOptimizerResponse(
        objective_a_name=pareto.objective_a_name,
        objective_b_name=pareto.objective_b_name,
        n_evaluated=pareto.n_evaluated,
        all_points=all_points,
        pareto_front=pareto_front,
        dominated_points=dominated_points,
        warnings=warnings,
    )


@router.post("/efficient-frontier/run", response_model=EfficientFrontierResponse)
def run_efficient_frontier(req: EfficientFrontierRequest) -> EfficientFrontierResponse:
    """Compute a long-only efficient frontier from historical asset returns."""
    cleaned_tickers = [ticker.strip().upper() for ticker in req.tickers if ticker.strip()]
    if len(cleaned_tickers) < 2:
        raise HTTPException(status_code=400, detail="At least two tickers are required")
    if len(set(cleaned_tickers)) != len(cleaned_tickers):
        raise HTTPException(status_code=400, detail="Tickers must be unique")

    try:
        histories = _load_histories(cleaned_tickers, req.start_date, req.end_date)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to load price data: {exc}") from exc

    try:
        result = compute_efficient_frontier(
            histories,
            n_portfolios=req.n_portfolios,
            risk_free_rate=req.risk_free_rate,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Efficient frontier failed: {exc}") from exc

    return EfficientFrontierResponse(
        portfolios=[_portfolio_to_response(portfolio) for portfolio in result.portfolios],
        frontier=[_portfolio_to_response(portfolio) for portfolio in result.frontier],
        max_sharpe=_portfolio_to_response(result.max_sharpe),
        min_volatility=_portfolio_to_response(result.min_volatility),
        asset_stats=[
            EfficientFrontierAssetStatResponse(
                ticker=stat.ticker,
                annual_return=stat.annual_return,
                annual_volatility=stat.annual_volatility,
            )
            for stat in result.asset_stats
        ],
        correlation_matrix=result.correlation_matrix,
    )
