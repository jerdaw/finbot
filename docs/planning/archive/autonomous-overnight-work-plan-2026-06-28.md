# Autonomous Overnight Work Plan - 2026-06-28

## Chosen Artifact Path

Path: `docs/planning/archive/autonomous-overnight-work-plan-2026-06-28.md`

Why this path fits: `docs/guidelines/roadmap-process.md` says active implementation plans belong in `docs/planning/` and should move to `docs/planning/archive/` after completion. This file is an active, reviewable planning artifact, not generated output, source code, test code, configuration, secrets, vendor content, or scratch state.

## 1. Repo Facts

### Stack And Major Components

- Python financial research platform with package code under `finbot/`, tests under `tests/`, scripts under `scripts/`, and docs under `docs/` and `docs_site/`.
- Python package metadata and tool configuration live in `pyproject.toml`; lockfile is `uv.lock`.
- Core domains: typed backtesting contracts, Backtrader-based backtesting, execution simulation, simulations, optimization, data quality, risk analytics, portfolio analytics, realtime quotes, factor analytics, health economics, and CLI/dashboard surfaces.
- Web backend: FastAPI/Pydantic under `web/backend/`, installed via the `web` optional extra.
- Web frontend: Next.js 16 / React 19 / TypeScript / Tailwind v4 / shadcn/ui / Recharts / Zustand under `web/frontend/`, using `pnpm`.
- Documentation platform: Zensical using `mkdocs.yml` compatibility configuration, per ADR-016 and docs workflow.
- Docker surfaces: root `Dockerfile`, `docker-compose.yml`, and API/frontend Dockerfiles under `web/`.

### Important Project Rules

- Active plans go in `docs/planning/`; completed plans go in `docs/planning/archive/`.
- Only actual human contributors, `dependabot[bot]`, and `github-actions[bot]` may be listed as authors or contributors. Do not credit automated coding tools in docs, commits, release notes, changelogs, or comments.
- `CLAUDE.md` and `GEMINI.md` are expected to remain relative symlinks to `AGENTS.md`.
- Use `uv` for dependency management. Base `uv sync` installs core runtime only; contributors normally use `uv sync --all-extras`.
- Do not weaken, skip, or delete tests/checks to make validation pass.
- Avoid credentialed, production-facing, deployment, data-migration, destructive, major dependency, and ambiguous product-decision work during unattended runs.
- The repository has a discovered Python support mismatch: AGENTS/CI mention Python 3.11, while `pyproject.toml` requires `>=3.12,<3.15` and mypy is configured for Python 3.12. Treat this as a blocked decision unless explicitly instructed.

### Discovered Commands

- Install:
  - `uv sync`
  - `uv sync --all-extras`
  - `uv sync --extra dashboard`
  - `uv sync --extra web`
- Python quality:
  - `uv run ruff check . --exclude notebooks/`
  - `uv run ruff format --check . --exclude notebooks/`
  - `uv run mypy finbot/`
  - `uv run bandit -r finbot -ll`
  - `uv run pre-commit run --all-files`
- Python tests:
  - `DYNACONF_ENV=development uv run pytest tests/ -v`
  - `DYNACONF_ENV=development uv run pytest tests/unit/ -v`
  - `DYNACONF_ENV=development uv run pytest --cov=finbot --cov-report=term-missing --cov-fail-under=60 tests/`
- Docs:
  - `uv run zensical build --clean --strict`
  - `uv run zensical serve`
- Frontend:
  - `cd web/frontend && corepack pnpm install`
  - `cd web/frontend && corepack pnpm typecheck`
  - `cd web/frontend && corepack pnpm build`
  - `cd web/frontend && NEXT_PUBLIC_API_URL=http://127.0.0.1:3100/_playwright_api corepack pnpm test:e2e`
- Docker/security:
  - `make docker-build`
  - `make docker-test`
  - `make docker-security-scan`
  - `./scripts/run_docker_security_scan.sh`

## 2. Baseline State

### Branch And Git Status

- Branch: `main`
- Upstream status: `## main...origin/main`
- Recent commits:
  - `0eeced7 docs: clarify remaining security posture work`
  - `44da837 fix: remediate frontend audit findings`
  - `c0a9915 ci: tighten workflow permissions`
  - `2ad99a5 ci: update setup-node action`
  - `a77a880 chore: close stable baseline`
- Pre-existing dirty worktree before this plan file:
  - `M CLAUDE.md`
  - `M GEMINI.md`
  - `M scripts/generate_changelog.sh`
  - `M scripts/run_docker_security_scan.sh`
  - `M scripts/test_release_workflow.sh`
  - `M scripts/test_testpypi_workflow.sh`
  - `M web/frontend/scripts/run-playwright-server.sh`
- `git diff --stat` showed zero insertions/deletions for the five shell scripts and line-ending warnings that LF would be replaced by CRLF if Git touches them.
- Windows Git could not diff the symlink paths and printed `CLAUDE.md: Function not implemented` and `GEMINI.md: Function not implemented`.
- WSL `ls -l` showed `CLAUDE.md -> AGENTS.md` and `GEMINI.md -> AGENTS.md`.
- Do not edit, normalize, revert, or stage those pre-existing dirty files during the overnight run unless a queued item explicitly requires it and the user confirms ownership.

### Environment Assumptions And Blockers

- Current shell: PowerShell from the Windows host against a WSL UNC checkout.
- Windows Python available: `Python 3.13.13`.
- Local `.venv` is Windows-style and usable:
  - `.venv\Scripts\python.exe --version`: `Python 3.13.13`
  - `.venv\Scripts\python.exe -m pytest --version`: `pytest 9.0.3`
  - `.venv\Scripts\python.exe -m ruff --version`: `ruff 0.15.10`
  - `.venv\Scripts\python.exe -m mypy --version`: `mypy 1.20.1`
  - `.venv\Scripts\python.exe -m bandit --version`: `bandit 1.9.4`
