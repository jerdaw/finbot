# Fund Simulator

The fund simulator models leveraged ETFs with realistic fees, borrowing costs, and spread expenses. It uses vectorized NumPy operations for high performance.

## Overview

The fund simulator:

- Simulates leveraged fund returns from underlying index data
- Accounts for expense ratios, borrowing costs (LIBOR), and spread
- Uses adjustment constants calibrated to real ETF data
- Processes 40 years of data in ~110ms (92,000 trading days/second)
- Validates against actual ETF performance with 2-5% tracking error

## Key Functions

### simulate_fund

Generic fund simulation function that looks up configuration from registry:

::: finbot.services.simulation.sim_specific_funds.simulate_fund
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### fund_simulator

Core simulation function with full parameter control:

::: finbot.services.simulation.fund_simulator.fund_simulator
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Simulation Equation

The core simulation equation is:

```
simulated_return = (underlying_change * leverage - daily_expenses) * mult_constant + add_constant
```

Where:
- `underlying_change`: Daily return of the underlying index
- `leverage`: Leverage ratio (1x, 2x, 3x, -1x, -2x, -3x)
- `daily_expenses`: Expense ratio + swap rate + spread + borrowing costs (LIBOR)
- `mult_constant`: Multiplicative adjustment factor (typically 1.0)
- `add_constant`: Additive adjustment factor (calibrated to real data)

## Expense Components

### Expense Ratio
Annual management fee charged by the fund:
- **SPY**: 0.0945% (very low, index fund)
- **UPRO**: 0.91% (leveraged, higher management)
- **TQQQ**: 0.86% (leveraged)

### Swap Rate (Overnight Borrowing)
Cost to maintain leveraged positions overnight:
- Approximated using overnight LIBOR rates
- Applied as `LIBOR * leverage_factor` for leveraged funds
- Zero for 1x funds

### Spread
Bid-ask spread and trading friction:
- **Default**: 0.05% (5 basis points)
- Higher for less liquid funds

### Borrowing Costs
Additional costs for short positions and leverage beyond swap:
- Zero for long-only 1x funds
- Increases with leverage ratio

## Quick Start

```python
from finbot.services.simulation.fund_simulator import simulate_fund
from finbot.utils.data_collection_utils.yfinance import get_history

# Simulate UPRO (3x leveraged S&P 500)
upro_sim = simulate_fund('UPRO', start_date='2010-01-01', end_date='2024-01-01')

# Access simulation results
print(upro_sim.columns)  # ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
print(f"Total return: {(upro_sim['Close'][-1] / upro_sim['Close'][0] - 1) * 100:.2f}%")

# Custom parameters
custom_sim = fund_simulator(
    price_df=spy_data,
    leverage_ratio=2.0,
    expense_ratio=0.01,
    spread=0.0005,
    swap_rate_df=libor_data,
    mult_constant=1.0,
    add_constant=0.0
)
```

## Pre-configured Funds

Finbot includes pre-configured simulations for 15 popular funds:

### Stock Funds

| Fund | Underlying | Leverage | Expense Ratio |
|------|------------|----------|---------------|
| **SPY** | S&P 500 | 1x | 0.0945% |
| **SSO** | S&P 500 | 2x | 0.91% |
| **UPRO** | S&P 500 | 3x | 0.91% |
| **QQQ** | Nasdaq 100 | 1x | 0.20% |
| **QLD** | Nasdaq 100 | 2x | 0.95% |
| **TQQQ** | Nasdaq 100 | 3x | 0.86% |

### Bond Funds

| Fund | Underlying | Leverage | Expense Ratio |
|------|------------|----------|---------------|
| **TLT** | 20Y Treasury | 1x | 0.15% |
| **UBT** | 20Y Treasury | 2x | 0.95% |
| **TMF** | 20Y Treasury | 3x | 1.09% |
| **IEF** | 7-10Y Treasury | 1x | 0.15% |
| **UST** | 7-10Y Treasury | 2x | 0.95% |
| **TYD** | 7-10Y Treasury | 3x | 1.09% |
| **SHY** | 1-3Y Treasury | 1x | 0.15% |

### Hybrid Funds

| Fund | Underlying | Composition |
|------|------------|-------------|
| **NTSX** | 90% S&P 500 + 60% Treasury futures | 1.5x effective leverage |

## Performance

Based on comprehensive benchmarks:

| Data Size | Time (ms) | Throughput (days/sec) |
|-----------|-----------|----------------------|
| 1 month (21 days) | 91.67 ± 10.52 | ~230 |
| 1 year (252 days) | 91.83 ± 9.67 | ~2,744 |
| 5 years (1,260 days) | 93.22 ± 9.93 | ~13,517 |
| 10 years (2,520 days) | 95.84 ± 10.64 | ~26,289 |
| 20 years (5,040 days) | 101.80 ± 11.48 | ~49,500 |
| 40 years (10,080 days) | 109.79 ± 12.77 | ~91,818 |

**Key Findings:**
- Sub-linear O(n) scaling: 480x data → 1.2x time
- Vectorized NumPy is faster than numba JIT compilation
- Processes 40 years of daily data in ~110ms

## Tracking Accuracy

Simulations validate against actual ETF data:

| Fund | Tracking Error | Sample Period |
|------|----------------|---------------|
| **UPRO** | 2-4% | 2010-2024 |
| **TQQQ** | 3-5% | 2010-2024 |
| **TMF** | 2-3% | 2010-2024 |

Tracking error sources:
- LIBOR approximation (overnight vs 3-month)
- Rebalancing timing differences
- Dividend reinvestment assumptions
- Intraday volatility (using daily data)

## Advanced Usage

### Historical Extension

Simulate funds before their inception:

```python
# UPRO launched in 2009, simulate back to 1990
upro_extended = simulate_fund('UPRO', start_date='1990-01-01', end_date='2024-01-01')

# Compare to actual data
actual_upro = get_history('UPRO', start='2009-06-25')
simulated_overlap = upro_extended.loc['2009-06-25':]

# Calculate tracking error
tracking_error = (simulated_overlap['Close'] / actual_upro['Close'] - 1).std()
print(f"Tracking error: {tracking_error:.2%}")
```

### Custom Fund Creation

Create hypothetical funds with custom parameters:

```python
# Hypothetical 5x leveraged S&P 500
extreme_leverage = fund_simulator(
    price_df=spy_data,
    leverage_ratio=5.0,
    expense_ratio=0.015,  # 1.5% expense ratio
    spread=0.001,  # 10 bps spread
    swap_rate_df=libor_data,
    mult_constant=1.0,
    add_constant=0.0
)

# Inverse leveraged fund
inverse_fund = fund_simulator(
    price_df=spy_data,
    leverage_ratio=-2.0,  # 2x inverse
    expense_ratio=0.0095,
    spread=0.0005,
    swap_rate_df=libor_data
)
```

### Sensitivity Analysis

Test impact of different expense assumptions:

```python
base_sim = simulate_fund('UPRO')

# Higher expenses
high_expense = fund_simulator(
    price_df=spy_data,
    leverage_ratio=3.0,
    expense_ratio=0.02,  # 2% vs 0.91% actual
    spread=0.001,
    swap_rate_df=libor_data
)

# Compare performance
base_return = (base_sim['Close'][-1] / base_sim['Close'][0] - 1)
high_expense_return = (high_expense['Close'][-1] / high_expense['Close'][0] - 1)
expense_drag = base_return - high_expense_return
print(f"Expense drag: {expense_drag:.2%}")
```

## Data Requirements

### Price Data Format

Input `price_df` must be a pandas DataFrame with:
- **Index**: DatetimeIndex (daily frequency)
- **Columns**: `Open`, `High`, `Low`, `Close`, `Volume`
- **Format**: Decimal (not percentage) prices

### LIBOR Data Format

Input `swap_rate_df` must be a pandas DataFrame with:
- **Index**: DatetimeIndex matching price_df
- **Column**: Interest rates as decimal (0.02 = 2%)
- **Source**: Approximated overnight LIBOR from `approximate_overnight_libor()`

## Implementation Details

The simulator uses:
- **Vectorized NumPy**: All operations vectorized for performance
- **Daily rebalancing**: Leveraged positions rebalanced at close
- **Compound returns**: Accurate multi-day return calculation
- **Missing data handling**: Forward-fill for gaps in LIBOR data

## See Also

- [Specific Funds](specific-funds.md) - Pre-configured fund simulations
- [Bond Ladder](bond-ladder.md) - Bond portfolio simulation
- [Monte Carlo](monte-carlo.md) - Risk analysis with simulated data
- [Performance Benchmarks](../../../../benchmarks.md) - Detailed performance analysis
