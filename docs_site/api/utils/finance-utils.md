# Finance Utilities

The `finance_utils` module provides 19 financial calculation and analysis functions for returns, drawdowns, time series statistics, and economic data.

## Overview

Key capabilities:

- **Returns Calculation**: Compound growth rate (CGR), percentage change
- **Risk Metrics**: Drawdown analysis, volatility, time series statistics
- **Time Period Analysis**: Detect data frequency, calculate periods per year
- **Price Adjustments**: Inflation adjustment, merge overlapping price series
- **Economic Cycles**: US GDP recession dates and classifications
- **Trend Analysis**: Bull/bear/sideways market classification

## Quick Reference

| Function | Purpose | Location |
|----------|---------|----------|
| `get_cgr` | Compound growth rate (CAGR) | `finbot.utils.finance_utils.get_cgr` |
| `get_pct_change` | Percentage change between values | `finbot.utils.finance_utils.get_pct_change` |
| `get_drawdown` | Calculate drawdown from price series | `finbot.utils.finance_utils.get_drawdown` |
| `get_periods_per_year` | Detect data frequency (daily, weekly, monthly) | `finbot.utils.finance_utils.get_periods_per_year` |
| `get_risk_free_rate` | Fetch current risk-free rate from FRED | `finbot.utils.finance_utils.get_risk_free_rate` |
| `merge_price_histories` | Merge overlapping price series | `finbot.utils.finance_utils.merge_price_histories` |
| `get_timeseries_stats` | Comprehensive statistics (mean, std, Sharpe, etc.) | `finbot.utils.finance_utils.get_timeseries_stats` |
| `get_theta_decay` | Calculate leveraged ETF decay | `finbot.utils.finance_utils.get_theta_decay` |
| `get_inflation_adjusted_value` | Adjust for CPI inflation | `finbot.utils.finance_utils.get_inflation_adjusted_value` |
| `get_price_trend_classifications` | Classify bull/bear/sideways periods | `finbot.utils.finance_utils.get_price_trend_classifications` |

## Core Functions

### get_cgr

Calculate compound annual growth rate.

**Location:** `finbot.utils.finance_utils.get_cgr`

```python
def get_cgr(
    initial_value: float,
    final_value: float,
    years: float
) -> float
```

**Parameters:**
- `initial_value` (float): Starting value
- `final_value` (float): Ending value
- `years` (float): Time period in years

**Returns:** Compound annual growth rate as decimal (0.10 = 10%)

**Example:**

```python
from finbot.utils.finance_utils.get_cgr import get_cgr

# Calculate CAGR for 5-year investment
initial_value = 100000
final_value = 150000
years = 5

cagr = get_cgr(initial_value, final_value, years)
print(f"CAGR: {cagr:.2%}")  # Output: CAGR: 8.45%
```

### get_drawdown

Calculate drawdown from peak.

**Location:** `finbot.utils.finance_utils.get_drawdown`

```python
def get_drawdown(prices: pd.Series) -> pd.Series
```

**Parameters:**
- `prices` (pd.Series): Price series with DatetimeIndex

**Returns:** Series of drawdown percentages (negative values)

**Example:**

```python
from finbot.utils.finance_utils.get_drawdown import get_drawdown
import pandas as pd

# Load price history
prices = pd.read_parquet('spy_prices.parquet')['Close']

# Calculate drawdown
drawdown = get_drawdown(prices)

# Analyze
max_dd = drawdown.min()
print(f"Maximum drawdown: {max_dd:.2%}")

# Find max drawdown date
max_dd_date = drawdown.idxmin()
print(f"Occurred on: {max_dd_date}")
```

### get_periods_per_year

Detect data frequency.

**Location:** `finbot.utils.finance_utils.get_periods_per_year`

```python
def get_periods_per_year(data: pd.Series | pd.DataFrame) -> int
```

**Parameters:**
- `data` (pd.Series | pd.DataFrame): Time series data with DatetimeIndex

**Returns:** Number of periods per year (252 for daily, 52 for weekly, 12 for monthly)

**Example:**

```python
from finbot.utils.finance_utils.get_periods_per_year import get_periods_per_year

# Detect frequency of price data
periods = get_periods_per_year(daily_prices)
print(f"Periods per year: {periods}")  # Output: 252 (trading days)

# Use for annualization
daily_returns = daily_prices.pct_change()
annual_volatility = daily_returns.std() * np.sqrt(periods)
```

### merge_price_histories

Merge overlapping price series with priority control.

**Location:** `finbot.utils.finance_utils.merge_price_histories`

```python
def merge_price_histories(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    priority: str = 'second'
) -> pd.DataFrame
```

**Parameters:**
- `df1` (pd.DataFrame): First price DataFrame
- `df2` (pd.DataFrame): Second price DataFrame
- `priority` (str): Which DataFrame takes precedence ('first' or 'second')

**Returns:** Merged DataFrame with overlapping dates resolved by priority

**Example:**

```python
from finbot.utils.finance_utils.merge_price_histories import merge_price_histories

# Merge simulated pre-inception data with actual ETF data
simulated = simulate_fund('UPRO', start='1990-01-01', end='2009-06-24')
actual = get_history('UPRO', start='2009-06-25')

# Merge with priority to actual data
merged = merge_price_histories(simulated, actual, priority='second')

# Result: 1990-2009 from simulation, 2009+ from actual
```

### get_risk_free_rate

Fetch current risk-free rate from FRED.

**Location:** `finbot.utils.finance_utils.get_risk_free_rate`

```python
def get_risk_free_rate(fallback: float = 0.02) -> float
```

**Parameters:**
- `fallback` (float, optional): Fallback rate if FRED unavailable (default: 0.02)

**Returns:** Risk-free rate as decimal

**Example:**

```python
from finbot.utils.finance_utils.get_risk_free_rate import get_risk_free_rate

# Get latest 3-month T-bill rate from FRED
rf_rate = get_risk_free_rate()
print(f"Risk-free rate: {rf_rate:.2%}")

# Use in Sharpe ratio calculation
sharpe = (portfolio_return - rf_rate) / portfolio_std
```

## Complete Function List

### Returns and Growth
- `get_cgr`: Compound growth rate
- `get_pct_change`: Percentage change
- `get_open_close_percent_change`: Open-to-close change

### Risk Metrics
- `get_drawdown`: Drawdown from peak
- `get_theta_decay`: Leveraged ETF decay
- `get_timeseries_stats`: Comprehensive statistics

### Time and Frequency
- `get_periods_per_year`: Detect data frequency
- `get_investment_event_horizon`: Calculate holding period

### Price Operations
- `merge_price_histories`: Merge overlapping series
- `get_inflation_adjusted_value`: CPI adjustment
- `get_series_adjusted_for_inflation`: Series-wide inflation adjustment

### Market Analysis
- `get_price_trend_classifications`: Bull/bear/sideways classification
- `get_us_gdp_recession_dates`: Recession periods
- `get_us_gdp_non_recession_dates`: Expansion periods
- `get_us_gdp_cycle_dates`: Full cycle dates
- `get_us_gdp_recessions_bools`: Boolean recession indicators

### Data and Utilities
- `get_risk_free_rate`: Fetch from FRED
- `get_mult_from_suffix`: Parse K/M/B/T multipliers
- `get_number_from_suffix`: Convert formatted strings to numbers

## See Also

- [Datetime Utilities](datetime-utils.md) - Time period calculations
- [Pandas Utilities](pandas-utils.md) - DataFrame operations
- [Data Science Utilities](data-science-utils.md) - Statistical analysis
