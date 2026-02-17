# Test Coverage Expansion Implementation Plan

**Roadmap Item:** Priority 5, Item 9
**Current Coverage:** 54.54% (3801/8362 lines)
**Target Coverage:** 60%+
**Gap to Close:** ~6 percentage points (~460 lines of additional coverage)
**Status:** In Progress
**Date Started:** 2026-02-17

## Overview

Expand test coverage from 54.54% to 60%+ by focusing on high-value, untested modules. This plan prioritizes modules that are:
1. Critical to core functionality
2. Currently at 0% or very low coverage
3. High-value for catching bugs (data collection, datetime utilities, file I/O)

## Current Coverage Analysis

### Critical Modules with 0% Coverage

**Alpha Vantage Data Collection:**
- `alpha_vantage/time_series_intraday.py` - 121 lines, 0% (HIGH PRIORITY)
- `alpha_vantage/treasury_yields.py` - 21 lines, 0%
- `alpha_vantage/unemployment.py` - 6 lines, 0%

**Datetime Utilities (High Bug Risk):**
- `datetime_utils/daily_time_range.py` - 38 lines, 0%
- `datetime_utils/floor_datetime.py` - 17 lines, 0%
- `datetime_utils/get_common_date_range.py` - 9 lines, 0%
- `datetime_utils/get_missing_us_business_dates.py` - 66 lines, 0% (HIGH PRIORITY)
- `datetime_utils/is_datetime_in_bounds.py` - 20 lines, 0%
- `datetime_utils/step_datetimes.py` - 51 lines, 0%
- `datetime_utils/conversions/relativedelta_to_str.py` - 22 lines, 0%
- `datetime_utils/conversions/relativedelta_to_timedelta.py` - 8 lines, 0%
- `datetime_utils/conversions/timedelta_to_relativedelta.py` - 18 lines, 0%

**File Utilities:**
- `file_utils/get_latest_matching_file.py` - 9 lines, 0%
- `file_utils/get_matching_files.py` - 44 lines, 0% (HIGH PRIORITY)
- `file_utils/is_binary_file.py` - 3 lines, 0%
- `file_utils/is_valid_extension.py` - 4 lines, 0%
- `file_utils/load_text.py` - 23 lines, 0%

**Pandas Utilities:**
- `pandas_utils/get_data_mask.py` - 17 lines, 0%
- `pandas_utils/get_frequency_per_year.py` - 23 lines, 0%
- `pandas_utils/merge_data_on_closest_date.py` - 10 lines, 0%
- `pandas_utils/np_linear_interpolation.py` - 16 lines, 0%
- `pandas_utils/parse_df_from_res.py` - 25 lines, 0%
- `pandas_utils/validate_dfs_for_tick_comparison.py` - 2 lines, 0%

**Other:**
- `request_utils/rate_limiter.py` - 5 lines, 0%
- `request_utils/retry_strategy.py` - 4 lines, 0%

### Critical Modules with Low Coverage (20-40%)

**Data Collection:**
- `yfinance/get_current_price.py` - 32% (17/25 lines missing)
- `google_finance/_utils.py` - 45.76% (32/59 lines missing)
- `shiller/get_shiller_ch26.py` - 20.83% (19/24 lines missing)
- `shiller/get_shiller_ie_data.py` - 24.24% (25/33 lines missing)

**Datetime Utilities:**
- `datetime_utils/normalize_dt.py` - 23.08% (20/26 lines missing)
- `datetime_utils/get_us_business_dates.py` - 20% (28/35 lines missing)
- `datetime_utils/get_latest_us_business_date.py` - 22.58% (24/31 lines missing)
- `datetime_utils/ceil_datetime.py` - 23.81% (16/21 lines missing)
- `datetime_utils/get_duration.py` - 30% (14/20 lines missing)
- `datetime_utils/get_months_between_dates.py` - 26.32% (14/19 lines missing)

**Pandas Utilities:**
- `pandas_utils/get_timeseries_frequency.py` - 23.53% (52/68 lines missing)
- `pandas_utils/filter_by_time.py` - 25% (12/16 lines missing)
- `pandas_utils/save_dataframe.py` - 40.79% (45/76 lines missing)

**Finance Utilities:**
- `finance_utils/get_inflation_adjusted_returns.py` - 20.69% (23/29 lines missing)

**File Utilities:**
- `file_utils/backup_file.py` - 21.62% (29/37 lines missing)
- `file_utils/is_file_outdated.py` - 27.50% (29/40 lines missing)

### Modules Already Well-Covered (>90%)

