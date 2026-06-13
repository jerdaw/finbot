# Autonomous Maintenance Follow-Up

**Status:** Complete
**Date:** 2026-06-13
**Related records:** `docs/planning/roadmap.md`, `docs/planning/archive/public-github-cleanup-2026-06-04.md`, `docs/planning/archive/archived-bb-backbetter-incorporation-audit-2026-04-27.md`

## Scope

This pass closed the safe autonomous follow-ups that did not require product,
branding, hosting, licensing, or repository-governance decisions.

## Changes

- Added a concise missing-data policy tradeoff reference to both the repository
  guide and the published docs-site guide.
- Added small contributor examples for current Yahoo Finance, FRED, Alpha
  Vantage, and BLS wrappers in the published data-collection utility page.
- Added deterministic queue-logging regression coverage that verifies log
  records are enqueued instead of synchronously emitted by downstream handlers.
- Added focused tests for implemented outlier and data-integrity utilities.
- Moved backtesting portfolio presets/options out of the large page module into
  a local options module.
- Moved remaining pure backtesting/share helper functions into existing utility
  modules and fixed the extracted comparison table's `DataTable` column
  contract.

## Verification

- `.\.venv\Scripts\python.exe -m pytest tests/unit/test_infrastructure_api_manager_and_logging.py tests/unit/test_data_cleaning_utilities.py -q`
  - Result: 19 passed.
- `.\.venv\Scripts\ruff.exe check tests/unit/test_infrastructure_api_manager_and_logging.py tests/unit/test_data_cleaning_utilities.py`
  - Result: passed.
- Gitleaks v8.30.1 git-history scan from WSL:
  - Scope: 272 commits, about 21.14 MB.
  - Result: no leaks found.
- Gitleaks v8.30.1 current tracked/unignored worktree scan from a temporary
  `git ls-files` copy:
  - Scope: about 7.32 MB.
  - Result: no leaks found.
- Tracked parquet golden datasets were read with `pyarrow` through pandas:
  - `QQQ_history_1d.parquet`: 6,772 rows, no nulls.
  - `SPY_history_1d.parquet`: 8,314 rows, no nulls.
  - `TLT_history_1d.parquet`: 5,921 rows, no nulls.
- Frontend TypeScript check from a local temp copy of `web/frontend` using the
  pinned `pnpm@10.33.0` package-manager version:
  - `pnpm typecheck`
  - Result: passed.

## Tooling Notes

- Windows Docker was installed but the Docker Desktop Linux engine was not
  running, so Gitleaks was downloaded as a temporary official release binary
  instead of run through Docker.
- A direct Windows/UNC `pnpm install` failed because pnpm could not treat the
  WSL UNC path as a valid Windows disk. Frontend validation was run from a
  temporary Windows-path copy of `web/frontend`.
- `mkdocs build --strict` could not complete from the WSL UNC path because
  Material for MkDocs/Jinja failed to load an internal template through the
  `\\?\\UNC` site-packages path, even though the template file exists in the
  virtual environment. This appears to be an environment/path issue rather than
  a markdown-content failure.

## Remaining Human or External Decisions

- Decide whether old Backtrader PDFs should be referenced externally. Do not
  commit PDFs without license and storage review.
- Continue broad `web/frontend/src/app/backtesting/page.tsx` component
  extraction before the next large backtesting feature tranche. This pass
  reduced duplicated static/helper code but did not finish full page
  decomposition.
