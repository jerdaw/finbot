# Finbot Roadmap

**Created:** 2026-02-10
**Last Updated:** 2026-02-11
**Status:** All priorities complete

Improvements, fixes, and enhancements identified from a comprehensive project evaluation. Organized by priority tier. All items have been implemented — see Completed Items table below and git history for details.

---

## Priority 0: Bugs and Architectural Hazards ✓

All 6 items complete. Fixed logger duplication, import-time side effects, dangerous error handling, dual config system, ruff version mismatch, and added Dependabot.

## Priority 1: Critical Gaps ✓

All 3 items complete. Expanded test coverage (18 → 262 tests, 34.57% coverage), created 5 example notebooks with findings, and produced 3 research summaries.

**Remaining (Deferred — Not Blocking):**
- [ ] Add tests for `bond_ladder_simulator` end-to-end (requires yield data from FRED)
- [ ] Add tests for `backtest_batch`: parallel execution, result aggregation
- [ ] Add tests for `rebalance_optimizer`
- [ ] Add tests for `approximate_overnight_libor` (requires FRED data)
- [ ] Add tests for data collection utilities: `get_history`, `get_fred_data` (requires mock API responses)
- [ ] Populate `tests/integration/` with at least one end-to-end pipeline test (requires data files)
- [ ] Increase coverage target from 30% to 60% as more tests are added
- [ ] Consider publishing research findings as a blog post or short paper for external visibility

## Priority 2: High-Impact Improvements ✓

All 6 items complete. Added CLI interface (4 commands), fixed code smells, refactored fund simulations to data-driven config, improved git history (CHANGELOG.md), completed incomplete components, added Makefile.

**Remaining (Deferred — Not Blocking):**
- [ ] Apply data-driven config pattern to `sim_specific_bond_indexes.py` (only 3 functions, not worth refactoring)
- [ ] Adopt conventional commit format going forward

## Priority 3: Moderate Improvements ✓

All 7 items complete. Improved documentation (160 module docstrings, MkDocs site, ADRs), strengthened type safety (146 → 0 mypy errors), added performance benchmarks, improved CI/CD pipeline, improved pre-commit hooks, modernized pyproject.toml metadata, consolidated package layout.

**Remaining (Deferred — Not Blocking):**
- [ ] Enable stricter mypy settings (`disallow_untyped_defs`, etc.)
- [ ] Add `py.typed` marker file for PEP 561 compliance
- [ ] Pin CI action versions to SHA hashes
- [ ] Add scheduled CI for daily update pipeline (requires API keys in CI)

## Priority 4: Polish and Extensibility ✓

All 6 items complete. Added containerization, Streamlit web dashboard (6 pages), health economics extension (QALY simulator, CEA, treatment optimizer), additional strategies (DualMomentum, RiskParity, multi-asset Monte Carlo, inflation-adjusted returns), migrated from Poetry to uv, added data quality/observability.

**Remaining (Deferred — Not Blocking):**
- [ ] Add options overlay strategy (covered calls, protective puts) — requires options pricing model, Greeks calculations, and options chain data
- [ ] Investigate epidemiological backtesting — not feasible with Backtrader (finance-specific); would need purpose-built SIR/SEIR simulator

---

## Completed Items

| Item | Completed | Notes |
|------|-----------|-------|
| Fix logger code duplication (0.1) | 2026-02-10 | Consolidated to `libs/logger/utils.py`, changed `InfoFilter` to `NonErrorFilter` |
| Fix import-time side effects (0.2) | 2026-02-10 | Converted to lazy function `get_alpha_vantage_rapi_headers()` |
| Fix dangerous error handling (0.3) | 2026-02-10 | Replaced 8 bare `except Exception:` blocks with specific exceptions |
| Consolidate dual config system (0.4) | 2026-02-10 | Created `settings_accessors.py`, deleted 5 obsolete config files |
| Update ruff and fix version mismatch (0.5) | 2026-02-10 | Updated to v0.11, expanded rules, fixed all 103 violations → 0 |
| Add Dependabot configuration (0.6) | 2026-02-10 | Weekly pip + GitHub Actions updates, grouped minor/patch |
| Expand test coverage (1.1) | 2026-02-11 | 18 → 262 tests, 34.57% coverage, 14 test files |
| Add example notebooks (1.2) | 2026-02-10 | 5 notebooks (fund sim, DCA, backtests, Monte Carlo, bond ladder) |
| Produce research summaries (1.3) | 2026-02-10 | 3 research docs (~50 pages): ETF accuracy, DCA findings, strategy results |
| Add CLI interface (2.1) | 2026-02-10 | Click-based CLI: simulate, backtest, optimize, update commands |
| Fix code smells (2.2) | 2026-02-10 | Logger, risk-free rate, vectorization, named constants, DCAParameters dataclass |
| Refactor fund simulations (2.3) | 2026-02-10 | FundConfig dataclass + FUND_CONFIGS registry, ~288 → ~80 lines |
| Improve git history (2.4) | 2026-02-11 | Created comprehensive CHANGELOG.md |
| Complete incomplete components (2.5) | 2026-02-10 | Added NTSX to pipeline, removed empty dirs, clarified rebalance optimizer |
| Add Makefile (2.6) | 2026-02-10 | 14 targets covering all development workflows |
| Improve documentation (3.1) | 2026-02-11 | 160 module docstrings, MkDocs site, expanded README, ADR-002, utils README |
| Strengthen type safety (3.2) | 2026-02-11 | 146 → 0 mypy errors across 295 files, fixed CLI backtest/optimize commands |
| Add performance benchmarks (3.3) | 2026-02-10 | Fund sim: 40yr in ~110ms, DCA: ~70-80 combos/sec |
| Improve CI/CD pipeline (3.4) | 2026-02-10 | 8 CI checks: lint, format, type, security, audit, tests, coverage, metadata |
| Improve pre-commit hooks (3.5) | 2026-02-10 | 17 hooks (15 auto + 2 manual), mixed-line-ending for WSL |
| Modernize pyproject.toml (3.6) | 2026-02-10 | PEP 621 metadata, 0 deprecation warnings |
| Consolidate package layout (3.7) | 2026-02-11 | Single `finbot` namespace, ADR-004 |
| Add containerization (4.1) | 2026-02-11 | Multi-stage Dockerfile, docker-compose, 6 Makefile targets |
| Add Streamlit dashboard (4.2) | 2026-02-11 | 6 pages, reusable components, CLI command, Docker service |
| Health economics extension (4.3) | 2026-02-11 | QALY simulator, cost-effectiveness analysis, treatment optimizer |
| Additional strategies/simulators (4.4) | 2026-02-11 | DualMomentum, RiskParity, multi-asset Monte Carlo, inflation-adjusted returns |
| Migrate Poetry to uv (4.5) | 2026-02-11 | Lock 5x faster, sync 4.4x faster, PEP 621 metadata |
| Data quality and observability (4.6) | 2026-02-11 | `finbot status` CLI, freshness registry, DataFrame validation |
