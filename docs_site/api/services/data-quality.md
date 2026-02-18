# Data Quality

The data quality module provides tools for monitoring data freshness, validating DataFrames, and tracking data source health.

## Overview

The data quality module supports:

- **Data Freshness Monitoring**: Track staleness of cached data sources
- **DataFrame Validation**: Lightweight schema and quality checks
- **Data Source Registry**: Centralized tracking of 7 data sources
- **CLI Integration**: `finbot status` command for quick health checks

## Modules

### Data Source Registry

Registry of data sources with staleness thresholds:

::: finbot.services.data_quality.data_source_registry
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### Data Freshness Checking

Scans directories and reports freshness status:

::: finbot.services.data_quality.check_data_freshness
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### DataFrame Validation

Validates DataFrame structure and content:

::: finbot.services.data_quality.validate_dataframe
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Quick Start

### Check Data Freshness

```python
from finbot.services.data_quality.check_data_freshness import check_all_data_sources

# Check all data sources
status = check_all_data_sources()

for source_name, source_status in status.items():
    print(f"{source_name}: {source_status['status']}")
    if source_status['status'] == 'STALE':
        print(f"  Age: {source_status['age_days']:.1f} days")
        print(f"  Threshold: {source_status['threshold_days']} days")
```

### Validate DataFrame

```python
from finbot.services.data_quality.validate_dataframe import validate_dataframe
import pandas as pd

# Load data
df = pd.read_parquet('price_data.parquet')

# Validate
errors = validate_dataframe(
    df,
    required_columns=['Open', 'High', 'Low', 'Close', 'Volume'],
    allow_duplicates=False,
    allow_nulls=False
)

if errors:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("Data is valid")
```

### CLI Usage

```bash
# Check data freshness from command line
finbot status

# Example output:
# Data Source Status
# ==================
# YFinance: ✓ FRESH (0.2 days old, threshold: 1 day)
# FRED: ✓ FRESH (0.5 days old, threshold: 7 days)
# Google Finance: ⚠ STALE (8.3 days old, threshold: 7 days)
# ...
```

## Data Source Registry

The registry tracks 7 data sources:

| Source | Directory | Threshold (days) | Update Frequency |
|--------|-----------|------------------|------------------|
| **YFinance** | `yfinance_data/` | 1 | Daily |
| **FRED** | `fred_data/` | 7 | Weekly |
| **Google Finance** | `google_finance_data/` | 7 | Weekly |
| **Alpha Vantage** | `alpha_vantage_data/` | 7 | Weekly |
| **BLS** | `bls_data/` | 30 | Monthly |
| **Shiller** | `shiller_data/` | 90 | Quarterly |
| **Simulations** | `simulations/` | 1 | Daily |

## Freshness Status

Data sources are classified as:

- **FRESH**: Age < threshold (✓ green)
- **STALE**: Age ≥ threshold (⚠ yellow)
- **MISSING**: No data files found (✗ red)

## Validation Checks

The DataFrame validator performs:

1. **Empty check**: Ensures DataFrame is not empty
2. **Schema check**: Validates required columns exist
3. **Duplicate check**: Checks for duplicate rows (optional)
4. **Null check**: Checks for missing values (optional)

## Advanced Usage

### Custom Data Source

```python
from finbot.services.data_quality.data_source_registry import DataSource, DATA_SOURCES

# Add custom data source
custom_source = DataSource(
    name='Custom API',
    directory='custom_data',
    staleness_threshold_days=3
)

DATA_SOURCES['custom'] = custom_source
```

### Detailed Freshness Report

```python
from finbot.services.data_quality.check_data_freshness import check_data_source_freshness
from finbot.services.data_quality.data_source_registry import DATA_SOURCES

# Check specific source
source = DATA_SOURCES['yfinance']
status = check_data_source_freshness(source)

print(f"Source: {status['name']}")
print(f"Status: {status['status']}")
print(f"Most recent file: {status['most_recent_file']}")
print(f"Age (days): {status['age_days']:.2f}")
print(f"Threshold (days): {status['threshold_days']}")
print(f"File count: {status['file_count']}")
```

### Custom Validation Rules

```python
from finbot.services.data_quality.validate_dataframe import validate_dataframe

def validate_price_data(df):
    """Validate price data with custom rules."""
    errors = []

    # Standard validation
    errors.extend(validate_dataframe(
        df,
        required_columns=['Open', 'High', 'Low', 'Close', 'Volume']
    ))

    # Custom rules
    if (df['High'] < df['Low']).any():
        errors.append("High prices must be >= Low prices")

    if (df['Close'] < 0).any():
        errors.append("Prices must be non-negative")

    if not df.index.is_monotonic_increasing:
        errors.append("Index must be sorted chronologically")

    return errors
```

## Integration with Update Pipeline

The data quality module integrates with the daily update pipeline:

```python
# scripts/update_daily.py
from finbot.services.data_quality.check_data_freshness import check_all_data_sources

# Check data freshness before running simulations
status = check_all_data_sources()
stale_sources = [name for name, s in status.items() if s['status'] == 'STALE']

if stale_sources:
    logger.warning(f"Stale data sources detected: {stale_sources}")
    # Proceed anyway or trigger updates
```

## Observability Features

### Logging

All data quality checks are logged:

```python
from finbot.config import logger

logger.info("Running data freshness check")
status = check_all_data_sources()
logger.info(f"Checked {len(status)} data sources")
```

### Metrics

Data quality metrics available:

- **Age (days)**: Time since most recent update
- **File count**: Number of files in data directory
- **Status**: FRESH, STALE, or MISSING
- **Threshold compliance**: Age < threshold

## Best Practices

1. **Run daily**: Check data freshness as part of daily pipeline
2. **Set appropriate thresholds**: Balance freshness vs. API rate limits
3. **Monitor trends**: Track staleness over time
4. **Validate early**: Check data quality immediately after collection
5. **Log failures**: Record validation errors for debugging

## Limitations

- **File-based only**: Checks file modification times, not content
- **No content validation**: Doesn't verify data correctness, only presence
- **Simple schema checks**: Basic column presence, not deep schema validation
- **No automatic remediation**: Detects issues but doesn't fix them

## Future Enhancements

Potential improvements:

- Content-based freshness (check latest date in data, not file modification time)
- Deep schema validation with Pandera or Great Expectations
- Automatic data refresh triggers
- Alerting integration (email, Slack)
- Data quality dashboards

## See Also

- [Data Quality & Monitoring Guide](../../user-guide/data-quality-guide.md) - Operations documentation
- [CLI Reference](../../user-guide/cli-reference.md#status) - `finbot status` command
