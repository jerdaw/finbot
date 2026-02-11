# Implementation Guide: Priority 0.4 - Consolidate Dual Config System

**Status:** Ready for implementation
**Complexity:** HIGH - Affects 14 files across the codebase
**Estimated Time:** 2-3 hours
**Risk:** Medium - Requires careful testing of all data collection utilities

---

## Overview

The project currently has two independent configuration systems running simultaneously:
- **Config** (BaseConfig singleton) - Used for API keys and MAX_THREADS
- **settings** (Dynaconf) - Used for environment-aware YAML configuration

This creates confusion and should be consolidated into a single Dynaconf-based system.

---

## Current State Analysis

### Config Usage Breakdown

**Property: `Config.MAX_THREADS`** (12 occurrences)
- `finbot/utils/pandas_utils/save_dataframes.py`
- `finbot/utils/pandas_utils/load_dataframes.py`
- `finbot/utils/pandas_utils/save_dataframe.py`
- `finbot/utils/data_collection_utils/pdr/_utils.py`
- `finbot/utils/data_collection_utils/yfinance/_yfinance_utils.py`
- `finbot/utils/data_collection_utils/scrapers/msci/_utils.py`
- `finbot/utils/data_collection_utils/scrapers/msci/get_msci_data.py`
- `finbot/utils/file_utils/are_files_outdated.py`

**Property: `Config.alpha_vantage_api_key`** (3 occurrences)
- `finbot/utils/data_collection_utils/alpha_vantage/_alpha_vantage_utils.py` (2 times)
- `constants/api_constants.py` (inside function - already fixed to be lazy)

**Property: `Config.us_bureau_of_labor_statistics_api_key`** (2 occurrences)
- `finbot/utils/data_collection_utils/bls/_bls_utils.py`
- `finbot/utils/data_collection_utils/bls/get_all_popular_bls_datas.py`

**Property: `Config.google_finance_service_account_credentials_path`** (1 occurrence)
- `finbot/utils/data_collection_utils/google_finance/_utils.py`

---

## Implementation Steps

### Step 1: Add MAX_THREADS to Dynaconf Settings

**File:** `config/settings.yaml`

Add this section:
```yaml
default:
  threading:
    max_threads: null  # Will be calculated at runtime
    reserved_threads: 1
```

**File:** `config/development.yaml`

Add:
```yaml
threading:
  reserved_threads: 1
```

**File:** `config/production.yaml`

Add:
```yaml
threading:
  reserved_threads: 2  # More conservative in production
```

### Step 2: Create a settings accessor module

**File:** `config/settings_accessors.py` (NEW FILE)

```python
"""
Settings accessors for commonly used config values.

This module provides convenient access to settings values with
computed defaults where appropriate.
"""
from __future__ import annotations

from config.api_key_manager import APIKeyManager
from config.project_config import settings
from finbot.utils.multithreading_utils.get_max_threads import get_max_threads

# Singleton APIKeyManager instance
_api_key_manager = APIKeyManager()


def get_max_threads() -> int:
    """
    Get the maximum number of threads for parallel operations.

    Returns from settings if configured, otherwise computes based on CPU count.
    """
    max_threads = settings.get("threading.max_threads")
    if max_threads is not None:
        return max_threads

    reserved_threads = settings.get("threading.reserved_threads", 1)
    return get_max_threads(reserved_threads=reserved_threads)


def get_alpha_vantage_api_key() -> str:
    """Get Alpha Vantage API key from environment."""
    return _api_key_manager.get_key("ALPHA_VANTAGE_API_KEY")


def get_nasdaq_data_link_api_key() -> str:
    """Get NASDAQ Data Link API key from environment."""
    return _api_key_manager.get_key("NASDAQ_DATA_LINK_API_KEY")


def get_us_bureau_of_labor_statistics_api_key() -> str:
    """Get US Bureau of Labor Statistics API key from environment."""
    return _api_key_manager.get_key("US_BUREAU_OF_LABOR_STATISTICS_API_KEY")


def get_google_finance_service_account_credentials_path() -> str:
    """Get Google Finance service account credentials path from environment."""
    return _api_key_manager.get_key("GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH")


# Backward compatibility: expose as module-level constants for easy migration
MAX_THREADS = get_max_threads()
```

### Step 3: Update config/__init__.py

**File:** `config/__init__.py`

Replace entire contents with:
```python
from __future__ import annotations

from config.project_config import settings
from libs.logger import logger
from config import settings_accessors

# Determine the running environment
permitted_envs = ["production", "development"]
if settings.current_env not in permitted_envs:
    raise ValueError(f"Environment variable 'ENV' must be one of {permitted_envs}.")

__all__ = ["settings", "logger", "settings_accessors"]
```

### Step 4: Update all Config.MAX_THREADS usages

For each file using `Config.MAX_THREADS`, change:

**BEFORE:**
```python
from config import Config

MAX_THREADS = Config.MAX_THREADS
```

**AFTER:**
```python
from config import settings_accessors

MAX_THREADS = settings_accessors.MAX_THREADS
```

Files to update (8 files):
1. `finbot/utils/pandas_utils/save_dataframes.py`
2. `finbot/utils/pandas_utils/load_dataframes.py`
3. `finbot/utils/pandas_utils/save_dataframe.py`
4. `finbot/utils/data_collection_utils/pdr/_utils.py`
5. `finbot/utils/data_collection_utils/yfinance/_yfinance_utils.py`
6. `finbot/utils/data_collection_utils/scrapers/msci/_utils.py`
7. `finbot/utils/data_collection_utils/scrapers/msci/get_msci_data.py`
8. `finbot/utils/file_utils/are_files_outdated.py`

### Step 5: Update API key usages

**File:** `finbot/utils/data_collection_utils/alpha_vantage/_alpha_vantage_utils.py`

