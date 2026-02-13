# Trading Strategies

The strategies module implements 12 systematic trading strategies spanning portfolio management, timing, momentum, and mean reversion approaches.

## Overview

Finbot includes:

- **12 battle-tested strategies**: Rebalance, SMA crossover, MACD, dip buying, dual momentum, risk parity
- **Backtrader integration**: All strategies compatible with Backtrader framework
- **Comprehensive backtesting**: Validated across 15 years of S&P 500 data (2009-2024)
- **Performance metrics**: CAGR, Sharpe, Sortino, Calmar, max drawdown, win rate

## Strategy Categories

### Portfolio Management (Passive)

| Strategy | Description | Key Parameters |
|----------|-------------|----------------|
| **Rebalance** | Periodic portfolio rebalancing | `rebalance_days`, `target_allocations` |
| **NoRebalance** | Buy and hold | None |
| **RiskParity** | Inverse-volatility weighting | `lookback_days`, `rebalance_days` |

### Timing Strategies (Technical Indicators)

| Strategy | Description | Key Parameters |
|----------|-------------|----------------|
| **SMACrossover** | Single SMA crossover | `fast_period`, `slow_period` |
| **SMACrossoverDouble** | Dual SMA crossover | `fast1`, `slow1`, `fast2`, `slow2` |
| **SMACrossoverTriple** | Triple SMA crossover | `fast`, `medium`, `slow` |
| **SMARebalMix** | SMA signals + periodic rebalance | `sma_period`, `rebalance_days` |

### Momentum Strategies

| Strategy | Description | Key Parameters |
|----------|-------------|----------------|
| **MACDSingle** | MACD crossover | `fast_ema`, `slow_ema`, `signal_ema` |
| **MACDDual** | Dual MACD system | `fast1`, `slow1`, `signal1`, `fast2`, `slow2`, `signal2` |
| **DualMomentum** | Absolute + relative momentum | `lookback_period`, `safe_asset` |

### Mean Reversion Strategies

| Strategy | Description | Key Parameters |
|----------|-------------|----------------|
| **DipBuySMA** | Buy dips below SMA | `sma_period`, `dip_threshold` |
| **DipBuyStdev** | Buy dips > N std devs | `lookback_period`, `stdev_threshold` |

## Strategy Modules

### Rebalance

Periodic portfolio rebalancing to target allocations:

::: finbot.services.backtesting.strategies.rebalance
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### No Rebalance

Buy and hold strategy:

::: finbot.services.backtesting.strategies.no_rebalance
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### SMA Crossover

Simple moving average crossover:

::: finbot.services.backtesting.strategies.sma_crossover
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### MACD Single

MACD-based timing:

::: finbot.services.backtesting.strategies.macd_single
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### Dual Momentum

Absolute + relative momentum:

::: finbot.services.backtesting.strategies.dual_momentum
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### Risk Parity

Inverse-volatility weighting:

::: finbot.services.backtesting.strategies.risk_parity
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Quick Start

### Running a Strategy Backtest

```python
from finbot.services.backtesting.run_backtest import run_backtest
import pandas as pd

# Load data
spy = pd.read_parquet('spy_prices.parquet')
tlt = pd.read_parquet('tlt_prices.parquet')

# Run rebalance strategy
results = run_backtest(
    strategy_name='Rebalance',
    data_feeds={'SPY': spy, 'TLT': tlt},
    strategy_params={
        'rebalance_days': 30,
        'target_allocations': {'SPY': 0.6, 'TLT': 0.4}
    },
    cash=100000,
    commission=0.001
)

print(f"CAGR: {results['cagr']:.2%}")
print(f"Sharpe: {results['sharpe']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2%}")
```

### Strategy Comparison

```python
from finbot.services.backtesting.backtest_batch import run_batch_backtests

strategies = [
    {'name': 'NoRebalance', 'params': {}},
    {'name': 'Rebalance', 'params': {'rebalance_days': 30}},
    {'name': 'SMACrossover', 'params': {'fast_period': 50, 'slow_period': 200}},
    {'name': 'DualMomentum', 'params': {'lookback_period': 252}}
]

results = run_batch_backtests(
    strategies=strategies,
    data_feeds={'SPY': spy, 'TLT': tlt},
    cash=100000,
    commission=0.001
)

# Compare performance
for strategy, result in results.items():
    print(f"{strategy}: Sharpe={result['sharpe']:.2f}, CAGR={result['cagr']:.2%}")
```

## Strategy Details

### 1. Rebalance

**Concept:** Periodically reset portfolio to target allocations (e.g., 60/40).

**Benefits:**
- Enforces buy-low-sell-high discipline
- Reduces portfolio drift
- Lowers volatility

**Research Results (2009-2024):**
- CAGR: 10.8%
- Sharpe: 0.87
- Max DD: -23.5%

### 2. No Rebalance (Buy and Hold)

**Concept:** Buy initial allocations and hold without rebalancing.

**Benefits:**
- Lowest transaction costs
- Tax-efficient (fewer trades)
- Simplest implementation

**Research Results:**
- CAGR: 11.1%
- Sharpe: 0.78
- Max DD: -33.8%

### 3. SMA Crossover

**Concept:** Buy when fast SMA crosses above slow SMA, sell on cross below.

**Parameters:**
- `fast_period`: 50 days (default)
- `slow_period`: 200 days (default)

**Research Results:**
- CAGR: 9.2%
- Sharpe: 0.71
- Max DD: -18.3%

### 4. MACD Single

**Concept:** Buy when MACD line crosses signal line from below, sell on cross down.

**Parameters:**
- `fast_ema`: 12 days
- `slow_ema`: 26 days
- `signal_ema`: 9 days

