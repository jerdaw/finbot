# Archived `bb` and `backbetter` Incorporation Audit

**Status:** Audit complete; no production code changes made
**Created:** 2026-04-27
**Current repo:** `jerdaw/finbot`
**Archived repos audited:** `jerdaw/bb`, `jerdaw/backbetter`
**Audit workspace:** `/tmp/finbot-archive-audit`

## Summary

`jerdaw/bb` is best treated as a direct historical ancestor of Finbot. Its useful
systems have mostly already been migrated and modernized under the `finbot/`
namespace: data collection, API management, logging, config, data science
utilities, date/file/pandas helpers, tracked collections, and early Backtrader
references.

`jerdaw/backbetter` is not a functional backtesting engine. It is a small
archived package scaffold with a version constant, Sphinx stubs, and an older
dependency manifest. There is no algorithmic backtesting functionality to port.

The main incorporation opportunities are documentation and validation follow-up,
not wholesale code import.

## Audit Method

- Cloned both archived repos into `/tmp/finbot-archive-audit`.
- Collected Git metadata, tracked file counts, manifests, docs, tests, scripts,
  notebooks, and top-level package structure.
- Compared `bb` paths to likely Finbot destinations:
  - `app/utils/` -> `finbot/utils/`
  - `config/` -> `finbot/config/`
  - `constants/` -> `finbot/constants/`
  - `libs/` -> `finbot/libs/`
  - `app/services/backtesting/` -> `finbot/services/backtesting/`
  - `docs/` and `assets/docs/` -> `docs/`
  - `scripts/` -> `scripts/`
- Compared public Python symbol names for mapped files. Only old internal names
  or casing variants were missing from Finbot.
- Reviewed missing docs, scripts, notebooks, tests, static assets, and dependency
  manifests for reusable concepts.
- Performed a second full-file reconciliation of all 290 tracked `bb` files,
  including package stubs, project tooling, old templates, static data, tests,
  notebooks, exception classes, singleton helpers, and tracked collection CSVs.

## Full `bb` Coverage Check

Every tracked file in `bb` was assigned to an audit bucket. The second pass did
not identify additional production functionality that should be ported.

| Bucket | Files | Decision |
| :--- | ---: | :--- |
| General utilities | 84 | Already present under `finbot/utils/`, including class/singleton helpers. |
| Data collection | 44 | Already present under `finbot/utils/data_collection_utils/`, expanded in current Finbot. |
| Data science utilities | 42 | Already present under `finbot/utils/data_science_utils/`; documentation/test follow-up only. |
| Constants | 23 | Already present; tracked collection CSVs checked byte-for-byte where applicable. |
| Config | 15 | Current Dynaconf/lazy-key config supersedes the old modules. |
| Libs | 15 | API manager and logger already present and expanded. |
| Notebooks | 13 | Historical examples only; no runtime incorporation recommended. |
| Package stubs | 12 | Empty or namespace-only files; no action. |
| Scripts | 11 | Mostly placeholders or Poetry-era workflow helpers; reject. |
| Tests | 8 | Logging intent noted as a future test idea; placeholders rejected. |
| Docs | 7 | Missing-data docs are useful; other docs are obsolete or optional research references. |
| Project tooling | 5 | Current `uv`, Ruff, pre-commit, and docs supersede old Poetry/Pylint setup. |
| Web shell/templates | 3 | Obsolete Flask-era shell; current Streamlit/Next.js/FastAPI supersedes it. |
| Exceptions | 1 | Core file/save/load/parse/data-type exceptions already exist; unused request/rate-limit classes rejected. |
| Plotting utility | 1 | Existing plotting/chart surfaces supersede the old interactive helper. |
| Static data artifact | 1 | Static `gspc.csv` rejected; current parquet/fetcher data is authoritative. |

Symbol-level differences after path mapping were limited to:

- `RequestError`, `RateLimitError`, `RateLimitReachedError`, and
  `RateLimitExceededError` from `bb/app/exceptions.py`. These were unused in
  `bb`; current Finbot uses request/HTTP exceptions and typed rate-limit config
  instead of these archive-only classes.
- `Standardize_types`, which is the old typo-cased form of current
  `standardize_types`.
- `_load_env_key`, replaced by lazy API key loading plus `.env` fallback in
  `finbot/config/api_key_manager.py`.
- `_resolve_dir` and `_check_dir`, replaced by current `_process_dir` behavior
  that creates and resolves required directories.

