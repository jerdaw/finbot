# Stable Baseline Closeout

**Date:** 2026-06-14
**Status:** Complete

## Scope

This closeout prepares Finbot for an extended dormant period while preserving a
clear restart path.

## Completed Work

- Migrated the generated documentation site from the old MkDocs command surface
  to Zensical.
- Replaced `mkdocs gh-deploy` with GitHub Pages artifact deployment.
- Added ADR-016 for the documentation-platform decision.
- Reconciled P11 from an open decision track to a completed migration.
- Replaced public docs-site symlink wrappers with real Markdown pages so the
  strict Zensical build is stable.
- Tightened docs validation to `uv run zensical build --clean --strict`.
- Split the largest remaining backtesting portfolio-builder component into
  focused child components.
- Added a stable-baseline restart guide for future contributors.
- Hardened workflow token permissions after the final GitHub Security tab
  review by adding explicit read-only defaults and narrowing release/security
  upload writes to the jobs that need them.
- Moved remaining P5/P7 items that require external data, human design assets,
  manual media production, or risky published-history rewrites into explicit
  deferrals.

## Deferred Scope

- External simulation validation baselines.
- Human-approved project logo or brand guide.
- Manual overview/tutorial/contributing videos and project poster.
- Published-history rewrite work.
- Old Backtrader PDF external-reference handling until license/storage review.
- Broad dependency updates until GitHub Actions budget allows narrow validated
  replay branches.
- GitHub branch-protection/required-review policy and OpenSSF Scorecard Docker
  digest/hash-pinning recommendations, which are governance and supply-chain
  hardening choices rather than unfinished baseline features.
- Production hosting/domain/TLS/secret-management decisions.

## Validation

- `zensical build --clean --strict` passed in a clean temporary docs
  environment with Zensical 0.0.45 and `mkdocstrings-python` 2.0.2.
- Targeted Python tests, frontend typecheck in a temporary local copy, YAML
  parsing, pre-commit hooks, staged-diff review, and secret scanning passed.
- GitHub CI passed on the final stable-baseline commit, including frontend
  typecheck/build and mocked Chromium workflow tests. Local Playwright browser
  execution remains intentionally left to GitHub CI.

## Restart Pointers

- Restart guide: `docs/guides/stable-baseline-restart-guide.md`
- Roadmap: `docs/planning/roadmap.md`
- Docs platform decision: `docs/adr/ADR-016-zensical-docs-platform.md`
