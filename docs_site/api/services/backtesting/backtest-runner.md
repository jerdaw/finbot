# BacktestRunner

The `BacktestRunner` class is the low-level orchestrator behind Finbot's Backtrader-based backtesting flow. It works with explicit strategy classes, broker objects, sizers, and price-history DataFrames.

## Overview

`BacktestRunner`:

- Accepts a `price_histories` mapping of tickers to pandas DataFrames
- Truncates inputs to the shared date range and prefers adjusted close data when available
- Installs analyzers and observers before running Backtrader
- Returns a one-row metrics DataFrame from `run_backtest()`
- Exposes value history and trade data after execution

## Quick Start

```python
import backtrader as bt

from finbot.services.backtesting.backtest_runner import BacktestRunner
from finbot.services.backtesting.brokers.fixed_commission_scheme import FixedCommissionScheme
from finbot.services.backtesting.strategies.rebalance import Rebalance
from finbot.utils.data_collection_utils.yfinance.get_history import get_history

spy_data = get_history("SPY", adjust_price=True)
tlt_data = get_history("TLT", adjust_price=True)

runner = BacktestRunner(
    price_histories={"SPY": spy_data, "TLT": tlt_data},
    start=None,
    end=None,
    duration=None,
    start_step=None,
    init_cash=100000,
    strat=Rebalance,
    strat_kwargs={"rebal_proportions": [0.6, 0.4], "rebal_interval": 63},
    broker=bt.brokers.BackBroker,
    broker_kwargs={},
    broker_commission=FixedCommissionScheme,
    sizer=bt.sizers.AllInSizer,
    sizer_kwargs={},
    plot=False,
)

stats = runner.run_backtest()
print(stats[["CAGR", "Sharpe", "Max Drawdown"]])
```

## Class: BacktestRunner

**Location:** `finbot.services.backtesting.backtest_runner`

### Constructor

```python
BacktestRunner(
    price_histories: dict[str, pd.DataFrame],
    start: pd.Timestamp | None,
    end: pd.Timestamp | None,
    duration: pd.Timedelta | None,
    start_step: pd.Timedelta | None,
    init_cash: float,
    strat: Any,
    strat_kwargs: dict[str, Any],
    broker: Any,
    broker_kwargs: dict[str, Any],
    broker_commission: Any,
    sizer: Any,
    sizer_kwargs: dict[str, Any],
    plot: bool,
)
```

**Key parameters:**

- `price_histories`: mapping of symbols to OHLCV DataFrames
- `start`, `end`: optional date bounds
- `duration`, `start_step`: optional rolling-window controls for batch workflows
- `init_cash`: starting portfolio cash
- `strat`: Backtrader strategy class, not a string name
- `strat_kwargs`: keyword arguments passed into the strategy constructor
- `broker`, `broker_kwargs`, `broker_commission`: broker wiring
- `sizer`, `sizer_kwargs`: position-sizing configuration
- `plot`: whether to call Backtrader plotting after execution

### Methods

#### `run_backtest()`

Execute the backtest and return the one-row metrics DataFrame.

#### `get_value_history()`

Return the post-run `Value` and `Cash` time series as a DataFrame.

#### `get_trades()`

Return the trade list captured by the trade analyzer.

#### `get_test_stats()`

Recompute and return the metrics DataFrame from the captured value history.

## Supported Strategies

- `Rebalance`
- `NoRebalance`
- `SMACrossover`
- `SMACrossoverDouble`
- `SMACrossoverTriple`
- `MACDSingle`
- `MACDDual`
- `DipBuySMA`
- `DipBuyStdev`
- `SMARebalMix`
- `DualMomentum`
- `RiskParity`
- `RegimeAdaptive`

## Examples

### Single-Asset SMA Crossover

```python
from finbot.services.backtesting.strategies.sma_crossover import SMACrossover

spy_data = get_history("SPY", adjust_price=True)

runner = BacktestRunner(
    price_histories={"SPY": spy_data},
    start=None,
    end=None,
    duration=None,
    start_step=None,
    init_cash=100000,
    strat=SMACrossover,
    strat_kwargs={"fast_ma": 50, "slow_ma": 200},
    broker=bt.brokers.BackBroker,
    broker_kwargs={},
    broker_commission=FixedCommissionScheme,
    sizer=bt.sizers.AllInSizer,
    sizer_kwargs={},
    plot=False,
)

stats = runner.run_backtest()
print(stats[["CAGR", "Sharpe", "Max Drawdown"]])
```

### Restricting the Date Window

```python
import pandas as pd

runner = BacktestRunner(
    price_histories={"SPY": spy_data},
    start=pd.Timestamp("2015-01-01"),
    end=pd.Timestamp("2024-01-01"),
    duration=None,
    start_step=None,
    init_cash=100000,
    strat=SMACrossover,
    strat_kwargs={"fast_ma": 50, "slow_ma": 200},
    broker=bt.brokers.BackBroker,
    broker_kwargs={},
    broker_commission=FixedCommissionScheme,
    sizer=bt.sizers.AllInSizer,
    sizer_kwargs={},
    plot=False,
)
```

## See Also

- [run_backtest Function](run-backtest.md) - Thin wrapper around `BacktestRunner`
- [compute_stats Function](compute-stats.md) - Metrics generation
- [User Guide: Backtesting](../../../user-guide/backtesting.md) - Tutorial path and entry points
