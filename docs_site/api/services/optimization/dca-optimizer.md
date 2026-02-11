# DCA Optimizer

The DCA (Dollar Cost Averaging) optimizer performs grid search across asset allocation ratios, DCA durations, and purchase intervals to find optimal portfolio strategies.

## Overview

The optimizer:

- Tests combinations of allocation ratios, DCA durations, and purchase intervals
- Calculates CAGR, Sharpe ratio, Sortino ratio, max drawdown, and std dev for each
- Uses multiprocessing for parallel evaluation (~70-80 combinations/second)
- Returns results ranked by Sharpe ratio
- Supports 2-asset portfolios (extensible to N assets)

## Quick Start

```python
from finbot.services.optimization.dca_optimizer import dca_optimizer
import pandas as pd

# Load price data
spy = pd.read_parquet('spy_prices.parquet')['Close']
tlt = pd.read_parquet('tlt_prices.parquet')['Close']

# Merge on common dates
combined = pd.DataFrame({'SPY': spy, 'TLT': tlt}).dropna()

# Run optimizer
results = dca_optimizer(
    price_history=combined,
    ratio_linspace=(0.50, 0.95, 10),  # Test 50% to 95% in SPY (10 values)
    dca_duration_days=365 * 5,  # 5-year DCA period
    dca_step_days=30,  # Monthly purchases
    trial_duration_days=365 * 10,  # 10-year trial period
    starting_cash=100000
)

# View top results
print(results.head())
print(f"Optimal allocation: {results.iloc[0]['ratio']:.0%} SPY / {1-results.iloc[0]['ratio']:.0%} TLT")
print(f"Optimal Sharpe: {results.iloc[0]['sharpe']:.2f}")
```

## API Reference

::: finbot.services.optimization.dca_optimizer.dca_optimizer
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Parameters Explained

### ratio_linspace
Defines the range of allocation ratios to test:
- **Format**: `(start, stop, num_points)`
- **Example**: `(0.5, 0.95, 10)` tests 50%, 55%, 60%, ..., 95% in asset 1
- **Interpretation**: `ratio` is allocation to first asset, `1-ratio` is allocation to second

### dca_duration_days
How long the DCA accumulation period lasts:
- **Short (1-2 years)**: Better for fast-moving bull markets
- **Medium (3-5 years)**: Balanced, averages out volatility
- **Long (7-10 years)**: Better for volatile markets, maximum cost averaging

### dca_step_days
Frequency of purchases during DCA period:
- **Daily (1)**: Maximum cost averaging, high transaction costs
- **Weekly (7)**: Good balance
- **Monthly (30)**: Standard DCA approach, realistic for most investors
- **Quarterly (90)**: Minimal transactions, less cost averaging benefit

### trial_duration_days
Total time horizon for evaluation (must be > dca_duration_days):
- **Should be 2-3x dca_duration_days** for meaningful results
- Includes both accumulation (DCA) and hold period
- Example: 5-year DCA + 5-year hold = 10-year trial

## Optimization Metrics

The optimizer calculates these metrics for each combination:

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| **CAGR** | Compound Annual Growth Rate | Higher is better (growth) |
| **Sharpe** | Risk-adjusted return (Rf=2%) | Higher is better (>1 good, >2 excellent) |
| **Sortino** | Downside risk-adjusted return | Higher is better (focuses on negative volatility) |
| **Max Drawdown** | Largest peak-to-trough decline | Lower is better (risk metric) |
| **Std Dev** | Annualized volatility | Lower is better (risk metric) |

Results are sorted by **Sharpe ratio** (best risk-adjusted return).

## Performance

Based on comprehensive benchmarks:

| Test Case | Combinations | Time (s) | Rate (comb/s) |
|-----------|--------------|----------|---------------|
| Simple | 500 | 7.10 | 70.4 |
| Medium | 1,000 | 13.22 | 75.6 |
| Large | 2,000 | 26.45 | 75.6 |

**Key Findings:**
- Consistent ~70-80 combinations/second across data sizes
- Multiprocessing scales well with parameter space
- Can evaluate 1,000 strategies in ~13 seconds

## Examples

### Classic 60/40 Validation

Test if 60/40 SPY/TLT is optimal:

```python
results = dca_optimizer(
    price_history=spy_tlt_combined,
    ratio_linspace=(0.4, 0.8, 9),  # Test 40% to 80% SPY
    dca_duration_days=365 * 5,
    dca_step_days=30,
    trial_duration_days=365 * 15
)

# Find 60/40 allocation
row_60_40 = results[abs(results['ratio'] - 0.6) < 0.01]
print(f"60/40 Sharpe: {row_60_40.iloc[0]['sharpe']:.2f}")
print(f"Best Sharpe: {results.iloc[0]['sharpe']:.2f}")
```

### Leveraged Portfolio Optimization

Optimize UPRO/TMF allocation:

```python
upro = get_history('UPRO')['Close']
tmf = get_history('TMF')['Close']
combined = pd.DataFrame({'UPRO': upro, 'TMF': tmf}).dropna()

results = dca_optimizer(
    price_history=combined,
    ratio_linspace=(0.3, 0.7, 9),  # Test 30% to 70% UPRO
    dca_duration_days=365 * 3,  # Shorter for leveraged
    dca_step_days=30,
    trial_duration_days=365 * 10
)

print(f"Optimal UPRO allocation: {results.iloc[0]['ratio']:.0%}")
print(f"Expected CAGR: {results.iloc[0]['cagr']:.2%}")
print(f"Expected Max DD: {results.iloc[0]['max_dd']:.2%}")
```

### DCA Duration Sensitivity

Test impact of DCA duration:

```python
durations = [365, 365*2, 365*3, 365*5, 365*7]
duration_results = []

for duration in durations:
    results = dca_optimizer(
        price_history=combined,
        ratio_linspace=(0.6, 0.6, 1),  # Fixed 60% allocation
        dca_duration_days=duration,
        dca_step_days=30,
        trial_duration_days=duration * 2
    )
    duration_results.append({
        'duration_years': duration / 365,
        'sharpe': results.iloc[0]['sharpe'],
        'cagr': results.iloc[0]['cagr']
    })

duration_df = pd.DataFrame(duration_results)
print(duration_df)
```

### Purchase Frequency Comparison

Test daily vs weekly vs monthly purchases:

```python
frequencies = [1, 7, 30, 90]  # Daily, weekly, monthly, quarterly
freq_results = []

for freq in frequencies:
    results = dca_optimizer(
        price_history=combined,
        ratio_linspace=(0.6, 0.6, 1),
        dca_duration_days=365 * 5,
        dca_step_days=freq,
        trial_duration_days=365 * 10
    )
    freq_results.append({
        'frequency': f"Every {freq} days",
        'sharpe': results.iloc[0]['sharpe'],
        'num_purchases': 365 * 5 // freq
    })

freq_df = pd.DataFrame(freq_results)
print(freq_df)
```

## Results DataFrame

The optimizer returns a pandas DataFrame with these columns:

```python
>>> results.columns
Index(['start_idx', 'ratio', 'cagr', 'sharpe', 'sortino', 'max_dd', 'std'], dtype='object')

>>> results.dtypes
start_idx      int64
ratio        float64
cagr         float64
sharpe       float64
sortino      float64
max_dd       float64
std          float64
dtype: object
```

### Column Descriptions

- **start_idx**: Starting index in price history for this trial
- **ratio**: Allocation ratio to first asset (0-1)
- **cagr**: Compound annual growth rate (decimal, e.g., 0.12 = 12%)
- **sharpe**: Sharpe ratio with 2% risk-free rate
- **sortino**: Sortino ratio (downside risk only)
- **max_dd**: Maximum drawdown (decimal, e.g., -0.20 = -20%)
- **std**: Annualized standard deviation (volatility)

## Multiprocessing

The optimizer uses `multiprocessing.Pool` to parallelize trials:

```python
# Automatically uses all available CPU cores minus 1
num_workers = multiprocessing.cpu_count() - 1

with Pool(num_workers) as pool:
    results = pool.map(_mp_helper, parameter_combinations)
```

**Benefits:**
- Linear speedup with CPU cores (4 cores ≈ 4x faster)
- Evaluates independent trials in parallel
- Automatically chunks work across processes

**Considerations:**
- Overhead for small parameter spaces (<100 combinations)
- Memory usage scales with number of workers
- Not compatible with Jupyter notebooks (use `if __name__ == '__main__'`)

## Limitations

- **Two assets only**: Current implementation supports 2-asset portfolios
- **Equal purchase amounts**: Buys equal dollar amounts at each step
- **No transaction costs**: Assumes zero trading fees
- **Historical data**: Optimizes on past data (risk of overfitting)
- **Static allocation**: Doesn't consider dynamic rebalancing during DCA
- **No dividends**: Price appreciation only

## Best Practices

1. **Use sufficient trial duration**: At least 2x DCA duration
2. **Test multiple periods**: Don't rely on single historical period
3. **Consider transaction costs**: Adjust for your broker's fees
4. **Validate on out-of-sample data**: Test on recent data not used for optimization
5. **Use Monte Carlo**: Complement with forward-looking simulations
6. **Consider taxes**: Optimize after-tax returns if relevant

## See Also

- [Research: DCA Optimization Findings](../../../../research/dca-optimization.md) - Detailed research results
- [Monte Carlo Simulator](../simulation/monte-carlo.md) - Forward-looking risk analysis
- [Rebalance Optimizer](../backtesting/rebalance-optimizer.md) - Post-accumulation rebalancing
- [Performance Benchmarks](../../../../benchmarks.md) - Optimization performance analysis