- `uv` is not on PATH in PowerShell or WSL zsh. Repo-standard `uv run ...` commands are blocked in this execution environment unless `uv` becomes available.
- WSL zsh also lacks `python`, `node`, `corepack`, and `pnpm` on PATH.
- PowerShell lacks `node`, `corepack`, and `pnpm` on PATH. Frontend validation is blocked.
- Local `.venv` appears to be a minimal/core environment, not all extras:
  - `fastapi`, `pydantic`, and `streamlit` are missing.
  - Web-router and dashboard import tests fail until `web` and `dashboard` extras are installed.
- Zensical package files are present under `.venv\Lib\site-packages`, but no `zensical.exe` console script was found in `.venv\Scripts`, and `.venv\Scripts\python.exe -m zensical --version` failed with `No module named zensical.__main__; 'zensical' is a package and cannot be directly executed`. Docs build is blocked without `uv run zensical ...` or a working console script.
- `.venv\Scripts\mypy.exe finbot/` exits with status 1 but emitted no diagnostics in this environment, even with `--show-traceback`, `--no-error-summary`, and `--verbose`. Treat mypy as blocked until it can be rerun in the repo-standard uv/CI environment.

### Commands Run Before Any Source/Test/Product Changes

- `rg --files ...` for instructions, docs, configs, workflows, scripts, and planning files: passed.
- `rg -n ...` over AGENTS, README, CONTRIBUTING, docs guidelines, pyproject, Makefile, workflows, package files: passed.
- `git -c safe.directory=//wsl.localhost/Ubuntu/home/jer/repos/finbot status --short --branch`: passed; dirty status listed above.
- `git -c safe.directory=//wsl.localhost/Ubuntu/home/jer/repos/finbot diff --name-status`: partial; shell scripts listed, symlink diff failed with `Function not implemented`.
- `git -c safe.directory=//wsl.localhost/Ubuntu/home/jer/repos/finbot diff --stat`: partial; zero insertions/deletions for shell scripts, symlink diff failed with `Function not implemented`.
- `wsl.exe -d Ubuntu --cd /home/jer/repos/finbot git branch --show-current`: passed; `main`.
- `wsl.exe -d Ubuntu --cd /home/jer/repos/finbot git log -5 --oneline`: passed.
- `wsl.exe -d Ubuntu --cd /home/jer/repos/finbot ls -l AGENTS.md CLAUDE.md GEMINI.md`: passed; symlinks point to `AGENTS.md`.
- `.venv\Scripts\python.exe -m ruff check . --exclude notebooks/`: passed, `All checks passed!`
- `.venv\Scripts\python.exe -m ruff format --check . --exclude notebooks/`: passed, `579 files already formatted`
- `.venv\Scripts\python.exe -m bandit -r finbot -ll`: passed; no medium/high issues identified. Metrics reported 23 low-severity findings.
- `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_data_quality.py tests/unit/test_realtime_data_cache.py -q`: passed, `27 passed`.
- `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_imports.py tests/unit/test_data_quality.py tests/unit/test_realtime_data_cache.py tests/unit/test_web_backend_routers.py -q`: failed during collection because `fastapi` is missing.
- `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_imports.py tests/unit/test_data_quality.py tests/unit/test_realtime_data_cache.py -q`: failed with 15 optional-surface import failures due missing `streamlit`, `fastapi`, and `pydantic`; 55 tests passed.
- `.venv\Scripts\mypy.exe finbot/`: failed with exit code 1 and no captured diagnostics.
- `node --version`, `corepack --version`, `pnpm --version`: failed; commands not found.
- `.venv\Scripts\python.exe -m zensical --version`: failed; no module `zensical.__main__`.

## 3. Candidate Work Inventory

### AUT-001 - DataFrame Validation Result Regression Coverage

- Objective: Expand regression tests for `ValidationResult` path conversion, row/column counts, empty-frame error behavior, and `is_valid` semantics.
- Likely files/areas: `tests/unit/test_data_quality.py`, `finbot/services/data_quality/validate_dataframe.py` only if tests expose a bug.
- Risk level: Low.
- Acceptance criteria: Tests assert exact `file_path`, `row_count`, `col_count`, `errors`, `warnings`, and `is_valid` for valid and empty inputs.
- Validation commands: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_data_quality.py -q`; ruff check/format check.
- Rollback plan: Revert the test additions and any directly related implementation hunk.
- Blocker if not safe: None.

### AUT-002 - Combined DataFrame Validation Warnings And Errors

- Objective: Add tests for simultaneous missing columns, duplicate index warnings, null warnings, and minimum-row errors without changing severity semantics.
- Likely files/areas: `tests/unit/test_data_quality.py`, possibly `finbot/services/data_quality/validate_dataframe.py`.
- Risk level: Low.
- Acceptance criteria: Missing columns and too-few rows remain errors; duplicate index and nulls remain warnings; mixed cases preserve all messages deterministically.
- Validation commands: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_data_quality.py -q`; ruff check/format check.
- Rollback plan: Revert the focused tests and any implementation fix.
- Blocker if not safe: None.

### AUT-003 - QuoteCache Expiry And Size Semantics

- Objective: Add regression tests that document `QuoteCache.size()` includes expired entries until accessed, and that `get()` removes expired entries.
- Likely files/areas: `tests/unit/test_realtime_data_cache.py`, `finbot/services/realtime_data/quote_cache.py` only if tests reveal a defect.
- Risk level: Low.
- Acceptance criteria: Expired entries are counted before lookup, removed after lookup, and non-expired entries remain retrievable.
- Validation commands: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_realtime_data_cache.py -q`; ruff check/format check.
- Rollback plan: Revert cache tests and any minimal implementation fix.
- Blocker if not safe: None.

### AUT-004 - QuoteCache TTL Guardrail

- Objective: Add validation that `ttl_seconds` must be positive and test zero/negative TTL construction.
- Likely files/areas: `finbot/services/realtime_data/quote_cache.py`, `tests/unit/test_realtime_data_cache.py`.
- Risk level: Low to Medium because invalid constructor inputs would change from accepted to rejected.
- Acceptance criteria: `QuoteCache(ttl_seconds=0)` and negative TTL raise `ValueError` with a clear message; existing positive-TTL tests pass.
- Validation commands: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_realtime_data_cache.py -q`; ruff check/format check.
- Rollback plan: Revert constructor guard and tests.
- Blocker if not safe: Check for existing callers passing zero/negative TTL with `rg "QuoteCache\\("`; do not proceed if found outside tests without explicit intent.

