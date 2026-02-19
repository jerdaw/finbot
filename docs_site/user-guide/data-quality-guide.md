# Data Quality and Monitoring Guide

**Created:** 2026-02-16
**Status:** Active

---

## Overview

Finbot maintains a comprehensive data quality and monitoring infrastructure to ensure the reliability of the daily data pipeline. This guide explains how to monitor data freshness, diagnose staleness issues, validate data integrity, and extend the monitoring system.

**Key capabilities:**
- Automatic freshness monitoring for 7 data sources
- CLI status command with staleness detection
- DataFrame validation utilities
- Centralized data source registry

---

## Quick Reference

```bash
# Check data freshness status
finbot status

# Show only stale data sources
finbot status --stale-only

# Update all data sources
finbot update

# Run daily pipeline with verbose output
finbot update --verbose
```

---

## Data Quality Infrastructure

### Architecture Overview

```
finbot/services/data_quality/
├── data_source_registry.py    # Registry of 7 tracked data sources
├── check_data_freshness.py    # Freshness monitoring engine
└── validate_dataframe.py      # DataFrame validation utilities
```

**Data flow:**
1. `data_source_registry.py` defines data sources and staleness thresholds
2. `check_data_freshness.py` scans directories and computes staleness
3. `finbot status` CLI command displays results in formatted table
4. `validate_dataframe.py` validates loaded DataFrames for common issues

---

## Data Source Registry

### Registered Data Sources

The registry tracks 7 data sources with specific staleness thresholds:

| Source | Directory | Max Age | Update Frequency | Description |
|--------|-----------|---------|------------------|-------------|
| Yahoo Finance | `yfinance_data/history/` | 3 days | Daily (market hours) | OHLCV price histories |
| Google Finance | `google_finance_data/` | 3 days | Daily | Index data from Google Sheets |
| FRED | `fred_data/` | 7 days | Weekly | Federal Reserve economic data |
| Shiller | `shiller_data/` | 35 days | Monthly | CAPE ratios, PE ratios, long-term S&P data |
| Alpha Vantage | `alpha_vantage_data/` | 7 days | Weekly | Intraday data, sentiment scores |
| BLS | `bls_data/` | 35 days | Monthly | CPI, unemployment, labor statistics |
| Simulations | `simulations/` | 3 days | Daily | Fund and index simulation results |

**File format:** All data sources use **parquet** format (fast, safe, interoperable).

### Staleness Thresholds Explained

**Why different thresholds?**

Data sources have different natural update frequencies based on their upstream publication schedules:

- **3 days** (Yahoo Finance, Google Finance, Simulations): Market data updated daily during trading days. 3-day threshold accounts for weekends.

- **7 days** (FRED, Alpha Vantage): Economic data updated weekly or as published. 7-day threshold provides buffer for delayed releases.

- **35 days** (Shiller, BLS): Monthly economic reports. 35-day threshold (just over 1 month) flags missed updates without false alarms.

**Staleness calculation:**
```python
age_days = (datetime.now() - newest_file_mtime).total_seconds() / 86400
is_stale = age_days > source.max_age_days
```

---

## Using the CLI Status Command

### Basic Usage

```bash
# Show all data sources
finbot status
```

**Example output:**
```
Data Source Status
==================
+----------------+-------+--------+------------------+----------+--------+
| Source         | Files |   Size | Last Updated     |      Age | Status |
+----------------+-------+--------+------------------+----------+--------+
| Yahoo Finance  |    67 | 15.2 MB| 2026-02-16 09:15 |   2h ago |   OK   |
| Google Finance |     4 |  2.1 MB| 2026-02-16 09:12 |   2h ago |   OK   |
| FRED           |    38 |  8.7 MB| 2026-02-14 10:30 |  2d 0h ago|   OK   |
| Shiller        |     2 |  1.4 MB| 2026-01-28 14:22 | 19d 5h ago|   OK   |
| Alpha Vantage  |    12 |  3.8 MB| 2026-02-15 08:00 |  1d 3h ago|   OK   |
| BLS            |     5 |  1.9 MB| 2026-01-20 11:15 | 27d 0h ago|   OK   |
| Simulations    |    16 | 12.3 MB| 2026-02-16 09:20 |   1h ago |   OK   |
+----------------+-------+--------+------------------+----------+--------+

Total: 144 files (45.4 MB) across 7 sources
All data sources are fresh.
```