**BEFORE:**
```python
from config import Config, logger

# Line with RapidAPI key
"X-RapidAPI-Key": Config.alpha_vantage_api_key,

# Line with API parameter
req_params["apikey"] = str(Config.alpha_vantage_api_key)
```

**AFTER:**
```python
from config import logger, settings_accessors

# Line with RapidAPI key
"X-RapidAPI-Key": settings_accessors.get_alpha_vantage_api_key(),

# Line with API parameter
req_params["apikey"] = str(settings_accessors.get_alpha_vantage_api_key())
```

**File:** `finbot/utils/data_collection_utils/bls/_bls_utils.py`

**BEFORE:**
```python
from config import Config

"registrationkey": Config.us_bureau_of_labor_statistics_api_key,
```

**AFTER:**
```python
from config import settings_accessors

"registrationkey": settings_accessors.get_us_bureau_of_labor_statistics_api_key(),
```

**File:** `finbot/utils/data_collection_utils/bls/get_all_popular_bls_datas.py`

**BEFORE:**
```python
from config import Config

payload = json.dumps({"registrationkey": Config.us_bureau_of_labor_statistics_api_key})
```

**AFTER:**
```python
from config import settings_accessors

payload = json.dumps({"registrationkey": settings_accessors.get_us_bureau_of_labor_statistics_api_key()})
```

**File:** `finbot/utils/data_collection_utils/google_finance/_utils.py`

**BEFORE:**
```python
from config import Config

SERVICE_ACCOUNT_FILE = Config.google_finance_service_account_credentials_path
```

**AFTER:**
```python
from config import settings_accessors

SERVICE_ACCOUNT_FILE = settings_accessors.get_google_finance_service_account_credentials_path()
```

**File:** `constants/api_constants.py`

**BEFORE:**
```python
def get_alpha_vantage_rapi_headers() -> dict[str, str]:
    from config import Config

    return {
        "X-RapidAPI-Key": Config.alpha_vantage_api_key,
        ...
    }
```

**AFTER:**
```python
def get_alpha_vantage_rapi_headers() -> dict[str, str]:
    from config import settings_accessors

    return {
        "X-RapidAPI-Key": settings_accessors.get_alpha_vantage_api_key(),
        ...
    }
```

### Step 6: Delete obsolete config files

Delete these files:
- `config/base_config.py`
- `config/development_config.py`
- `config/production_config.py`
- `config/staging_config.py`
- `config/testing_config.py`

### Step 7: Update imports that reference logger and Config together

Some files import both. Update them:

**Files with `from config import Config, logger`:**
- `finbot/utils/pandas_utils/save_dataframe.py`
- `finbot/utils/data_collection_utils/alpha_vantage/sentiment.py`
- `finbot/utils/data_collection_utils/alpha_vantage/_alpha_vantage_utils.py`
- `finbot/utils/data_collection_utils/pdr/_utils.py`
- `finbot/utils/data_collection_utils/yfinance/_yfinance_utils.py`
- `finbot/utils/data_collection_utils/scrapers/msci/_utils.py`

Change to:
```python
from config import logger, settings_accessors
```

---

## Testing Checklist

After implementation, test these scenarios:

### Unit Tests
- [ ] Import `config` module without errors
- [ ] Import `config.settings_accessors` without errors
- [ ] Verify `settings_accessors.MAX_THREADS` returns an integer
- [ ] Verify API key accessors raise `OSError` when env vars not set
- [ ] Verify API key accessors return correct values when env vars are set

### Integration Tests
- [ ] Run `scripts/update_daily.py` (tests data collection utilities)
- [ ] Test pandas save/load operations (tests MAX_THREADS in pandas_utils)
- [ ] Test any backtest that uses threading
- [ ] Verify logger still works after config changes

### Smoke Tests
```bash
# Test imports
python -c "from config import settings, logger, settings_accessors; print('✓ Imports work')"

# Test MAX_THREADS
python -c "from config import settings_accessors; print(f'MAX_THREADS: {settings_accessors.MAX_THREADS}')"

# Test API key accessor (will fail if env var not set - that's correct)
python -c "from config import settings_accessors; settings_accessors.get_alpha_vantage_api_key()"
```

---

## Rollback Plan

If something goes wrong:

1. **Revert commits:** `git revert <commit-hash>`
2. **Manual rollback:** Restore these files from git history:
   - `config/__init__.py`
   - `config/base_config.py`
   - All 14 files that were modified
3. **Emergency patch:** Create `config/settings_accessors.py` that imports from `Config`:
   ```python
   from config.base_config import BaseConfig
   _config = BaseConfig()
   MAX_THREADS = _config.MAX_THREADS
   get_alpha_vantage_api_key = lambda: _config.alpha_vantage_api_key
   # etc.
   ```

---

## Benefits

After this consolidation:
- ✅ Single source of truth for configuration
- ✅ No more circular dependency between config/ and libs/
- ✅ Consistent configuration API across the codebase
- ✅ Easier to add new configuration values
- ✅ Better separation of concerns (API keys handled by one manager)
- ✅ Settings can be overridden per environment in YAML files

---

## Estimated Effort

- Creating `settings_accessors.py`: 20 minutes
- Updating 14 files: 30 minutes
- Adding YAML config: 10 minutes
- Testing: 30 minutes
- Documentation updates: 10 minutes

**Total: ~2 hours**

---

## Notes

- The `settings_accessors` module provides a clean migration path
- API key accessors remain lazy (only loaded when called)
- MAX_THREADS is computed once at module load time (acceptable since it won't change)
- If needed, MAX_THREADS can be made a function for dynamic recomputation
- The APIKeyManager singleton is preserved for consistency
- All changes are backward-compatible at the import level