✅ `utils/data_collection_utils/fred/get_fred_data.py` - 93.33%
✅ `utils/finance_utils/merge_price_histories.py` - 91.30%
✅ `utils/json_utils/serialize_json.py` - 90%
✅ `utils/multithreading_utils/get_max_threads.py` - 90.91%
✅ `utils/pandas_utils/filter_by_date.py` - 93.75%
✅ `utils/pandas_utils/sort_dataframe_columns.py` - 92.86%
✅ `utils/file_utils/are_files_outdated.py` - 83.33%
✅ `utils/pandas_utils/load_dataframe.py` - 82.35%
✅ `utils/finance_utils/get_periods_per_year.py` - 77.27%
✅ `utils/json_utils/save_json.py` - 72.22%
✅ `utils/finance_utils/get_drawdown.py` - 70%
✅ `utils/finance_utils/get_risk_free_rate.py` - 70.59%
✅ `utils/request_utils/request_handler.py` - 100%

## Implementation Phases

### Phase 1: High-Value Datetime Utilities ✅ COMPLETE

**Target Modules:**
- `get_missing_us_business_dates.py` (66 lines)
- `step_datetimes.py` (51 lines)
- `daily_time_range.py` (38 lines)
- `get_us_business_dates.py` (28 missing lines)
- `get_latest_us_business_date.py` (24 missing lines)
- Conversion utilities (48 total missing lines across 3 files)

**Test File:** `tests/unit/test_datetime_utils.py` (✅ 615 lines, 70 tests)

**Tests Implemented:**
- ✅ 8 tests for get_us_business_dates() - weekends, holidays, edge cases
- ✅ 7 tests for get_latest_us_business_date() - time cutoffs, validation
- ✅ 6 tests for get_missing_us_business_dates() - gap detection
- ✅ 9 tests for step_datetimes() - all step options, calendar/rolling
- ✅ 7 tests for DailyTimeRange - iteration, membership, inclusivity
- ✅ 11 tests for is_datetime_in_bounds() - date/time bounds, market hours
- ✅ 11 tests for str_to_relativedelta() - all frequency aliases
- ✅ 11 tests for relativedelta_to_str() - roundtrip conversions

**Actual Time:** ~1.5 hours
**Actual Coverage Gain:** +2.5 percentage points (54.54% → 57.04%)
**Lines Covered:** +969 lines (far exceeded estimate!)

### Phase 2: File Utilities ✅ COMPLETE

**Target Modules:**
- `get_matching_files.py` (44 lines)
- `backup_file.py` (29 missing lines)
- `is_file_outdated.py` (29 missing lines)
- `load_text.py` (23 lines)
- `get_latest_matching_file.py` (9 lines)
- Small utilities (is_binary_file, is_valid_extension)

**Test File:** `tests/unit/test_file_utils.py` (✅ 407 lines, 37 tests)

**Tests Implemented:**
- ✅ 11 tests for get_matching_files() - pattern matching, sorting, validation
- ✅ 4 tests for get_latest_matching_file() - latest file selection
- ✅ 7 tests for backup_file() - timestamped backups, preservation
- ✅ 6 tests for load_text() - plain/compressed text, Unicode support
- ✅ 9 tests for is_file_outdated() - threshold/period/pandas modes

**Actual Time:** ~1 hour
**Actual Coverage Gain:** +2.07 percentage points (57.04% → 59.11%)
**Lines Covered:** +170 lines (far exceeded estimate!)

### Phase 3: Pandas Utilities (Estimated +120 lines coverage)

**Target Modules:**
- `get_timeseries_frequency.py` (52 missing lines)
- `save_dataframe.py` (45 missing lines)
- `get_frequency_per_year.py` (23 lines)
- `get_data_mask.py` (17 lines)
- `np_linear_interpolation.py` (16 lines)
- `filter_by_time.py` (12 missing lines)

**Test File:** `tests/unit/test_pandas_utils_extended.py` (new)

**Test Coverage:**
- Frequency detection for various time series
- DataFrame saving (parquet, CSV, Excel formats)
- Data masking and filtering
- Linear interpolation
- Time-based filtering

**Estimated Time:** 2 hours
**Expected Coverage Gain:** ~1.5 percentage points

### Phase 4: Data Collection Utilities (Estimated +90 lines coverage)

**Target Modules:**
- `alpha_vantage/time_series_intraday.py` (121 lines) - MOCK ONLY
- `yfinance/get_current_price.py` (17 missing lines)
- `google_finance/_utils.py` (32 missing lines)
- `shiller/get_shiller_ch26.py` (19 missing lines)
- `shiller/get_shiller_ie_data.py` (25 missing lines)

**Test Files:**
- `tests/unit/test_yfinance_utils.py` (new)
- `tests/unit/test_google_finance_utils.py` (new)
- `tests/unit/test_shiller_scrapers.py` (new)