### Advanced Options

```bash
# Show only stale data sources
finbot status --stale-only

# Show staleness thresholds
finbot status --verbose
```

**Example stale output:**
```
Data Source Status
==================
+----------------+-------+--------+------------------+----------+--------+
| Source         | Files |   Size | Last Updated     |      Age | Status |
+----------------+-------+--------+------------------+----------+--------+
| Yahoo Finance  |    67 | 15.2 MB| 2026-02-10 09:15 |  6d 2h ago| STALE |
| Simulations    |    16 | 12.3 MB| 2026-02-10 09:20 |  6d 1h ago| STALE |
+----------------+-------+--------+------------------+----------+--------+

Total: 144 files (45.4 MB) across 7 sources
Warning: 2 source(s) are stale. Run 'finbot update' to refresh.
```

### Understanding Status Output

**Columns explained:**
- **Source**: Data source name (from registry)
- **Files**: Number of parquet files matching the source pattern
- **Size**: Total size of all files (human-readable)
- **Last Updated**: Timestamp of newest file modification
- **Age**: Human-readable age (minutes/hours/days from now)
- **Status**: `OK` or `STALE` based on staleness threshold

**Age formatting:**
- Less than 1 hour: `45m ago`
- Less than 1 day: `8h ago`
- 1+ days: `3d 6h ago`
- No data: `no data`

---

## Troubleshooting Data Freshness Issues

### Diagnostic Workflow

1. **Identify stale sources:**
   ```bash
   finbot status --stale-only
   ```

2. **Check for errors in logs:**
   ```bash
   # View latest log file
   tail -n 100 logs/finbot.log

   # Search for errors in last update
   grep ERROR logs/finbot.log | tail -n 20
   ```

3. **Run manual update:**
   ```bash
   finbot update --verbose
   ```

4. **Verify freshness:**
   ```bash
   finbot status
   ```

### Common Issues and Solutions

#### Issue: Yahoo Finance data is stale

**Symptoms:**
- `finbot status` shows Yahoo Finance as STALE
- Last updated >3 days ago

**Causes:**
- Network connectivity issues
- Yahoo Finance API rate limiting
- Ticker symbol changes/delistings

**Solutions:**
```bash
# 1. Check network connectivity
ping finance.yahoo.com

# 2. Run update with verbose logging
finbot update --verbose

# 3. Check logs for specific ticker errors
grep "yfinance" logs/finbot.log | tail -n 50

# 4. If rate limited, wait 1 hour and retry
# Yahoo Finance has informal rate limits (~2000 requests/hour)
```

**Manual workaround:**
```python
# Test specific ticker in Python
from finbot.utils.data_collection_utils.yfinance.get_history import get_history

# Force update for specific ticker
df = get_history("SPY", force_update=True)
print(df.tail())
```

#### Issue: Google Finance data is stale

**Symptoms:**
- Google Finance shown as STALE
- Missing API credentials error in logs

**Causes:**
- Missing Google service account credentials
- Credentials file path incorrect
- Google Sheets API disabled

**Solutions:**
```bash
# 1. Check if credentials file exists
echo $GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH
ls -l $GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH

# 2. Set credentials path if missing
export GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH=/path/to/credentials.json

# 3. Verify credentials are valid JSON
python3 -c "import json; json.load(open('$GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH'))"

# 4. Run update
finbot update
```

#### Issue: FRED data is stale

**Symptoms:**
- FRED shown as STALE (>7 days old)
- API key errors in logs