## Repo Metadata

| Repo | Archived | Default branch | Last audited commit | Last commit date | Primary language | Tracked files | Finding |
| :--- | :--- | :--- | :--- | :--- | :--- | ---: | :--- |
| `jerdaw/bb` | Yes | `main` | `5b69a2e49e3087a95e795ad3464657f2867750c8` | 2024-02-05 | Jupyter Notebook / Python | 290 | Historical Finbot ancestor; mostly absorbed. |
| `jerdaw/backbetter` | Yes | `main` | `1a5446544bd55b758f222696d13bd10d10ac23b4` | 2022-04-01 | Python | 14 | Package scaffold only; no reusable engine code. |

`bb` tracked surface:

| Type | Count |
| :--- | ---: |
| Python files | 249 |
| Notebooks | 10 |
| Docs/assets docs | 7 |
| Scripts | 11 |

`backbetter` tracked surface:

| Type | Count |
| :--- | ---: |
| Python files | 4 |
| Notebooks | 0 |
| Docs | 2 |

## Crosswalk

| Archived source | Current Finbot equivalent | Status | Incorporation decision |
| :--- | :--- | :--- | :--- |
| `bb/app/utils/data_collection_utils/alpha_vantage/` | `finbot/utils/data_collection_utils/alpha_vantage/` | Already in Finbot, modernized | Do not port; use as historical reference only. |
| `bb/app/utils/data_collection_utils/fred/` | `finbot/utils/data_collection_utils/fred/` | Already in Finbot | Do not port. |
| `bb/app/utils/data_collection_utils/bls/` | `finbot/utils/data_collection_utils/bls/` | Already in Finbot | Do not port. |
| `bb/app/utils/data_collection_utils/google_finance/` | `finbot/utils/data_collection_utils/google_finance/` | Already in Finbot | Do not port. |
| `bb/app/utils/data_collection_utils/scrapers/shiller/` | `finbot/utils/data_collection_utils/scrapers/shiller/` | Already in Finbot | Do not port. |
| `bb/app/utils/data_collection_utils/scrapers/msci/` | `finbot/utils/data_collection_utils/scrapers/msci/` | Already in Finbot | Do not port. |
| `bb/app/utils/data_collection_utils/scrapers/multpl.py` | Current data collection and Shiller/market data surfaces | Not retained as standalone module | Reject unless a future data-source backlog explicitly reintroduces Multpl. |
| `bb/app/utils/data_collection_utils/pdr/` | `finbot/utils/data_collection_utils/pdr/` | Already in Finbot | Do not port. |
| `bb/app/utils/data_collection_utils/yfinance/` | `finbot/utils/data_collection_utils/yfinance/` plus real-time providers | Already in Finbot, expanded | Do not port. |
| `bb/app/exceptions.py` | `finbot/exceptions.py` | Mostly already in Finbot | Do not port unused request/rate-limit exception classes. |
| `bb/app/utils/class_utils/singleton_metas.py` | `finbot/utils/class_utils/singleton_metas.py` | Already in Finbot, expanded docs | Do not port. |
| `bb/app/utils/data_science_utils/data_cleaning/missing_data_handlers/` | `finbot/utils/data_science_utils/data_cleaning/missing_data_handlers/`, `finbot/core/contracts/missing_data.py`, `tests/unit/test_missing_data_policies.py` | Already in Finbot, expanded | Consider docs-only P0 below. |
| `bb/app/utils/data_science_utils/data_cleaning/outlier_handlers/` | `finbot/utils/data_science_utils/data_cleaning/outlier_handlers/` | Already in Finbot | No direct port; consider future user-facing docs if this surface becomes public. |
| `bb/app/utils/data_science_utils/data_transformation/scalers_normalizers/` | `finbot/utils/data_science_utils/data_transformation/scalers_normalizers/` | Already in Finbot | Consider docs-only P2 below. |
| `bb/app/utils/datetime_utils/`, `dict_utils/`, `file_utils/`, `json_utils/`, `pandas_utils/` | `finbot/utils/...` | Already in Finbot | No port. |
| `bb/app/utils/finance_utils/` | `finbot/utils/finance_utils/` | Already in Finbot, expanded | No port. |
| `bb/app/utils/plotting_utils/interactive/interactive_plotter.py` | Streamlit dashboard, Next.js charts, Plotly/Recharts wrappers | Superseded | Reject. |
| `bb/app/utils/request_utils/` | `finbot/utils/request_utils/` | Already in Finbot, expanded with rate limiting/retry strategy | No port. |
| `bb/config/` | `finbot/config/` | Partially retained; current Dynaconf config supersedes older split config modules | Reject old config modules. |
| `bb/constants/` | `finbot/constants/` | Already in Finbot, expanded | No port. |
| `bb/constants/tracked_collections/*.csv` | `finbot/constants/tracked_collections/*.csv` | Byte-identical for CSV files checked | No port. |
| `bb/libs/api_manager/` | `finbot/libs/api_manager/` | Already in Finbot | No port. |
| `bb/libs/logger/` | `finbot/libs/logger/`, `finbot/config/logging_config.py` | Already in Finbot, expanded | P0 test idea only. |
| `bb/app/services/backtesting/` | `finbot/services/backtesting/` | Empty package stub in archive; Finbot has full engine | Reject. |
| `bb/app/services/investing/`, `bb/app/models/` | None needed | Empty package stubs | Reject. |
| `bb/app/templates/*.html`, `bb/main.py` | Streamlit dashboard and Next.js/FastAPI web app | Obsolete Flask-era placeholders | Reject. |
| `bb/docs/missing_data_handler.md` | Missing as standalone docs; behavior exists in code/tests | Useful reference | P0 docs candidate. |
| `bb/docs/scaler_classification.md` | No standalone equivalent | Reference-only | P2 docs candidate if scaler docs are expanded. |
| `bb/docs/python_data_science_libs.md` | Current dependency decisions in ADRs and guides | Mostly obsolete | Reject, except as historical context. |
| `bb/assets/docs/development_dependencies.md` | `docs/guides/pre-commit-hooks-usage.md`, `docs/guides/docker-security-scanning.md`, `pyproject.toml` | Obsolete Poetry-era summary | Reject. |
| `bb/docs/backtrader/*.pdf` | Current ADRs, user guides, and blog docs | External reference PDFs only | P2 research archive candidate if licensing/storage is acceptable. |
| `bb/notebooks/app/apis/*.ipynb` | Existing data collectors and tests | Useful as historical examples only | P2 reference candidate; do not make runtime notebooks. |
| `bb/notebooks/app/utils/preprocessing_utils/data_transformations/*.ipynb` | Current scaler/normalizer modules | Useful tutorial material only | P2 reference candidate. |
| `bb/assets/gspc.csv` | `finbot/data/yfinance_data/history/^GSPC_history_1d.parquet` | Static duplicate data through 2023-12-15 | Reject as data artifact; maybe use as offline fixture only if a test needs frozen data. |
| `bb/scripts/*.py`, `bb/scripts/*.sh` | Current `scripts/`, `uv`, Makefile, docs | Mostly placeholders or Poetry-era helpers | Reject, except narrow test-structure idea below. |
| `backbetter/backbetter/__init__.py` | None | Version constant only | Reject. |
| `backbetter/docs/`, `README.rst` | None | Empty Sphinx stubs | Reject. |
| `backbetter/pyproject.toml` | Finbot `pyproject.toml`, ADR-001 | Old NumPy/numba/polars experiment | Reject. |

