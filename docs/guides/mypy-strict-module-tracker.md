# Mypy Strict Module Tracker

Tracks package scopes where stricter function-signature rules are enforced.

## Enforced Scopes

The following module scopes are enforced via `pyproject.toml` overrides:

1. `finbot.adapters.*`
2. `finbot.cli.*`
3. `finbot.config.*`
4. `finbot.constants.*`
5. `finbot.core.*`
6. `finbot.dashboard.*`
7. `finbot.services.execution.*`
8. `finbot.services.backtesting.*`
9. `finbot.services.simulation.*`
10. `finbot.libs.api_manager.*`
11. `finbot.libs.logger.*`
12. `finbot.services.data_quality.*`
13. `finbot.services.health_economics.*`
14. `finbot.services.optimization.*`
15. `finbot.utils.request_utils.*`
16. `finbot.utils.pandas_utils.*`
17. `finbot.utils.datetime_utils.*`
18. `finbot.utils.file_utils.*`
19. `finbot.utils.multithreading_utils.*`
20. `finbot.utils.finance_utils.*`
21. `finbot.utils.class_utils.*`
22. `finbot.utils.dict_utils.*`
23. `finbot.utils.function_utils.*`
24. `finbot.utils.json_utils.*`
25. `finbot.utils.validation_utils.*`
26. `finbot.utils.vectorization_utils.*`
27. `finbot.utils.plotting_utils.*`
28. `finbot.utils.data_science_utils.data_analysis.*`
29. `finbot.utils.data_collection_utils.bls.*`
30. `finbot.utils.data_collection_utils.fred.*`
31. `finbot.utils.data_collection_utils.yfinance.*`
32. `finbot.utils.data_science_utils.data_transformation.*` (full scope: interpolators, scalers_normalizers, data_smoothing, rebase)
33. `finbot.utils.data_collection_utils.alpha_vantage.*`
34. `finbot.utils.data_collection_utils.google_finance.*`
35. `finbot.utils.data_collection_utils.pdr.*`
36. `finbot.utils.data_collection_utils.scrapers.*`
37. `finbot.utils.data_science_utils.data_cleaning.*`

Enforced flags (all 37 scopes):

- `disallow_untyped_defs = true`
- `disallow_incomplete_defs = true`

### Stricter flags (selective scopes, 2026-02-24)

| Scope | `warn_return_any` | `disallow_any_generics` |
| --- | --- | --- |
| `finbot.cli.*` | ✅ | ✅ |
| `finbot.services.data_quality.*` | ✅ | ✅ |
| `finbot.core.*` | ✅ | — |
| `finbot.constants.*` | ✅ | — |
| `finbot.services.execution.*` | ✅ | — |
| `finbot.services.health_economics.*` | ✅ | — |
| `finbot.adapters.*` | — | ✅ |

## Current Status (2026-02-24)

All `finbot/` namespaces are now under strict mypy enforcement (37 scopes total). Full coverage achieved.

