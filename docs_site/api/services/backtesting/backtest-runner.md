# BacktestRunner

The `BacktestRunner` class is the main orchestrator for running backtests in Finbot. It wraps Backtrader's Cerebro engine and provides a simplified interface for testing trading strategies.

## Overview

`BacktestRunner` provides:

- Strategy initialization with parameters
- Data feed management (multiple assets)
- Broker configuration (cash, commission)
- Custom analyzers for performance tracking
- Results processing and statistics computation

## Quick Start

```python
from finbot.services.backtesting.backtest_runner import BacktestRunner
import pandas as pd

# Load price data
spy_data = pd.read_parquet('spy_prices.parquet')
tlt_data = pd.read_parquet('tlt_prices.parquet')

# Create backtest runner
runner = BacktestRunner(
    strategy='Rebalance',
    data_feeds={'SPY': spy_data, 'TLT': tlt_data},
    strategy_params={'rebalance_days': 30},
    cash=100000,
    commission=0.001
)

# Run backtest
results = runner.run()

# Get statistics
stats = runner.get_stats()
print(f"CAGR: {stats['CAGR']:.2%}")
print(f"Sharpe: {stats['Sharpe']:.2f}")
print(f"Max Drawdown: {stats['Max Drawdown']:.2%}")
```

## Class: BacktestRunner

**Location:** `finbot.services.backtesting.backtest_runner`

### Constructor

```python
BacktestRunner(
    strategy: str,
    data_feeds: dict[str, pd.DataFrame],
    strategy_params: dict[str, Any] = None,
    cash: float = 100000,
    commission: float = 0.001
)
```

**Parameters:**

- `strategy` (str): Strategy name (Rebalance, SMACrossover, etc.)
- `data_feeds` (dict): Dictionary mapping tickers to DataFrames
- `strategy_params` (dict, optional): Strategy-specific parameters
- `cash` (float, optional): Starting cash amount (default: 100000)
- `commission` (float, optional): Commission rate (default: 0.001)

### Methods

#### run()

Execute the backtest and return results.

```python
results = runner.run()
```

**Returns:** Dictionary with backtest results including portfolio values, returns, and analyzer data.

#### get_stats()

Calculate performance statistics.

```python
stats = runner.get_stats()
```

**Returns:** Dictionary with performance metrics:
- CAGR: Compound annual growth rate
- Sharpe: Sharpe ratio
- Sortino: Sortino ratio
- Calmar: Calmar ratio
- Max Drawdown: Maximum drawdown percentage
- Win Rate: Percentage of winning trades
- Volatility: Annualized volatility

## Supported Strategies

- **Rebalance**: Periodic portfolio rebalancing
- **NoRebalance**: Buy and hold
- **SMACrossover**: Simple moving average crossover
- **SMACrossoverDouble**: Dual SMA crossover
- **SMACrossoverTriple**: Triple SMA crossover
- **MACDSingle**: MACD-based strategy
- **MACDDual**: Dual MACD strategy
- **DipBuySMA**: Buy dips with SMA filter
- **DipBuyStdev**: Buy dips with standard deviation filter
- **SMARebalMix**: Mixed SMA + rebalance approach

## Performance Metrics

The backtest computes the following metrics using quantstats:

| Metric | Description |
|--------|-------------|
| **CAGR** | Compound Annual Growth Rate |
| **Sharpe Ratio** | Risk-adjusted return (Rf = 2%) |
| **Sortino Ratio** | Downside risk-adjusted return |
| **Calmar Ratio** | CAGR / Max Drawdown |
| **Max Drawdown** | Largest peak-to-trough decline |
| **Win Rate** | Percentage of winning trades |
| **Kelly Criterion** | Optimal position sizing |
| **Volatility** | Annualized standard deviation |

## Examples

### Basic Rebalance Strategy

```python
runner = BacktestRunner(
    strategy='Rebalance',
    data_feeds={'SPY': spy, 'TLT': tlt},
    strategy_params={
        'rebalance_days': 30,
        'target_allocations': {'SPY': 0.6, 'TLT': 0.4}
    }
)
results = runner.run()
```

### SMA Crossover with Custom Parameters

```python
runner = BacktestRunner(
    strategy='SMACrossover',
    data_feeds={'SPY': spy},
    strategy_params={
        'fast_period': 50,
        'slow_period': 200
    },
    cash=100000,
    commission=0.001
)
results = runner.run()
```

## See Also

- [run_backtest Function](../../user-guide/api-examples.md#run-backtest) - Single backtest execution
- [compute_stats Function](../../user-guide/api-examples.md#compute-stats) - Performance metrics
- [User Guide: Backtesting](../../user-guide/quick-start.md#backtest-a-strategy) - Tutorial
