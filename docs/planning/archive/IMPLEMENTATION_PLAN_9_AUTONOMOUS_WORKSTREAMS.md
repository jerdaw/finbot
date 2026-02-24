# Implementation Plan 9: All 5 Autonomous Workstreams

**Status:** COMPLETED (2026-02-24)
**Scope:** Unit tests, mypy strict enforcement, mocked data-collection tests, docstring coverage, stricter mypy flags

## Context

Finbot's Priorities 0-7 were essentially complete. Five categories of autonomous technical work remained: (1) unit tests for 0%-coverage modules, (2) mypy strict enforcement on remaining namespaces, (3) mocked tests for data collection utilities, (4) docstring coverage toward 80%, and (5) stricter mypy flags. This plan executed all five as 18 sequential phases.

**Baseline:** ~1200 tests, 67.3% coverage, 65.9% docstrings, 31 mypy strict scopes.

## Results

| Metric | Before | After |
|--------|--------|-------|
| Tests | ~1200 | 1398 (+198) |
| Docstrings | 65.9% | 75.6% |
| mypy strict scopes | 31 | 37 (all namespaces) |
| Stricter flags | 0 scopes | 7 scopes with `warn_return_any` / `disallow_any_generics` |
| Interrogate threshold | 55% | 73% |

## Phase Summary

| Phase | Workstream | Deliverable |
|-------|-----------|-------------|
| 1 | WS1 Tests | 63 tests — datetime utils (ceil, floor, duration, months, conversions, constants) |
| 2 | WS1 Tests | 23 tests — is_binary, data_mask, frequency, merge_closest |
| 3 | WS1 Tests | 36 tests — adj_finders, gen_rebal_proportions, snapshot_utils, backtrader indicators |
| 4 | WS1 Tests | 31 tests — datetime constants, tracked collections (MSCI, FRED, funds, tracker) |
| 5 | WS2 mypy | `finbot.adapters.*` strict — 0 fixes needed |
| 6 | WS2 mypy | `finbot.config.*` strict — 4 return type fixes |
| 7 | WS2 mypy | `finbot.constants.*` strict — 9 return type fixes |
| 8 | WS3 Tests | 18 mocked tests — Alpha Vantage base utils |
| 9 | WS3 Tests | 19 mocked tests — YFinance base utils |
| 10 | WS3 Tests | 13 mocked tests — Alpha Vantage wrappers |
| 11 | WS2 mypy | `finbot.services.simulation.*` strict — 21 fixes |
| 12 | WS4 Docs | Docstrings for nautilus adapter (~37 methods) |
| 13 | WS4 Docs | Docstrings for api_manager + logger (~60 items) |
| 14 | WS4 Docs | Docstrings for strategies, analyzers, brokers (~55 items) |
| 15 | WS2 mypy | `finbot.cli.*` strict — 0 fixes needed |
| 16 | WS2 mypy | `finbot.dashboard.*` strict — 2 fixes |
| 17 | Tracker | Updated mypy tracker (31 to 37 scopes), raised interrogate threshold (55 to 73%) |
| 18 | WS5 mypy | Enabled `warn_return_any` on 6 scopes, `disallow_any_generics` on 3 scopes |

## New Test Files Created

- `tests/unit/test_datetime_utils_extended.py` (63 tests)
- `tests/unit/test_adj_finders.py` (9 tests)
- `tests/unit/test_gen_rebal_proportions.py` (8 tests)
- `tests/unit/test_snapshot_utils.py` (8 tests)
- `tests/unit/test_backtrader_indicators.py` (11 tests)
- `tests/unit/test_tracked_collections.py` (26 tests)
- `tests/unit/test_alpha_vantage_utils.py` (18 tests)
- `tests/unit/test_yfinance_utils.py` (19 tests)
- `tests/unit/test_alpha_vantage_wrappers.py` (13 tests)

## Existing Test Files Modified

- `tests/unit/test_file_utils.py` — added TestIsBinary (6 tests)
- `tests/unit/test_pandas_utils.py` — added TestGetDataMask (6), TestGetFrequencyPerInterval (6), TestMergeDataOnClosestDate (5)

## Source Files Modified (Type Annotations)

- `finbot/config/project_config.py` — return type annotations
- `finbot/config/logging_config.py` — return type annotation
- `finbot/constants/host_constants.py` — return type annotations
- `finbot/constants/tracked_collections/_utils.py` — return type annotation
- `finbot/constants/tracked_collections/tracked_funds.py` — return type annotations
- `finbot/constants/tracked_collections/tracked_fred.py` — return type annotations
- `finbot/services/simulation/sim_specific_funds.py` — return type annotations on all 17 functions
- `finbot/services/simulation/monte_carlo/sim_types.py` — return type annotation
- `finbot/services/simulation/monte_carlo/visualization.py` — return type annotations
- `finbot/dashboard/utils/experiment_comparison.py` — highlight_row type annotation
- `finbot/dashboard/pages/7_experiments.py` — _get_registry return type

## Verification

```
uv run pytest tests/ -v                    # 1398 passed
uv run mypy finbot/                        # 0 errors, 378 files
uv run ruff check .                        # All checks passed
uv run ruff format --check .               # 509 files already formatted
uv run interrogate finbot/ -v              # 75.6% (threshold 73.0%)
```
