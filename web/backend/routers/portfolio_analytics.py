"""Portfolio analytics router — rolling metrics, benchmark, drawdown, correlation."""

from __future__ import annotations

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

from finbot.services.portfolio_analytics.benchmark import compute_benchmark_comparison
from finbot.services.portfolio_analytics.correlation import compute_diversification_metrics
from finbot.services.portfolio_analytics.drawdown import compute_drawdown_analysis
from finbot.services.portfolio_analytics.rolling import compute_rolling_metrics
from finbot.utils.data_collection_utils.yfinance.get_history import get_history
from web.backend.schemas.portfolio_analytics import (
    BenchmarkRequest,
    BenchmarkResponse,
    CorrelationRequest,
    CorrelationResponse,
    DrawdownPeriodSchema,
    DrawdownRequest,
    DrawdownResponse,
    RollingMetricsRequest,
    RollingMetricsResponse,
)
from web.backend.services.serializers import sanitize_value

router = APIRouter()


def _load_returns(
    ticker: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.Series:
    """Load price history and return a daily returns Series.

    Raises HTTPException(400) if price data cannot be loaded.
    """
    try:
        df = get_history(ticker.upper())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load price data for {ticker}: {e}") from e

    if df is None or df.empty:
        raise HTTPException(status_code=400, detail=f"No price data available for {ticker}")

    series = df["Close"]
    if start_date is not None:
        series = series[series.index >= pd.Timestamp(start_date)]
    if end_date is not None:
        series = series[series.index <= pd.Timestamp(end_date)]

    returns = series.pct_change().dropna()
    if returns.empty:
        raise HTTPException(status_code=400, detail=f"Insufficient return data for {ticker} after filtering")

    return returns


@router.post("/rolling", response_model=RollingMetricsResponse)
def rolling_metrics(req: RollingMetricsRequest) -> RollingMetricsResponse:
    """Compute rolling Sharpe, volatility, and optionally beta."""
    returns_series = _load_returns(req.ticker, req.start_date, req.end_date)
    returns_arr = returns_series.values

    benchmark_arr: np.ndarray | None = None
    if req.benchmark_ticker is not None:
        bench_series = _load_returns(req.benchmark_ticker, req.start_date, req.end_date)
        # Align by index intersection
        common_idx = returns_series.index.intersection(bench_series.index)
        if len(common_idx) < 30:
            raise HTTPException(status_code=400, detail="Insufficient overlapping data between ticker and benchmark")
        returns_arr = returns_series.loc[common_idx].values
        benchmark_arr = bench_series.loc[common_idx].values

    try:
        result = compute_rolling_metrics(
            returns=returns_arr,
            window=req.window,
            benchmark_returns=benchmark_arr,
            risk_free_rate=req.risk_free_rate,
            dates=[timestamp.isoformat() for timestamp in returns_series.index if benchmark_arr is None]
            if benchmark_arr is None
            else [timestamp.isoformat() for timestamp in returns_series.loc[common_idx].index],
        )
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rolling metrics computation failed: {e}") from e

    sharpe_list = [sanitize_value(v) for v in result.sharpe]
    vol_list = [sanitize_value(v) for v in result.volatility]
    beta_list = [sanitize_value(v) for v in result.beta] if result.beta is not None else None
    dates_list = list(result.dates)

    # Compute means ignoring NaN values
    sharpe_arr_np = np.array(result.sharpe, dtype=float)
    vol_arr_np = np.array(result.volatility, dtype=float)
    mean_sharpe = sanitize_value(float(np.nanmean(sharpe_arr_np)))
    mean_vol = sanitize_value(float(np.nanmean(vol_arr_np)))

    mean_beta: float | None = None
    if result.beta is not None:
        beta_arr_np = np.array(result.beta, dtype=float)
        mean_beta = sanitize_value(float(np.nanmean(beta_arr_np)))

    return RollingMetricsResponse(
        window=result.window,
        n_obs=result.n_obs,
        sharpe=sharpe_list,
        volatility=vol_list,
        beta=beta_list,
        dates=dates_list,
        mean_sharpe=mean_sharpe,
        mean_vol=mean_vol,
        mean_beta=mean_beta,
    )


@router.post("/benchmark", response_model=BenchmarkResponse)
def benchmark_comparison(req: BenchmarkRequest) -> BenchmarkResponse:
    """Compute benchmark comparison statistics (alpha, beta, R-squared, etc.)."""
    portfolio_series = _load_returns(req.portfolio_ticker, req.start_date, req.end_date)
    benchmark_series = _load_returns(req.benchmark_ticker, req.start_date, req.end_date)

    # Align by index intersection
    common_idx = portfolio_series.index.intersection(benchmark_series.index)
    if len(common_idx) < 30:
        raise HTTPException(status_code=400, detail="Insufficient overlapping data between portfolio and benchmark")

    portfolio_arr = portfolio_series.loc[common_idx].values
    benchmark_arr = benchmark_series.loc[common_idx].values

    try:
        result = compute_benchmark_comparison(
            portfolio_returns=portfolio_arr,
            benchmark_returns=benchmark_arr,
            risk_free_rate=req.risk_free_rate,
            benchmark_name=req.benchmark_ticker.upper(),
        )
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benchmark comparison failed: {e}") from e

    return BenchmarkResponse(
        alpha=sanitize_value(result.alpha),
        beta=sanitize_value(result.beta),
        r_squared=sanitize_value(result.r_squared),
        tracking_error=sanitize_value(result.tracking_error),
        information_ratio=sanitize_value(result.information_ratio),
        up_capture=sanitize_value(result.up_capture),
        down_capture=sanitize_value(result.down_capture),
        benchmark_name=result.benchmark_name,
        n_observations=result.n_observations,
    )


@router.post("/drawdown", response_model=DrawdownResponse)
def drawdown_analysis(req: DrawdownRequest) -> DrawdownResponse:
    """Compute drawdown analysis with top-N episodes and underwater curve."""
    returns_series = _load_returns(req.ticker, req.start_date, req.end_date)

    try:
        result = compute_drawdown_analysis(
            returns=returns_series.values,
            top_n=req.top_n,
        )
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drawdown analysis failed: {e}") from e

    periods = [
        DrawdownPeriodSchema(
            start_idx=p.start_idx,
            trough_idx=p.trough_idx,
            end_idx=p.end_idx,
            depth=sanitize_value(p.depth),
            duration_bars=p.duration_bars,
            recovery_bars=p.recovery_bars,
        )
        for p in result.periods
    ]

    underwater = [sanitize_value(v) for v in result.underwater_curve]

    return DrawdownResponse(
        periods=periods,
        underwater_curve=underwater,
        n_periods=result.n_periods,
        max_depth=sanitize_value(result.max_depth),
        avg_depth=sanitize_value(result.avg_depth),
        avg_duration_bars=sanitize_value(result.avg_duration_bars),
        avg_recovery_bars=sanitize_value(result.avg_recovery_bars),
        current_drawdown=sanitize_value(result.current_drawdown),
        n_observations=result.n_observations,
    )


@router.post("/correlation", response_model=CorrelationResponse)
def correlation_metrics(req: CorrelationRequest) -> CorrelationResponse:
    """Compute correlation and diversification metrics for multiple assets."""
    # Load returns for each ticker
    all_series: dict[str, pd.Series] = {}
    for ticker in req.tickers:
        all_series[ticker.upper()] = _load_returns(ticker, req.start_date, req.end_date)

    # Align all series by common index
    combined = pd.DataFrame(all_series)
    combined = combined.dropna()

    if len(combined) < 30:
        raise HTTPException(status_code=400, detail="Insufficient overlapping data across tickers")

    # Remap weights to upper-cased ticker names if provided
    weights: dict[str, float] | None = None
    if req.weights is not None:
        weights = {k.upper(): v for k, v in req.weights.items()}

    try:
        result = compute_diversification_metrics(
            returns_df=combined,
            weights=weights,
        )
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Correlation computation failed: {e}") from e

    return CorrelationResponse(
        n_assets=result.n_assets,
        weights={k: sanitize_value(v) for k, v in result.weights.items()},
        herfindahl_index=sanitize_value(result.herfindahl_index),
        effective_n=sanitize_value(result.effective_n),
        diversification_ratio=sanitize_value(result.diversification_ratio),
        avg_pairwise_correlation=sanitize_value(result.avg_pairwise_correlation),
        correlation_matrix={
            outer: {inner: sanitize_value(val) for inner, val in row.items()}
            for outer, row in result.correlation_matrix.items()
        },
        individual_vols={k: sanitize_value(v) for k, v in result.individual_vols.items()},
        portfolio_vol=sanitize_value(result.portfolio_vol),
        n_observations=result.n_observations,
    )
