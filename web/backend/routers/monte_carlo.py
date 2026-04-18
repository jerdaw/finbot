"""Monte Carlo simulation router."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

from finbot.services.simulation.monte_carlo.monte_carlo_simulator import monte_carlo_simulator
from finbot.services.simulation.monte_carlo.multi_asset_monte_carlo import multi_asset_monte_carlo
from finbot.utils.data_collection_utils.yfinance.get_history import get_history
from web.backend.schemas.monte_carlo import (
    MonteCarloRequest,
    MonteCarloResponse,
    MultiAssetAssetStat,
    MultiAssetMonteCarloRequest,
    MultiAssetMonteCarloResponse,
    MultiAssetWeight,
    PercentileBand,
)
from web.backend.services.serializers import sanitize_value

router = APIRouter()

MAX_SAMPLE_PATHS = 50
PERCENTILES = [5, 25, 50, 75, 95]


@router.post("/run", response_model=MonteCarloResponse)
def run_monte_carlo(req: MonteCarloRequest) -> MonteCarloResponse:
    """Run Monte Carlo simulation for a single asset."""
    try:
        price_df = get_history(req.ticker.upper())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load price data for {req.ticker}: {e}") from e

    try:
        trials_df = monte_carlo_simulator(
            equity_data=price_df,
            sim_periods=req.sim_periods,
            n_sims=req.n_sims,
            start_price=req.start_price,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monte Carlo simulation failed: {e}") from e

    trials = trials_df.values  # shape: (n_sims, sim_periods)
    periods = list(range(trials.shape[1]))

    # Compute percentile bands
    bands: list[PercentileBand] = []
    for p in PERCENTILES:
        pct_vals = np.percentile(trials, p, axis=0)
        bands.append(
            PercentileBand(
                label=f"p{p}",
                values=[sanitize_value(v) for v in pct_vals],
            )
        )

    # Select sample paths (evenly spaced across simulations)
    n_paths = min(MAX_SAMPLE_PATHS, trials.shape[0])
    indices = np.linspace(0, trials.shape[0] - 1, n_paths, dtype=int)
    sample_paths = [[sanitize_value(v) for v in trials[i]] for i in indices]

    # Final value statistics
    final_values = trials[:, -1]
    statistics = {
        "mean": sanitize_value(np.mean(final_values)),
        "median": sanitize_value(np.median(final_values)),
        "std": sanitize_value(np.std(final_values)),
        "min": sanitize_value(np.min(final_values)),
        "max": sanitize_value(np.max(final_values)),
        "p5": sanitize_value(np.percentile(final_values, 5)),
        "p25": sanitize_value(np.percentile(final_values, 25)),
        "p75": sanitize_value(np.percentile(final_values, 75)),
        "p95": sanitize_value(np.percentile(final_values, 95)),
        "prob_loss": sanitize_value(float(np.mean(final_values < trials[0, 0]))),
    }

    return MonteCarloResponse(
        periods=periods,
        bands=bands,
        sample_paths=sample_paths,
        statistics=statistics,
    )


def _extract_returns_frame(price_data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    series = {}
    for ticker, df in price_data.items():
        column = "Adj Close" if "Adj Close" in df.columns else "Close"
        series[ticker] = df[column].pct_change()
    return pd.DataFrame(series).dropna()


def _validate_multi_asset_request(req: MultiAssetMonteCarloRequest) -> tuple[list[str], dict[str, float] | None]:
    cleaned_tickers = [ticker.strip().upper() for ticker in req.tickers if ticker.strip()]
    if len(cleaned_tickers) < 2:
        raise HTTPException(status_code=400, detail="At least two tickers are required")
    if len(set(cleaned_tickers)) != len(cleaned_tickers):
        raise HTTPException(status_code=400, detail="Tickers must be unique")
    if req.weights is not None and len(req.weights) != len(cleaned_tickers):
        raise HTTPException(status_code=400, detail="weights length must match ticker count")

    if req.weights is None:
        return cleaned_tickers, None

    try:
        raw_weights = [float(value) for value in req.weights]
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="weights must contain numeric values") from exc
    if any(value < 0 for value in raw_weights):
        raise HTTPException(status_code=400, detail="weights must be non-negative")
    if sum(raw_weights) <= 0:
        raise HTTPException(status_code=400, detail="weights must sum to a positive value")

    return cleaned_tickers, dict(zip(cleaned_tickers, raw_weights, strict=True))


def _build_portfolio_bands(portfolio_trials: np.ndarray) -> list[PercentileBand]:
    portfolio_bands: list[PercentileBand] = []
    for percentile in PERCENTILES:
        values = np.percentile(portfolio_trials, percentile, axis=0)
        portfolio_bands.append(
            PercentileBand(
                label=f"p{percentile}",
                values=[sanitize_value(value) for value in values],
            )
        )
    return portfolio_bands


def _build_portfolio_statistics(portfolio_trials: np.ndarray, *, start_value: float) -> dict[str, float | None]:
    final_values = portfolio_trials[:, -1]
    return {
        "mean": sanitize_value(np.mean(final_values)),
        "median": sanitize_value(np.median(final_values)),
        "std": sanitize_value(np.std(final_values)),
        "min": sanitize_value(np.min(final_values)),
        "max": sanitize_value(np.max(final_values)),
        "p5": sanitize_value(np.percentile(final_values, 5)),
        "p25": sanitize_value(np.percentile(final_values, 25)),
        "p75": sanitize_value(np.percentile(final_values, 75)),
        "p95": sanitize_value(np.percentile(final_values, 95)),
        "prob_loss": sanitize_value(float(np.mean(final_values < start_value))),
    }


def _build_multi_asset_response(
    *,
    cleaned_tickers: list[str],
    price_data: dict[str, pd.DataFrame],
    result: dict[str, Any],
    start_value: float,
) -> MultiAssetMonteCarloResponse:
    portfolio_trials = result["portfolio_trials"].to_numpy()
    periods = list(range(portfolio_trials.shape[1]))
    n_paths = min(MAX_SAMPLE_PATHS, portfolio_trials.shape[0])
    indices = np.linspace(0, portfolio_trials.shape[0] - 1, n_paths, dtype=int)
    sample_paths = [[sanitize_value(value) for value in portfolio_trials[index]] for index in indices]

    weights = result["weights"]
    returns_df = _extract_returns_frame(price_data)
    correlation = result["correlation"]
    return MultiAssetMonteCarloResponse(
        periods=periods,
        portfolio_bands=_build_portfolio_bands(portfolio_trials),
        portfolio_sample_paths=sample_paths,
        portfolio_statistics=_build_portfolio_statistics(portfolio_trials, start_value=start_value),
        weights=[
            MultiAssetWeight(ticker=ticker, weight=sanitize_value(float(weights.loc[ticker])) or 0.0)
            for ticker in cleaned_tickers
        ],
        asset_statistics=[
            MultiAssetAssetStat(
                ticker=ticker,
                weight=sanitize_value(float(weights.loc[ticker])) or 0.0,
                annual_return=sanitize_value(float(returns_df[ticker].mean() * 252.0)),
                annual_volatility=sanitize_value(float(returns_df[ticker].std(ddof=1) * np.sqrt(252.0))),
            )
            for ticker in cleaned_tickers
        ],
        correlation_matrix={
            row: {column: sanitize_value(value) or 0.0 for column, value in correlation.loc[row].to_dict().items()}
            for row in correlation.index
        },
    )


@router.post("/multi-asset/run", response_model=MultiAssetMonteCarloResponse)
def run_multi_asset_monte_carlo(req: MultiAssetMonteCarloRequest) -> MultiAssetMonteCarloResponse:
    """Run correlated multi-asset Monte Carlo portfolio simulation."""
    cleaned_tickers, weight_map = _validate_multi_asset_request(req)

    try:
        price_data = {ticker: get_history(ticker) for ticker in cleaned_tickers}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to load price data: {exc}") from exc

    try:
        result = multi_asset_monte_carlo(
            price_data=price_data,
            sim_periods=req.sim_periods,
            n_sims=req.n_sims,
            weights=weight_map,
            start_value=req.start_value,
            show_progress=False,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Multi-asset Monte Carlo simulation failed: {exc}") from exc

    return _build_multi_asset_response(
        cleaned_tickers=cleaned_tickers,
        price_data=price_data,
        result=result,
        start_value=req.start_value,
    )
