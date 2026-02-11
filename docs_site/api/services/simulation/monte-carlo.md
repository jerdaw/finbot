# Monte Carlo Simulator

The Monte Carlo simulator generates probabilistic forecasts of portfolio performance using historical return distributions and random sampling.

## Overview

The Monte Carlo simulator:

- Generates thousands of possible future return paths
- Samples from historical return distributions
- Accounts for portfolio volatility and correlations
- Provides percentile analysis (5th, 25th, 50th, 75th, 95th)
- Tests withdrawal sustainability and retirement planning
- Visualizes probability distributions and confidence bands

## Quick Start

```python
from finbot.services.simulation.monte_carlo.monte_carlo_simulator import monte_carlo_simulator
import pandas as pd

# Load historical returns
spy_returns = pd.read_parquet('spy_prices.parquet')['Close'].pct_change()

# Run Monte Carlo simulation
results = monte_carlo_simulator(
    returns_series=spy_returns,
    num_trials=10000,
    num_periods=252 * 30,  # 30 years of daily returns
    starting_value=100000
)

# Analyze results
print(f"Median final value: ${results['final_values'].median():,.0f}")
print(f"5th percentile: ${results['final_values'].quantile(0.05):,.0f}")
print(f"95th percentile: ${results['final_values'].quantile(0.95):,.0f}")

# Calculate probability of doubling investment
prob_double = (results['final_values'] >= 200000).sum() / len(results['final_values'])
print(f"Probability of doubling: {prob_double:.1%}")
```

## API Reference

::: finbot.services.simulation.monte_carlo.monte_carlo_simulator.monte_carlo_simulator
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Simulation Types

### Normal Distribution

::: finbot.services.simulation.monte_carlo.sim_types.sim_type_nd
    options:
      show_root_heading: true
      show_source: true
      heading_level: 4

Assumes returns follow a normal distribution:
- Mean = historical mean return
- Std dev = historical volatility
- Fastest method, but ignores skewness and kurtosis

### Historical Bootstrap

Randomly samples actual historical returns:
- Preserves real return distribution
- Captures fat tails and skewness
- Requires sufficient historical data (>1000 observations)

## Output Structure

The simulator returns a dictionary containing:

```python
{
    'trials': np.ndarray,  # Shape: (num_trials, num_periods)
    'final_values': np.ndarray,  # Shape: (num_trials,)
    'mean_path': np.ndarray,  # Shape: (num_periods,)
    'percentiles': {
        5: np.ndarray,  # 5th percentile path
        25: np.ndarray,  # 25th percentile path
        50: np.ndarray,  # 50th percentile (median)
        75: np.ndarray,  # 75th percentile path
        95: np.ndarray  # 95th percentile path
    }
}
```

## Examples

### Retirement Planning

Test 4% withdrawal rule:

```python
# 60/40 portfolio returns
portfolio_returns = 0.6 * spy_returns + 0.4 * tlt_returns

# Run simulation with withdrawals
starting_value = 1_000_000
annual_withdrawal = 40_000  # 4% rule
years = 30

results = monte_carlo_simulator(
    returns_series=portfolio_returns,
    num_trials=10000,
    num_periods=252 * years,
    starting_value=starting_value
)

# Simulate withdrawals
withdrawal_per_day = annual_withdrawal / 252
trials_with_withdrawals = results['trials'].copy()

for i in range(trials_with_withdrawals.shape[1]):
    trials_with_withdrawals[:, i] -= withdrawal_per_day

# Calculate success rate (portfolio doesn't deplete)
final_values_with_withdrawal = trials_with_withdrawals[:, -1]
success_rate = (final_values_with_withdrawal > 0).sum() / len(final_values_with_withdrawal)

print(f"4% rule success rate: {success_rate:.1%}")
print(f"Median final value: ${np.median(final_values_with_withdrawal):,.0f}")
```

### Value at Risk (VaR)

Calculate probability of specific losses:

```python
results = monte_carlo_simulator(
    returns_series=portfolio_returns,
    num_trials=10000,
    num_periods=252 * 1,  # 1 year
    starting_value=100000
)

# Calculate VaR at different confidence levels
losses = 100000 - results['final_values']
var_95 = np.percentile(losses, 95)
var_99 = np.percentile(losses, 99)

print(f"VaR (95%): ${var_95:,.0f} maximum loss")
print(f"VaR (99%): ${var_99:,.0f} maximum loss")

# Conditional VaR (CVaR / Expected Shortfall)
cvar_95 = losses[losses >= var_95].mean()
print(f"CVaR (95%): ${cvar_95:,.0f} expected loss if VaR exceeded")
```

### Multi-Asset Portfolio

Simulate correlated assets:

```python
import numpy as np

# Calculate correlation matrix
returns_df = pd.DataFrame({
    'SPY': spy_returns,
    'TLT': tlt_returns,
    'GLD': gld_returns
})
correlation_matrix = returns_df.corr()

# Cholesky decomposition for correlated sampling
L = np.linalg.cholesky(correlation_matrix)

# Generate correlated returns
num_trials = 10000
num_periods = 252 * 10

uncorrelated_returns = np.random.normal(
    loc=returns_df.mean().values,
    scale=returns_df.std().values,
    size=(num_trials, num_periods, 3)
)

# Apply correlation
correlated_returns = uncorrelated_returns @ L.T

# Simulate portfolio (equal weight)
weights = np.array([0.33, 0.33, 0.34])
portfolio_returns = (correlated_returns * weights).sum(axis=2)

# Calculate final values
cumulative_returns = (1 + portfolio_returns).cumprod(axis=1)
final_values = 100000 * cumulative_returns[:, -1]

print(f"Median final value: ${np.median(final_values):,.0f}")
print(f"5th percentile: ${np.percentile(final_values, 5):,.0f}")
print(f"95th percentile: ${np.percentile(final_values, 95):,.0f}")
```

### Leveraged Portfolio Risk

Analyze risk of leveraged strategies:

```python
# UPRO (3x leveraged S&P 500) returns
upro_returns = spy_returns * 3  # Simplified for illustration

results_spy = monte_carlo_simulator(spy_returns, 10000, 252*10, 100000)
results_upro = monte_carlo_simulator(upro_returns, 10000, 252*10, 100000)

# Compare distributions
print("SPY Simulation:")
print(f"  Median: ${results_spy['final_values'].median():,.0f}")
print(f"  5th percentile: ${np.percentile(results_spy['final_values'], 5):,.0f}")

print("\nUPRO Simulation:")
print(f"  Median: ${results_upro['final_values'].median():,.0f}")
print(f"  5th percentile: ${np.percentile(results_upro['final_values'], 5):,.0f}")

# Calculate probability of loss
prob_loss_spy = (results_spy['final_values'] < 100000).sum() / 10000
prob_loss_upro = (results_upro['final_values'] < 100000).sum() / 10000

print(f"\nProbability of loss after 10 years:")
print(f"  SPY: {prob_loss_spy:.1%}")
print(f"  UPRO: {prob_loss_upro:.1%}")
```

## Visualization

### Plot Trials

```python
from finbot.services.simulation.monte_carlo.visualization import plot_trials

plot_trials(
    results['trials'],
    results['percentiles'],
    title="Monte Carlo Simulation: 10,000 Trials",
    xlabel="Trading Days",
    ylabel="Portfolio Value ($)"
)
```

### Plot Distribution

```python
from finbot.services.simulation.monte_carlo.visualization import plot_distribution

plot_distribution(
    results['final_values'],
    title="Final Value Distribution After 30 Years",
    xlabel="Final Portfolio Value ($)",
    initial_value=100000
)
```

## Key Assumptions

### What Monte Carlo Captures

- Historical return distribution (mean, volatility)
- Random variation and uncertainty
- Compound return effects
- Path-dependent outcomes

### What Monte Carlo Doesn't Capture

- **Regime changes**: Market conditions may differ from historical
- **Structural breaks**: Economic crises not in historical data
- **Fat tails**: May underestimate extreme events
- **Time-varying volatility**: Assumes constant volatility
- **Mean reversion**: Doesn't model market cycles
- **Autocorrelation**: Assumes independent returns

## Best Practices

1. **Use sufficient trials**: At least 10,000 for stable percentiles
2. **Historical data quality**: Minimum 5-10 years of data
3. **Include multiple scenarios**: Test bull, bear, and sideways markets separately
4. **Stress test**: Add extreme scenarios not in historical data
5. **Validate assumptions**: Check if normal distribution is appropriate
6. **Combine with fundamentals**: Don't rely solely on historical returns
7. **Update regularly**: Re-run with latest historical data

## Limitations

- **Backward-looking**: Based entirely on past performance
- **Distribution assumptions**: Normal distribution may not capture reality
- **Independence assumption**: Ignores serial correlation
- **No structural change**: Assumes future like past
- **Overfitting risk**: Historical period may not be representative

## See Also

- [Research: Monte Carlo Risk Analysis](../../../../research/monte-carlo-analysis.md) - Detailed findings
- [Notebook: Monte Carlo Demo](../../../../notebooks/04_monte_carlo_risk_analysis.ipynb) - Interactive examples
- [Visualization](visualization.md) - Plotting functions
- [DCA Optimizer](../optimization/dca-optimizer.md) - Complementary optimization approach
