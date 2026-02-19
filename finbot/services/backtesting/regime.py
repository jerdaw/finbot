"""Market regime detection and analysis for backtesting."""

from __future__ import annotations

import numpy as np
import pandas as pd

from finbot.core.contracts import BacktestRunResult
from finbot.core.contracts.regime import MarketRegime, RegimeConfig, RegimeMetrics, RegimePeriod


class SimpleRegimeDetector:
    """Simple threshold-based regime detector using rolling returns and volatility.

    Classification logic:
    1. VOLATILE: If volatility > volatility_threshold
    2. BULL: If return > bull_threshold and not volatile
    3. BEAR: If return < bear_threshold and not volatile
    4. SIDEWAYS: Otherwise
    """

    def detect(  # noqa: C901
        self,
        market_data: pd.DataFrame,
        config: RegimeConfig | None = None,
    ) -> list[RegimePeriod]:
        """Detect market regimes using rolling statistics.

        Args:
            market_data: DataFrame with DatetimeIndex and 'Close' or 'Adj Close' column
            config: Regime detection configuration (uses defaults if None)

        Returns:
            List of regime periods in chronological order

        Raises:
            ValueError: If market_data is invalid
        """
        if config is None:
            config = RegimeConfig()

        # Validate market data
        if not isinstance(market_data.index, pd.DatetimeIndex):
            raise ValueError("market_data must have DatetimeIndex")

        # Determine which price column to use
        if "Adj Close" in market_data.columns:
            price_col = "Adj Close"
        elif "Close" in market_data.columns:
            price_col = "Close"
        else:
            raise ValueError("market_data must have 'Close' or 'Adj Close' column")

        prices = market_data[price_col].copy()

        # Calculate daily returns
        returns = prices.pct_change()

        # Calculate rolling annualized returns
        # Use simple compounding: (1 + mean_daily_return)^252 - 1
        rolling_returns = returns.rolling(window=config.lookback_days).mean() * 252

        # Calculate rolling annualized volatility
        # Volatility = std_daily * sqrt(252)
        rolling_vol = returns.rolling(window=config.lookback_days).std() * (252**0.5)

        # Classify each day
        regime_series = pd.Series(index=prices.index, dtype=object)

        for date in prices.index:
            ret = rolling_returns.loc[date]
            vol = rolling_vol.loc[date]

            # Skip if we don't have enough data yet
            if pd.isna(ret) or pd.isna(vol):
                regime_series.loc[date] = None
                continue

            # Classify regime
            if vol > config.volatility_threshold:
                regime = MarketRegime.VOLATILE
            elif ret > config.bull_threshold:
                regime = MarketRegime.BULL
            elif ret < config.bear_threshold:
                regime = MarketRegime.BEAR
            else:
                regime = MarketRegime.SIDEWAYS

            regime_series.loc[date] = regime

        # Convert series to periods
        periods: list[RegimePeriod] = []
        current_regime: MarketRegime | None = None
        period_start: pd.Timestamp | None = None
        period_returns: list[float] = []
        period_vols: list[float] = []

        for date in pd.DatetimeIndex(regime_series.index):
            regime = regime_series.loc[date]
            if regime is None:
                continue

            if regime != current_regime:
                # Save previous period if exists
                if current_regime is not None and period_start is not None:
                    periods.append(
                        RegimePeriod(
                            regime=current_regime,
                            start=period_start,
                            end=date - pd.Timedelta(days=1),  # Previous day
                            market_return=sum(period_returns) / len(period_returns) if period_returns else 0.0,
                            market_volatility=sum(period_vols) / len(period_vols) if period_vols else 0.0,
                        )
                    )

                # Start new period
                current_regime = regime
                period_start = date
                period_returns = [float(rolling_returns.loc[date])]
                period_vols = [float(rolling_vol.loc[date])]
            else:
                # Continue current period
                period_returns.append(float(rolling_returns.loc[date]))
                period_vols.append(float(rolling_vol.loc[date]))

        # Don't forget the last period
        if current_regime is not None and period_start is not None:
            periods.append(
                RegimePeriod(
                    regime=current_regime,
                    start=period_start,
                    end=prices.index[-1],
                    market_return=sum(period_returns) / len(period_returns) if period_returns else 0.0,
                    market_volatility=sum(period_vols) / len(period_vols) if period_vols else 0.0,
                )
            )

        return periods


