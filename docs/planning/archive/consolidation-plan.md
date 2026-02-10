# Consolidation Plan: Three Repos to One Finbot (Archived)

**Status:** Complete
**Completed:** 2026-02-09
**Related ADR:** [ADR-001](../../adr/ADR-001-consolidate-three-repos.md)

## Summary

Consolidated three repos (`finbot`, `bb`, `backbetter`) from `/home/jer/localsync/old-finance/` into a single new repo at `/home/jer/localsync/finbot/`.

## Phases Completed

| Phase | Description | Key Outcomes |
| --- | --- | --- |
| 1 | Scaffold new repo | pyproject.toml, directory structure, poetry install |
| 2 | Port bb infrastructure | config, constants, libs, 174 utils files |
| 3 | Port simulation system | 21 files, numba removed, pickle to parquet |
| 4 | Port backtesting engine | 31 files, strategies flattened, imports unified |
| 5 | Port orchestration + optimization | update_daily.py, DCA optimizer |
| 6 | Quality assurance | ruff clean, all key imports verified |

## What Was Dropped

| Source | What | Why |
| --- | --- | --- |
| finbot | `data_mining/` | bb's `data_collection_utils` supersedes |
| finbot | `data_manipulation/` | Ortex evaluators dead without Scrapy |
| finbot | `utilities/` | bb has enhanced versions |
| finbot | `secrets/` | Replaced by Dynaconf + path_constants |
| finbot | Strategy runner scripts | Hardcoded test params, not reusable |
| bb | flask dependency | Never meaningfully used |
| backbetter | Entire repo | 6 LOC scaffold |
