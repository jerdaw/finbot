# DCA Optimizer

The DCA (Dollar Cost Averaging) optimizer sweeps front-loading ratios, DCA durations, purchase intervals, and trial windows for a single price series.

This page documents the DCA-specific optimizer. Finbot's broader optimization
surface also includes `pareto_optimizer` for multi-objective strategy sweeps
and `efficient_frontier` for long-only portfolio trade-off analysis.

## Overview

The optimizer:

- Works on one pandas `Series` of close prices
- Evaluates combinations of front-loading ratio, DCA duration, purchase interval, and trial duration
- Calculates final value, percent change, CAGR, max drawdown, standard deviation, and Sharpe ratio for each trial
- Uses multiprocessing for parallel evaluation
- Returns either aggregated summary DataFrames or the raw per-trial table

## Quick Start

```python
from finbot.services.optimization.dca_optimizer import dca_optimizer
from finbot.utils.data_collection_utils.yfinance.get_history import get_history

spy = get_history("SPY", adjust_price=True)["Close"]

ratio_df, duration_df = dca_optimizer(
    price_history=spy,
    ticker="SPY",
    starting_cash=100000,
)

print(ratio_df.head())
print(duration_df.head())
```

## API Reference

::: finbot.services.optimization.dca_optimizer.dca_optimizer
options:
show_root_heading: true
show_source: true
heading_level: 3

## Parameters Explained

### `ratio_range`

Defines how aggressively the schedule front-loads purchases:

- **Format**: tuple of scalar ratios such as `(1, 1.5, 2, 3, 5, 10)`
- `1` means even purchasing through the DCA window
- Higher values buy more at the beginning and taper toward the end

### `dca_durations`

How long the DCA accumulation period lasts, measured in trading bars:

- **Short (1-2 years)**: Better for fast-moving bull markets
- **Medium (3-5 years)**: Balanced, averages out volatility
- **Long (7-10 years)**: Better for volatile markets, maximum cost averaging

### `dca_steps`

Frequency of purchases during the DCA window:

- **Daily (1)**: Maximum cost averaging, high transaction costs
- **Weekly (7)**: Good balance
- **Monthly (30)**: Standard DCA approach, realistic for most investors
- **Quarterly (90)**: Minimal transactions, less cost averaging benefit

### `trial_durations`

Total evaluation windows, measured in trading bars:

- Each trial must be at least as long as the chosen DCA duration
- Longer windows include both accumulation and post-DCA holding periods

### `analyze_results`

Controls the return type:

- `True` (default): returns `(ratio_df, duration_df)`
- `False`: returns the raw per-trial DataFrame

## Optimization Metrics

The optimizer calculates these metrics for each combination:

| Metric           | Description                    | Interpretation                           |
| ---------------- | ------------------------------ | ---------------------------------------- |
| **CAGR**         | Compound Annual Growth Rate    | Higher is better (growth)                |
| **Sharpe**       | Risk-adjusted return (Rf=2%)   | Higher is better (>1 good, >2 excellent) |
| **Max Drawdown** | Largest peak-to-trough decline | Lower is better (risk metric)            |
| **Std Dev**      | Annualized volatility          | Lower is better (risk metric)            |

Raw results are typically sorted or filtered downstream by **Sharpe ratio**.

## Performance

Based on comprehensive benchmarks:

| Test Case | Combinations | Time (s) | Rate (comb/s) |
| --------- | ------------ | -------- | ------------- |
| Simple    | 500          | 7.10     | 70.4          |
| Medium    | 1,000        | 13.22    | 75.6          |
| Large     | 2,000        | 26.45    | 75.6          |

**Key Findings:**

- Consistent ~70-80 combinations/second across data sizes
- Multiprocessing scales well with parameter space
- Can evaluate 1,000 strategies in ~13 seconds

## Examples

### Raw Trial Table