### AUT-005 - JSON Serializer Scalar Safety

- Objective: Add direct unit coverage for `sanitize_value()` handling of Python floats, numpy scalars, `NaN`, infinities, `Decimal`, pandas timestamps, dates, bools, and arrays.
- Likely files/areas: new or existing unit test file under `tests/unit/`; `web/backend/services/serializers.py`.
- Risk level: Low.
- Acceptance criteria: Every scalar output is JSON-safe, non-finite numbers become `None`, numpy scalars become native Python types, and datetimes become ISO strings.
- Validation commands: targeted serializer pytest; ruff check/format check.
- Rollback plan: Revert serializer tests and any minimal serializer fix.
- Blocker if not safe: None; this module imports without FastAPI.

### AUT-006 - JSON Serializer Container Helpers

- Objective: Add direct tests for `dataframe_to_records()`, `series_to_timeseries()`, and `stats_df_to_dict()` with datetime indices, string indices, empty inputs, and null/non-finite values.
- Likely files/areas: new or existing unit test file under `tests/unit/`; `web/backend/services/serializers.py`.
- Risk level: Low.
- Acceptance criteria: Helpers return stable keys (`date` or `index`), preserve names, return empty shapes for empty inputs, and sanitize all values recursively.
- Validation commands: targeted serializer pytest; ruff check/format check.
- Rollback plan: Revert serializer tests and any minimal serializer fix.
- Blocker if not safe: None; do not import FastAPI routers for this item.

### AUT-007 - VaR Parameter Validation

- Objective: Add explicit validation for invalid `confidence`, `horizon_days`, `n_simulations`, and negative `portfolio_value` in VaR analytics.
- Likely files/areas: `finbot/services/risk_analytics/var.py`, `tests/unit/test_var.py`.
- Risk level: Low to Medium because invalid inputs will raise clearer errors instead of falling through to scipy/numpy behavior.
- Acceptance criteria: `confidence` must be in `(0, 1)`, `horizon_days >= 1`, `n_simulations >= 1` for Monte Carlo, and `portfolio_value` must be non-negative when provided.
- Validation commands: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_var.py -q`; ruff check/format check.
- Rollback plan: Revert validation helper and tests.
- Blocker if not safe: None.

### AUT-008 - VaR Non-Finite Returns Validation

- Objective: Add tests and implementation checks rejecting `NaN` and infinity in `compute_var()`, `compute_cvar()`, and `var_backtest()`.
- Likely files/areas: `finbot/services/risk_analytics/var.py`, `tests/unit/test_var.py`.
- Risk level: Low to Medium because invalid inputs will become explicit errors.
- Acceptance criteria: Non-finite returns raise `ValueError` with a clear message; existing valid VaR/CVaR/backtest behavior remains unchanged.
- Validation commands: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_var.py -q`; ruff check/format check.
- Rollback plan: Revert validation and tests.
- Blocker if not safe: None.

### AUT-009 - VaR Backtest Edge Cases

- Objective: Cover `min_history` edge cases and method enum/string equivalence in `var_backtest()`.
- Likely files/areas: `tests/unit/test_var.py`, `finbot/services/risk_analytics/var.py` only if a defect appears.
- Risk level: Low.
- Acceptance criteria: `min_history < 30` or non-positive values are handled intentionally, enum and string methods produce equivalent results, and too-short data errors remain clear.
- Validation commands: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_var.py -q`; ruff check/format check.
- Rollback plan: Revert tests and any direct fix.
- Blocker if not safe: Define intended `min_history` behavior before changing implementation; if ambiguous, document as blocked.

### AUT-010 - Diversification Non-Finite Input Validation

- Objective: Reject `NaN` and infinity in multi-asset returns and weights before computing correlation/diversification metrics.
- Likely files/areas: `finbot/services/portfolio_analytics/correlation.py`, `tests/unit/test_correlation_diversification.py`.
- Risk level: Low to Medium because invalid inputs become explicit errors.
- Acceptance criteria: Non-finite returns or weights raise `ValueError`; existing valid diversification tests still pass.
- Validation commands: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_correlation_diversification.py -q`; ruff check/format check.
- Rollback plan: Revert validation and tests.
- Blocker if not safe: None.

### AUT-011 - Diversification Degenerate-Series Coverage

- Objective: Add tests for zero-volatility or perfectly correlated asset series and document the current `diversification_ratio` behavior.
- Likely files/areas: `tests/unit/test_correlation_diversification.py`, possibly `finbot/services/portfolio_analytics/correlation.py`.
- Risk level: Low.
- Acceptance criteria: Degenerate cases return finite, deterministic values or raise explicit `ValueError` if the current behavior is not JSON-safe.
- Validation commands: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_correlation_diversification.py -q`; ruff check/format check.
- Rollback plan: Revert tests and any minimal guardrail.
- Blocker if not safe: If expected behavior is product-sensitive, document and skip implementation changes.

### AUT-012 - Rolling Metrics Non-Finite Input Validation

- Objective: Add validation for non-finite returns, benchmark returns, risk-free rate, and dates alignment in rolling portfolio metrics.
- Likely files/areas: `finbot/services/portfolio_analytics/rolling.py`, `tests/unit/test_rolling_metrics.py`.
- Risk level: Low to Medium because invalid inputs become explicit errors.
- Acceptance criteria: Non-finite numeric inputs raise clear `ValueError`; date-length and annualization validations remain intact.
- Validation commands: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_rolling_metrics.py -q`; ruff check/format check.
- Rollback plan: Revert validation and tests.
- Blocker if not safe: None.

