# Trading Strategies

The strategies module implements 13 systematic trading strategies spanning portfolio management, timing, momentum, mean reversion, and regime-aware approaches.

## Overview

Finbot includes:

- **13 battle-tested strategies**: Rebalance, SMA crossover, MACD, dip buying, dual momentum, risk parity, and regime-adaptive allocation
- **Backtrader integration**: All strategies compatible with Backtrader framework
- **Comprehensive backtesting**: Validated across 15 years of S&P 500 data (2009-2024)
- **Performance metrics**: CAGR, Sharpe, Sortino, Calmar, max drawdown, win rate

## Strategy Categories

### Portfolio Management (Passive)

| Strategy        | Description                    | Key Parameters                        |
| --------------- | ------------------------------ | ------------------------------------- |
| **Rebalance**   | Periodic portfolio rebalancing | `rebal_proportions`, `rebal_interval` |
| **NoRebalance** | Buy and hold                   | `equity_proportions`                  |
| **RiskParity**  | Inverse-volatility weighting   | `vol_window`, `rebal_interval`        |

### Timing Strategies (Technical Indicators)

| Strategy               | Description                      | Key Parameters                 |
| ---------------------- | -------------------------------- | ------------------------------ |
| **SMACrossover**       | Single SMA crossover             | `fast_ma`, `slow_ma`           |
| **SMACrossoverDouble** | Dual SMA crossover               | `fast_ma`, `slow_ma`           |
| **SMACrossoverTriple** | Triple SMA crossover             | `fast_ma`, `med_ma`, `slow_ma` |
| **SMARebalMix**        | SMA signals + periodic rebalance | `fast_ma`, `med_ma`, `slow_ma` |

### Momentum Strategies

| Strategy         | Description                  | Key Parameters                        |
| ---------------- | ---------------------------- | ------------------------------------- |
| **MACDSingle**   | MACD crossover               | `fast_ma`, `slow_ma`, `signal_period` |
| **MACDDual**     | Dual MACD system             | `fast_ma`, `slow_ma`, `signal_period` |
| **DualMomentum** | Absolute + relative momentum | `lookback`, `rebal_interval`          |

### Mean Reversion Strategies

| Strategy        | Description           | Key Parameters                  |
| --------------- | --------------------- | ------------------------------- |
| **DipBuySMA**   | Buy dips below SMA    | `fast_ma`, `med_ma`, `slow_ma`  |
| **DipBuyStdev** | Buy dips > N std devs | `buy_quantile`, `sell_quantile` |

### Regime-Aware Strategies

| Strategy           | Description                                            | Key Parameters                                                                    |
| ------------------ | ------------------------------------------------------ | --------------------------------------------------------------------------------- |
| **RegimeAdaptive** | Shift equity/bond allocation by detected market regime | `lookback`, `rebal_interval`, `bull_threshold`, `bear_threshold`, `vol_threshold` |

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

### Regime Adaptive

Market-regime-aware allocation shifts:

::: finbot.services.backtesting.strategies.regime_adaptive
options:
show_root_heading: true
show_source: true
heading_level: 3

## Quick Start

### Running a Strategy Backtest

```python
import backtrader as bt

from finbot.services.backtesting.run_backtest import run_backtest
from finbot.services.backtesting.brokers.fixed_commission_scheme import FixedCommissionScheme
from finbot.services.backtesting.strategies.rebalance import Rebalance
import pandas as pd

# Load data
spy = pd.read_parquet('spy_prices.parquet')
tlt = pd.read_parquet('tlt_prices.parquet')

# Run rebalance strategy
stats = run_backtest(
    price_histories={'SPY': spy, 'TLT': tlt},
    start=None,
    end=None,
    duration=None,
    start_step=None,
    init_cash=100000,
    strat=Rebalance,
    strat_kwargs={'rebal_proportions': [0.6, 0.4], 'rebal_interval': 63},
    broker=bt.brokers.BackBroker,
    broker_kwargs={},
    broker_commission=FixedCommissionScheme,
    sizer=bt.sizers.AllInSizer,
    sizer_kwargs={},
    plot=False,
)

print(stats[["CAGR", "Sharpe", "Max Drawdown"]])
```

### Strategy Comparison

