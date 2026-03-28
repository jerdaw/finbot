"""Risk analytics router — VaR, stress testing, Kelly criterion."""

from __future__ import annotations

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

from finbot.services.risk_analytics.kelly import compute_kelly_from_returns, compute_multi_asset_kelly
from finbot.services.risk_analytics.stress import SCENARIOS, run_stress_test
from finbot.services.risk_analytics.var import compute_cvar, compute_var, var_backtest
from finbot.utils.data_collection_utils.yfinance.get_history import get_history
from web.backend.schemas.risk_analytics import (
    CVaRResultSchema,
    KellyRequest,
    KellyResponse,
    MultiKellyRequest,
    MultiKellyResponse,
    StressTestRequest,
    StressTestResponse,
    StressTestResultSchema,
    VaRBacktestRequest,
    VaRBacktestResponse,
    VaRRequest,
    VaRResponse,
    VaRResultSchema,
)
from web.backend.services.serializers import sanitize_value

router = APIRouter()


def _load_returns(ticker: str, start_date: str | None, end_date: str | None) -> np.ndarray:
    """Load price history for a ticker and return daily returns as a numpy array.

    Args:
        ticker: Stock ticker symbol.
        start_date: Optional start date filter (ISO format string).
        end_date: Optional end date filter (ISO format string).

    Returns:
        1-D numpy array of daily returns.

    Raises:
        HTTPException: If price data cannot be loaded or is empty.
    """
    try:
        df = get_history(ticker.upper())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load price data for {ticker}: {e}") from e

    if df is None or df.empty:
        raise HTTPException(status_code=400, detail=f"No price data available for {ticker}")

    if start_date is not None:
        df = df[df.index >= pd.Timestamp(start_date)]
    if end_date is not None:
        df = df[df.index <= pd.Timestamp(end_date)]

    if df.empty:
        raise HTTPException(status_code=400, detail=f"No price data for {ticker} in the specified date range")

    returns = df["Close"].pct_change().dropna().to_numpy()

    if len(returns) == 0:
        raise HTTPException(status_code=400, detail=f"Insufficient price data for {ticker} to compute returns")

    return returns


@router.post("/var", response_model=VaRResponse)
def compute_var_endpoint(req: VaRRequest) -> VaRResponse:
    """Compute Value at Risk using all three methods plus CVaR."""
    returns = _load_returns(req.ticker, req.start_date, req.end_date)

    try:
        hist = compute_var(
            returns,
            confidence=req.confidence,
            method="historical",
            horizon_days=req.horizon_days,
            portfolio_value=req.portfolio_value,
        )
        param = compute_var(
            returns,
            confidence=req.confidence,
            method="parametric",
            horizon_days=req.horizon_days,
            portfolio_value=req.portfolio_value,
        )
        mc = compute_var(
            returns,
            confidence=req.confidence,
            method="montecarlo",
            horizon_days=req.horizon_days,
            portfolio_value=req.portfolio_value,
        )
        cvar_result = compute_cvar(returns, confidence=req.confidence, method="historical")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VaR computation failed: {e}") from e

    def _var_schema(r) -> VaRResultSchema:
        return VaRResultSchema(
            var=sanitize_value(r.var),
            confidence=sanitize_value(r.confidence),
            method=str(r.method),
            horizon_days=r.horizon_days,
            n_observations=r.n_observations,
            var_dollars=sanitize_value(r.var_dollars),
        )

    return VaRResponse(
        historical=_var_schema(hist),
        parametric=_var_schema(param),
        montecarlo=_var_schema(mc),
        cvar=CVaRResultSchema(
            cvar=sanitize_value(cvar_result.cvar),
            var=sanitize_value(cvar_result.var),
            confidence=sanitize_value(cvar_result.confidence),
            method=str(cvar_result.method),
            n_tail_obs=cvar_result.n_tail_obs,
            n_observations=cvar_result.n_observations,
        ),
    )