**Causes:**
- Missing FRED API key (note: FRED may work without key but has lower rate limits)
- Network issues
- FRED service outage

**Solutions:**
```bash
# 1. Check API key (optional but recommended)
echo $FRED_API_KEY

# 2. Test FRED connectivity
python3 -c "from finbot.utils.data_collection_utils.fred.get_fred_data import get_fred_data; print(get_fred_data('SP500', force_update=True).tail())"

# 3. Run full update
finbot update
```

#### Issue: Simulations are stale

**Symptoms:**
- Simulations shown as STALE
- Files older than 3 days

**Causes:**
- Upstream data dependencies stale (Yahoo Finance, Google Finance)
- Simulation pipeline errors
- Missing LIBOR data for overnight rates

**Solutions:**
```bash
# 1. Check upstream dependencies first
finbot status | grep -E "(Yahoo|Google|FRED)"

# 2. Update upstream data
finbot update --verbose

# 3. Check simulation logs
grep "simulation" logs/finbot.log | tail -n 50

# 4. Verify simulations regenerated
ls -lth finbot/data/simulations/ | head -n 20
```

**Dependency chain:**
```
FRED data (overnight rates)
  → approximate_overnight_libor()
    → index simulators (SP500TR, ND100TR, bond indexes)
      → fund simulators (SPY, SSO, UPRO, TLT, etc.)
```

If simulations fail, check each dependency in order.

---

## DataFrame Validation

### Using validate_dataframe()

The `validate_dataframe()` utility catches common data quality issues after loading parquet files.

**Basic usage:**
```python
from finbot.utils.pandas_utils.load_df import load_df
from finbot.services.data_quality.validate_dataframe import validate_dataframe

# Load DataFrame
df = load_df("finbot/data/yfinance_data/history/SPY_history_1d.parquet")

# Validate
result = validate_dataframe(
    df=df,
    file_path="SPY_history_1d.parquet",
    min_rows=100,
    expected_columns=["Open", "High", "Low", "Close", "Volume"],
    check_duplicates=True,
    check_nulls=True,
)

# Check results
if not result.is_valid:
    print(f"Validation failed with {len(result.errors)} errors:")
    for error in result.errors:
        print(f"  - {error}")

if result.warnings:
    print(f"Warnings ({len(result.warnings)}):")
    for warning in result.warnings:
        print(f"  - {warning}")
```

### Validation Checks

| Check | Description | Failure Type |
|-------|-------------|--------------|
| Empty DataFrame | `df.empty == True` | Error (blocks) |
| Minimum rows | `len(df) < min_rows` | Error (blocks) |
| Expected columns | Missing required columns | Error (blocks) |
| Duplicate indices | `df.index.duplicated().any()` | Warning (non-blocking) |
| Null values | `df.isnull().sum() > 0` | Warning (non-blocking) |

**ValidationResult attributes:**
```python
result.is_valid          # bool: True if no errors
result.row_count         # int: Number of rows
result.col_count         # int: Number of columns
result.errors            # list[str]: Blocking errors
result.warnings          # list[str]: Non-blocking warnings
result.file_path         # Path: Source file path
```

### Example: Validating Price History

```python
from pathlib import Path
from finbot.utils.pandas_utils.load_df import load_df
from finbot.services.data_quality.validate_dataframe import validate_dataframe

def validate_price_history(ticker: str) -> bool:
    """Validate a ticker's price history."""
    file_path = Path(f"finbot/data/yfinance_data/history/{ticker}_history_1d.parquet")

    if not file_path.exists():
        print(f"Error: {file_path} does not exist")
        return False

    df = load_df(file_path)

    result = validate_dataframe(
        df=df,
        file_path=file_path,
        min_rows=252,  # At least 1 trading year
        expected_columns=["Open", "High", "Low", "Close", "Volume", "Adj Close"],
        check_duplicates=True,
        check_nulls=True,
    )

    if result.is_valid:
        print(f"✓ {ticker}: {result.row_count} rows, {result.col_count} columns")
        return True
    else:
        print(f"✗ {ticker}: FAILED validation")
        for error in result.errors:
            print(f"  ERROR: {error}")
        for warning in result.warnings:
            print(f"  WARN: {warning}")
        return False

# Validate multiple tickers
tickers = ["SPY", "QQQ", "TLT", "GLD"]
for ticker in tickers:
    validate_price_history(ticker)
```