### AUT-013 - Benchmark Analytics Input Guardrails

- Objective: Add explicit handling for non-finite values and constant benchmark returns before OLS regression.
- Likely files/areas: `finbot/services/portfolio_analytics/benchmark.py`, `tests/unit/test_benchmark.py`.
- Risk level: Medium because constant benchmark behavior may affect callers that currently rely on scipy's implicit behavior.
- Acceptance criteria: Non-finite arrays raise `ValueError`; constant benchmark arrays either raise a clear `ValueError` or have a documented deterministic output verified by tests.
- Validation commands: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_benchmark.py -q`; ruff check/format check.
- Rollback plan: Revert guardrails and tests.
- Blocker if not safe: If constant benchmark semantics are ambiguous, only add tests for current behavior and record a follow-up.

### AUT-014 - Factor Regression Infinite-Value Validation

- Objective: Extend existing factor regression `NaN` checks to reject infinity in portfolio and factor returns.
- Likely files/areas: `finbot/services/factor_analytics/factor_regression.py`, `tests/unit/test_factor_regression.py`.
- Risk level: Low.
- Acceptance criteria: `np.inf` and `-np.inf` inputs raise `ValueError`; existing factor model detection and rolling R-squared tests pass.
- Validation commands: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_factor_regression.py -q`; ruff check/format check.
- Rollback plan: Revert validation and tests.
- Blocker if not safe: None.

### AUT-015 - Factor Attribution And Risk Validation Parity

- Objective: Align factor attribution and factor risk input validation with factor regression for non-finite values and invalid annualization factors.
- Likely files/areas: `finbot/services/factor_analytics/factor_attribution.py`, `finbot/services/factor_analytics/factor_risk.py`, `tests/unit/test_factor_attribution.py`, `tests/unit/test_factor_risk.py`.
- Risk level: Low to Medium because invalid inputs become explicit errors.
- Acceptance criteria: Attribution and risk decomposition reject non-finite returns/factors; supplied `annualization_factor < 1` raises before computing or accepting a regression result.
- Validation commands: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_factor_attribution.py tests/unit/test_factor_risk.py -q`; ruff check/format check.
- Rollback plan: Revert validation and tests.
- Blocker if not safe: None.

### AUT-016 - Contract Cost Serialization Round-Trip

- Objective: Add a regression test that `BacktestRunResult` with a populated `CostSummary` round-trips through `backtest_result_to_payload()` and `backtest_result_from_payload()`.
- Likely files/areas: `tests/unit/test_core_contracts.py`, `finbot/core/contracts/serialization.py`.
- Risk level: Low.
- Acceptance criteria: Cost totals, cost event timestamp, symbol, type, amount, and basis survive serialization/deserialization.
- Validation commands: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_core_contracts.py -q`; ruff check/format check.
- Rollback plan: Revert test and any direct serializer fix.
- Blocker if not safe: None.

### AUT-017 - Contract Payload Migration Defaults Coverage

- Objective: Add tests that legacy/migrated payloads get stable defaults for assumptions, artifacts, warnings, optional cost payloads, and random seed.
- Likely files/areas: `tests/unit/test_core_contracts.py`, `finbot/core/contracts/versioning.py`, `finbot/core/contracts/serialization.py`.
- Risk level: Low.
- Acceptance criteria: Missing optional fields are filled with documented empty/default values, and existing legacy migration tests still pass.
- Validation commands: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_core_contracts.py -q`; ruff check/format check.
- Rollback plan: Revert tests and any minimal migration fix.
- Blocker if not safe: None.

### AUT-018 - CostSummary Aggregation Edge Cases

- Objective: Add tests for empty `cost_events`, unknown-symbol absence, repeated symbols, and all `CostType` buckets in `CostSummary`.
- Likely files/areas: `tests/unit/test_cost_models.py`, `finbot/core/contracts/costs.py` only if tests reveal a defect.
- Risk level: Low.
- Acceptance criteria: `total_costs`, `costs_by_type()`, and `costs_by_symbol()` produce deterministic, complete results.
- Validation commands: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_cost_models.py -q`; ruff check/format check.
- Rollback plan: Revert tests and any direct fix.
- Blocker if not safe: None.

### AUT-019 - Backend Serializer Tests Without Web Extras

- Objective: Create a focused serializer test module that imports only `web.backend.services.serializers`, proving backend utility coverage can run without FastAPI/Pydantic extras.
- Likely files/areas: new `tests/unit/test_web_backend_serializers.py`, `web/backend/services/serializers.py`.
- Risk level: Low.
- Acceptance criteria: Test module passes in the current minimal venv and does not import routers, schemas, FastAPI, or Pydantic.
- Validation commands: targeted serializer pytest; ruff check/format check.
- Rollback plan: Delete the new test file and revert serializer changes if any.
- Blocker if not safe: None.

### AUT-020 - Optional Surface Import Test Setup

- Objective: Document or resolve why `tests/unit/test_imports.py` expects dashboard/web imports while the local baseline lacks optional extras.
- Likely files/areas: `tests/unit/test_imports.py`, setup docs, pyproject optional extras.
- Risk level: Medium.
- Acceptance criteria: The repo has an explicit, non-weakened way to run optional import tests with `web` and `dashboard` extras; no skips are added merely to hide missing dependencies.
- Validation commands: repo-standard `uv sync --extra web --extra dashboard`; import tests; full ruff/format.
- Rollback plan: Revert any test/docs/config changes.
- Blocker if not safe: Blocked in current environment because `uv`, `fastapi`, `pydantic`, and `streamlit` are unavailable; do not queue overnight.

### AUT-021 - Frontend Typecheck And E2E Triage

- Objective: Run frontend typecheck/build/e2e and fix only narrow, validated failures.
- Likely files/areas: `web/frontend/src/`, `web/frontend/tests/e2e/`, `web/frontend/package.json`.
- Risk level: Medium.
- Acceptance criteria: `corepack pnpm typecheck`, `corepack pnpm build`, and mocked Playwright tests pass without broad rewrites.
- Validation commands: frontend pnpm commands from AGENTS.
- Rollback plan: Revert frontend hunks and generated artifacts.
- Blocker if not safe: Blocked because Node/Corepack/pnpm are not on PATH; do not queue overnight.