def segment_by_regime(
    result: BacktestRunResult,
    market_data: pd.DataFrame,
    equity_curve: pd.Series | None = None,
    detector: SimpleRegimeDetector | None = None,
    config: RegimeConfig | None = None,
) -> dict[MarketRegime, RegimeMetrics]:
    """Segment backtest results by market regime.

    Note: This is a simplified implementation that assumes the backtest
    result has artifacts containing trade-level or daily data. A full
    implementation would need access to the strategy's equity curve
    or trade timestamps to properly segment performance.

    For now, we detect regimes from market data and provide regime
    statistics. Users can manually correlate with backtest periods.

    Args:
        result: Backtest result to segment
        market_data: Market data used for regime detection
        equity_curve: Optional portfolio value series indexed by datetime
        detector: Regime detector implementation (uses SimpleRegimeDetector if None)
        config: Regime configuration (uses defaults if None)

    Returns:
        Dictionary mapping each regime to its metrics

    Raises:
        ValueError: If inputs are invalid
    """
    if detector is None:
        detector = SimpleRegimeDetector()

    # Detect regimes
    periods = detector.detect(market_data, config)

    # Count periods and days per regime
    regime_stats: dict[MarketRegime, dict] = {
        MarketRegime.BULL: {"count": 0, "days": 0},
        MarketRegime.BEAR: {"count": 0, "days": 0},
        MarketRegime.SIDEWAYS: {"count": 0, "days": 0},
        MarketRegime.VOLATILE: {"count": 0, "days": 0},
    }

    for period in periods:
        regime_stats[period.regime]["count"] += 1
        days = (period.end - period.start).days + 1
        regime_stats[period.regime]["days"] += days

    returns: pd.Series | None = None
    regime_by_date: pd.Series | None = None
    if equity_curve is not None and not equity_curve.empty:
        returns = equity_curve.pct_change().dropna()
        if not returns.empty:
            regime_by_date = pd.Series(index=market_data.index, dtype=object)
            for period in periods:
                mask = (regime_by_date.index >= period.start) & (regime_by_date.index <= period.end)
                regime_by_date.loc[mask] = period.regime

    # Create RegimeMetrics for each regime.
    regime_metrics: dict[MarketRegime, RegimeMetrics] = {}

    for regime in MarketRegime:
        stats = regime_stats[regime]
        metrics: dict[str, float | int] = {}
        if returns is not None and regime_by_date is not None:
            aligned_regimes = regime_by_date.reindex(returns.index)
            regime_returns = returns[aligned_regimes == regime].astype(float)
            if not regime_returns.empty:
                values = regime_returns.to_numpy(dtype=float)
                days = len(values)
                total_return = float(np.prod(values + 1.0) - 1.0)
                std_daily = float(np.std(values, ddof=1)) if days > 1 else 0.0
                mean_daily = float(np.mean(values))
                volatility = float(std_daily * (252**0.5))
                sharpe = float((mean_daily / std_daily) * (252**0.5)) if std_daily > 0 else 0.0
                cagr = float((1 + total_return) ** (252 / days) - 1) if total_return > -1 else -1.0
                metrics = {
                    "cagr": cagr,
                    "volatility": volatility,
                    "sharpe": sharpe,
                    "total_return": total_return,
                    "days": days,
                }

        regime_metrics[regime] = RegimeMetrics(
            regime=regime,
            count_periods=stats["count"],
            total_days=stats["days"],
            metrics=metrics,
        )

    return regime_metrics