```python
import backtrader as bt
import pandas as pd

from finbot.services.backtesting.brokers.fixed_commission_scheme import FixedCommissionScheme
from finbot.services.backtesting.run_backtest import run_backtest
from finbot.services.backtesting.strategies.rebalance import Rebalance
from finbot.services.backtesting.strategies.no_rebalance import NoRebalance
from finbot.services.backtesting.strategies.sma_crossover import SMACrossover

spy = pd.read_parquet('spy_prices.parquet')
tlt = pd.read_parquet('tlt_prices.parquet')

strategies = [
    ('NoRebalance', {'SPY': spy}, NoRebalance, {'equity_proportions': [1.0]}),
    ('Rebalance', {'SPY': spy, 'TLT': tlt}, Rebalance, {'rebal_proportions': [0.6, 0.4], 'rebal_interval': 63}),
    ('SMACrossover', {'SPY': spy}, SMACrossover, {'fast_ma': 50, 'slow_ma': 200}),
]

for name, price_histories, strat, strat_kwargs in strategies:
    stats = run_backtest(
        price_histories=price_histories,
        start=None,
        end=None,
        duration=None,
        start_step=None,
        init_cash=100000,
        strat=strat,
        strat_kwargs=strat_kwargs,
        broker=bt.brokers.BackBroker,
        broker_kwargs={},
        broker_commission=FixedCommissionScheme,
        sizer=bt.sizers.AllInSizer,
        sizer_kwargs={},
        plot=False,
    )
    print(f"{name}: Sharpe={stats['Sharpe'].iloc[0]:.2f}, CAGR={stats['CAGR'].iloc[0]:.2%}")
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

- `fast_ma`: 50 days (default)
- `slow_ma`: 200 days (default)

**Research Results:**

- CAGR: 9.2%
- Sharpe: 0.71
- Max DD: -18.3%

### 4. MACD Single

**Concept:** Buy when MACD line crosses signal line from below, sell on cross down.

**Parameters:**

- `fast_ma`: 12 days
- `slow_ma`: 26 days
- `signal_period`: 9 days

**Research Results:**

- CAGR: 8.8%
- Sharpe: 0.69
- Max DD: -19.5%

### 5. Dual Momentum

**Concept:** Combine absolute momentum (asset vs. cash) and relative momentum (asset vs. safe asset).

**Parameters:**

- `lookback`: 252 days (12 months)
- `rebal_interval`: 21 days (default)

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

- `vol_window`: 63 days
- `rebal_interval`: 21 days

**Benefits:**

- Balances risk contribution
- Reduces concentration risk
- Diversifies across volatility regimes

**Research Results:**

- CAGR: 10.3%
- Sharpe: 0.85
- Max DD: -20.1%

### 7. Dip Buy SMA

**Concept:** Buy when the moving averages are ordered `slow > medium > fast`, signalling a local dip.

**Parameters:**

- `fast_ma`: 20 days
- `med_ma`: 50 days
- `slow_ma`: 200 days

**Research Results:**

- CAGR: 9.5%
- Sharpe: 0.73
- Max DD: -25.8%

### 8. Dip Buy Stdev

**Concept:** Buy when negative returns fall into a deep historical quantile and optionally rotate on unusually strong positive returns.

**Parameters:**

- `buy_quantile`: 0.10
- `sell_quantile`: 1.0

**Research Results:**

- CAGR: 9.1%
- Sharpe: 0.70
- Max DD: -27.3%

## Performance Comparison (2009-2024)

Ranked by Sharpe ratio:

| Strategy      | CAGR  | Sharpe | Sortino | Calmar | Max DD |
| ------------- | ----- | ------ | ------- | ------ | ------ |
| Rebalance     | 10.8% | 0.87   | 1.21    | 0.46   | -23.5% |
| Risk Parity   | 10.3% | 0.85   | 1.18    | 0.51   | -20.1% |
| Dual Momentum | 10.5% | 0.82   | 1.15    | 0.69   | -15.2% |
| No Rebalance  | 11.1% | 0.78   | 1.08    | 0.33   | -33.8% |
| Dip Buy SMA   | 9.5%  | 0.73   | 1.01    | 0.37   | -25.8% |
| SMA Crossover | 9.2%  | 0.71   | 0.98    | 0.50   | -18.3% |
| Dip Buy Stdev | 9.1%  | 0.70   | 0.96    | 0.33   | -27.3% |
| MACD Single   | 8.8%  | 0.69   | 0.95    | 0.45   | -19.5% |

**Key Findings:**

- Periodic rebalancing improved Sharpe by 12% vs. buy-and-hold
- Dual momentum achieved best drawdown control (-15.2%)
- No single strategy dominated all metrics
- Risk-adjusted returns matter more than absolute returns

## Strategy Parameters

### Optimizing Parameters

Use grid search to find optimal parameters:

```python
grid_results = []

for fast in [20, 50, 100]:
    for slow in [100, 200, 300]:
        if fast >= slow:
            continue
        stats = run_backtest(
            price_histories={'SPY': spy},
            start=None,
            end=None,
            duration=None,
            start_step=None,
            init_cash=100000,
            strat=SMACrossover,
            strat_kwargs={'fast_ma': fast, 'slow_ma': slow},
            broker=bt.brokers.BackBroker,
            broker_kwargs={},
            broker_commission=FixedCommissionScheme,
            sizer=bt.sizers.AllInSizer,
            sizer_kwargs={},
            plot=False,
        )
        grid_results.append((fast, slow, stats['Sharpe'].iloc[0]))

best = max(grid_results, key=lambda item: item[2])
print(f"Best params: fast_ma={best[0]}, slow_ma={best[1]}, Sharpe={best[2]:.2f}")
```

### Parameter Sensitivity

Common parameter ranges:

| Strategy      | Parameter      | Typical Range | Impact                                 |
| ------------- | -------------- | ------------- | -------------------------------------- |
| Rebalance     | rebal_interval | 21-63         | Higher = lower turnover, higher drift  |
| SMA Crossover | fast_ma        | 20-100        | Lower = more responsive, more whipsaws |
| SMA Crossover | slow_ma        | 100-300       | Higher = slower trend changes          |
| MACD          | fast_ma        | 8-16          | Lower = more signals                   |
| MACD          | slow_ma        | 20-32         | Higher = smoother signals              |
| Dual Momentum | lookback       | 126-378       | Higher = slower momentum detection     |
| Risk Parity   | vol_window     | 30-120        | Higher = slower volatility adaptation  |

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

See [Strategy Backtest Results](../../../research/strategy-backtesting.md) for detailed analysis.

## See Also

- [BacktestRunner](backtest-runner.md) - Main backtesting orchestrator
- [Compute Stats](compute-stats.md) - Performance metrics
- [Strategy Backtest Results](../../../research/strategy-backtesting.md) - Research documentation
- [Strategy Comparison Notebook](https://github.com/jerdaw/finbot/blob/main/notebooks/03_backtest_strategy_comparison.ipynb) - Interactive examples
