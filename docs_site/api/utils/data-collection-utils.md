# Data Collection Utilities

This page is a public wrapper for Finbot's data-collection utility surface.

## Typical Topics

- Yahoo Finance history collection
- FRED, BLS, and Alpha Vantage fetch helpers
- Google Finance and other external-source adapters
- request/retry patterns for data retrieval

## Key Reference Point

### FRED

Use the repository data-collection helpers for FRED-backed market and macro
data retrieval.

## Contributor Examples

These snippets are intended for wrapper smoke checks and contributor
orientation. Prefer cached reads for routine development, and use
`force_update=True` only when intentionally refreshing provider data.

### Yahoo Finance History

```python
import datetime as dt

from finbot.utils.data_collection_utils.yfinance.get_history import get_history

prices = get_history(
    "SPY",
    start_date=dt.date(2024, 1, 1),
    end_date=dt.date(2024, 12, 31),
    check_update=True,
)
print(prices.tail())
```

### FRED Series

```python
import datetime as dt

from finbot.utils.data_collection_utils.fred.get_fred_data import get_fred_data

rates = get_fred_data(
    ["FEDFUNDS", "DGS10"],
    start_date=dt.date(2020, 1, 1),
    check_update=True,
)
print(rates.tail())
```

### Alpha Vantage Quote

Set `ALPHA_VANTAGE_API_KEY` in the environment before running keyed Alpha
Vantage helpers.

```python
from finbot.utils.data_collection_utils.alpha_vantage.global_quote import get_global_quote

quote = get_global_quote("SPY")
print(quote[["symbol", "price", "volume"]])
```

### BLS Series

Set `US_BUREAU_OF_LABOR_STATISTICS_API_KEY` when using authenticated BLS
requests. The wrapper also uses cached parquet files when available.

```python
import datetime as dt

from finbot.utils.data_collection_utils.bls.get_bls_data import get_bls_data

cpi = get_bls_data(
    "CUUR0000SA0",
    start_date=dt.date(2020, 1, 1),
    check_update=True,
)
print(cpi.tail())
```

## See Also

- [Utility source tree](https://github.com/jerdaw/finbot/tree/main/finbot/utils)
- [Data Quality Guide](../../user-guide/data-quality-guide.md)