### AUT-022 - Documentation Build Triage

- Objective: Run strict docs build and fix broken links/API docs only if failures are clear and local.
- Likely files/areas: `docs/`, `docs_site/`, `mkdocs.yml`.
- Risk level: Low to Medium.
- Acceptance criteria: `uv run zensical build --clean --strict` passes; fixes are docs-only unless a broken public API reference exposes a code bug.
- Validation commands: `uv run zensical build --clean --strict`.
- Rollback plan: Revert docs/config changes and generated site output.
- Blocker if not safe: Blocked because `uv` is unavailable and the local venv has no working `zensical` console entry point; do not queue overnight.

### AUT-023 - Python Version Matrix Alignment

- Objective: Align declared Python support across AGENTS, README, pyproject, ruff target, mypy config, and CI matrices.
- Likely files/areas: `AGENTS.md`, `README.md`, `pyproject.toml`, `.github/workflows/ci.yml`, `.github/workflows/ci-heavy.yml`.
- Risk level: Medium to High.
- Acceptance criteria: Exactly one supported Python range is documented and enforced; CI matrices match packaging metadata; tests validate on supported versions.
- Validation commands: full Python CI-equivalent checks across supported versions.
- Rollback plan: Revert docs/config/workflow changes.
- Blocker if not safe: Blocked because this is a support-policy decision; do not queue overnight without explicit target.

### AUT-024 - Pre-Existing Dirty Script/Symlink Audit

- Objective: Investigate the pre-existing dirty shell scripts and symlink status without changing them.
- Likely files/areas: `CLAUDE.md`, `GEMINI.md`, `scripts/*.sh`, `web/frontend/scripts/run-playwright-server.sh`.
- Risk level: Medium because these are pre-existing user changes.
- Acceptance criteria: A status note explains whether changes are line-ending, symlink metadata, or content changes; no files are edited unless separately authorized.
- Validation commands: `git status`, `git diff --name-status`, WSL `git diff`, `file`, `ls -l`.
- Rollback plan: No rollback for inspection-only work; do not revert user changes.
- Blocker if not safe: Do not modify these files during an unattended run.

### AUT-025 - Docker And Release Script Validation

- Objective: Validate Docker security and release helper scripts after the dirty-script status is resolved.
- Likely files/areas: Dockerfiles, `scripts/run_docker_security_scan.sh`, release workflow scripts.
- Risk level: High for unattended work because it may require Docker, network, and touched dirty scripts.
- Acceptance criteria: Script validation passes without changing release semantics or touching credentials.
- Validation commands: `make docker-build`, `make docker-security-scan`, release test scripts.
- Rollback plan: Revert script/Docker changes.
- Blocker if not safe: Blocked by dirty scripts, possible Docker/network requirements, and release-surface risk; do not queue overnight.

## 4. Safe Overnight Work Queue

Only work these queued items unless the user updates this plan. For every item: make a small diff, run the item-specific pytest command, run ruff check and ruff format check, review the diff, and stop if validation fails in a way that requires product judgment.

### A. Core Queue

1. AUT-001 - DataFrame Validation Result Regression Coverage
2. AUT-002 - Combined DataFrame Validation Warnings And Errors
3. AUT-003 - QuoteCache Expiry And Size Semantics
4. AUT-005 - JSON Serializer Scalar Safety
5. AUT-006 - JSON Serializer Container Helpers
6. AUT-019 - Backend Serializer Tests Without Web Extras
7. AUT-016 - Contract Cost Serialization Round-Trip
8. AUT-018 - CostSummary Aggregation Edge Cases
9. AUT-007 - VaR Parameter Validation
10. AUT-008 - VaR Non-Finite Returns Validation

Core Queue rationale: These items are local, deterministic, credential-free, and validate in the current `.venv` without optional web/dashboard/frontend extras. They mostly add regression tests and narrow guardrails around JSON safety and invalid numeric inputs.

### B. Extension Queue

1. AUT-010 - Diversification Non-Finite Input Validation
2. AUT-011 - Diversification Degenerate-Series Coverage
3. AUT-012 - Rolling Metrics Non-Finite Input Validation
4. AUT-013 - Benchmark Analytics Input Guardrails
5. AUT-014 - Factor Regression Infinite-Value Validation
6. AUT-015 - Factor Attribution And Risk Validation Parity
7. AUT-017 - Contract Payload Migration Defaults Coverage
8. AUT-004 - QuoteCache TTL Guardrail, only after confirming no production callers intentionally pass zero/negative TTL.
9. AUT-009 - VaR Backtest Edge Cases, only if intended `min_history` behavior is unambiguous from existing code/tests.

Extension Queue rationale: These items remain safe and reviewable, but more of them add explicit validation behavior. They should continue only after the Core Queue is green.

## 5. Do Not Do Overnight

- Do not touch `CLAUDE.md`, `GEMINI.md`, dirty shell scripts, or `web/frontend/scripts/run-playwright-server.sh` except for inspection/status notes.
- Do not run `git reset`, `git checkout --`, destructive cleanup, recursive delete, generated-output deletion, or broad line-ending normalization.
- Do not stage, commit, push, create PRs, publish packages, deploy docs/sites, or run release workflows.
- Do not change credentials, secret handling, `.env` files, API keys, production settings, or scheduled data-update behavior.
- Do not run data collection against live providers, market APIs, external credentialed services, or production endpoints.
- Do not perform data migrations, schema migrations, broad rewrites, package layout changes, or public product direction changes.
- Do not add major dependencies or update lockfiles.
- Do not weaken, skip, delete, xfail, or loosen tests/checks to make a run green.
- Do not modify CI support matrices or Python version policy without explicit human direction.
- Do not work on frontend items until Node/Corepack/pnpm are available and validation can run.
- Do not work on FastAPI/dashboard import failures until optional extras are installed through the repo-standard dependency flow.
- Do not work on docs-build failures until `uv run zensical build --clean --strict` is runnable.
- Do not run Docker/security/release script work unattended while the script files are already dirty.

