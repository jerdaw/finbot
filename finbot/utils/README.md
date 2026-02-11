# Finbot Utilities Library

**Comprehensive collection of 176 utility functions for financial data analysis**

This directory contains a modular utility library organized into 15 categories, providing reusable tools for data collection, financial calculations, data manipulation, and visualization.

## Quick Reference

| Category | Files | Purpose | Key Functions |
|----------|-------|---------|---------------|
| [data_collection_utils/](#data-collection) | ~50 files | Fetch data from external APIs | `get_history()`, `get_fred_data()`, `get_sentiment()` |
| [finance_utils/](#finance-calculations) | ~20 files | Financial calculations and metrics | `get_cgr()`, `get_drawdown()`, `get_risk_free_rate()` |
| [pandas_utils/](#pandas-operations) | ~30 files | DataFrame operations and I/O | `save_dataframe()`, `filter_by_date()`, `hash_dataframe()` |
| [datetime_utils/](#datetime-operations) | ~25 files | Date/time conversions and utilities | `get_us_business_dates()`, `get_duration()` |
| [plotting_utils/](#visualization) | ~8 files | Interactive plotly visualizations | `plot_price_history()`, `plot_returns()` |
| [request_utils/](#http-requests) | ~6 files | HTTP requests with retry logic | `RequestHandler`, rate limiting, caching |
| [data_science_utils/](#data-science) | ~12 files | Data cleaning and transformation | Scalers, imputation, outlier detection |
| [file_utils/](#file-operations) | ~8 files | File system operations | `backup_file()`, `are_files_outdated()` |
| [validation_utils/](#validation) | ~5 files | Input validation helpers | `validate_types()`, type checking |
| [multithreading_utils/](#multithreading) | ~3 files | Parallel processing utilities | `get_max_threads()` |
| [dict_utils/](#dictionary-operations) | ~3 files | Dictionary manipulation | Flattening, merging, sorting |
| [json_utils/](#json-operations) | ~2 files | JSON serialization | Custom encoders for numpy/pandas |
| [vectorization_utils/](#vectorization) | ~2 files | Numpy vectorization helpers | Array operations |
| [function_utils/](#function-utilities) | ~2 files | Function decorators and wrappers | Retry logic, caching |
| [class_utils/](#class-utilities) | ~1 file | Class-related utilities | Metaclasses, decorators |

---

## Detailed Category Descriptions

### Data Collection

**Location**: `finbot/utils/data_collection_utils/`
**Purpose**: Fetch financial and economic data from 6+ external sources

#### Data Sources

| Source | Module | Key Functions | Data Types |
|--------|--------|---------------|-----------|
| **Yahoo Finance** | `yfinance/` | `get_history()`, `get_multiple_histories()` | Price histories (OHLCV), splits, dividends |
| **FRED** | `fred/` | `get_fred_data()`, `get_multiple_fred_data()` | Economic indicators, yields, rates |
| **Alpha Vantage** | `alpha_vantage/` | `get_avapi_base()`, `get_sentiment()` | Intraday data, sentiment scores, economic data |
| **Google Finance** | `google_finance/` | `get_sheet_base()` | Index data from Google Sheets |
| **BLS** | `bls/` | `get_bls_data()`, `get_all_popular_bls_datas()` | CPI, unemployment, labor statistics |
| **Shiller** | `scrapers/shiller/` | `get_shiller_data()` | CAPE ratios, PE ratios, long-term S&P data |
| **MSCI** | `scrapers/msci/` | `get_msci_data()` | MSCI index data |
| **PDR** | `pdr/` | `get_pdr_base()` | Pandas DataReader wrapper for various sources |

#### Features

- **Automatic caching**: All data saved as parquet files with smart update detection
- **Rate limiting**: Built-in respect for API rate limits
- **Retry logic**: Exponential backoff for failed requests
- **Parallel fetching**: Multithreaded data collection for multiple symbols
- **Format normalization**: Consistent DataFrame output across all sources

#### Example Usage

```python
from finbot.utils.data_collection_utils.yfinance import get_history
from finbot.utils.data_collection_utils.fred import get_fred_data

# Fetch price history
spy_df = get_history(
    symbols="SPY",
    start_date=datetime(2020, 1, 1),
    check_update=True
)

# Fetch economic data
gdp_df = get_fred_data(
    series_ids="GDP",
    start_date=datetime(2000, 1, 1)
)
```

---

### Finance Calculations

**Location**: `finbot/utils/finance_utils/`
**Purpose**: Financial metrics, returns analysis, and risk calculations

#### Key Functions

| Function | Purpose | Returns |
|----------|---------|---------|
| `get_cgr()` | Compound growth rate | Annualized growth rate |
| `get_pct_change()` | Percentage change | Percent change (optionally * 100) |
| `get_drawdown()` | Drawdown from peak | Series of drawdown percentages |
| `get_periods_per_year()` | Detect data frequency | Number of periods per year (252, 12, 4, 1) |
| `get_risk_free_rate()` | Fetch current risk-free rate | Float (current 3-month T-Bill rate) |
| `merge_price_histories()` | Merge overlapping price series | Combined DataFrame |
| `get_timeseries_stats()` | Calculate comprehensive stats | Dict with mean, std, sharpe, etc. |

#### Example Usage

```python
from finbot.utils.finance_utils import get_cgr, get_drawdown, get_periods_per_year

# Calculate annualized return
cagr = get_cgr(start_value=100, end_value=150, n_periods=252)

# Get drawdown series
drawdowns = get_drawdown(price_series)

# Detect frequency
periods = get_periods_per_year(price_df)  # Returns 252 for daily data
```

---

### Pandas Operations

**Location**: `finbot/utils/pandas_utils/`
**Purpose**: DataFrame I/O, filtering, hashing, and transformation

#### Key Functions

| Function | Purpose | Notes |
|----------|---------|-------|
| `save_dataframe()` | Save DataFrame to parquet | Smart backup on changes |
| `load_dataframe()` | Load DataFrame from parquet | Error handling, type preservation |
| `save_dataframes()` | Save multiple DataFrames (parallel) | Uses multithreading |
| `load_dataframes()` | Load multiple DataFrames (parallel) | Uses multithreading |
| `filter_by_date()` | Filter DataFrame by date range | Handles None gracefully |
| `hash_dataframe()` | Generate DataFrame hash | For change detection |
| `sort_dataframe_columns()` | Sort columns alphabetically | In-place or return new |
| `get_timeseries_frequency()` | Detect DataFrame frequency | Daily, weekly, monthly, etc. |

#### Features

- **Safety checks**: `_df_save_safety_check()` warns on data loss
- **Smart backups**: Automatically backs up files when safety check fails
- **Compression**: Zstandard compression by default
- **Parallel I/O**: Multithreaded save/load for multiple files

#### Example Usage

```python
from finbot.utils.pandas_utils import save_dataframe, load_dataframe, filter_by_date

# Save with safety checks
save_dataframe(df, file_path="data/spy.parquet", smart_backup=True)

# Load data
df = load_dataframe("data/spy.parquet")

# Filter by date
filtered = filter_by_date(df, start_date=datetime(2020, 1, 1))
```

---

### Datetime Operations

**Location**: `finbot/utils/datetime_utils/`
**Purpose**: Date conversions, business date calculations, and time ranges

#### Key Functions

| Function | Purpose | Example |
|----------|---------|---------|
| `get_us_business_dates()` | Generate US business date range | `get_us_business_dates(start, end)` |
| `get_missing_us_business_dates()` | Find missing business dates | For data validation |
| `get_latest_us_business_date()` | Get most recent business date | Respects market hours |
| `get_duration()` | Calculate duration between dates | Returns tuple (years, days) |
| `validate_start_end_dates()` | Validate date range | Raises on invalid ranges |
| `datetime_to_date()` | Convert datetime to date | Safe conversion |
| `get_months_between_dates()` | Count months between dates | For date arithmetic |

#### Example Usage

```python
from finbot.utils.datetime_utils import get_us_business_dates, get_latest_us_business_date

# Get all business dates in range
bdates = get_us_business_dates(
    start_date=datetime(2020, 1, 1),
    end_date=datetime(2020, 12, 31)
)

# Get latest business date (respects market hours)
latest = get_latest_us_business_date(min_time=time(hour=16))
```

---

### Visualization

**Location**: `finbot/utils/plotting_utils/`
**Purpose**: Interactive plotly charts for financial data

#### Available Plots

- `plot_price_history()` - Time series price charts
- `plot_returns()` - Returns distribution and time series
- `plot_drawdown()` - Drawdown visualization
- `plot_correlation_matrix()` - Asset correlation heatmap
- `plot_monte_carlo_trials()` - Monte Carlo simulation results
- `plot_histogram()` - Distribution histograms
- Custom plotly configurations with consistent styling

#### Example Usage

```python
from finbot.utils.plotting_utils import plot_price_history, plot_returns

# Interactive price chart
fig = plot_price_history(price_df, title="SPY Price History")
fig.show()

# Returns analysis
fig = plot_returns(returns_series, title="Daily Returns Distribution")
fig.show()
```

---

### HTTP Requests

**Location**: `finbot/utils/request_utils/`
**Purpose**: Robust HTTP requests with retry logic, rate limiting, and caching

#### Key Components

| Component | Purpose |
|-----------|---------|
| `RequestHandler` | Main request handler class with retry logic |
| `RateLimiter` | Token bucket rate limiting |
| `RetryStrategy` | Exponential backoff configuration |
| Response caching | Zstandard-compressed response caching |

#### Features

- **Automatic retries**: Exponential backoff with jitter
- **Rate limiting**: Token bucket algorithm
- **Response caching**: Compressed JSON caching by source
- **Timeout handling**: Configurable connection and read timeouts
- **Error handling**: Comprehensive exception handling and logging

#### Example Usage

```python
from finbot.utils.request_utils import RequestHandler

handler = RequestHandler()
response = handler.make_json_request(
    url="https://api.example.com/data",
    payload_kwargs={"params": {"symbol": "SPY"}},
    timeout=(10, 30),
    save_dir="responses/example_api"
)
```

---

### Data Science

**Location**: `finbot/utils/data_science_utils/`
**Purpose**: Data cleaning, transformation, and preprocessing

#### Available Tools

- **Scalers**: StandardScaler, MinMaxScaler, RobustScaler
- **Imputation**: Mean, median, forward-fill, backward-fill
- **Outlier detection**: IQR method, Z-score method
- **Data cleaning**: Remove duplicates, handle missing values
- **Normalization**: Various normalization strategies

---

### File Operations

**Location**: `finbot/utils/file_utils/`
**Purpose**: File system utilities with safety checks

#### Key Functions

- `backup_file()` - Create timestamped backups
- `is_file_outdated()` - Check if file needs updating
- `are_files_outdated()` - Batch check multiple files (parallel)
- File age calculations
- Safe file operations

---

### Additional Categories

#### Validation (`validation_utils/`)
- Type validation helpers
- Input validation functions
- Schema validation

#### Multithreading (`multithreading_utils/`)
- `get_max_threads()` - Calculate optimal thread count
- Thread pool configuration

#### Dictionary Operations (`dict_utils/`)
- Flatten nested dictionaries
- Merge dictionaries
- Sort by keys/values

#### JSON Operations (`json_utils/`)
- Custom JSON encoders for numpy/pandas types
- Safe serialization/deserialization

#### Vectorization (`vectorization_utils/`)
- Numpy vectorization helpers
- Array operations

---

## Design Philosophy

### Principles

1. **Modularity**: Each utility is self-contained and can be used independently
2. **Consistency**: Uniform API across all utilities (keyword args, error handling, logging)
3. **Safety**: Smart defaults, input validation, comprehensive error messages
4. **Performance**: Multithreading, caching, vectorization where appropriate
5. **Reliability**: Retry logic, rate limiting, graceful degradation

### Best Practices

- **Import patterns**: Import specific functions, not entire modules
  ```python
  # Good
  from finbot.utils.finance_utils import get_cgr, get_drawdown

  # Avoid
  from finbot.utils.finance_utils import *
  ```

- **Error handling**: All utilities log errors and provide helpful messages
- **Type hints**: Gradually adding type annotations (see Priority 3.2 in roadmap)
- **Documentation**: All public functions have docstrings with examples

---

## Contributing New Utilities

When adding new utility functions:

1. **Choose the right category**: Place in appropriate subdirectory
2. **Follow naming conventions**: Use descriptive names (`get_*`, `calculate_*`, `validate_*`)
3. **Add docstrings**: Include purpose, args, returns, raises, and example
4. **Add tests**: Create unit tests in `tests/unit/`
5. **Update this README**: Add function to appropriate category table
6. **Use logger**: Import from `config` and use instead of `print()`

Example template:

```python
"""Module description."""

from __future__ import annotations

from config import logger


def your_function(arg1: type, arg2: type) -> return_type:
    """
    One-line description.

    Detailed description if needed.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When this happens

    Example:
        >>> result = your_function(1, 2)
        >>> print(result)
        3
    """
    logger.info(f"Doing something with {arg1} and {arg2}")
    return arg1 + arg2
```

---

## See Also

- [Main README](../../README.md) - Project overview and quick start
- [AGENTS.md](../../AGENTS.md) - Comprehensive internal documentation
- [Architecture Diagrams](../../README.md#architecture) - Visual representation of utility usage
- [Example Notebooks](../../notebooks/) - Real-world usage examples
