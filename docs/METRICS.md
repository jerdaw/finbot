# Public Metrics Snapshot

This file is the manual source of truth for public-facing counts and labels that
appear in README files, docs summaries, and portfolio-facing materials.

**Last verified:** 2026-04-16
**Status:** Manual snapshot until CI-backed automation is added.

## Verified Counts

| Metric | Current Value | Scope | Verification Method |
| --- | --- | --- | --- |
| Backtesting strategies | 13 | Concrete strategy modules under `finbot/services/backtesting/strategies/` excluding `__init__.py` | Directory inventory on 2026-04-16 |
| Backend routers | 12 | Routers included by `web/backend/main.py` | Source review on 2026-04-16 |
| Frontend pages | 13 total | Dashboard home + 12 task pages under `web/frontend/src/app/` | File inventory on 2026-04-16 |
| Core notebooks | 6 | Primary numbered notebooks `01` through `06` | Repository inventory on 2026-04-16 |
| Supporting notebooks | 2 | `corporate_actions_and_missing_data_demo.ipynb`, `cost_model_examples.ipynb` | Repository inventory on 2026-04-16 |

## Public-Writing Policy

Use **exact numbers** only where the count is stable and easy to verify.

- Safe to keep exact: strategy count, router count, page count, numbered core
  notebook count.
- Prefer qualitative wording: automated test count, code coverage percentage,
  total documentation pages, and other values that drift quickly without an
  automated update path.

## Recommended Public Language

- **Test suite**: "large automated test suite" or "CI-validated automated
  tests"
- **Coverage**: "coverage tracked in CI" or "coverage monitored in CI"
- **Documentation**: "extensive documentation" or "published docs and project
  notes"

## Files That Should Follow This Snapshot

- `README.md`
- `web/README.md`
- `web/frontend/README.md`
- `notebooks/README.md`
- `docs_site/index.md`
- `docs/applications/*.md`

If a public-facing file needs a new exact number, verify it here first.