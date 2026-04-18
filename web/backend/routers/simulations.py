"""Simulations router — wraps fund and bond ladder simulation services."""

from __future__ import annotations

from typing import Annotated

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from finbot.services.simulation.bond_ladder.bond_ladder_simulator import bond_ladder_simulator
from finbot.services.simulation.sim_specific_funds import FUND_CONFIGS, simulate_fund
from finbot.utils.data_collection_utils.yfinance.get_history import get_history
from web.backend.schemas.simulations import (
    BondLadderMetric,
    BondLadderRequest,
    BondLadderResponse,
    FundInfo,
    SimulationResponse,
    TimeSeries,
)
from web.backend.services.serializers import sanitize_value, series_to_timeseries

router = APIRouter()

DEFAULT_BOND_LADDER_NAMES = {
    "SHY": "1-3 Year Treasury",
    "IEF": "7-10 Year Treasury",
    "TLT": "20+ Year Treasury",
}


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


def _filter_history(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    return df[(df.index >= start) & (df.index <= end)].copy()


def _normalize_series(series: pd.Series) -> pd.Series:
    if series.empty:
        return series
    start_value = float(series.iloc[0])
    if start_value == 0:
        return series
    return series / start_value * 100.0


def _compute_metric_row(ticker: str, name: str, series: pd.Series) -> BondLadderMetric:
    clean = series.dropna().astype(float)
    if clean.empty:
        return BondLadderMetric(ticker=ticker, name=name)

    returns = clean.pct_change().dropna()
    total_return = float(clean.iloc[-1] / clean.iloc[0] - 1.0) if float(clean.iloc[0]) != 0 else None
    n_years = len(clean) / 252.0
    cagr = (
        ((float(clean.iloc[-1]) / float(clean.iloc[0])) ** (1 / n_years) - 1.0)
        if n_years > 0 and float(clean.iloc[0]) != 0
        else None
    )
    volatility = float(returns.std(ddof=1) * np.sqrt(252)) if len(returns) >= 2 else None
    peak = clean.cummax()
    drawdown = (clean - peak) / peak
    max_drawdown = float(drawdown.min()) if not drawdown.empty else None

    return BondLadderMetric(
        ticker=ticker,
        name=name,
        start_value=sanitize_value(float(clean.iloc[0])),
        end_value=sanitize_value(float(clean.iloc[-1])),
        total_return=sanitize_value(total_return),
        cagr=sanitize_value(cagr),
        volatility=sanitize_value(volatility),
        max_drawdown=sanitize_value(max_drawdown),
    )


@router.post("/bond-ladder/run", response_model=BondLadderResponse)
def run_bond_ladder(req: BondLadderRequest) -> BondLadderResponse:
    """Run the bond ladder research surface with optional ETF comparisons."""
    if req.max_maturity_years <= req.min_maturity_years:
        raise HTTPException(status_code=400, detail="max_maturity_years must be greater than min_maturity_years")

    try:
        ladder_df = bond_ladder_simulator(
            min_maturity_years=req.min_maturity_years,
            max_maturity_years=req.max_maturity_years,
            save_db=False,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Bond ladder simulation failed: {exc}") from exc

    ladder_close = ladder_df["Close"].dropna().astype(float)
    if ladder_close.empty:
        raise HTTPException(status_code=500, detail="Bond ladder simulation returned no usable data")

    start = pd.Timestamp(ladder_close.index.min())
    end = pd.Timestamp(ladder_close.index.max())

    base_series = _normalize_series(ladder_close) if req.normalize else ladder_close
    ladder_label = f"{req.min_maturity_years}Y-{req.max_maturity_years}Y Ladder"
    series_list = [series_to_timeseries(base_series, name=ladder_label)]
    metrics = [_compute_metric_row("BOND_LADDER", ladder_label, base_series)]

    cleaned_compare = [ticker.strip().upper() for ticker in req.compare_tickers if ticker.strip()]
    for ticker in dict.fromkeys(cleaned_compare):
        try:
            price_df = get_history(ticker)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Failed to load comparison ticker {ticker}: {exc}") from exc

        compare_df = _filter_history(price_df, start, end)
        if compare_df.empty:
            continue

        column = "Adj Close" if "Adj Close" in compare_df.columns else "Close"
        compare_series = compare_df[column].dropna().astype(float)
        if compare_series.empty:
            continue
        compare_series = _normalize_series(compare_series) if req.normalize else compare_series

        series_list.append(series_to_timeseries(compare_series, name=ticker))
        metrics.append(
            _compute_metric_row(
                ticker,
                DEFAULT_BOND_LADDER_NAMES.get(ticker, ticker),
                compare_series,
            )
        )

    return BondLadderResponse(series=series_list, metrics=metrics)
