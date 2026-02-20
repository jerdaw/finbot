# Mypy Strict Module Tracker

Tracks package scopes where stricter function-signature rules are enforced.

## Enforced Scopes

The following module scopes are enforced via `pyproject.toml` overrides:

1. `finbot.core.*`
2. `finbot.services.execution.*`
3. `finbot.services.backtesting.*`
4. `finbot.libs.api_manager.*`
5. `finbot.libs.logger.*`
6. `finbot.services.data_quality.*`
7. `finbot.services.health_economics.*`
8. `finbot.services.optimization.*`
9. `finbot.utils.request_utils.*`
10. `finbot.utils.pandas_utils.*`
11. `finbot.utils.datetime_utils.*`
12. `finbot.utils.file_utils.*`
13. `finbot.utils.multithreading_utils.*`
14. `finbot.utils.finance_utils.*`
15. `finbot.utils.class_utils.*`
16. `finbot.utils.dict_utils.*`
17. `finbot.utils.function_utils.*`
18. `finbot.utils.json_utils.*`
19. `finbot.utils.validation_utils.*`
20. `finbot.utils.vectorization_utils.*`
21. `finbot.utils.plotting_utils.*`
22. `finbot.utils.data_science_utils.data_analysis.*`

Enforced flags:

- `disallow_untyped_defs = true`
- `disallow_incomplete_defs = true`

## Current Status (2026-02-20)

| Scope | Strict Status | Notes |
| --- | --- | --- |
| `finbot.core.*` | ✅ Enabled | Clean under strict function-signature rules |
| `finbot.services.execution.*` | ✅ Enabled | Clean under strict function-signature rules |
| `finbot.services.backtesting.*` | ✅ Enabled | Clean under strict function-signature rules |
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
| `finbot.utils.*` | ⏳ Pending | Legacy utility subpackages still pending staged rollout |

## Policy for New Code

For new modules in strict-enabled namespaces:

1. All function signatures must include argument and return types.
2. Partial signatures are not allowed.
3. New `# type: ignore` comments require justification and should be scoped narrowly.
4. Changes should keep `uv run mypy finbot/` clean.

For new modules outside strict-enabled namespaces:

1. Prefer complete signatures by default.
2. If untyped signatures are introduced for practical reasons, add a follow-up task to type them.

## Validation Commands

```bash
uv run mypy finbot/
uv run mypy \
  finbot/libs/api_manager \
  finbot/libs/logger \
  finbot/services/data_quality \
  finbot/services/health_economics \
  finbot/services/optimization \
  finbot/utils/request_utils \
  finbot/utils/pandas_utils \
  finbot/utils/datetime_utils \
  finbot/utils/file_utils \
  finbot/utils/multithreading_utils \
  finbot/utils/finance_utils \
  finbot/utils/class_utils \
  finbot/utils/dict_utils \
  finbot/utils/function_utils \
  finbot/utils/json_utils \
  finbot/utils/validation_utils \
  finbot/utils/vectorization_utils \
  finbot/utils/plotting_utils \
  finbot/utils/data_science_utils/data_analysis \
  --disallow-untyped-defs --disallow-incomplete-defs
```
