# Walk-Forward Testing and Regime Analysis Guide

**Last Updated:** 2026-02-16
**Status:** Production Ready

This guide explains how to use walk-forward testing and regime analysis to validate strategy robustness and understand performance across different market conditions.

## Table of Contents

1. [Walk-Forward Testing](#walk-forward-testing)
2. [Regime Analysis](#regime-analysis)
3. [Examples](#examples)
4. [Best Practices](#best-practices)

---

## Walk-Forward Testing

### What is Walk-Forward Testing?

Walk-forward testing validates strategy robustness by testing on multiple out-of-sample periods:

1. **Split data** into training and testing windows
2. **(Optional) Optimize** parameters on training window
3. **Test** on out-of-sample window
4. **Roll forward** and repeat

This prevents overfitting to a single time period and provides more realistic performance expectations.

### Types of Walk-Forward

**Rolling Window:**
- Both train and test windows move forward
- Fixed window sizes
- More conservative (less training data per iteration)

**Anchored/Expanding Window:**
- Training start is fixed, end expands
- Test window moves forward
- More data for later tests
- Assumes recent data more relevant

### Configuration

```python
from finbot.core.contracts import WalkForwardConfig

# Rolling window
config_rolling = WalkForwardConfig(
    train_window=100,  # 100 trading days (~4 months)
    test_window=20,    # 20 trading days (~1 month)
    step_size=20,      # Move forward 20 days each iteration
    anchored=False,    # Rolling window
)

# Expanding window
config_anchored = WalkForwardConfig(
    train_window=100,
    test_window=20,
    step_size=20,
    anchored=True,     # Training start fixed
)
```

### Running Walk-Forward Analysis

```python
from finbot.core.contracts import BacktestRunRequest
from finbot.services.backtesting.adapters.backtrader_adapter import BacktraderAdapter
from finbot.services.backtesting.walkforward import run_walk_forward
import pandas as pd

# Load price data
prices = {...}  # Your price data dict

# Create adapter
adapter = BacktraderAdapter(price_histories=prices)

# Create base request
request = BacktestRunRequest(
    strategy_name="Rebalance",
    symbols=("SPY", "TLT"),
    start=pd.Timestamp("2020-01-01"),
    end=pd.Timestamp("2023-12-31"),
    initial_cash=10000.0,
    parameters={"rebal_proportions": [0.6, 0.4], "rebal_interval": 20},
)

# Configure walk-forward
config = WalkForwardConfig(
    train_window=100,
    test_window=20,
    step_size=20,
    anchored=False,
)

# Run analysis
result = run_walk_forward(
    engine=adapter,
    request=request,
    config=config,
    include_train=True,  # Also run backtests on training periods
)

# Access results
print(f"Total windows tested: {len(result.windows)}")
print(f"Average out-of-sample CAGR: {result.summary_metrics['cagr_mean']:.2%}")
print(f"CAGR std dev: {result.summary_metrics['cagr_std']:.2%}")
print(f"CAGR range: {result.summary_metrics['cagr_min']:.2%} to {result.summary_metrics['cagr_max']:.2%}")
```

### Understanding Results

**WalkForwardResult Structure:**
```python
@dataclass
class WalkForwardResult:
    config: WalkForwardConfig           # Configuration used
    windows: tuple[WalkForwardWindow]   # Window definitions
    test_results: tuple[BacktestRunResult]  # Out-of-sample results
    train_results: tuple[BacktestRunResult]  # In-sample results (optional)
    summary_metrics: dict[str, float]   # Aggregated statistics
```

**Summary Metrics:**
- `{metric}_mean`: Average across all windows
- `{metric}_min`: Worst-case performance
- `{metric}_max`: Best-case performance
- `{metric}_std`: Variability/consistency
- `window_count`: Number of windows tested

**Interpretation:**
- **High std dev** → Strategy inconsistent across time periods
- **Large min/max spread** → Performance highly period-dependent
- **Mean << Best** → May have been overfit to specific period
- **Consistent performance** → More likely to work going forward

---

## Regime Analysis

### What is Regime Analysis?

Regime analysis segments backtest results by market conditions to understand when a strategy works best.

### Market Regimes

```python
from finbot.core.contracts import MarketRegime

# Four regime classifications
MarketRegime.BULL      # Strong upward trend
MarketRegime.BEAR      # Downward trend
MarketRegime.SIDEWAYS  # Range-bound
MarketRegime.VOLATILE  # High volatility
```

### Detection Configuration

```python
from finbot.core.contracts import RegimeConfig

config = RegimeConfig(
    bull_threshold=0.15,         # 15% annual return
    bear_threshold=-0.10,        # -10% annual return
    volatility_threshold=0.25,   # 25% annual volatility
    lookback_days=252,           # 1 year rolling window
)
```

**Classification Logic:**
1. Calculate rolling returns and volatility (lookback window)
2. If volatility > threshold → **VOLATILE**
3. Else if return > bull_threshold → **BULL**
4. Else if return < bear_threshold → **BEAR**
5. Else → **SIDEWAYS**

### Running Regime Analysis

```python
from finbot.services.backtesting.regime import SimpleRegimeDetector, segment_by_regime

# Run backtest
adapter = BacktraderAdapter(price_histories=prices)
result = adapter.run(request)

# Detect regimes in market data (use benchmark like SPY)
detector = SimpleRegimeDetector()
config = RegimeConfig()  # Use defaults

# Segment results
regime_metrics = segment_by_regime(
    result=result,
    market_data=prices["SPY"],  # Use market benchmark
    detector=detector,
    config=config,
)

# Analyze by regime
for regime, metrics in regime_metrics.items():
    print(f"\n{regime.upper()} Regime:")
    print(f"  Periods: {metrics.count_periods}")
    print(f"  Total days: {metrics.total_days}")
    # Note: Detailed strategy metrics per regime require equity curve
    # Current implementation provides regime detection and period counts
```

### Understanding Regimes

**BULL Market:**
- Sustained positive returns
- Lower volatility
- Most strategies perform well
- Good for momentum/trend-following

**BEAR Market:**
- Negative returns
- Often higher volatility
- Tests defensive capabilities
- Important for risk management

**SIDEWAYS Market:**
- Low absolute returns
- Moderate volatility
- Mean-reversion strategies may excel
- Trend strategies struggle

**VOLATILE Market:**
- High price swings
- Regardless of direction
- Tests risk controls
- Opportunity for short-term strategies

---

## Examples

### Example 1: Basic Walk-Forward

```python
import yfinance as yf
from finbot.core.contracts import BacktestRunRequest, WalkForwardConfig
from finbot.services.backtesting.adapters.backtrader_adapter import BacktraderAdapter
from finbot.services.backtesting.walkforward import run_walk_forward

# Download data
spy = yf.download("SPY", start="2018-01-01", end="2023-12-31")

# Create adapter
adapter = BacktraderAdapter(price_histories={"SPY": spy})

# Configure walk-forward (1-year train, 1-month test, 1-month step)
config = WalkForwardConfig(
    train_window=252,  # 1 year
    test_window=21,    # 1 month
    step_size=21,      # 1 month
    anchored=False,
)

# Create request
request = BacktestRunRequest(
    strategy_name="NoRebalance",
    symbols=("SPY",),
    start=spy.index[0],
    end=spy.index[-1],
    initial_cash=10000.0,
    parameters={"equity_proportions": [1.0]},
)

# Run walk-forward
wf_result = run_walk_forward(adapter, request, config)

# Print summary
print(f"\nWalk-Forward Analysis Summary")
print(f"=" * 50)
print(f"Windows tested: {int(wf_result.summary_metrics['window_count'])}")
print(f"Average CAGR: {wf_result.summary_metrics['cagr_mean']:.2%}")
print(f"CAGR std dev: {wf_result.summary_metrics['cagr_std']:.2%}")
print(f"CAGR range: [{wf_result.summary_metrics['cagr_min']:.2%}, {wf_result.summary_metrics['cagr_max']:.2%}]")
print(f"Average Sharpe: {wf_result.summary_metrics['sharpe_mean']:.2f}")
```

### Example 2: Regime Detection

```python
from finbot.services.backtesting.regime import SimpleRegimeDetector
import yfinance as yf

# Download SPY data
spy = yf.download("SPY", start="2018-01-01", end="2023-12-31")

# Detect regimes
detector = SimpleRegimeDetector()
periods = detector.detect(spy)

# Print regime periods
print(f"\nDetected {len(periods)} regime periods:")
for i, period in enumerate(periods[:10], 1):  # First 10
    print(f"{i}. {period.regime.upper():10} | {period.start.date()} to {period.end.date()} | "
          f"Return: {period.market_return:>6.1%} | Vol: {period.market_volatility:>6.1%}")
```

### Example 3: Combined Analysis

```python
# Run walk-forward with regime awareness
import pandas as pd

# 1. Run walk-forward
wf_result = run_walk_forward(adapter, request, config)

# 2. For each window, detect regime
detector = SimpleRegimeDetector()

for i, (window, test_result) in enumerate(zip(wf_result.windows, wf_result.test_results)):
    # Get market data for this test period
    test_data = spy.loc[window.test_start:window.test_end]

    # Detect regime (will be partial/incomplete due to short window)
    # Better to pre-detect regimes on full dataset

    print(f"\nWindow {i}:")
    print(f"  Test period: {window.test_start.date()} to {window.test_end.date()}")
    print(f"  CAGR: {test_result.metrics['cagr']:.2%}")
    print(f"  Sharpe: {test_result.metrics['sharpe']:.2f}")
```

---

## Best Practices

### Walk-Forward

**1. Choose Appropriate Window Sizes**
```python
# Too small: Not enough data, noisy results
WalkForwardConfig(train_window=10, test_window=5, step_size=5)  # ❌

# Too large: Few windows, less validation
WalkForwardConfig(train_window=500, test_window=100, step_size=100)  # ⚠️

# Reasonable: Multiple windows, sufficient data
WalkForwardConfig(train_window=252, test_window=21, step_size=21)  # ✅
```

**2. Step Size Trade-offs**
- **Small step**: More windows, overlapping periods
- **Large step**: Fewer windows, independent periods
- **Recommendation**: Step size ≈ test window for independence

**3. Use Expanding Windows for Long Histories**
```python
# For 10+ years of data, expanding window makes sense
config = WalkForwardConfig(
    train_window=252,
    test_window=21,
    step_size=21,
    anchored=True,  # Use all historical data
)
```

**4. Interpret Results Carefully**
- Walk-forward is NOT prediction of future performance
- Shows consistency across different periods
- Variability is information (not noise)

### Regime Analysis

**1. Use Market Benchmark**
```python
# Detect regimes on broad market index, not individual stocks
regime_metrics = segment_by_regime(
    result=result,
    market_data=prices["SPY"],  # ✅ Market benchmark
    # NOT prices["AAPL"]  # ❌ Individual stock
)
```

**2. Customize Thresholds**
```python
# Default thresholds may not fit all markets/periods
# Adjust based on your market and timeframe
config = RegimeConfig(
    bull_threshold=0.10,   # Lower for sideways market
    bear_threshold=-0.05,   # Smaller for less volatile period
    volatility_threshold=0.30,  # Higher for stable period
)
```

**3. Understand Limitations**
- Regime detection is backward-looking
- Cannot predict future regime changes
- Thresholds are subjective
- Useful for historical analysis, not real-time trading

**4. Combine with Other Analysis**
```python
# Don't rely solely on regime analysis
# Combine with:
# - Walk-forward testing
# - Drawdown analysis
# - Transaction cost analysis
# - Monte Carlo simulation
```

---

## Limitations and Caveats

### Walk-Forward Limitations

1. **Computationally Expensive**: Runs multiple backtests
2. **No Guarantee**: Past consistency ≠ future consistency
3. **Depends on History**: Results vary by time period chosen
4. **Parameter Optimization**: Not included (requires additional implementation)

### Regime Detection Limitations

1. **Backward-Looking**: Regimes identified after-the-fact
2. **Threshold-Dependent**: Different thresholds = different regimes
3. **Simplified**: Real markets have complex, overlapping regimes
4. **Strategy Metrics**: Current implementation doesn't fully segment strategy returns by regime (requires equity curve access)

### Future Enhancements

**Walk-Forward:**
- Parameter optimization during training windows
- Multi-objective optimization (risk-adjusted)
- Combinatorial optimization strategies

**Regime Detection:**
- Machine learning-based detection
- Multiple regime dimensions (return, volatility, correlation)
- Economic cycle regimes
- Real-time regime classification

---

## Further Reading

- Pardo, R. (2008). *The Evaluation and Optimization of Trading Strategies*. Wiley.
- De Prado, M. L. (2018). *Advances in Financial Machine Learning*. Wiley.
- [Backtest Runner Documentation](../api/backtesting/backtest_runner.md)
- [BacktraderAdapter API Reference](../api/backtesting/backtrader_adapter.md)

---

## Changelog

**2026-02-16:**
- Initial documentation for walk-forward testing and regime analysis
- Examples for rolling and expanding windows
- Regime detection methodology and classification logic
- Best practices and limitations