## Incorporation Candidates

| Priority | Candidate | Rationale | Target area | Test expectations |
| :--- | :--- | :--- | :--- | :--- |
| P0 | Add a concise missing-data method reference to the current docs site | `bb/docs/missing_data_handler.md` describes fill/interpolation choices that match user-facing missing-data policy concepts. Finbot already has behavior and tests, but the user docs could better explain method tradeoffs. | `docs/guides/data-quality-guide.md` or `docs_site/user-guide/backtesting.md` | Docs-only; verify links/render if docs tooling is used. No unit tests. |
| P0 | Strengthen logging overhead or queue behavior tests if a future logging pass needs it | `bb/tests/functional/logging/test_logger_non_blocking.py` captures the intent that logging should not materially block application work. Finbot already has stronger formatter/API-manager logging tests, but not a direct queue overhead assertion. | `tests/unit/test_infrastructure_api_manager_and_logging.py` or a focused logging test | Use deterministic queue-handler behavior; avoid timing-fragile assertions unless marked performance. |
| P1 | Review data cleaning/outlier utility tests for coverage gaps | The archived outlier and data-integrity modules now exist in Finbot with changed implementations. The value is not old code, but confirmation that current utilities have focused tests and docs before exposing them more prominently. | `tests/unit/test_data_quality.py`, `tests/unit/test_coverage_boost.py`, or dedicated utility tests | Add focused unit tests only for current behavior. Do not port old implementations. |
| P1 | Add API-provider notebook examples as documentation snippets, not notebooks | The API notebooks show exploratory usage for Alpha Vantage, yfinance, and pandas-datareader. Finbot already has wrappers and tests; snippets could help contributors manually inspect provider behavior. | Contributor docs or provider-specific API docs | Docs-only unless examples are converted into doctest-like snippets. |
| P2 | Preserve scaler/normalizer notebooks as research reference material | The scaler notebooks are educational and may help explain transformations, but current code is already present. | Optional `docs/research/` note, not runtime notebooks | None. |
| P2 | Preserve Backtrader PDFs only if license/storage policy allows | `bb/docs/backtrader/*.pdf` may be useful local reference material, but Finbot already has substantial Backtrader/Nautilus guidance and blog docs. | Optional external-reference note; avoid committing PDFs without license review | None. |

