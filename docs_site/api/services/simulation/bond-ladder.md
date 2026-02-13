# Bond Ladder Simulator

The bond ladder simulator models fixed-income portfolios with staggered maturities, accounting for yield curves, reinvestment, and present value calculations.

## Overview

The bond ladder simulator provides:

- **Bond modeling**: Individual bond cash flows with coupon payments
- **Ladder construction**: Portfolios with staggered maturities (e.g., 1-10 years)
- **Yield curve integration**: Historical yield data from FRED
- **Present value calculation**: Using `numpy_financial.pv()`
- **Reinvestment simulation**: Maturing bonds reinvested at current yields

## Modules

### Bond Ladder Simulator

Main simulation orchestrator:

::: finbot.services.simulation.bond_ladder.bond_ladder_simulator
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### Bond Class

Individual bond representation:

::: finbot.services.simulation.bond_ladder.bond
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### Ladder Class

Bond ladder portfolio:

::: finbot.services.simulation.bond_ladder.ladder
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### Yield Curve Builder

Constructs yield curves from FRED data:

::: finbot.services.simulation.bond_ladder.build_yield_curve
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Quick Start

### Basic Bond Ladder

```python
from finbot.services.simulation.bond_ladder.bond_ladder_simulator import simulate_bond_ladder
from finbot.services.simulation.bond_ladder.build_yield_curve import build_yield_curve
import pandas as pd

# Build yield curve from FRED data
yield_curve = build_yield_curve(
    start_date='2010-01-01',
    end_date='2024-01-01'
)

# Simulate 10-year ladder with $100,000
results = simulate_bond_ladder(
    initial_investment=100000,
    ladder_years=10,
    yield_curve=yield_curve,
    coupon_frequency='semiannual'
)

print(f"Total value: ${results['total_value'][-1]:,.0f}")
print(f"Total return: {(results['total_value'][-1] / 100000 - 1) * 100:.2f}%")
```

### Custom Ladder Configuration

```python
# 5-year ladder with quarterly coupons
results = simulate_bond_ladder(
    initial_investment=50000,
    ladder_years=5,
    yield_curve=yield_curve,
    coupon_frequency='quarterly',
    reinvestment_strategy='extend_ladder'
)
```

## Ladder Strategies

### Traditional Ladder

Equal amounts invested across maturities:

```python
# $100,000 across 10 bonds (1-10 years)
# Each bond: $10,000
ladder = simulate_bond_ladder(
    initial_investment=100000,
    ladder_years=10,
    allocation='equal'
)
```

### Barbell Ladder

Concentrated at short and long maturities:

```python
# 50% in 1-year, 50% in 10-year
ladder = simulate_bond_ladder(
    initial_investment=100000,
    ladder_years=10,
    allocation='barbell',
    short_weight=0.5,
    long_weight=0.5
)
```

### Bullet Ladder

Concentrated at specific maturity:

```python
# All maturing in year 5
ladder = simulate_bond_ladder(
    initial_investment=100000,
    ladder_years=5,
    allocation='bullet',
    target_year=5
)
```

## Bond Mechanics

### Coupon Payments

Bonds pay periodic interest:

```python
from finbot.services.simulation.bond_ladder.bond import Bond

# 5-year bond with 3% coupon, semiannual payments
bond = Bond(
    face_value=10000,
    coupon_rate=0.03,
    years_to_maturity=5,
    coupon_frequency='semiannual'
)

# Get cash flows
cash_flows = bond.get_cash_flows()
# Returns: [(0.5 years, $150), (1.0 years, $150), ..., (5.0 years, $10,150)]
```

### Present Value

Bonds are valued using discount rates:

```python
import numpy_financial as npf

# Present value of 5-year bond with 3% coupon at 4% discount rate
pv = npf.pv(
    rate=0.04 / 2,  # Semiannual discounting
    nper=10,  # 5 years × 2 periods/year
    pmt=150,  # $150 coupon payment
    fv=10000  # $10,000 face value
)

print(f"Present value: ${-pv:,.2f}")  # Negative because it's a cost
```

### Yield Curve

Historical yields from FRED:

```python
from finbot.services.simulation.bond_ladder.get_yield_history import get_yield_history

# Get 10-year Treasury yields
yields_10y = get_yield_history(
    symbol='DGS10',  # FRED symbol for 10-year constant maturity
    start_date='2010-01-01',
    end_date='2024-01-01'
)

print(f"Average 10Y yield: {yields_10y.mean():.2%}")
```

