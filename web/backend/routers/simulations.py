"""Simulations router — wraps fund simulation services."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from finbot.services.simulation.sim_specific_funds import FUND_CONFIGS, simulate_fund
from web.backend.schemas.simulations import FundInfo, SimulationResponse, TimeSeries
from web.backend.services.serializers import sanitize_value

router = APIRouter()


@router.get("/funds", response_model=list[FundInfo])
def list_funds() -> list[FundInfo]:
    """List all available funds for simulation."""
    return [
        FundInfo(
            ticker=cfg.ticker,
            name=cfg.name,
            leverage=cfg.leverage_mult,
            annual_er_pct=cfg.annual_er_pct,
        )
        for cfg in FUND_CONFIGS.values()
    ]


@router.get("/run", response_model=SimulationResponse)
def run_simulation(
    tickers: Annotated[list[str], Query(min_length=1)],
    normalize: Annotated[bool, Query()] = False,
) -> SimulationResponse:
    """Run fund simulations for the given tickers."""
    series_list: list[TimeSeries] = []
    metrics_list: list[dict[str, object]] = []

    for ticker in tickers:
        ticker_upper = ticker.upper()
        if ticker_upper not in FUND_CONFIGS:
            raise HTTPException(status_code=400, detail=f"Unknown fund ticker: {ticker_upper}")

        try:
            df = simulate_fund(ticker_upper, save_sim=False, force_update=False)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Simulation failed for {ticker_upper}: {e}") from e

        close = df["Close"]
        if normalize and len(close) > 0:
            first_val = close.iloc[0]
            if first_val != 0:
                close = close / first_val * 100

        dates = [d.isoformat() for d in close.index]
        values = [sanitize_value(v) for v in close.values]
        series_list.append(TimeSeries(name=ticker_upper, dates=dates, values=values))

        # Compute basic metrics
        if len(df) > 1:
            total_return = (df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) if df["Close"].iloc[0] != 0 else 0
            n_years = len(df) / 252
            cagr = ((1 + total_return) ** (1 / n_years) - 1) if n_years > 0 else 0
            daily_returns = df["Close"].pct_change().dropna()
            vol = float(daily_returns.std() * (252**0.5)) if len(daily_returns) > 0 else 0
            peak = df["Close"].cummax()
            drawdown = (df["Close"] - peak) / peak
            max_dd = float(drawdown.min())
        else:
            total_return = cagr = vol = max_dd = 0.0

        cfg = FUND_CONFIGS[ticker_upper]
        metrics_list.append(
            {
                "ticker": ticker_upper,
                "name": cfg.name,
                "leverage": cfg.leverage_mult,
                "total_return": sanitize_value(total_return),
                "cagr": sanitize_value(cagr),
                "volatility": sanitize_value(vol),
                "max_drawdown": sanitize_value(max_dd),
            }
        )

    return SimulationResponse(series=series_list, metrics=metrics_list)
