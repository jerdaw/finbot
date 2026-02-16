"""Walk-forward testing implementation for backtesting validation."""

from __future__ import annotations

from copy import deepcopy

import pandas as pd

from finbot.core.contracts import BacktestRunRequest
from finbot.core.contracts.interfaces import BacktestEngine
from finbot.core.contracts.walkforward import WalkForwardConfig, WalkForwardResult, WalkForwardWindow


def generate_windows(
    start: pd.Timestamp,
    end: pd.Timestamp,
    config: WalkForwardConfig,
    *,
    trading_days: pd.DatetimeIndex | None = None,
) -> list[WalkForwardWindow]:
    """Generate walk-forward windows.

    Args:
        start: Start date of entire period
        end: End date of entire period
        config: Walk-forward configuration
        trading_days: Optional pre-computed trading days index.
                     If None, generates business days.

    Returns:
        List of walk-forward windows in chronological order

    Raises:
        ValueError: If insufficient data for at least one window
    """
    # Generate trading days if not provided
    if trading_days is None:
        trading_days = pd.bdate_range(start, end)
    else:
        # Filter to requested range
        trading_days = trading_days[(trading_days >= start) & (trading_days <= end)]

    total_days = len(trading_days)
    min_required = config.train_window + config.test_window

    if total_days < min_required:
        raise ValueError(
            f"Insufficient data: need at least {min_required} days "
            f"(train={config.train_window}, test={config.test_window}), "
            f"got {total_days} days"
        )

    windows: list[WalkForwardWindow] = []
    window_id = 0

    # Calculate number of complete windows
    if config.anchored:
        # Expanding window: train_start is fixed
        anchor_start = trading_days[0]
        position = config.train_window

        while position + config.test_window <= total_days:
            train_start = anchor_start
            train_end = trading_days[position - 1]
            test_start = trading_days[position]
            test_end = trading_days[min(position + config.test_window - 1, total_days - 1)]

            windows.append(
                WalkForwardWindow(
                    window_id=window_id,
                    train_start=train_start,
                    train_end=train_end,
                    test_start=test_start,
                    test_end=test_end,
                )
            )

            window_id += 1
            position += config.step_size

            # Stop if we can't fit another full test window
            if position + config.test_window > total_days:
                break

    else:
        # Rolling window: both train and test windows move
        position = 0

        while position + config.train_window + config.test_window <= total_days:
            train_start = trading_days[position]
            train_end = trading_days[position + config.train_window - 1]
            test_start = trading_days[position + config.train_window]
            test_end = trading_days[position + config.train_window + config.test_window - 1]

            windows.append(
                WalkForwardWindow(
                    window_id=window_id,
                    train_start=train_start,
                    train_end=train_end,
                    test_start=test_start,
                    test_end=test_end,
                )
            )

            window_id += 1
            position += config.step_size

    if not windows:
        raise ValueError(
            f"Could not generate any windows with config: "
            f"train={config.train_window}, test={config.test_window}, "
            f"step={config.step_size}, total_days={total_days}"
        )

    return windows


def run_walk_forward(
    engine: BacktestEngine,
    request: BacktestRunRequest,
    config: WalkForwardConfig,
    *,
    include_train: bool = False,
) -> WalkForwardResult:
    """Run walk-forward analysis.

    Args:
        engine: Backtest engine to use
        request: Base backtest request (will be modified per window)
        config: Walk-forward configuration
        include_train: If True, also run backtests on training periods

    Returns:
        Walk-forward results with per-window metrics

    Raises:
        ValueError: If request dates don't allow walk-forward windows
    """
    # Determine date range from request
    if request.start is None or request.end is None:
        raise ValueError("Walk-forward requires explicit start and end dates in request")

    # Generate windows
    windows = generate_windows(request.start, request.end, config)

    # Run backtests for each window
    train_results: list = []
    test_results: list = []

    for window in windows:
        # Run test window (out-of-sample)
        test_request = BacktestRunRequest(
            strategy_name=request.strategy_name,
            symbols=request.symbols,
            start=window.test_start,
            end=window.test_end,
            initial_cash=request.initial_cash,
            parameters=deepcopy(request.parameters),
        )
        test_result = engine.run(test_request)
        test_results.append(test_result)

        # Optionally run train window (in-sample)
        if include_train:
            train_request = BacktestRunRequest(
                strategy_name=request.strategy_name,
                symbols=request.symbols,
                start=window.train_start,
                end=window.train_end,
                initial_cash=request.initial_cash,
                parameters=deepcopy(request.parameters),
            )
            train_result = engine.run(train_request)
            train_results.append(train_result)

    # Calculate summary metrics across all test windows
    summary_metrics = _calculate_summary_metrics(test_results)

    return WalkForwardResult(
        config=config,
        windows=tuple(windows),
        test_results=tuple(test_results),
        train_results=tuple(train_results) if include_train else (),
        summary_metrics=summary_metrics,
    )


def _calculate_summary_metrics(results: list) -> dict[str, float]:
    """Calculate aggregate metrics across multiple backtest results.

    Args:
        results: List of BacktestRunResult objects

    Returns:
        Dictionary of aggregated metrics
    """
    if not results:
        return {}

    # Extract metric names from first result
    metric_names = list(results[0].metrics.keys())

    summary: dict[str, float] = {}

    for metric_name in metric_names:
        values = [r.metrics.get(metric_name, 0.0) for r in results]

        # Calculate statistics for this metric
        summary[f"{metric_name}_mean"] = sum(values) / len(values)
        summary[f"{metric_name}_min"] = min(values)
        summary[f"{metric_name}_max"] = max(values)

        # Standard deviation
        mean = summary[f"{metric_name}_mean"]
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        summary[f"{metric_name}_std"] = variance**0.5

    # Add count
    summary["window_count"] = float(len(results))

    return summary