**Example output:**
```
✓ SPY: 5432 rows, 6 columns
✓ QQQ: 4821 rows, 6 columns
✗ TLT: FAILED validation
  ERROR: Expected at least 252 rows, got 180
  WARN: Null values in 1 columns
✓ GLD: 3456 rows, 6 columns
```

---

## Adding New Data Sources to Registry

### Step-by-Step Guide

**1. Add directory constant (if new source):**

Edit `finbot/constants/path_constants.py`:
```python
# Subdirectories under DATA_DIR
NEW_SOURCE_DATA_DIR = _process_dir(DATA_DIR / "new_source_data")
```

**2. Add data source to registry:**

Edit `finbot/services/data_quality/data_source_registry.py`:
```python
from finbot.constants.path_constants import NEW_SOURCE_DATA_DIR

DATA_SOURCES: tuple[DataSource, ...] = (
    # ... existing sources ...
    DataSource(
        name="New Source",
        directory=NEW_SOURCE_DATA_DIR,
        pattern="*.parquet",  # Glob pattern for files
        max_age_days=7,       # Staleness threshold
        description="Description of data source",
    ),
)
```

**3. Create data collection utility:**

Create `finbot/utils/data_collection_utils/new_source/get_new_source_data.py`:
```python
"""Fetch data from New Source.

Description of what this source provides and how often it updates.
"""

from __future__ import annotations

import datetime
import pandas as pd

from finbot.constants.path_constants import NEW_SOURCE_DATA_DIR
from finbot.utils.pandas_utils.save_df import save_df
from finbot.config import logger


def get_new_source_data(
    symbols: list[str] | str,
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    force_update: bool = False,
) -> pd.DataFrame:
    """Fetch data from New Source.

    Args:
        symbols: Symbol(s) to fetch.
        start_date: Start date for data.
        end_date: End date for data.
        force_update: Force re-download even if cached.

    Returns:
        DataFrame with fetched data.
    """
    if not isinstance(symbols, list):
        symbols = [symbols]

    # TODO: Implement data fetching logic
    # This is a template - adapt to your data source

    results = []
    for symbol in symbols:
        logger.info(f"Fetching {symbol} from New Source")

        # Check cache first
        cache_path = NEW_SOURCE_DATA_DIR / f"{symbol}.parquet"
        if cache_path.exists() and not force_update:
            df = pd.read_parquet(cache_path)
            logger.info(f"Loaded {symbol} from cache ({len(df)} rows)")
        else:
            # Fetch from API/scraper
            df = _fetch_from_api(symbol, start_date, end_date)

            # Save to cache
            save_df(df, cache_path)
            logger.info(f"Saved {symbol} to cache ({len(df)} rows)")

        results.append(df)

    # Combine results
    if len(results) == 1:
        return results[0]
    return pd.concat(results, axis=1)


def _fetch_from_api(
    symbol: str,
    start_date: datetime.date | None,
    end_date: datetime.date | None,
) -> pd.DataFrame:
    """Fetch data from API."""
    # TODO: Implement actual API call
    raise NotImplementedError("Implement API fetching logic")
```

**4. Add to daily update pipeline:**