## 6. Final Completion Checklist

Run the broadest available checks after the queue, preferring repo-standard `uv` commands if `uv` becomes available. If `uv` remains unavailable, use the `.venv\Scripts\python.exe` fallback commands listed below and record the blocker.

### Required Final Checks In Current Environment

- `git -c safe.directory=//wsl.localhost/Ubuntu/home/jer/repos/finbot status --short --branch`
- `.venv\Scripts\python.exe -m ruff check . --exclude notebooks/`
- `.venv\Scripts\python.exe -m ruff format --check . --exclude notebooks/`
- `.venv\Scripts\python.exe -m bandit -r finbot -ll`
- Targeted pytest commands for every touched area, for example:
  - `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_data_quality.py tests/unit/test_realtime_data_cache.py -q`
  - `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_var.py tests/unit/test_correlation_diversification.py tests/unit/test_rolling_metrics.py tests/unit/test_benchmark.py -q`
  - `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_factor_regression.py tests/unit/test_factor_attribution.py tests/unit/test_factor_risk.py -q`
  - `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_core_contracts.py tests/unit/test_cost_models.py -q`
  - Serializer-specific pytest module if created.

### Preferred Final Checks If Repo-Standard Tooling Becomes Available

- `uv run ruff check . --exclude notebooks/`
- `uv run ruff format --check . --exclude notebooks/`
- `DYNACONF_ENV=development uv run pytest tests/unit/test_data_quality.py tests/unit/test_realtime_data_cache.py tests/unit/test_var.py tests/unit/test_correlation_diversification.py tests/unit/test_rolling_metrics.py tests/unit/test_benchmark.py tests/unit/test_factor_regression.py tests/unit/test_factor_attribution.py tests/unit/test_factor_risk.py tests/unit/test_core_contracts.py tests/unit/test_cost_models.py -q`
- `uv run mypy finbot/`
- `uv run bandit -r finbot -ll`

### Review Requirements

- Final diff review: inspect `git diff --stat` and `git diff --check`.
- Secret check: inspect diffs for API keys, tokens, credentials, local paths, `.env` content, generated data dumps, and accidental notebook/output blobs.
- Dead-code/regression review: verify changed source has tests that would fail before the fix when behavior changes; remove unused helpers/imports introduced during the run.
- Status inventory: list completed item IDs, skipped item IDs with blockers, validation commands and results, and any pre-existing dirty files still present.
- Do not report success for blocked checks. State exact missing dependency/tooling/service for each skipped validation.

## 7. Implementation Status

Status artifact path: `docs/planning/archive/autonomous-overnight-work-plan-2026-06-28.md`.

### Queue Status