```python
raw_results = dca_optimizer(
    price_history=spy,
    ticker="SPY",
    starting_cash=100000,
    analyze_results=False,
    save_df=False,
)

best_trial = raw_results.sort_values("Sharpe", ascending=False).iloc[0]
print(best_trial[["DCA Ratio", "DCA Duration", "DCA Step", "Sharpe", "CAGR"]])
```

### Custom Parameter Sweep

```python
raw_results = dca_optimizer(
    price_history=spy,
    ticker="SPY",
    ratio_range=(1, 1.5, 2, 3),
    dca_durations=(21, 63, 126, 252),
    dca_steps=(5, 21, 63),
    trial_durations=(252 * 3, 252 * 5),
    starting_cash=100000,
    analyze_results=False,
    save_df=False,
)

print(raw_results.head())
```

### Aggregated Ratio View

```python
ratio_df, duration_df = dca_optimizer(
    price_history=spy,
    ticker="SPY",
    starting_cash=100000,
)

print(ratio_df.sort_values("Ratio Sharpe Avg", ascending=False).head())
print(duration_df.sort_values("Duration Sharpe Avg", ascending=False).head())
```

## Results DataFrame

When `analyze_results=False`, the optimizer returns a pandas DataFrame with these columns:

```python
>>> results.columns
Index(['Trial End', 'Trial Duration', 'DCA Duration', 'DCA Ratio', 'DCA Step',
     'Final Value', 'Pct Change', 'CAGR', 'Max Drawdown', 'STDev', 'Sharpe'],
    dtype='object')
```

### Column Descriptions

- **Trial Start**: index value for the evaluation window start
- **Trial End**: evaluation window end
- **Trial Duration**: full trial length in trading bars
- **DCA Duration**: accumulation window length
- **DCA Ratio**: front-loading ratio for the purchase schedule
- **DCA Step**: spacing between purchases in trading bars
- **Final Value**: ending portfolio value
- **Pct Change**: total percent change from starting cash
- **CAGR**: compound annual growth rate
- **Max Drawdown**: maximum drawdown percentage
- **STDev**: standard deviation of the value path
- **Sharpe**: Sharpe ratio using the current risk-free-rate helper

## Multiprocessing

The optimizer parallelizes trials with `tqdm.contrib.concurrent.process_map`:

```python
from tqdm.contrib.concurrent import process_map

results = process_map(_mp_helper, params_list, chunksize=1000)
```

**Benefits:**

- Linear speedup with CPU cores (4 cores ≈ 4x faster)
- Evaluates independent trials in parallel
- Automatically chunks work across processes

**Considerations:**

- Overhead for small parameter spaces (<100 combinations)
- Memory usage scales with number of workers
- Large parameter grids can still take noticeable wall-clock time

## Limitations

- **Single series input**: Current implementation optimizes one price series at a time
- **Schedule shape only**: It optimizes DCA schedule shape, not cross-asset allocation
- **No transaction costs**: Assumes zero trading fees
- **Historical data**: Optimizes on past data (risk of overfitting)
- **No dynamic rebalancing**: This optimizer is separate from portfolio rebalancing logic

## Best Practices

1. **Use sufficient trial duration**: At least 2x DCA duration
2. **Test multiple periods**: Don't rely on single historical period
3. **Consider transaction costs**: Adjust for your broker's fees
4. **Validate on out-of-sample data**: Test on recent data not used for optimization
5. **Use Monte Carlo**: Complement with forward-looking simulations
6. **Consider taxes**: Optimize after-tax returns if relevant

## See Also

- [Research: DCA Optimization Findings](../../../research/dca-optimization.md) - Detailed research results
- [Monte Carlo Simulator](../simulation/monte-carlo.md) - Forward-looking risk analysis
- [Trading Strategies](../backtesting/strategies.md) - Related backtesting context
- `finbot.services.optimization.pareto_optimizer` - Multi-objective backtest comparison
- `finbot.services.optimization.efficient_frontier` - Historical long-only frontier sampling
- [Performance Benchmarks](https://github.com/jerdaw/finbot/blob/main/docs/benchmarks.md) - Optimization performance analysis