Edit `scripts/update_daily.py`:
```python
from finbot.utils.data_collection_utils.new_source.get_new_source_data import get_new_source_data

def update_new_source_data() -> None:
    """Update data from New Source."""
    symbols = ["SYMBOL1", "SYMBOL2", "SYMBOL3"]
    for symbol in symbols:
        get_new_source_data(symbol, force_update=True)

def update_daily() -> None:
    """Run the full daily data update pipeline."""
    logger.info("Starting daily data update")
    t_start = perf_counter()

    steps = [
        (update_yf_price_histories, "YF Price Histories"),
        (update_gf_price_histories, "GF Price Histories"),
        (update_fred_data, "FRED Data"),
        (update_shiller_data, "Shiller Data"),
        (update_new_source_data, "New Source Data"),  # Add here
        (update_simulations, "Simulations"),
    ]
    # ... rest of function
```

**5. Test the integration:**

```bash
# 1. Verify directory was created
ls -la finbot/data/new_source_data/

# 2. Test data collection
python3 -c "from finbot.utils.data_collection_utils.new_source.get_new_source_data import get_new_source_data; print(get_new_source_data('TEST_SYMBOL'))"

# 3. Run full update
finbot update --verbose

# 4. Check status
finbot status | grep "New Source"
```

### Example: Adding Polygon.io Data Source

**Complete example** of adding a new financial data provider:

```python
# 1. path_constants.py
POLYGON_DATA_DIR = _process_dir(DATA_DIR / "polygon_data")

# 2. data_source_registry.py
DataSource(
    name="Polygon.io",
    directory=POLYGON_DATA_DIR,
    pattern="*.parquet",
    max_age_days=3,  # Daily market data
    description="Real-time and historical market data",
)

# 3. get_polygon_data.py
from finbot.constants.path_constants import POLYGON_DATA_DIR
from finbot.config import settings_accessors

def get_polygon_data(ticker: str, force_update: bool = False) -> pd.DataFrame:
    """Fetch data from Polygon.io API."""
    api_key = settings_accessors.get_polygon_api_key()  # Add to settings_accessors
    cache_path = POLYGON_DATA_DIR / f"{ticker}.parquet"

    if cache_path.exists() and not force_update:
        return pd.read_parquet(cache_path)

    # Fetch from API
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/2020-01-01/2026-12-31?apiKey={api_key}"
    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame(data['results'])
    df['date'] = pd.to_datetime(df['t'], unit='ms')
    df.set_index('date', inplace=True)

    save_df(df, cache_path)
    return df

# 4. update_daily.py
def update_polygon_data() -> None:
    """Update Polygon.io data."""
    tickers = ["SPY", "QQQ", "IWM"]
    for ticker in tickers:
        get_polygon_data(ticker, force_update=True)
```

---

## Best Practices

### Data Collection

1. **Always use parquet format:**
   ```python
   # Good
   save_df(df, path_with_parquet_extension)

   # Bad (don't use pickle)
   df.to_pickle("data.pkl")
   ```

2. **Implement caching with force_update flag:**
   ```python
   def get_data(symbol: str, force_update: bool = False) -> pd.DataFrame:
       cache_path = DATA_DIR / f"{symbol}.parquet"

       if cache_path.exists() and not force_update:
           return pd.read_parquet(cache_path)

       # Fetch fresh data
       df = fetch_from_api(symbol)
       save_df(df, cache_path)
       return df
   ```

3. **Use retry logic for network operations:**
   ```python
   from finbot.utils.request_utils.request_with_retry import request_with_retry

   response = request_with_retry(
       url=url,
       max_retries=3,
       backoff_factor=2.0,
   )
   ```

4. **Log all data operations:**
   ```python
   from finbot.config import logger

   logger.info(f"Fetching {symbol} from API")
   logger.warning(f"Cache miss for {symbol}, fetching fresh data")
   logger.error(f"Failed to fetch {symbol}: {error}")
   ```

### Data Validation

1. **Validate immediately after loading:**
   ```python
   df = load_df(path)
   result = validate_dataframe(df, path, min_rows=1, check_duplicates=True)

   if not result.is_valid:
       raise ValueError(f"Invalid data in {path}: {result.errors}")
   ```