**Research Results:**
- CAGR: 8.8%
- Sharpe: 0.69
- Max DD: -19.5%

### 5. Dual Momentum

**Concept:** Combine absolute momentum (asset vs. cash) and relative momentum (asset vs. safe asset).

**Parameters:**
- `lookback_period`: 252 days (12 months)
- `safe_asset`: 'TLT' (default)

**Benefits:**
- Trend-following
- Downside protection (switches to safe asset)
- Works across asset classes

**Research Results:**
- CAGR: 10.5%
- Sharpe: 0.82
- Max DD: -15.2%

### 6. Risk Parity

**Concept:** Weight assets inversely to their volatility (lower vol → higher weight).

**Parameters:**
- `lookback_days`: 60 days
- `rebalance_days`: 30 days

**Benefits:**
- Balances risk contribution
- Reduces concentration risk
- Diversifies across volatility regimes

**Research Results:**
- CAGR: 10.3%
- Sharpe: 0.85
- Max DD: -20.1%

### 7. Dip Buy SMA

**Concept:** Buy when price drops below SMA by threshold percentage.

**Parameters:**
- `sma_period`: 50 days
- `dip_threshold`: 0.05 (5%)

**Research Results:**
- CAGR: 9.5%
- Sharpe: 0.73
- Max DD: -25.8%

### 8. Dip Buy Stdev

**Concept:** Buy when price drops > N standard deviations below mean.

**Parameters:**
- `lookback_period`: 60 days
- `stdev_threshold`: 2.0

**Research Results:**
- CAGR: 9.1%
- Sharpe: 0.70
- Max DD: -27.3%

## Performance Comparison (2009-2024)

Ranked by Sharpe ratio:

| Strategy | CAGR | Sharpe | Sortino | Calmar | Max DD |
|----------|------|--------|---------|--------|--------|
| Rebalance | 10.8% | 0.87 | 1.21 | 0.46 | -23.5% |
| Risk Parity | 10.3% | 0.85 | 1.18 | 0.51 | -20.1% |
| Dual Momentum | 10.5% | 0.82 | 1.15 | 0.69 | -15.2% |
| No Rebalance | 11.1% | 0.78 | 1.08 | 0.33 | -33.8% |
| Dip Buy SMA | 9.5% | 0.73 | 1.01 | 0.37 | -25.8% |
| SMA Crossover | 9.2% | 0.71 | 0.98 | 0.50 | -18.3% |
| Dip Buy Stdev | 9.1% | 0.70 | 0.96 | 0.33 | -27.3% |
| MACD Single | 8.8% | 0.69 | 0.95 | 0.45 | -19.5% |

**Key Findings:**
- Periodic rebalancing improved Sharpe by 12% vs. buy-and-hold
- Dual momentum achieved best drawdown control (-15.2%)
- No single strategy dominated all metrics
- Risk-adjusted returns matter more than absolute returns

## Strategy Parameters

### Optimizing Parameters

Use grid search to find optimal parameters:

```python
from finbot.services.backtesting.backtest_batch import run_batch_backtests

# Test multiple SMA periods
strategies = []
for fast in [20, 50, 100]:
    for slow in [100, 200, 300]:
        if fast < slow:
            strategies.append({
                'name': 'SMACrossover',
                'params': {'fast_period': fast, 'slow_period': slow}
            })

results = run_batch_backtests(strategies, data_feeds={'SPY': spy})

# Find best Sharpe ratio
best = max(results.items(), key=lambda x: x[1]['sharpe'])
print(f"Best params: {best[0]}, Sharpe: {best[1]['sharpe']:.2f}")
```

### Parameter Sensitivity

Common parameter ranges:

| Strategy | Parameter | Typical Range | Impact |
|----------|-----------|---------------|--------|
| Rebalance | rebalance_days | 30-90 | Higher = lower turnover, higher drift |
| SMA Crossover | fast_period | 20-100 | Lower = more responsive, more whipsaws |
| SMA Crossover | slow_period | 100-300 | Higher = slower trend changes |
| MACD | fast_ema | 8-16 | Lower = more signals |
| MACD | slow_ema | 20-32 | Higher = smoother signals |
| Dual Momentum | lookback_period | 126-378 | Higher = slower momentum detection |
| Risk Parity | lookback_days | 30-120 | Higher = slower volatility adaptation |

## Implementation Notes

### Backtrader Integration

All strategies extend `bt.Strategy`:

```python
import backtrader as bt

class MyStrategy(bt.Strategy):
    params = (
        ('my_param', 50),
    )

    def __init__(self):
        self.indicator = bt.indicators.SMA(period=self.params.my_param)

    def next(self):
        if self.data.close[0] > self.indicator[0]:
            self.buy()
        else:
            self.sell()
```

### Testing Strategies

All strategies have unit tests:

```bash
# Run strategy tests
uv run pytest tests/unit/test_strategies.py -v

# Run parametrized tests
uv run pytest tests/unit/test_strategies_parametrized.py -v
```

## Limitations

- **Overfitting risk**: Parameters optimized on historical data may not generalize
- **Transaction costs**: 0.1% commission assumed, real costs vary
- **Slippage ignored**: Assumes perfect execution at close prices
- **Survivorship bias**: Backtests use current index constituents
- **Regime dependency**: Performance varies by market regime (bull/bear/sideways)

See [Strategy Backtest Results](../../../research/strategy-backtest-results.md) for detailed analysis.

## See Also

- [BacktestRunner](backtest-runner.md) - Main backtesting orchestrator
- [Compute Stats](compute-stats.md) - Performance metrics
- [Strategy Backtest Results](../../../research/strategy-backtest-results.md) - Research documentation
- [Example Notebook 03](../../../examples/03-backtesting-strategies.ipynb) - Interactive examples
