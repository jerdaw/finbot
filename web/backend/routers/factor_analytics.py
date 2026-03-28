"""Factor analytics router -- Fama-French-style regression, attribution, and risk decomposition."""

from __future__ import annotations

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

from finbot.core.contracts.factor_analytics import FactorModelType
from finbot.services.factor_analytics.factor_attribution import compute_factor_attribution
from finbot.services.factor_analytics.factor_regression import compute_factor_regression, compute_rolling_r_squared
from finbot.services.factor_analytics.factor_risk import compute_factor_risk
from finbot.utils.data_collection_utils.yfinance.get_history import get_history
from web.backend.schemas.factor_analytics import (
    FactorAttributionResponse,
    FactorRegressionRequest,
    FactorRegressionResponse,
    FactorRiskResponse,
    RollingRSquaredRequest,
    RollingRSquaredResponse,
)
from web.backend.services.serializers import sanitize_value

router = APIRouter()


def _load_returns(ticker: str, start_date: str | None, end_date: str | None) -> np.ndarray:
    """Fetch price history for *ticker* and compute daily returns."""
    try:
        price_df = get_history(ticker.upper())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load price data for {ticker}: {e}") from e

    col = "Close" if "Close" in price_df.columns else "Adj Close"

    if start_date is not None:
        price_df = price_df.loc[start_date:]
    if end_date is not None:
        price_df = price_df.loc[:end_date]

    returns = price_df[col].pct_change().dropna()
    if returns.empty:
        raise HTTPException(status_code=400, detail=f"No return data available for {ticker}")

    return returns.to_numpy(dtype=float)


def _build_factor_df(factor_data: list[dict[str, float]], factor_names: list[str]) -> pd.DataFrame:
    """Convert list-of-dicts factor data into a DataFrame with *factor_names* columns."""
    df = pd.DataFrame(factor_data)
    missing = [name for name in factor_names if name not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Factor data missing columns: {missing}")
    return df[factor_names]


@router.post("/regression", response_model=FactorRegressionResponse)
def run_regression(req: FactorRegressionRequest) -> FactorRegressionResponse:
    """Run OLS factor regression on ticker returns."""
    returns = _load_returns(req.ticker, req.start_date, req.end_date)
    factor_df = _build_factor_df(req.factor_data, req.factor_names)

    # Align lengths (returns may differ from factor_data length)
    min_len = min(len(returns), len(factor_df))
    returns = returns[:min_len]
    factor_df = factor_df.iloc[:min_len]

    model_type = FactorModelType(req.model_type) if req.model_type is not None else None

    try:
        result = compute_factor_regression(returns, factor_df, model_type=model_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Factor regression failed: {e}") from e

    return FactorRegressionResponse(
        loadings={k: sanitize_value(v) for k, v in result.loadings.items()},
        alpha=sanitize_value(result.alpha),
        r_squared=sanitize_value(result.r_squared),
        adj_r_squared=sanitize_value(result.adj_r_squared),
        residual_std=sanitize_value(result.residual_std),
        t_stats={k: sanitize_value(v) for k, v in result.t_stats.items()},
        p_values={k: sanitize_value(v) for k, v in result.p_values.items()},
        factor_names=list(result.factor_names),
        model_type=result.model_type.value,
        n_observations=result.n_observations,
    )


@router.post("/attribution", response_model=FactorAttributionResponse)
def run_attribution(req: FactorRegressionRequest) -> FactorAttributionResponse:
    """Decompose portfolio return into per-factor contributions."""
    returns = _load_returns(req.ticker, req.start_date, req.end_date)
    factor_df = _build_factor_df(req.factor_data, req.factor_names)

    min_len = min(len(returns), len(factor_df))
    returns = returns[:min_len]
    factor_df = factor_df.iloc[:min_len]

    try:
        result = compute_factor_attribution(returns, factor_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Factor attribution failed: {e}") from e

    return FactorAttributionResponse(
        factor_contributions={k: sanitize_value(v) for k, v in result.factor_contributions.items()},
        alpha_contribution=sanitize_value(result.alpha_contribution),
        total_return=sanitize_value(result.total_return),
        explained_return=sanitize_value(result.explained_return),
        residual_return=sanitize_value(result.residual_return),
        factor_names=list(result.factor_names),
        n_observations=result.n_observations,
    )


@router.post("/risk-decomposition", response_model=FactorRiskResponse)
def run_risk_decomposition(req: FactorRegressionRequest) -> FactorRiskResponse:
    """Decompose portfolio variance into systematic and idiosyncratic components."""
    returns = _load_returns(req.ticker, req.start_date, req.end_date)
    factor_df = _build_factor_df(req.factor_data, req.factor_names)

    min_len = min(len(returns), len(factor_df))
    returns = returns[:min_len]
    factor_df = factor_df.iloc[:min_len]

    try:
        result = compute_factor_risk(returns, factor_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Factor risk decomposition failed: {e}") from e

    return FactorRiskResponse(
        systematic_variance=sanitize_value(result.systematic_variance),
        idiosyncratic_variance=sanitize_value(result.idiosyncratic_variance),
        total_variance=sanitize_value(result.total_variance),
        pct_systematic=sanitize_value(result.pct_systematic),
        marginal_contributions={k: sanitize_value(v) for k, v in result.marginal_contributions.items()},
        factor_names=list(result.factor_names),
        n_observations=result.n_observations,
    )


@router.post("/rolling-r-squared", response_model=RollingRSquaredResponse)
def run_rolling_r_squared(req: RollingRSquaredRequest) -> RollingRSquaredResponse:
    """Compute rolling-window R-squared for factor model fit over time."""
    returns = _load_returns(req.ticker, req.start_date, req.end_date)
    factor_df = _build_factor_df(req.factor_data, req.factor_names)

    min_len = min(len(returns), len(factor_df))
    returns = returns[:min_len]
    factor_df = factor_df.iloc[:min_len]

    try:
        values, dates = compute_rolling_r_squared(returns, factor_df, window=req.window)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rolling R-squared computation failed: {e}") from e

    return RollingRSquaredResponse(
        values=[sanitize_value(v) for v in values],
        dates=list(dates),
    )
