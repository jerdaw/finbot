# Corporate Actions and Data Quality Guide

**Last Updated:** 2026-02-16
**Status:** Production Ready

This guide explains how finbot handles corporate actions (stock splits, dividends) and data quality issues (missing values, gaps) in backtesting.

## Table of Contents

1. [Corporate Actions](#corporate-actions)
2. [Adjusted Prices](#adjusted-prices)
3. [Missing Data Policies](#missing-data-policies)
4. [Best Practices](#best-practices)
5. [Examples](#examples)

---

## Corporate Actions

Corporate actions like stock splits and dividend payments affect historical prices and can distort backtesting results if not handled correctly.

### Stock Splits

**What happens:**
- Share count increases (or decreases for reverse splits)
- Price per share adjusts proportionally
- Total portfolio value remains constant

**Example: 2:1 Stock Split**
- Before split: 100 shares @ $100 = $10,000
- After split: 200 shares @ $50 = $10,000

**How finbot handles it:**
- Uses adjusted prices that account for all historical splits
- OHLC prices are adjusted proportionally
- Original (unadjusted) prices preserved as `Close_Unadjusted`

### Dividends

**What happens:**
- Price drops by ~dividend amount on ex-dividend date
- Shareholders receive cash payment
- Historical prices adjusted to reflect total return

**Example: $2 Dividend**
- Day before ex-div: $100
- Ex-div date: ~$98 (price drops)
- Adjusted historical prices: subtract $2 from all pre-dividend prices

**How finbot handles it:**
- Uses adjusted prices that add back all historical dividends
- Reflects total return assuming dividend reinvestment
- Enables apples-to-apples comparison across time periods

---

## Adjusted Prices

### What Are Adjusted Prices?

Adjusted prices are historical prices that have been modified to account for corporate actions, creating a continuous price series that reflects total returns.

**Adjustment Types:**
- **Forward-adjusted**: Adjust future prices (not commonly used)
- **Backward-adjusted**: Adjust historical prices (industry standard, used by finbot)

### How Finbot Uses Adjusted Prices

By default, finbot uses the `Adj Close` column from price history data:

```python
# Automatic adjustment in BacktestRunner
if "Adj Close" in price_data.columns:
    # Save original close as reference
    price_data["Close_Unadjusted"] = price_data["Close"]

    # Replace Close with Adj Close
    price_data["Close"] = price_data["Adj Close"]

    # Adjust OHLC proportionally
    adjustment_factor = price_data["Close"] / price_data["Close_Unadjusted"]
    price_data["Open"] = price_data["Open"] * adjustment_factor
    price_data["High"] = price_data["High"] * adjustment_factor
    price_data["Low"] = price_data["Low"] * adjustment_factor
```

### Why Proportional OHLC Adjustment?

Simply replacing `Close` with `Adj Close` while leaving Open/High/Low unadjusted would violate price relationships:
- `Low` could be higher than `Close`
- `High` could be lower than `Close`
- Intraday ranges would be distorted

Proportional adjustment maintains these relationships.

### Data Sources

**YFinance** (default for finbot):
- Automatically provides `Adj Close` column
- Includes both `Close` (unadjusted) and `Adj Close` (adjusted)
- Adjustments updated daily

**Custom data:**
- Must include `Adj Close` column to use automatic adjustment
- If `Adj Close` is missing, raw `Close` is used (no adjustment)

---

## Missing Data Policies

Real-world price data often contains gaps due to:
- Market holidays
- Trading halts
- Data collection failures
- Delisted securities
- Limited historical data

Finbot provides 5 configurable policies for handling missing data.

### Policy Overview

| Policy | Description | Use Case | Risk |
|--------|-------------|----------|------|
| **FORWARD_FILL** (default) | Fill gaps with last known price | Normal market data with occasional gaps | May hide data quality issues |
| **DROP** | Remove rows with any missing values | Ensure complete data quality | May lose significant data |
| **ERROR** | Raise exception on missing data | Critical data quality requirements | Backtest will fail on any gap |
| **INTERPOLATE** | Linear interpolation between known values | Smooth transitions over gaps | May create unrealistic prices |
| **BACKFILL** | Fill gaps with next known price | Rare/special scenarios only | **Introduces look-ahead bias** |

### Configuration

Configure the policy when creating a BacktraderAdapter:

```python
from finbot.core.contracts import MissingDataPolicy
from finbot.services.backtesting.adapters.backtrader_adapter import BacktraderAdapter

# Example 1: Use default forward fill
adapter = BacktraderAdapter(
    price_histories=price_data,
    # missing_data_policy defaults to FORWARD_FILL
)

# Example 2: Strict data quality - fail on any gaps
adapter = BacktraderAdapter(
    price_histories=price_data,
    missing_data_policy=MissingDataPolicy.ERROR,
)

# Example 3: Drop incomplete rows
adapter = BacktraderAdapter(
    price_histories=price_data,
    missing_data_policy=MissingDataPolicy.DROP,
)

# Example 4: Interpolate gaps
adapter = BacktraderAdapter(
    price_histories=price_data,
    missing_data_policy=MissingDataPolicy.INTERPOLATE,
)
```

### Policy Behavior Details

#### FORWARD_FILL (Default)

```python
# Before
Date       Close
2020-01-01  100.0
2020-01-02  NaN
2020-01-03  NaN
2020-01-04  102.0

# After forward fill
Date       Close
2020-01-01  100.0
2020-01-02  100.0  # Filled with last known value
2020-01-03  100.0  # Filled with last known value
2020-01-04  102.0
```

**When to use:**
- Standard backtesting with typical market data
- Gaps are infrequent and short
- Willing to accept "price held constant" assumption

**Limitations:**
- May hide data quality problems
- Assumes no price movement during gap
- Can create unrealistic flat periods

#### DROP

```python
# Before
Date       Close
2020-01-01  100.0
2020-01-02  NaN
2020-01-03  NaN
2020-01-04  102.0

# After drop
Date       Close
2020-01-01  100.0
2020-01-04  102.0  # Rows with NaN removed
```

**When to use:**
- Data quality is paramount
- Gaps are rare
- Better to have less data than bad data

**Limitations:**
- Reduces dataset size
- May remove significant portions of data if gaps are frequent
- Changes the temporal spacing of data points

#### ERROR

```python
# Raises ValueError if any missing data detected
adapter = BacktraderAdapter(
    price_histories={"SPY": df_with_gaps},
    missing_data_policy=MissingDataPolicy.ERROR,
)

# This will raise:
# ValueError: Missing data detected in SPY with policy=ERROR.
#             Null counts by column: {'Close': 2, 'Open': 2, 'High': 2, 'Low': 2}
```

**When to use:**
- Production systems where data quality must be guaranteed
- Research requiring complete data
- Want to be alerted immediately to any data issues

**Limitations:**
- Backtest will fail on any gap
- Requires perfect data or pre-cleaning
- May need fallback policy for development

#### INTERPOLATE

```python
# Before
Date       Close
2020-01-01  100.0
2020-01-02  NaN
2020-01-03  NaN
2020-01-04  103.0

# After interpolate (linear)
Date       Close
2020-01-01  100.0
2020-01-02  101.0  # Interpolated
2020-01-03  102.0  # Interpolated
2020-01-04  103.0
```

**When to use:**
- Want smooth transitions over gaps
- Gaps are short (1-3 days)
- Prefer realistic-looking prices over "flat" forward fill

**Limitations:**
- Assumes linear price movement
- Creates synthetic prices that never actually traded
- May not reflect actual market behavior

#### BACKFILL (Use with Caution)

```python
# Before
Date       Close
2020-01-01  100.0
2020-01-02  NaN
2020-01-03  NaN
2020-01-04  105.0

# After backfill
Date       Close
2020-01-01  100.0
2020-01-02  105.0  # Filled with FUTURE value
2020-01-03  105.0  # Filled with FUTURE value
2020-01-04  105.0
```

⚠️ **WARNING: Introduces look-ahead bias!**

**When to use:**
- **Rarely used in backtesting** (look-ahead bias)
- Data preparation outside of backtesting
- Specific research scenarios where bias is understood

**Limitations:**
- **Uses future information to fill past gaps**
- **Will produce unrealistic backtest results**
- Only use if you fully understand the implications

### Checking Applied Policy

The policy used is recorded in backtest results:

```python
result = adapter.run(request)

# Check which policy was used
policy = result.assumptions["missing_data_policy"]
print(f"Policy used: {policy}")  # e.g., "forward_fill"
```

---

## Best Practices

### 1. Always Use Adjusted Prices

```python
# ✅ GOOD - Uses adjusted prices automatically
df = yf.download("AAPL", start="2020-01-01", end="2023-12-31")
# YFinance includes both 'Close' and 'Adj Close' - finbot uses Adj Close

# ⚠️ CAUTION - Custom data without Adj Close
df_custom = pd.DataFrame(...)  # Only has 'Close', no 'Adj Close'
# Will use unadjusted prices - may distort results
```

**Fix:** Add `Adj Close` column to custom data or explicitly handle splits/dividends.

### 2. Understand Your Data Quality

```python
# Check for missing data before backtesting
def check_data_quality(df):
    null_counts = df.isnull().sum()
    null_cols = null_counts[null_counts > 0]

    if len(null_cols) > 0:
        print("⚠️ Missing data detected:")
        print(null_cols)

        # Calculate gap distribution
        for col in null_cols.index:
            gaps = df[col].isnull()
            consecutive = gaps.groupby((~gaps).cumsum()).sum()
            max_gap = consecutive.max()
            print(f"  {col}: {null_cols[col]} missing, max consecutive gap: {max_gap}")
    else:
        print("✅ No missing data")

check_data_quality(price_data["SPY"])
```

### 3. Choose Policy Based on Context

**Research/Development:**
- Use `FORWARD_FILL` (default) for flexibility
- Switch to `ERROR` when finalizing research
- Document which policy was used

**Production:**
- Use `ERROR` to catch data issues early
- Have monitoring for data quality
- Alert on any missing data

**Academic/Publication:**
- Use `DROP` or `ERROR` for strictest data quality
- Document any adjustments made
- Report number of observations used

### 4. Validate Results with Corporate Actions

When backtesting securities with known corporate actions:

```python
# Check if major corporate actions are handled correctly
def validate_corporate_actions(symbol, split_date, split_ratio):
    """Verify split handling in price data."""
    df = yf.download(symbol, start=split_date - pd.Timedelta(days=30),
                     end=split_date + pd.Timedelta(days=30))

    # Check Adj Close continuity (should be smooth)
    returns = df['Adj Close'].pct_change()
    print(f"Max single-day return near split: {returns.abs().max():.2%}")

    # Check for split marker (if available)
    if 'Stock Splits' in df.columns:
        splits = df['Stock Splits'][df['Stock Splits'] != 0]
        print(f"Detected splits: {splits}")

# Example: Tesla 5:1 split on 2020-08-31
validate_corporate_actions("TSLA", pd.Timestamp("2020-08-31"), 5.0)
```

### 5. Document Assumptions

Always document in your research:
- Which missing data policy was used
- Whether adjusted or unadjusted prices were used
- Any known data quality issues
- Date ranges with potential gaps

```python
# Include in backtest metadata
result = adapter.run(request)
print(f"""
Backtest Configuration:
- Strategy: {result.metadata.strategy_name}
- Missing Data Policy: {result.assumptions['missing_data_policy']}
- Commission Model: {result.assumptions['commission_model']}
- Date Range: {result.assumptions['start']} to {result.assumptions['end']}
""")
```

---

## Examples

### Example 1: Basic Backtest with Default Settings

```python
import pandas as pd
import yfinance as yf
from finbot.core.contracts import BacktestRunRequest
from finbot.services.backtesting.adapters.backtrader_adapter import BacktraderAdapter

# Download data (includes adjusted prices automatically)
spy = yf.download("SPY", start="2020-01-01", end="2023-12-31")

# Create adapter with defaults (FORWARD_FILL policy, adjusted prices)
adapter = BacktraderAdapter(
    price_histories={"SPY": spy}
)

# Run backtest
request = BacktestRunRequest(
    strategy_name="NoRebalance",
    symbols=("SPY",),
    start=None,
    end=None,
    initial_cash=10000.0,
    parameters={"equity_proportions": [1.0]},
)

result = adapter.run(request)
print(f"Final Value: ${result.metrics['ending_value']:,.2f}")
print(f"CAGR: {result.metrics['cagr']:.2%}")
```

### Example 2: Strict Data Quality with Error Policy

```python
from finbot.core.contracts import MissingDataPolicy

# Download multiple symbols
symbols = ["SPY", "TLT", "GLD"]
price_data = {sym: yf.download(sym, start="2020-01-01", end="2023-12-31")
              for sym in symbols}

# Use ERROR policy to fail on any missing data
adapter = BacktraderAdapter(
    price_histories=price_data,
    missing_data_policy=MissingDataPolicy.ERROR,
)

try:
    request = BacktestRunRequest(
        strategy_name="Rebalance",
        symbols=("SPY", "TLT", "GLD"),
        start=None,
        end=None,
        initial_cash=10000.0,
        parameters={"rebal_proportions": [0.6, 0.3, 0.1], "rebal_interval": 20},
    )
    result = adapter.run(request)
    print("✅ Data quality check passed - no missing data")
except ValueError as e:
    print(f"❌ Data quality issue: {e}")
```

### Example 3: Handling Stock Split

```python
# Example with Apple's 4:1 split on 2020-08-31
aapl = yf.download("AAPL", start="2019-01-01", end="2023-12-31")

# Verify split handling
split_date = pd.Timestamp("2020-08-31")
pre_split = aapl.loc[:split_date - pd.Timedelta(days=1), "Adj Close"].iloc[-1]
post_split = aapl.loc[split_date, "Adj Close"]

# Adj Close should be continuous (no 4x jump)
print(f"Pre-split Adj Close: ${pre_split:.2f}")
print(f"Post-split Adj Close: ${post_split:.2f}")
print(f"Change: {(post_split / pre_split - 1):.2%}")  # Should be small, not 300%

# Run backtest - adjusted prices handle split automatically
adapter = BacktraderAdapter(price_histories={"AAPL": aapl})
request = BacktestRunRequest(
    strategy_name="NoRebalance",
    symbols=("AAPL",),
    start=None,
    end=None,
    initial_cash=10000.0,
    parameters={"equity_proportions": [1.0]},
)

result = adapter.run(request)
print(f"Backtest successful: ${result.metrics['ending_value']:,.2f}")
```

### Example 4: Comparing Missing Data Policies

```python
import numpy as np

# Create data with intentional gaps
dates = pd.bdate_range("2020-01-01", periods=250)
prices = 100 + np.cumsum(np.random.randn(250) * 0.5)

df = pd.DataFrame(
    {
        "Open": prices * 0.99,
        "High": prices * 1.01,
        "Low": prices * 0.98,
        "Close": prices,
        "Adj Close": prices,
        "Volume": 1000000,
    },
    index=dates,
)

# Introduce gaps
df.iloc[50:55, df.columns.get_indexer(["Open", "High", "Low", "Close", "Adj Close"])] = np.nan
df.iloc[100:103, df.columns.get_indexer(["Open", "High", "Low", "Close", "Adj Close"])] = np.nan

# Test different policies
policies = [
    MissingDataPolicy.FORWARD_FILL,
    MissingDataPolicy.DROP,
    MissingDataPolicy.INTERPOLATE,
]

results = {}
for policy in policies:
    adapter = BacktraderAdapter(
        price_histories={"STOCK": df},
        missing_data_policy=policy,
    )

    request = BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("STOCK",),
        start=None,
        end=None,
        initial_cash=10000.0,
        parameters={"equity_proportions": [1.0]},
    )

    result = adapter.run(request)
    results[policy.value] = {
        "ending_value": result.metrics["ending_value"],
        "cagr": result.metrics["cagr"],
        "sharpe": result.metrics["sharpe"],
    }

# Compare results
print("\nPolicy Comparison:")
print("-" * 60)
for policy, metrics in results.items():
    print(f"{policy:15} | ${metrics['ending_value']:>10,.2f} | "
          f"CAGR: {metrics['cagr']:>6.2%} | Sharpe: {metrics['sharpe']:>5.2f}")
```

---

## Troubleshooting

### Issue: Backtest Results Don't Match Expected Returns

**Possible causes:**
1. Using unadjusted prices (no `Adj Close` column)
2. Missing corporate actions in custom data
3. Data source provides pre-adjusted prices

**Solution:**
```python
# Check if Adj Close is present
if "Adj Close" not in df.columns:
    print("⚠️ No Adj Close column - using unadjusted prices")

# For custom data, create Adj Close manually
df["Adj Close"] = df["Close"]  # Start with unadjusted
# Then apply your split/dividend adjustments
```

### Issue: Large Gaps in Data Cause Strange Results

**Possible causes:**
1. Forward fill creating unrealistic flat periods
2. Trading halts or delistings
3. Data collection failures

**Solution:**
```python
# Use DROP or ERROR policy to identify gaps
adapter = BacktraderAdapter(
    price_histories=price_data,
    missing_data_policy=MissingDataPolicy.ERROR,  # Fail on gaps
)

# Or manually inspect gaps before backtesting
gaps = df.isnull().sum()
print(f"Missing data: {gaps[gaps > 0]}")
```

### Issue: Backtest Fails with "Missing data detected"

**Possible causes:**
1. ERROR policy with incomplete data
2. Data source reliability issues
3. Symbol not traded during entire period

**Solution:**
```python
# Option 1: Use more permissive policy
adapter = BacktraderAdapter(
    price_histories=price_data,
    missing_data_policy=MissingDataPolicy.FORWARD_FILL,
)

# Option 2: Clean data before backtesting
df_clean = df.dropna()

# Option 3: Use only complete date range
first_valid = df.first_valid_index()
last_valid = df.last_valid_index()
df_clean = df.loc[first_valid:last_valid]
```

---

## Further Reading

- [Backtest Runner Documentation](../api/backtesting/backtest_runner.md)
- [BacktraderAdapter API Reference](../api/backtesting/backtrader_adapter.md)
- [Golden Strategy Definitions](../planning/golden-strategies-and-datasets.md)
- [Parity Testing Guide](../research/adapter-migration-status-2026-02-16.md)

---

## Changelog

**2026-02-16:**
- Initial documentation for corporate actions and missing data policies
- Added examples for all 5 missing data policies
- Documented adjusted price handling
- Added troubleshooting section