| Item | Status | Files Changed | Validation | Notes |
| --- | --- | --- | --- | --- |
| AUT-001 | Done | `tests/unit/test_data_quality.py` | Passed: `pytest tests/unit/test_data_quality.py -q` (14 passed); `ruff check`; `ruff format --check` | Added exact `ValidationResult` field assertions for valid and empty frames. Rollback: revert the focused test assertions. |
| AUT-002 | Done | `tests/unit/test_data_quality.py` | Passed: `pytest tests/unit/test_data_quality.py -q` (15 passed); `ruff check`; `ruff format --check` | Added a mixed validation regression test proving errors remain errors and duplicate/null findings remain warnings. Rollback: revert the focused test. |
| AUT-003 | Done | `tests/unit/test_realtime_data_cache.py` | Passed: `pytest tests/unit/test_realtime_data_cache.py -q` (15 passed); `ruff check`; `ruff format --check` | Added lazy-expiry size/prune regression tests. Initial parallel run printed 15 passed but reported shell exit 1; rerun returned exit 0. Rollback: revert the focused tests. |
| AUT-005 | Done | `tests/unit/test_web_backend_serializers.py` | Passed: `pytest tests/unit/test_web_backend_serializers.py -q` (14 passed); `ruff check`; `ruff format --check` | Added scalar `sanitize_value()` coverage for non-finite numbers, numpy scalars, decimals, dates, and arrays. Rollback: delete/revert the focused test file. |
| AUT-006 | Done | `tests/unit/test_web_backend_serializers.py` | Passed: `pytest tests/unit/test_web_backend_serializers.py -q` (21 passed); `ruff check`; `ruff format --check` | Added DataFrame, Series, stats DataFrame, empty-input, index-key, ISO-date, and sanitization coverage. Rollback: revert the focused tests. |
| AUT-019 | Done | `tests/unit/test_web_backend_serializers.py` | Passed: `pytest tests/unit/test_web_backend_serializers.py -q` (21 passed); `ruff check`; `ruff format --check`; no FastAPI/Pydantic/router/schema imports found | Confirmed focused backend serializer tests run without optional web extras. Rollback: delete/revert the focused test file. |
| AUT-016 | Done | `tests/unit/test_core_contracts.py` | Passed: `pytest tests/unit/test_core_contracts.py -q` (11 passed); `ruff check`; `ruff format --check` | Added `BacktestRunResult` cost summary/event serialization round-trip coverage. Rollback: revert the focused test. |
| AUT-018 | Done | `tests/unit/test_cost_models.py` | Passed: `pytest tests/unit/test_cost_models.py -q` (38 passed); `ruff check`; `ruff format --check` | Added empty-event, all-type bucket, repeated-symbol, and absent-symbol aggregation coverage. Rollback: revert the focused tests. |
| AUT-007 | Done | `finbot/services/risk_analytics/var.py`, `tests/unit/test_var.py` | Passed: `pytest tests/unit/test_var.py -q` (28 passed); `ruff check`; `ruff format --check` | Added explicit validation for confidence, horizon, Monte Carlo simulation count, and non-negative portfolio value. Rollback: revert validation helper/tests. |
| AUT-008 | Done | `finbot/services/risk_analytics/var.py`, `tests/unit/test_var.py` | Passed: `pytest tests/unit/test_var.py -q` (33 passed); `ruff check`; `ruff format --check` | Added explicit `NaN`/infinite returns rejection for VaR, CVaR, and backtest. Rollback: revert `_validate_returns` finite check and tests. |
| AUT-010 | Done | `finbot/services/portfolio_analytics/correlation.py`, `tests/unit/test_correlation_diversification.py` | Passed: `pytest tests/unit/test_correlation_diversification.py -q` (20 passed); `ruff check`; `ruff format --check` | Added finite numeric returns and finite weight validation; extracted weight validation to stay under complexity threshold. Rollback: revert helper/checks and tests. |
| AUT-011 | Done | `finbot/services/portfolio_analytics/correlation.py`, `tests/unit/test_correlation_diversification.py` | Passed: `pytest tests/unit/test_correlation_diversification.py -q` (21 passed); `ruff check`; `ruff format --check` | Added zero-variance asset rejection and finite perfect-correlation regression coverage. Rollback: revert zero-variance check and tests. |
| AUT-012 | Done | `finbot/services/portfolio_analytics/rolling.py`, `tests/unit/test_rolling_metrics.py` | Passed: `pytest tests/unit/test_rolling_metrics.py -q -p no:cacheprovider` (25 passed); `ruff check`; `ruff format --check` | Added finite input checks for returns, benchmark returns, and risk-free rate. Plain pytest showed all tests passed but crashed writing pytest cache on UNC path (`OSError: [Errno 22] Invalid argument`); cache-disabled rerun returned exit 0. Rollback: revert validation checks and tests. |
| AUT-013 | Done | `finbot/services/portfolio_analytics/benchmark.py`, `tests/unit/test_benchmark.py` | Passed: `pytest tests/unit/test_benchmark.py -q -p no:cacheprovider` (24 passed); `ruff check`; `ruff format --check` | Added finite input/risk-free-rate checks, explicit constant-benchmark rejection before OLS, and low-volatility nonconstant benchmark coverage. Rollback: revert validation checks and tests. |
| AUT-014 | Done | `finbot/services/factor_analytics/factor_regression.py`, `tests/unit/test_factor_regression.py` | Passed: `pytest tests/unit/test_factor_regression.py -q -p no:cacheprovider` (33 passed); `ruff check`; `ruff format --check` | Extended factor regression and rolling R-squared validation from NaN-only to NaN/infinite inputs. Rollback: revert finite checks and tests. |
| AUT-015 | Done | `finbot/services/factor_analytics/factor_attribution.py`, `finbot/services/factor_analytics/factor_risk.py`, `tests/unit/test_factor_attribution.py`, `tests/unit/test_factor_risk.py` | Passed: `pytest tests/unit/test_factor_attribution.py tests/unit/test_factor_risk.py -q -p no:cacheprovider` (48 passed); `ruff check`; `ruff format --check` | Added finite input and annualization validation parity for attribution and risk, including precomputed regression paths. Rollback: revert validation changes and tests. |
| AUT-017 | Done | `tests/unit/test_core_contracts.py` | Passed: `pytest tests/unit/test_core_contracts.py -q -p no:cacheprovider` (12 passed); `ruff check`; `ruff format --check` | Added legacy payload default coverage for assumptions, artifacts, warnings, random seed, and absent costs. Rollback: revert the focused test. |
| AUT-004 | Done | `finbot/services/realtime_data/quote_cache.py`, `tests/unit/test_realtime_data_cache.py` | Passed: `pytest tests/unit/test_realtime_data_cache.py -q -p no:cacheprovider` (17 passed); `ruff check`; `ruff format --check` | Added positive-TTL constructor guard and zero/negative TTL tests. Initial pytest attempt hit a Windows page-error crash while importing pandas from the UNC venv, and first rerun printed 17 passed with exit 1; second rerun returned exit 0. Rollback: revert guard and tests. |
| AUT-009 | Done | `finbot/services/risk_analytics/var.py`, `tests/unit/test_var.py` | Passed: `pytest tests/unit/test_var.py -q -p no:cacheprovider` (36 passed); `ruff check`; `ruff format --check` | Added explicit `min_history >= 30` guard, exact-minimum coverage, and string/enum method equivalence test. Rollback: revert guard and tests. |

### Status Log

