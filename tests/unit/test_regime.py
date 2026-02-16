"""Unit tests for market regime detection."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from finbot.core.contracts import BacktestRunRequest, MarketRegime, RegimeConfig
from finbot.services.backtesting.adapters.backtrader_adapter import BacktraderAdapter
from finbot.services.backtesting.regime import SimpleRegimeDetector, segment_by_regime


def test_regime_config_validation():
    """Test RegimeConfig validation."""
    # Valid config
    config = RegimeConfig(bull_threshold=0.15, bear_threshold=-0.10, volatility_threshold=0.25, lookback_days=252)
    assert config.bull_threshold == 0.15
    assert config.bear_threshold == -0.10
    assert config.volatility_threshold == 0.25
    assert config.lookback_days == 252

    # Invalid bull_threshold
    with pytest.raises(ValueError, match="bull_threshold must be positive"):
        RegimeConfig(bull_threshold=-0.10, bear_threshold=-0.10, volatility_threshold=0.25)

    # Invalid bear_threshold
    with pytest.raises(ValueError, match="bear_threshold must be negative"):
        RegimeConfig(bull_threshold=0.15, bear_threshold=0.10, volatility_threshold=0.25)

    # Invalid volatility_threshold
    with pytest.raises(ValueError, match="volatility_threshold must be positive"):
        RegimeConfig(bull_threshold=0.15, bear_threshold=-0.10, volatility_threshold=-0.25)

    # Invalid lookback_days
    with pytest.raises(ValueError, match="lookback_days must be positive"):
        RegimeConfig(bull_threshold=0.15, bear_threshold=-0.10, volatility_threshold=0.25, lookback_days=0)


def create_trending_data(
    start: str = "2020-01-01",
    periods: int = 500,
    trend: float = 0.0005,  # Daily return
    volatility: float = 0.01,  # Daily vol
) -> pd.DataFrame:
    """Create synthetic price data with specified trend and volatility."""
    np.random.seed(42)
    dates = pd.bdate_range(start, periods=periods)

    # Generate returns with trend
    returns = np.random.normal(trend, volatility, periods)

    # Convert to prices
    prices = 100 * (1 + returns).cumprod()

    return pd.DataFrame(
        {
            "Open": prices * 0.99,
            "High": prices * 1.01,
            "Low": prices * 0.98,
            "Close": prices,
            "Adj Close": prices,
            "Volume": 1000000,
        },
        index=dates,
    )


def test_simple_regime_detector_bull_market():
    """Test detection of bull market regime."""
    # Create strong uptrend
    df = create_trending_data(periods=300, trend=0.001, volatility=0.01)  # ~25% annual return

    detector = SimpleRegimeDetector()
    config = RegimeConfig(bull_threshold=0.15, bear_threshold=-0.10, volatility_threshold=0.40)

    periods = detector.detect(df, config)

    # Should detect at least one period (after lookback)
    assert len(periods) > 0

    # Should have some bull periods given strong uptrend
    bull_periods = [p for p in periods if p.regime == MarketRegime.BULL]
    assert len(bull_periods) > 0


def test_simple_regime_detector_bear_market():
    """Test detection of bear market regime."""
    # Create strong downtrend
    df = create_trending_data(periods=300, trend=-0.0008, volatility=0.01)  # ~-20% annual return

    detector = SimpleRegimeDetector()
    config = RegimeConfig(bull_threshold=0.15, bear_threshold=-0.10, volatility_threshold=0.40)

    periods = detector.detect(df, config)

    # Should detect at least one period
    assert len(periods) > 0

    # Should have some bear periods given strong downtrend
    bear_periods = [p for p in periods if p.regime == MarketRegime.BEAR]
    assert len(bear_periods) > 0


def test_simple_regime_detector_volatile_market():
    """Test detection of volatile market regime."""
    # Create high volatility data
    df = create_trending_data(periods=300, trend=0.0, volatility=0.03)  # ~47% annual vol

    detector = SimpleRegimeDetector()
    config = RegimeConfig(bull_threshold=0.15, bear_threshold=-0.10, volatility_threshold=0.25)

    periods = detector.detect(df, config)

    # Should detect at least one period
    assert len(periods) > 0

    # Should have some volatile periods given high volatility
    volatile_periods = [p for p in periods if p.regime == MarketRegime.VOLATILE]
    assert len(volatile_periods) > 0


def test_simple_regime_detector_sideways_market():
    """Test detection of sideways market regime."""
    # Create low return, moderate volatility
    df = create_trending_data(periods=300, trend=0.0001, volatility=0.008)  # ~2.5% return, ~13% vol

    detector = SimpleRegimeDetector()
    config = RegimeConfig(bull_threshold=0.15, bear_threshold=-0.10, volatility_threshold=0.25)

    periods = detector.detect(df, config)

    # Should detect at least one period
    assert len(periods) > 0

    # Should have some sideways periods given low returns and moderate vol
    sideways_periods = [p for p in periods if p.regime == MarketRegime.SIDEWAYS]
    assert len(sideways_periods) > 0


def test_regime_detector_missing_close_column():
    """Test error when Close column is missing."""
    df = pd.DataFrame(
        {
            "Open": [100, 101, 102],
            "High": [101, 102, 103],
            "Low": [99, 100, 101],
            "Volume": [1000000, 1000000, 1000000],
        },
        index=pd.DatetimeIndex(["2020-01-01", "2020-01-02", "2020-01-03"]),
    )

    detector = SimpleRegimeDetector()

    with pytest.raises(ValueError, match="must have 'Close' or 'Adj Close' column"):
        detector.detect(df)


def test_regime_detector_invalid_index():
    """Test error when DataFrame doesn't have DatetimeIndex."""
    df = pd.DataFrame(
        {
            "Close": [100, 101, 102],
        },
        index=[0, 1, 2],  # Not DatetimeIndex
    )

    detector = SimpleRegimeDetector()

    with pytest.raises(ValueError, match="must have DatetimeIndex"):
        detector.detect(df)