## Reject List

- `jerdaw/backbetter` implementation: contains no meaningful backtesting
  functionality beyond `__version__`.
- `backbetter` dependency set: Python `<3.11`, old `numba`, `polars`, and old
  tooling are incompatible with Finbot's current decisions. ADR-001 already
  documents dropping numba in favor of vectorized NumPy.
- `bb` Poetry project setup and lockfile: Finbot uses `uv` and a modern
  `pyproject.toml`.
- `bb/config/*_config.py`: superseded by current Dynaconf settings and config
  accessors.
- `bb/app/templates/` and `bb/main.py`: obsolete Flask-era placeholders; Finbot
  has Streamlit and Next.js/FastAPI surfaces.
- `bb/scripts/data_cleanup.py`, `deploy_application.py`,
  `migrate_database.py`, `setup_environment.py`, `update_datas.py`: placeholders
  or obsolete automation.
- `bb/scripts/gitup.sh`, `activate_environment.sh`,
  `pre-commit_update_and_run.sh`: Poetry-era local workflow scripts; current
  docs and `uv` commands supersede them.
- `bb/assets/gspc.csv`: static market data artifact already represented by
  Finbot parquet data and fetchers; do not add another source of truth.
- `bb/notebooks/CUUR0000SA0.txt` and `bb/notebooks/SUUR0000SA0.txt`: empty
  files.
- `bb/docs/python_data_science_libs.md` and
  `bb/assets/docs/development_dependencies.md`: generic/obsolete dependency
  notes; current docs and ADRs are better sources of truth.

## Modernization Requirements For Any Follow-Up

- Keep imports under `finbot/`; do not reintroduce the old `app/` namespace.
- Use `uv` dependency management; do not restore Poetry workflows.
- Preserve Python `>=3.11,<3.15` compatibility.
- Use current Ruff/mypy conventions and avoid adding new mypy ignores unless a
  dependency gap is unavoidable.
- Prefer tests for current behavior over porting old tests verbatim.
- For docs, prefer short user-facing explanations over importing old notebook
  or generated prose wholesale.
- Do not credit automated coding tools or alter contributor attribution.

## Recommended Backlog

| Priority | Work item | Acceptance criteria |
| :--- | :--- | :--- |
| P0 | Add missing-data method/tradeoff docs based on current Finbot policies. | Current docs explain when fill/interpolate methods are appropriate and link to existing missing-data policy behavior. |
| P0 | Add or improve one logging queue/performance regression test if logging is touched again. | Test validates queue setup or nonblocking intent without brittle wall-clock thresholds. |
| P1 | Coverage review for current outlier/data-integrity utilities. | Any gaps are covered with focused tests against current implementations. |
| P1 | Convert provider notebooks into small contributor examples only where current wrappers lack examples. | Examples use current `finbot.utils.data_collection_utils` APIs and avoid committing executed notebook output. |
| P2 | Decide whether to archive Backtrader PDFs as external references. | License/storage decision recorded; no PDFs committed by default. |
| Reject | Port `backbetter` or old `bb` scaffolding. | No action. |

## Conclusion

No archived production code should be copied directly into Finbot. The archived
repos mainly confirm that Finbot already consolidated the valuable pieces. The
highest-value follow-up is a small documentation pass for missing-data method
tradeoffs, plus optional logging-test and utility-coverage polish during future
maintenance.