| Scope | Strict Status | Notes |
| --- | --- | --- |
| `finbot.adapters.*` | ✅ Enabled | Nautilus adapter signatures clean (2026-02-24) |
| `finbot.cli.*` | ✅ Enabled | Click commands and validators clean (2026-02-24) |
| `finbot.config.*` | ✅ Enabled | Dynaconf settings/logging config typed (2026-02-24) |
| `finbot.constants.*` | ✅ Enabled | Host constants/tracked collections typed (2026-02-24) |
| `finbot.core.*` | ✅ Enabled | Clean under strict function-signature rules |
| `finbot.dashboard.*` | ✅ Enabled | Dashboard pages and utils typed (2026-02-24) |
| `finbot.services.execution.*` | ✅ Enabled | Clean under strict function-signature rules |
| `finbot.services.backtesting.*` | ✅ Enabled | Clean under strict function-signature rules |
| `finbot.services.simulation.*` | ✅ Enabled | Fund/MC/bond simulators typed (2026-02-24) |
| `finbot.libs.api_manager.*` | ✅ Enabled | Typed APIs/resource groups/manager helpers |
| `finbot.libs.logger.*` | ✅ Enabled | Typed formatters/audit/queue setup helpers |
| `finbot.services.data_quality.*` | ✅ Enabled | Validators and freshness checks pass strict signatures |
| `finbot.services.health_economics.*` | ✅ Enabled | QALY/CEA/optimization service signatures clean |
| `finbot.services.optimization.*` | ✅ Enabled | DCA optimizer helper signatures completed |
| `finbot.utils.request_utils.*` | ✅ Enabled | Request handler + retry config signatures hardened |
| `finbot.utils.pandas_utils.*` | ✅ Enabled | Typed loader/saver/frequency/sorting helper signatures |
| `finbot.utils.datetime_utils.*` | ✅ Enabled | Date-window helpers and frequency/missing-date utilities typed |
| `finbot.utils.file_utils.*` | ✅ Enabled | Matching/latest-file helper signatures fully typed |
| `finbot.utils.multithreading_utils.*` | ✅ Enabled | Thread-budget helper scope clean under strict signatures |
| `finbot.utils.finance_utils.*` | ✅ Enabled | Core finance helpers/trend/cycle utilities typed for strict signatures |
| `finbot.utils.class_utils.*` | ✅ Enabled | Singleton metaclass helpers clean under strict signatures |
| `finbot.utils.dict_utils.*` | ✅ Enabled | Deterministic hashing utilities clean under strict signatures |
| `finbot.utils.function_utils.*` | ✅ Enabled | Logging decorator now typed with ParamSpec/TypeVar signatures |
| `finbot.utils.json_utils.*` | ✅ Enabled | JSON load/save/serialize helpers clean under strict signatures |
| `finbot.utils.validation_utils.*` | ✅ Enabled | Validation helper utilities clean under strict signatures |
| `finbot.utils.vectorization_utils.*` | ✅ Enabled | Vectorization profiling helpers fully typed and import-safe |
| `finbot.utils.plotting_utils.*` | ✅ Enabled | Interactive plotter helpers clean under strict signatures |
| `finbot.utils.data_science_utils.data_analysis.*` | ✅ Enabled | Correlation/telltale analysis helpers typed for strict signatures |
| `finbot.utils.data_collection_utils.bls.*` | ✅ Enabled | BLS API helpers/signatures hardened for strict typed-def enforcement |
| `finbot.utils.data_collection_utils.fred.*` | ✅ Enabled | FRED collection helper scope passes strict function-signature checks |
| `finbot.utils.data_collection_utils.yfinance.*` | ✅ Enabled | YFinance request/load helper signatures hardened for strict typed-def enforcement |
| `finbot.utils.data_science_utils.data_transformation.*` | ✅ Enabled | Full scope: interpolators, scalers_normalizers, data_smoothing, rebase (2026-02-23) |
| `finbot.utils.data_collection_utils.alpha_vantage.*` | ✅ Enabled | Sentiment plotting/retrieval signatures typed (2026-02-23) |
| `finbot.utils.data_collection_utils.google_finance.*` | ✅ Enabled | Google Sheets API helpers typed (2026-02-23) |
| `finbot.utils.data_collection_utils.pdr.*` | ✅ Enabled | pandas_datareader base helpers typed (2026-02-23) |
| `finbot.utils.data_collection_utils.scrapers.*` | ✅ Enabled | MSCI/Shiller/multpl scraper signatures typed (2026-02-23) |
| `finbot.utils.data_science_utils.data_cleaning.*` | ✅ Enabled | Outlier/missing-data/imputation handlers typed (2026-02-23) |

## Policy for New Code

For new modules in strict-enabled namespaces:

1. All function signatures must include argument and return types.
2. Partial signatures are not allowed.
3. New `# type: ignore` comments require justification and should be scoped narrowly.
4. Changes should keep `uv run mypy finbot/` clean.

## Validation Commands

```bash
uv run mypy finbot/
```