2. **Set appropriate min_rows thresholds:**
   ```python
   # Daily data: at least 1 trading year
   validate_dataframe(df, path, min_rows=252)

   # Weekly data: at least 1 year
   validate_dataframe(df, path, min_rows=52)

   # Monthly data: at least 1 year
   validate_dataframe(df, path, min_rows=12)
   ```

3. **Use expected_columns for schema validation:**
   ```python
   # OHLCV data
   validate_dataframe(
       df, path,
       expected_columns=["Open", "High", "Low", "Close", "Volume"]
   )

   # Economic data
   validate_dataframe(
       df, path,
       expected_columns=["value", "date"]
   )
   ```

### Monitoring

1. **Check status before long-running operations:**
   ```bash
   # Before running backtest
   finbot status --stale-only

   # If stale, update first
   finbot update
   ```

2. **Set up automated monitoring (cron/systemd):**
   ```bash
   # Daily update at 6 PM (after market close)
   0 18 * * 1-5 cd /path/to/finbot && finbot update

   # Daily status check at 7 PM
   0 19 * * * cd /path/to/finbot && finbot status --stale-only
   ```

3. **Monitor log files for errors:**
   ```bash
   # Check for errors in last 24 hours
   grep ERROR logs/finbot.log | tail -n 50

   # Watch logs in real-time
   tail -f logs/finbot.log
   ```

4. **Use verbose mode during troubleshooting:**
   ```bash
   # Normal operation
   finbot update

   # Troubleshooting
   finbot update --verbose
   ```

### Performance

1. **Batch updates when possible:**
   ```python
   # Good: batch fetch
   symbols = ["SPY", "QQQ", "IWM", "TLT"]
   get_history(symbols, force_update=True)

   # Bad: individual fetches
   for symbol in symbols:
       get_history(symbol, force_update=True)
   ```

2. **Use parquet compression:**
   ```python
   # Parquet automatically uses snappy compression
   df.to_parquet(path)  # Compressed by default
   ```

3. **Clean up old cache files periodically:**
   ```bash
   # Remove files older than 90 days
   find finbot/data/responses/ -name "*.zst" -mtime +90 -delete
   ```

---

## Maintenance Tasks

### Weekly

- [ ] Check data freshness: `finbot status`
- [ ] Review logs for errors: `grep ERROR logs/finbot.log | tail -n 100`
- [ ] Verify simulations are current: `ls -lth finbot/data/simulations/ | head`

### Monthly

- [ ] Check disk usage: `du -sh finbot/data/*`
- [ ] Review staleness thresholds (adjust if needed)
- [ ] Verify API keys are valid
- [ ] Clean up old response cache files

### Quarterly

- [ ] Audit data quality metrics
- [ ] Review and update data source registry
- [ ] Test disaster recovery (restore from backup)
- [ ] Update data collection utilities for API changes

---

## Reference

### Key Files

| File | Purpose |
|------|---------|
| `finbot/services/data_quality/data_source_registry.py` | Registry of tracked data sources |
| `finbot/services/data_quality/check_data_freshness.py` | Freshness monitoring engine |
| `finbot/services/data_quality/validate_dataframe.py` | DataFrame validation utilities |
| `finbot/cli/commands/status.py` | CLI status command implementation |
| `scripts/update_daily.py` | Daily data update pipeline |
| `finbot/constants/path_constants.py` | Data directory paths |

### Related Documentation

- [README.md](../../README.md): User-facing quick start
- [CLI Reference](../../docs_site/docs/user-guide/cli-reference.md): Full CLI documentation
- [Type Safety Guide](type-safety-improvement-guide.md): Type checking best practices
- [Pre-commit Hooks Guide](pre-commit-hooks-usage.md): Code quality automation

---

## Support

**Issues?** Check:
1. Recent logs: `tail -n 100 logs/finbot.log`
2. Network connectivity: `ping finance.yahoo.com`
3. API keys: `env | grep API_KEY`
4. Disk space: `df -h`

**Still stuck?** File an issue with:
- Output of `finbot status`
- Relevant log excerpts
- Steps to reproduce
