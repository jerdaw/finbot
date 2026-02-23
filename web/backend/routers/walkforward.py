"""Walk-forward analysis router."""

from __future__ import annotations

from datetime import UTC
from typing import Any

import backtrader as bt
import pandas as pd
from fastapi import APIRouter, HTTPException

from finbot.core.contracts.models import BacktestRunRequest
from finbot.core.contracts.walkforward import WalkForwardConfig
from finbot.services.backtesting.backtest_runner import BacktestRunner
from finbot.services.backtesting.brokers.commission_schemes import CommInfo_NoCommission
from finbot.services.backtesting.walkforward import run_walk_forward
from finbot.utils.data_collection_utils.yfinance.get_history import get_history
from web.backend.routers.backtesting import STRATEGIES
from web.backend.schemas.walkforward import WalkForwardRequest, WalkForwardResponse, WalkForwardWindowResult
from web.backend.services.serializers import sanitize_value

router = APIRouter()


class _BacktraderEngine:
    """Minimal BacktestEngine adapter for walk-forward analysis."""

    def run(self, request: BacktestRunRequest) -> Any:
        """Run a single backtest and return a BacktestRunResult-like object."""
        price_histories: dict[str, pd.DataFrame] = {}
        for symbol in request.symbols:
            price_histories[symbol] = get_history(symbol)

        strat_cls = STRATEGIES.get(request.strategy_name)
        if strat_cls is None:
            msg = f"Unknown strategy: {request.strategy_name}"
            raise ValueError(msg)

        runner = BacktestRunner(
            price_histories=price_histories,
            start=request.start,
            end=request.end,
            duration=None,
            start_step=None,
            init_cash=request.initial_cash,
            strat=strat_cls,
            strat_kwargs=dict(request.parameters),
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=CommInfo_NoCommission,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )
        stats_df = runner.run_backtest()
        import contextlib

        from finbot.core.contracts.models import BacktestRunMetadata, BacktestRunResult

        metrics: dict[str, float] = {}
        if stats_df is not None and not stats_df.empty:
            for col in stats_df.columns:
                val = stats_df[col].iloc[0]
                with contextlib.suppress(ValueError, TypeError):
                    metrics[col] = float(val)

        from datetime import datetime

        metadata = BacktestRunMetadata(
            run_id="wf-window",
            engine_name="backtrader",
            engine_version="1.9",
            strategy_name=request.strategy_name,
            created_at=datetime.now(tz=UTC),
            config_hash="",
            data_snapshot_id="",
        )
        return BacktestRunResult(metadata=metadata, metrics=metrics)


@router.post("/run", response_model=WalkForwardResponse)
def run_walkforward(req: WalkForwardRequest) -> WalkForwardResponse:
    """Run walk-forward analysis."""
    if req.strategy not in STRATEGIES:
        raise HTTPException(status_code=400, detail=f"Unknown strategy: {req.strategy}")

    config = WalkForwardConfig(
        train_window=req.train_window,
        test_window=req.test_window,
        step_size=req.step_size,
        anchored=req.anchored,
    )

    request = BacktestRunRequest(
        strategy_name=req.strategy,
        symbols=tuple(t.upper() for t in req.tickers),
        start=pd.Timestamp(req.start_date),
        end=pd.Timestamp(req.end_date),
        initial_cash=req.initial_cash,
        parameters=req.strategy_params,
    )

    engine = _BacktraderEngine()

    try:
        result = run_walk_forward(
            engine=engine,
            request=request,
            config=config,
            include_train=req.include_train,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Walk-forward analysis failed: {e}") from e

    windows = []
    for i, window in enumerate(result.windows):
        w_metrics = {}
        if i < len(result.test_results):
            w_metrics = {k: sanitize_value(v) for k, v in result.test_results[i].metrics.items()}
        windows.append(
            WalkForwardWindowResult(
                window_id=window.window_id,
                train_start=window.train_start.isoformat(),
                train_end=window.train_end.isoformat(),
                test_start=window.test_start.isoformat(),
                test_end=window.test_end.isoformat(),
                metrics=w_metrics,
            )
        )

    # Build summary table
    summary_table = []
    for w in windows:
        row: dict[str, Any] = {"window_id": w.window_id, "test_start": w.test_start, "test_end": w.test_end}
        row.update(w.metrics)
        summary_table.append(row)

    return WalkForwardResponse(
        config={
            "train_window": config.train_window,
            "test_window": config.test_window,
            "step_size": config.step_size,
            "anchored": config.anchored,
        },
        windows=windows,
        summary_metrics={k: sanitize_value(v) for k, v in result.summary_metrics.items()},
        summary_table=summary_table,
    )