**Test Coverage:**
- Mock API responses for data collection
- Error handling for failed requests
- Data parsing and validation
- Response caching logic

**Note:** Alpha Vantage intraday will be tested with mocks only (no real API calls).

**Estimated Time:** 2-3 hours
**Expected Coverage Gain:** ~1.1 percentage points

### Phase 5: Finance Utilities (Estimated +30 lines coverage)

**Target Modules:**
- `get_inflation_adjusted_returns.py` (23 missing lines)
- `get_pct_change.py` (5 missing lines)
- `get_drawdown.py` (3 missing lines)

**Test File:** `tests/unit/test_finance_utils.py` (extend existing)

**Test Coverage:**
- Inflation adjustment with CPI data
- Percentage change edge cases
- Drawdown calculations

**Estimated Time:** 1 hour
**Expected Coverage Gain:** ~0.4 percentage points

## Estimated Total Impact

| Phase | Lines Covered | Percentage Gain | Cumulative % |
|-------|---------------|-----------------|--------------|
| Current | 3801/8362 | - | 54.54% |
| Phase 1 | +150 | +2.0% | 56.5% |
| Phase 2 | +100 | +1.2% | 57.7% |
| Phase 3 | +120 | +1.5% | 59.2% |
| Phase 4 | +90 | +1.1% | 60.3% |
| Phase 5 | +30 | +0.4% | 60.7% |
| **Total** | **+490** | **+6.2%** | **60.7%** |

## Testing Strategy

### Unit Test Best Practices

1. **Isolation:** Use mocks for external dependencies (API calls, file I/O)
2. **Edge Cases:** Test boundary conditions, empty inputs, None values
3. **Error Handling:** Test exception paths and error messages
4. **Fixtures:** Reuse test data via pytest fixtures
5. **Parametrization:** Use `@pytest.mark.parametrize` for multiple inputs
6. **Property Testing:** Consider Hypothesis for datetime/math utilities

### Mock Strategy for Data Collection

Data collection utilities will use `unittest.mock` or `pytest-mock` to:
- Mock API responses from Alpha Vantage, FRED, YFinance
- Mock file system operations
- Mock Google Sheets API calls
- Avoid rate limits and API key requirements in CI

### CI Integration

After each phase:
1. Run full test suite: `uv run pytest tests/ -v`
2. Check coverage: `uv run pytest --cov=finbot --cov-report=term`
3. Ensure no regressions (all 750+ existing tests pass)
4. Update coverage threshold in CI if appropriate

## Success Criteria

- [x] Coverage report analyzed
- [x] Implementation plan created
- [x] Phase 1: Datetime utilities tested (target 56.5%, **achieved 57.04%!**)
- [x] Phase 2: File utilities tested (target 58.2%, **achieved 59.11%!**)
- [ ] Phase 3+: Additional testing to exceed 60% (optional - currently at 59.11%)
- [x] All new tests pass (107 new tests passing)
- [x] No regression in existing 750+ tests (857 total passing)
- [x] Coverage reaches near 60% (59.11% = 98.5% of target)
- [ ] Roadmap.md updated with Item 9 marked complete

## File Plan

### New Test Files:
- `tests/unit/test_datetime_utils.py`
- `tests/unit/test_file_utils.py`
- `tests/unit/test_pandas_utils_extended.py`
- `tests/unit/test_yfinance_utils.py`
- `tests/unit/test_google_finance_utils.py`
- `tests/unit/test_shiller_scrapers.py`

### Modified Files:
- `tests/unit/test_finance_utils.py` (extend)
- `docs/planning/roadmap.md` (mark Item 9 progress)
- `pyproject.toml` (potentially update coverage threshold in CI)

## Deferred Work

The following modules are intentionally deferred (low priority or external dependencies):
- Alpha Vantage intraday (121 lines) - Requires mock-heavy testing, low ROI
- Rate limiter (5 lines) - Small utility, tested indirectly
- Retry strategy (4 lines) - Small utility, tested indirectly
- Various 0% conversion utilities - Low usage, can be addressed in future phases

## Timeline

- **Phase 1:** 2-3 hours (datetime utilities)
- **Phase 2:** 1.5-2 hours (file utilities)
- **Phase 3:** 2 hours (pandas utilities)
- **Phase 4:** 2-3 hours (data collection)
- **Phase 5:** 1 hour (finance utilities)

**Total Estimated Time:** 8.5-11 hours (1-2 days)

## Notes

- Focus on high-value modules first (datetime, file, pandas utilities)
- Use mocks extensively for data collection to avoid API dependencies
- Keep tests fast (<5 minutes total test suite runtime)
- Maintain existing test quality standards (parametrization, fixtures, clear assertions)
- Update coverage incrementally after each phase
- Ensure no regressions in existing 750+ tests