- 2026-06-28: Re-read `AGENTS.md`, this planning artifact, `git status --short --branch`, current diff stat, and applicable instruction-file search. No `AGENTS.override.md` or nested AGENTS files were found. Pre-existing dirty files remain: `CLAUDE.md`, `GEMINI.md`, five shell scripts, and `web/frontend/scripts/run-playwright-server.sh`.
- 2026-06-28: AUT-001 completed with test-only coverage in `tests/unit/test_data_quality.py`; no source behavior changed.
- 2026-06-28: AUT-002 completed with test-only mixed error/warning coverage in `tests/unit/test_data_quality.py`; no source behavior changed.
- 2026-06-28: AUT-003 completed with test-only quote-cache lazy-expiry coverage in `tests/unit/test_realtime_data_cache.py`; no source behavior changed.
- 2026-06-28: AUT-005 completed with isolated backend serializer scalar tests in `tests/unit/test_web_backend_serializers.py`; no source behavior changed.
- 2026-06-28: AUT-006 completed with isolated backend serializer container-helper tests in `tests/unit/test_web_backend_serializers.py`; no source behavior changed.
- 2026-06-28: AUT-019 completed; `tests/unit/test_web_backend_serializers.py` imports only `web.backend.services.serializers` from the backend and passes without FastAPI/Pydantic extras.
- 2026-06-28: AUT-016 completed with contract cost serialization round-trip coverage in `tests/unit/test_core_contracts.py`; no source behavior changed.
- 2026-06-28: AUT-018 completed with CostSummary aggregation edge-case coverage in `tests/unit/test_cost_models.py`; no source behavior changed.
- 2026-06-28: AUT-007 completed with explicit VaR parameter validation in `finbot/services/risk_analytics/var.py` and tests in `tests/unit/test_var.py`.
- 2026-06-28: AUT-008 completed with VaR/CVaR/backtest non-finite returns validation in `finbot/services/risk_analytics/var.py` and tests in `tests/unit/test_var.py`.
- 2026-06-28: AUT-010 completed with diversification non-finite returns/weights validation in `finbot/services/portfolio_analytics/correlation.py` and tests in `tests/unit/test_correlation_diversification.py`.
- 2026-06-28: AUT-011 completed with zero-variance asset rejection and perfect-correlation finite-output coverage in diversification analytics.
- 2026-06-28: AUT-012 completed with rolling metrics finite-input validation in `finbot/services/portfolio_analytics/rolling.py`; pytest cache provider needed disabling on UNC path for reliable exit code.
- 2026-06-28: AUT-013 completed with benchmark analytics finite-input and constant-benchmark guardrails in `finbot/services/portfolio_analytics/benchmark.py`.
- 2026-06-28: AUT-014 completed with factor regression and rolling R-squared non-finite input validation.
- 2026-06-28: AUT-015 completed with factor attribution/risk finite-input and annualization validation parity.
- 2026-06-28: AUT-017 completed with contract migration default coverage; no source behavior changed.
- 2026-06-28: AUT-004 started after scanning `QuoteCache(...)` and `ttl_seconds` call sites; only production caller passes a positive default-configurable TTL.
- 2026-06-28: AUT-004 completed with a positive-TTL constructor guard and regression tests for zero/negative TTL.
- 2026-06-28: AUT-009 started after confirming `var_backtest()` cannot safely use `min_history` below the shared 30-observation VaR input floor.
- 2026-06-28: AUT-009 completed with explicit `min_history` guardrails and method enum/string equivalence coverage.
- 2026-06-28: Post-run audit tightened AUT-013's constant-benchmark guard from variance-based `isclose()` to standard-deviation `isclose()` and added low-volatility nonconstant benchmark coverage.

### Final Validation

- Completed queued items: AUT-001, AUT-002, AUT-003, AUT-005, AUT-006, AUT-019, AUT-016, AUT-018, AUT-007, AUT-008, AUT-010, AUT-011, AUT-012, AUT-013, AUT-014, AUT-015, AUT-017, AUT-004, AUT-009.
- Skipped/non-queued inventory remains as planned: AUT-020 through AUT-025 are blocked by missing optional tooling, product-policy decisions, pre-existing dirty files, or production/release/Docker risk.
- `uv --version` failed because `uv` is not on PATH in this shell; final checks used `.venv\Scripts\python.exe` fallbacks.
- Passed: `git -c safe.directory=//wsl.localhost/Ubuntu/home/jer/repos/finbot diff --check`; Windows Git still emitted the known `CLAUDE.md`/`GEMINI.md` symlink `Function not implemented` messages and LF-to-CRLF warnings.
- Reviewed: `git diff --stat`, `git diff --name-only`, `git ls-files -m -o --exclude-standard`, and final `git status --short --branch`.
- Passed: `.venv\Scripts\python.exe -m ruff check . --exclude notebooks/`.
- Passed: `.venv\Scripts\python.exe -m ruff format --check . --exclude notebooks/`.
- Passed: `.venv\Scripts\python.exe -m bandit -r finbot -ll` with no medium/high issues.
- Passed: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_data_quality.py tests/unit/test_realtime_data_cache.py -q -p no:cacheprovider` (32 passed).
- Passed: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_var.py tests/unit/test_correlation_diversification.py tests/unit/test_rolling_metrics.py tests/unit/test_benchmark.py -q -p no:cacheprovider` (106 passed).
- Passed: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_factor_regression.py tests/unit/test_factor_attribution.py tests/unit/test_factor_risk.py -q -p no:cacheprovider` (81 passed).
- Passed: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_core_contracts.py tests/unit/test_cost_models.py -q -p no:cacheprovider` (50 passed).
- Passed: `DYNACONF_ENV=development .venv\Scripts\python.exe -m pytest tests/unit/test_web_backend_serializers.py -q -p no:cacheprovider` (21 passed).
- Secret-pattern scan over changed source, tests, and this plan found no API-key, token, password, or private-key patterns.
- Dead-code/regression review: ruff found no unused imports/helpers; changed source behavior is covered by focused regression tests.
- Final dirty inventory still includes pre-existing dirty files not touched by this run: `CLAUDE.md`, `GEMINI.md`, `scripts/generate_changelog.sh`, `scripts/run_docker_security_scan.sh`, `scripts/test_release_workflow.sh`, `scripts/test_testpypi_workflow.sh`, and `web/frontend/scripts/run-playwright-server.sh`.
- Post-audit rerun passed the full touched-area pytest set in one command (290 passed), plus whole-repo ruff check, ruff format check, Bandit, `git diff --check`, and changed-file secret scan.
- Follow-up: installed `uv 0.11.25` for both Windows and WSL. Windows `uv` can run from `C:\Users\jer\.local\bin\uv.exe`, but repeated `uv run` on the UNC checkout left wrapper lock processes, so preferred validation was rerun from WSL with `UV_PROJECT_ENVIRONMENT=$HOME/.cache/uv-envs/finbot` to avoid touching the repo `.venv`.
- Passed after `uv` install: WSL `uv sync --group dev`; WSL `uv run ruff check . --exclude notebooks/`; WSL `uv run ruff format --check . --exclude notebooks/`; WSL `uv run bandit -r finbot -ll`; WSL `uv run pytest` for the 12 touched test modules (290 passed).
- Mypy follow-up: WSL `uv run mypy finbot/` now runs and reports 3 errors in `finbot/adapters/nautilus/nautilus_adapter.py` (`Unexpected keyword argument "frozen"` at lines 396, 594, and 967), outside this queue's touched files. WSL `uv run mypy` on the 8 touched source files passed with no issues.
