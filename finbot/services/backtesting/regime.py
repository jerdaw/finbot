"""Market regime detection and analysis for backtesting."""

from __future__ import annotations

from typing import cast

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

            ts = cast(pd.Timestamp, date)

            if regime != current_regime:
                # Save previous period if exists
                if current_regime is not None and period_start is not None:
                    periods.append(
                        RegimePeriod(
                            regime=current_regime,
                            start=period_start,
                            end=ts - pd.Timedelta(days=1),  # Previous day
                            market_return=sum(period_returns) / len(period_returns) if period_returns else 0.0,
                            market_volatility=sum(period_vols) / len(period_vols) if period_vols else 0.0,
                        )
                    )

                # Start new period
                current_regime = regime
                period_start = ts
                period_returns = [rolling_returns.loc[ts]]
                period_vols = [rolling_vol.loc[ts]]
            else:
                # Continue current period
                period_returns.append(rolling_returns.loc[ts])
                period_vols.append(rolling_vol.loc[ts])

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
    *,
    equity_curve: pd.Series | None = None,
) -> dict[MarketRegime, RegimeMetrics]:
    """Segment backtest results by market regime.

    When *equity_curve* is provided (a ``pd.Series`` with a
    ``DatetimeIndex`` mapping dates to portfolio value), per-regime
    performance metrics (CAGR, volatility, Sharpe) are computed by
    slicing the curve to each regime period.

    Without *equity_curve* the function returns metadata-only metrics
    (period counts and day totals), preserving backward compatibility.

    Args:
        result: Backtest result to segment.
        market_data: Market data used for regime detection (must contain
            a ``Close`` or ``Adj Close`` column with a ``DatetimeIndex``).
        detector: Regime detector implementation.  Defaults to
            ``SimpleRegimeDetector``.
        config: Regime detection configuration.  Uses defaults if None.
        equity_curve: Optional portfolio value time series.  When supplied,
            per-regime annualised return, volatility, and Sharpe ratio are
            computed and included in ``RegimeMetrics.metrics``.

    Returns:
        Dictionary mapping each ``MarketRegime`` to its ``RegimeMetrics``.

    Raises:
        ValueError: If inputs are invalid.
    """
    if detector is None:
        detector = SimpleRegimeDetector()

    # Detect regimes from market data
    periods = detector.detect(market_data, config)

    # Accumulate period counts and days per regime
    regime_stats: dict[MarketRegime, dict] = {
        MarketRegime.BULL: {"count": 0, "days": 0},
        MarketRegime.BEAR: {"count": 0, "days": 0},
        MarketRegime.SIDEWAYS: {"count": 0, "days": 0},
        MarketRegime.VOLATILE: {"count": 0, "days": 0},
    }

    for period in periods:
        regime_stats[period.regime]["count"] += 1
        days = int((period.end - period.start).days) + 1
        regime_stats[period.regime]["days"] += days

    # Accumulate equity-curve slices per regime (when curve is available)
    regime_returns: dict[MarketRegime, list[float]] = {r: [] for r in MarketRegime}

    if equity_curve is not None and not equity_curve.empty:
        curve = equity_curve.sort_index()
        for period in periods:
            # Slice to this period's date range (inclusive)
            mask = (curve.index >= period.start) & (curve.index <= period.end)
            slice_ = curve[mask]
            if len(slice_) < 2:
                continue
            daily_rets = slice_.pct_change().dropna().tolist()
            regime_returns[period.regime].extend(daily_rets)

    # Build RegimeMetrics for each regime
    regime_metrics: dict[MarketRegime, RegimeMetrics] = {}

    for regime in MarketRegime:
        stats = regime_stats[regime]
        computed: dict[str, float] = {}

        rets = regime_returns[regime]
        if rets:
            import math

            mean_daily = sum(rets) / len(rets)
            ann_return = mean_daily * 252
            variance = sum((r - mean_daily) ** 2 for r in rets) / max(len(rets) - 1, 1)
            ann_vol = math.sqrt(variance) * math.sqrt(252)
            sharpe = ann_return / ann_vol if ann_vol > 0 else 0.0
            _prod = cast(float, pd.Series(rets).add(1).prod())
            total_return = (_prod - 1) if rets else 0.0
            computed = {
                "cagr": ann_return,
                "volatility": ann_vol,
                "sharpe": sharpe,
                "total_return": total_return,
                "days": float(stats["days"]),
            }

        regime_metrics[regime] = RegimeMetrics(
            regime=regime,
            count_periods=stats["count"],
            total_days=stats["days"],
            metrics=computed,
        )

    return regime_metrics
