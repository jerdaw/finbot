"""Market regime detection and analysis for backtesting."""

from __future__ import annotations

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

        for date, regime in regime_series.items():
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
                period_returns = [rolling_returns.loc[date]]
                period_vols = [rolling_vol.loc[date]]
            else:
                # Continue current period
                period_returns.append(rolling_returns.loc[date])
                period_vols.append(rolling_vol.loc[date])

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

    # Create RegimeMetrics for each regime
    # Note: Without trade-level data, we can't properly segment strategy metrics
    # This is a placeholder that at least provides regime period statistics
    regime_metrics: dict[MarketRegime, RegimeMetrics] = {}

    for regime in MarketRegime:
        stats = regime_stats[regime]

        # For now, return empty metrics dict
        # A full implementation would need to:
        # 1. Access strategy equity curve from result.artifacts
        # 2. Calculate returns during each regime period
        # 3. Compute metrics (CAGR, Sharpe, etc.) for those returns

        regime_metrics[regime] = RegimeMetrics(
            regime=regime,
            count_periods=stats["count"],
            total_days=stats["days"],
            metrics={},  # Would contain actual strategy metrics per regime
        )

    return regime_metrics