## Reinvestment Strategies

### Extend Ladder

Reinvest maturing bonds at longest maturity:

```python
# When 1-year bond matures, buy new 10-year bond
results = simulate_bond_ladder(
    initial_investment=100000,
    ladder_years=10,
    reinvestment_strategy='extend_ladder'
)
```

### Maintain Maturity

Reinvest at same maturity:

```python
# When 1-year bond matures, buy new 1-year bond
results = simulate_bond_ladder(
    initial_investment=100000,
    ladder_years=10,
    reinvestment_strategy='maintain_maturity'
)
```

### Roll Down

Reinvest at next shorter maturity:

```python
# When 1-year bond matures, take cash (exit ladder)
results = simulate_bond_ladder(
    initial_investment=100000,
    ladder_years=10,
    reinvestment_strategy='roll_down'
)
```

## Advanced Features

### Interest Rate Sensitivity

Measure duration and convexity:

```python
# Duration: sensitivity to interest rate changes
duration = calculate_duration(bond, yield_rate=0.03)
print(f"Macaulay duration: {duration:.2f} years")

# Price change for 1% rate increase
price_change = -duration * 0.01 * bond.present_value
print(f"Expected price change: ${price_change:,.2f}")
```

### Total Return Analysis

Decompose returns into components:

```python
results = simulate_bond_ladder(...)

# Components:
# - Coupon income
# - Price appreciation/depreciation
# - Reinvestment income

total_return = results['total_value'][-1] / results['total_value'][0] - 1
coupon_return = results['coupon_income'].sum() / results['total_value'][0]
capital_return = total_return - coupon_return
```

## Data Requirements

### Yield Curve Data

Required FRED symbols for complete yield curve:

| Maturity | FRED Symbol | Description |
|----------|-------------|-------------|
| 1 month | DGS1MO | 1-Month Treasury |
| 3 months | DGS3MO | 3-Month Treasury |
| 6 months | DGS6MO | 6-Month Treasury |
| 1 year | DGS1 | 1-Year Treasury |
| 2 years | DGS2 | 2-Year Treasury |
| 3 years | DGS3 | 3-Year Treasury |
| 5 years | DGS5 | 5-Year Treasury |
| 7 years | DGS7 | 7-Year Treasury |
| 10 years | DGS10 | 10-Year Treasury |
| 20 years | DGS20 | 20-Year Treasury |
| 30 years | DGS30 | 30-Year Treasury |

## Performance

The bond ladder simulator:

- Processes 16,000+ trading days in seconds
- Uses vectorized NumPy operations
- Replaced numba `@jitclass` with plain Python classes
- Uses `numpy_financial.pv()` for present value calculations

## Limitations

- **No default risk**: Assumes all bonds pay as promised (Treasury assumption)
- **No callability**: Bonds cannot be called early
- **No inflation protection**: Nominal yields, not TIPS
- **Simplified taxes**: No tax modeling
- **No transaction costs**: Assumes frictionless reinvestment

## Use Cases

### Retirement Income

Create predictable cash flow stream:

```python
# Retiree needing $50,000/year for 20 years
ladder = simulate_bond_ladder(
    initial_investment=1000000,
    ladder_years=20,
    target_annual_income=50000
)
```

### Liability Matching

Match bond maturities to known future expenses:

```python
# College expenses: $30k/year for years 1-4
ladder = simulate_bond_ladder(
    initial_investment=120000,
    ladder_years=4,
    allocation=[30000, 30000, 30000, 30000]
)
```

### Interest Rate Hedging

Diversify reinvestment risk across maturities:

```python
# 10-year ladder reduces timing risk
ladder = simulate_bond_ladder(
    initial_investment=100000,
    ladder_years=10,
    allocation='equal'
)
```

## See Also

- [Fund Simulator](../fund-simulator.md) - Leveraged ETF simulation
- [Monte Carlo](monte-carlo.md) - Risk analysis with simulated data
- [FRED Data Collection](../../utils/data-collection-utils.md#fred) - Yield data retrieval
- [Example Notebook 05](../../examples/05-bond-ladder.ipynb) - Interactive examples