@router.post("/stress", response_model=StressTestResponse)
def run_stress_test_endpoint(req: StressTestRequest) -> StressTestResponse:
    """Run stress tests for specified scenarios."""
    returns = _load_returns(req.ticker, req.start_date, req.end_date)

    available = list(SCENARIOS.keys())
    for scenario_name in req.scenarios:
        if scenario_name not in SCENARIOS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown scenario: {scenario_name}. Available: {available}",
            )

    results: list[StressTestResultSchema] = []
    for scenario_name in req.scenarios:
        try:
            result = run_stress_test(returns, scenario=scenario_name, initial_value=req.initial_value)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Stress test failed for {scenario_name}: {e}") from e

        results.append(
            StressTestResultSchema(
                scenario_name=result.scenario_name,
                initial_value=sanitize_value(result.initial_value),
                trough_value=sanitize_value(result.trough_value),
                trough_return=sanitize_value(result.trough_return),
                max_drawdown_pct=sanitize_value(result.max_drawdown_pct),
                shock_duration_days=result.shock_duration_days,
                recovery_days=result.recovery_days,
                price_path=[sanitize_value(v) for v in list(result.price_path)],
            )
        )

    return StressTestResponse(results=results)


@router.post("/kelly", response_model=KellyResponse)
def compute_kelly_endpoint(req: KellyRequest) -> KellyResponse:
    """Compute Kelly criterion for a single asset."""
    returns = _load_returns(req.ticker, req.start_date, req.end_date)

    try:
        result = compute_kelly_from_returns(returns)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kelly computation failed: {e}") from e

    return KellyResponse(
        full_kelly=sanitize_value(result.full_kelly),
        half_kelly=sanitize_value(result.half_kelly),
        quarter_kelly=sanitize_value(result.quarter_kelly),
        win_rate=sanitize_value(result.win_rate),
        win_loss_ratio=sanitize_value(result.win_loss_ratio),
        expected_value=sanitize_value(result.expected_value),
        is_positive_ev=result.is_positive_ev,
        n_observations=result.n_observations,
    )


@router.post("/kelly-multi", response_model=MultiKellyResponse)
def compute_multi_kelly_endpoint(req: MultiKellyRequest) -> MultiKellyResponse:
    """Compute multi-asset Kelly weights."""
    returns_dict: dict[str, np.ndarray] = {}
    for ticker in req.tickers:
        returns_dict[ticker.upper()] = _load_returns(ticker, req.start_date, req.end_date)

    # Align lengths — use the shortest common length
    min_len = min(len(r) for r in returns_dict.values())
    returns_df = pd.DataFrame({t: r[-min_len:] for t, r in returns_dict.items()})

    try:
        result = compute_multi_asset_kelly(returns_df)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-asset Kelly computation failed: {e}") from e

    # Convert per-asset KellyResult dataclasses to KellyResponse schemas
    asset_results: dict[str, KellyResponse] = {}
    for asset, kr in result.asset_kelly_results.items():
        asset_results[asset] = KellyResponse(
            full_kelly=sanitize_value(kr.full_kelly),
            half_kelly=sanitize_value(kr.half_kelly),
            quarter_kelly=sanitize_value(kr.quarter_kelly),
            win_rate=sanitize_value(kr.win_rate),
            win_loss_ratio=sanitize_value(kr.win_loss_ratio),
            expected_value=sanitize_value(kr.expected_value),
            is_positive_ev=kr.is_positive_ev,
            n_observations=kr.n_observations,
        )

    # Sanitize correlation matrix values
    correlation_matrix: dict[str, dict[str, float]] = {}
    for outer_key, inner_dict in result.correlation_matrix.items():
        correlation_matrix[outer_key] = {k: sanitize_value(v) for k, v in inner_dict.items()}

    return MultiKellyResponse(
        weights={k: sanitize_value(v) for k, v in result.weights.items()},
        full_kelly_weights={k: sanitize_value(v) for k, v in result.full_kelly_weights.items()},
        half_kelly_weights={k: sanitize_value(v) for k, v in result.half_kelly_weights.items()},
        correlation_matrix=correlation_matrix,
        asset_results=asset_results,
        n_assets=result.n_assets,
        n_observations=result.n_observations,
    )


@router.post("/var-backtest", response_model=VaRBacktestResponse)
def run_var_backtest_endpoint(req: VaRBacktestRequest) -> VaRBacktestResponse:
    """Run a VaR model backtest (violation analysis)."""
    returns = _load_returns(req.ticker, req.start_date, req.end_date)

    try:
        result = var_backtest(returns, confidence=req.confidence, method=req.method)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VaR backtest failed: {e}") from e

    return VaRBacktestResponse(
        confidence=sanitize_value(result.confidence),
        method=str(result.method),
        n_observations=result.n_observations,
        n_violations=result.n_violations,
        violation_rate=sanitize_value(result.violation_rate),
        expected_violation_rate=sanitize_value(result.expected_violation_rate),
        is_calibrated=result.is_calibrated,
    )
