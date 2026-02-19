"""DCA Optimizer router."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from finbot.services.optimization.dca_optimizer import analyze_results_helper, dca_optimizer
from finbot.utils.data_collection_utils.yfinance.get_history import get_history
from web.backend.schemas.optimizer import DCAOptimizerRequest, DCAOptimizerResponse
from web.backend.services.serializers import dataframe_to_records

router = APIRouter()


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
