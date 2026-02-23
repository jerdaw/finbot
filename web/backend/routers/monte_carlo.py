"""Monte Carlo simulation router."""

from __future__ import annotations

import numpy as np
from fastapi import APIRouter, HTTPException

from finbot.services.simulation.monte_carlo.monte_carlo_simulator import monte_carlo_simulator
from finbot.utils.data_collection_utils.yfinance.get_history import get_history
from web.backend.schemas.monte_carlo import MonteCarloRequest, MonteCarloResponse, PercentileBand
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