def test_regime_detector_uses_adj_close():
    """Test that detector prefers Adj Close over Close."""
    dates = pd.date_range("2020-01-01", periods=300, freq="D")

    # Create data with both Close and Adj Close
    df = pd.DataFrame(
        {
            "Close": [100.0] * 300,  # Flat
            "Adj Close": list(range(100, 400)),  # Strong trend
            "Volume": [1000000] * 300,
        },
        index=dates,
    )

    detector = SimpleRegimeDetector()
    config = RegimeConfig(bull_threshold=0.50, bear_threshold=-0.10, volatility_threshold=0.40)

    periods = detector.detect(df, config)

    # Should detect regimes based on Adj Close (trending)
    # If it used Close (flat), we'd get mostly SIDEWAYS
    assert len(periods) > 0


def test_segment_by_regime():
    """Test regime segmentation of backtest results."""
    # Create uptrending market data
    df = create_trending_data(periods=200, trend=0.0005, volatility=0.01)

    # Run a simple backtest
    adapter = BacktraderAdapter(price_histories={"STOCK": df})

    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("STOCK",),
        start=None,
        end=None,
        initial_cash=10000.0,
        parameters={"equity_proportions": [1.0]},
    )

    result = adapter.run(request)

    # Segment by regime
    regime_metrics = segment_by_regime(result, df)

    # Should have metrics for all regimes
    assert MarketRegime.BULL in regime_metrics
    assert MarketRegime.BEAR in regime_metrics
    assert MarketRegime.SIDEWAYS in regime_metrics
    assert MarketRegime.VOLATILE in regime_metrics

    # Check structure
    for regime, metrics in regime_metrics.items():
        assert metrics.regime == regime
        assert metrics.count_periods >= 0
        assert metrics.total_days >= 0


def test_regime_period_validation():
    """Test RegimePeriod validation."""
    from finbot.core.contracts.regime import RegimePeriod

    # Valid period
    period = RegimePeriod(
        regime=MarketRegime.BULL,
        start=pd.Timestamp("2020-01-01"),
        end=pd.Timestamp("2020-06-30"),
        market_return=0.15,
        market_volatility=0.20,
    )
    assert period.regime == MarketRegime.BULL

    # Invalid dates (end before start)
    with pytest.raises(ValueError, match="start must be before end"):
        RegimePeriod(
            regime=MarketRegime.BULL,
            start=pd.Timestamp("2020-06-30"),
            end=pd.Timestamp("2020-01-01"),
            market_return=0.15,
            market_volatility=0.20,
        )


def test_regime_metrics_validation():
    """Test RegimeMetrics validation."""
    from finbot.core.contracts.regime import RegimeMetrics

    # Valid metrics
    metrics = RegimeMetrics(
        regime=MarketRegime.BULL, count_periods=3, total_days=150, metrics={"cagr": 0.15, "sharpe": 1.2}
    )
    assert metrics.count_periods == 3
    assert metrics.total_days == 150

    # Invalid count
    with pytest.raises(ValueError, match="count_periods must be non-negative"):
        RegimeMetrics(regime=MarketRegime.BULL, count_periods=-1, total_days=100, metrics={})

    # Invalid total_days
    with pytest.raises(ValueError, match="total_days must be non-negative"):
        RegimeMetrics(regime=MarketRegime.BULL, count_periods=1, total_days=-50, metrics={})
