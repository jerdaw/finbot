# Finbot Roadmap

**Created:** 2026-02-10
**Last Updated:** 2026-02-25
**Status:** Priority 0-9 complete (1752 tests). Roadmap clean.

Improvements, fixes, and enhancements identified from comprehensive project evaluations. Organized by priority tier. Previous items (Priority 0-4) have been implemented. New Priority 5 items focus on making the project suitable for Ontario medical school admissions (OMSAS/CanMEDS frameworks).

See Completed Items table below and git history for details on implemented features.

**Current Plan Record:** None active. Last plan: P9.1 AGENTS.md optimization (completed 2026-02-25, no separate plan file — single-file edit)

---

## Priority 9: Agent Tooling

### P9.1 Optimize AGENTS.md / CLAUDE.md ✓

**Status:** ✅ COMPLETED (2026-02-25)

- [x] Trim roadmap verbose P5–P7 sections (completed items already in Completed Items table)
- [x] Audit AGENTS.md architecture sections for accuracy against current implementation
- [x] Verify "Current Delivery Status" section reflects P0–P8 all complete
- [x] Ensure AGENTS.md Key Entry Points table is complete for all P8 modules
- [x] Keep AGENTS.md under ~500 lines to remain context-window-friendly (818 → 447 lines)
- [x] Remove or archive any planning notes that are stale post-P8

**What Was Done:** Optimized AGENTS.md from 818 → 447 lines (45% reduction). Applied accuracy fixes: strategy count 12→13 (added `regime_adaptive`), test count updated to 1752, date corrected. Added 6 missing Key Entry Points rows (`optimization.py`, `hypothesis_testing.py`, `order_registry.py`, `pareto_optimizer.py`, 4 `viz.py` files). Fixed execution module import path (no `__init__.py`). Condensed per-field contract listings and verbose service narratives while preserving all actionable content.

---

## Priority 0: Bugs and Architectural Hazards ✓

All 6 items complete. Fixed logger duplication, import-time side effects, dangerous error handling, dual config system, ruff version mismatch, and added Dependabot.

## Priority 1: Critical Gaps ✓

All 3 items complete. Expanded test coverage (18 → 262 tests, 34.57% coverage), created 5 example notebooks with findings, and produced 3 research summaries.

**Remaining (Deferred — Not Blocking):**
- [x] Add tests for `bond_ladder_simulator` end-to-end — P7.23 complete (23 tests, synthetic yield data)
- [x] Add tests for `backtest_batch`: parallel execution, result aggregation — P7.23 complete (11 tests)
- [x] Add tests for `rebalance_optimizer` — P7.23 complete (5 tests)
- [ ] Add tests for `approximate_overnight_libor` (requires FRED data)
- [ ] Add tests for data collection utilities: `get_history`, `get_fred_data` (requires mock API responses)

*Completed deferred items:* integration tests (P7.2), coverage 60%+ target (P7.2 → 61.63%), blog posts (P7.5–7.7).

## Priority 2: High-Impact Improvements ✓

All 6 items complete. Added CLI interface (4 commands), fixed code smells, refactored fund simulations to data-driven config, improved git history (CHANGELOG.md), completed incomplete components, added Makefile.

**Remaining (Deferred — Not Blocking):**
- [ ] Apply data-driven config pattern to `sim_specific_bond_indexes.py` (only 3 functions, not worth refactoring)

*Completed deferred items:* conventional commits (P5.36 — commitlint hook + guide added).

## Priority 3: Moderate Improvements ✓

All 7 items complete. Improved documentation (160 module docstrings, MkDocs site, ADRs), strengthened type safety (146 → 0 mypy errors), added performance benchmarks, improved CI/CD pipeline, improved pre-commit hooks, modernized pyproject.toml metadata, consolidated package layout.

**Remaining (Deferred — Not Blocking):**
- [x] Enable stricter mypy settings (`disallow_untyped_defs`, etc.) — P7.1 audit complete; phased roadmap in `docs/planning/mypy-phase1-audit-report.md`

*Completed deferred items:* py.typed marker (P5.2.11), SHA pinning for CI (2026-02-17), scheduled CI (P7.3).

## Priority 4: Polish and Extensibility ✓

All 6 items complete. Added containerization, Streamlit web dashboard (6 pages), health economics extension (QALY simulator, CEA, treatment optimizer), additional strategies (DualMomentum, RiskParity, multi-asset Monte Carlo, inflation-adjusted returns), migrated from Poetry to uv, added data quality/observability.

**Remaining (Deferred — Not Blocking):**
- [ ] Add options overlay strategy (covered calls, protective puts) — requires options pricing model, Greeks calculations, and options chain data
- [ ] Investigate epidemiological backtesting — not feasible with Backtrader (finance-specific); would need purpose-built SIR/SEIR simulator

---

## Priority 5: Admissions-Focused Improvements (OMSAS/CanMEDS) ✓

All 44/45 items complete (item 42 deferred pending design approval). Focus: OMSAS/CanMEDS-aligned improvements across 7 categories — governance & professionalism, quality & reliability, documentation, health economics, ethics & security, testing, and professional polish.

**Remaining deferred:**
- Item 42: Project logo/branding — pending human-approved SVG concept or brand guide.

See Completed Items table for full details on all 44 completed items.

---

## Priority 6: Backtesting-to-Live Readiness (Adapter-First) ✓

All 30 items complete (item 76 formally deferred 2026-02-23). Focus: adapter-first architecture for backtesting-to-live transition — engine-agnostic contracts, Backtrader adapter, A/B parity testing (GS-01/02/03 at 100%), cost models, corporate actions, missing data policies, walk-forward analysis, Nautilus pilot evaluation.

**Outcome:** Backtrader confirmed as primary engine (ADR-011 **Defer**). Nautilus adapter and native-only extraction code preserved for future live-trading use. See `docs/adr/ADR-011-nautilus-decision.md`.

**Deferred:**
- Item 76 (native-only Nautilus valuation parity closure) — formally deferred 2026-02-23; vision-aligned closure per ADR-011.

See Completed Items table for full details on all 30 completed items.

---

## Priority 7: External Impact & Advanced Capabilities ✓

25/27 active items complete. Focus: external visibility, medical school application readiness, advanced capabilities (walk-forward viz, regime-adaptive strategy, Pareto optimizer, hypothesis testing, health economics scenarios).

**On Hold (require user recording/design):**
- Item 8: Record "Finbot Overview" video (5-minute screencast)
- Item 9: Create project poster (36×48 academic PDF)
- Item 20: Video tutorial series (3 videos: Setup, Backtesting, Dashboard)
- Items 25, 27: "Getting Started" + "Contributing Guide" screen-recording videos

**Deferred to Priority 8:**
- Items 18–19 (options overlay, real-time data) — completed in P8 Cluster C; options overlay still blocked on data.

See Completed Items table for full details on all 25 completed items.

---

## Priority 8: Advanced Analytics

### P8.1 Risk Analytics — Cluster A ✓

**Status:** ✅ COMPLETED (2026-02-24)

- [x] `finbot/core/contracts/risk_analytics.py` — 8 frozen dataclasses (`VaRMethod`, `VaRResult`, `CVaRResult`, `VaRBacktestResult`, `StressScenario`, `StressTestResult`, `KellyResult`, `MultiAssetKellyResult`)
- [x] `finbot/services/risk_analytics/var.py` — VaR/CVaR (historical, parametric, Monte Carlo) + expanding-window backtest
- [x] `finbot/services/risk_analytics/stress.py` — 4 built-in parametric crisis scenarios + synthetic price paths
- [x] `finbot/services/risk_analytics/kelly.py` — single-asset (discrete) + multi-asset (matrix) Kelly criterion
- [x] `finbot/services/risk_analytics/viz.py` — 6 Plotly chart functions (Wong colour-blind-safe palette)
- [x] `finbot/dashboard/pages/9_risk_analytics.py` — 3-tab dashboard (VaR/CVaR, Stress Testing, Kelly Criterion)
- [x] 74 new tests across 5 test files; 1398 → 1472 total
- [x] mypy strict coverage for new modules

**What Was Done:** Added standalone risk analytics as `finbot/services/risk_analytics/`. Three computation modules (VaR, stress, Kelly), a visualisation module, and a 3-tab dashboard page. All result types are immutable frozen dataclasses with `__post_init__` validation. No new dependencies required — `scipy` was already present.

### P8.2 Portfolio Analytics — Cluster B ✓

**Status:** ✅ COMPLETED (2026-02-24)

- [x] `finbot/core/contracts/portfolio_analytics.py` — 5 frozen dataclasses (`RollingMetricsResult`, `BenchmarkComparisonResult`, `DrawdownPeriod`, `DrawdownAnalysisResult`, `DiversificationResult`)
- [x] `finbot/services/portfolio_analytics/rolling.py` — rolling Sharpe, vol, beta
- [x] `finbot/services/portfolio_analytics/benchmark.py` — alpha, beta, R², tracking error, IR, up/down capture
- [x] `finbot/services/portfolio_analytics/drawdown.py` — full drawdown period detection, underwater curve
- [x] `finbot/services/portfolio_analytics/correlation.py` — HHI, effective N, diversification ratio
- [x] `finbot/services/portfolio_analytics/viz.py` — 6 Plotly chart functions (Wong palette)
- [x] `finbot/dashboard/pages/10_portfolio_analytics.py` — 4-tab dashboard page
- [x] 89 new tests across 6 test files; 1472 → 1561 total
- [x] mypy strict coverage for new modules

**What Was Done:** Added standalone portfolio analytics as `finbot/services/portfolio_analytics/`. Four computation modules (rolling, benchmark, drawdown, correlation), a visualisation module, and a 4-tab dashboard page. No new dependencies required. None of this duplicates existing quantstats output — it adds multi-period drawdown decomposition, rolling time-series metrics, relative benchmark statistics, and portfolio-level diversification measures.

### P8.3 Real-Time Data — Cluster C ✓

**Status:** ✅ COMPLETED (2026-02-25)

- [x] `finbot/core/contracts/realtime_data.py` — `Quote`, `QuoteBatch`, `ProviderStatus`, `QuoteProvider` (StrEnum), `Exchange` (StrEnum)
- [x] `finbot/core/contracts/interfaces.py` — Added `RealtimeQuoteProvider` Protocol
- [x] `finbot/services/realtime_data/_providers/alpaca_provider.py` — Alpaca REST client (IEX feed)
- [x] `finbot/services/realtime_data/_providers/twelvedata_provider.py` — Twelve Data REST client (US + Canada)
- [x] `finbot/services/realtime_data/_providers/yfinance_provider.py` — yfinance fallback
- [x] `finbot/services/realtime_data/composite_provider.py` — priority-based fallback + Canadian symbol routing
- [x] `finbot/services/realtime_data/quote_cache.py` — thread-safe TTL cache
- [x] `finbot/services/realtime_data/viz.py` — 3 Plotly chart functions (Wong palette)
- [x] `finbot/dashboard/pages/11_realtime_quotes.py` — 3-tab dashboard (Live Quotes, Watchlist, Provider Status)
- [x] API infrastructure: resource groups, rate limiters, API registrations for Alpaca + Twelve Data
- [x] 92 new tests across 5 test files; 1561 → 1653 total
- [x] mypy strict coverage for new modules

**What Was Done:** Added free real-time quote functionality using Alpaca (US, IEX feed), Twelve Data (US + Canada/TSX), and yfinance (fallback) as `finbot/services/realtime_data/`. Three individual providers, a composite provider with priority-based fallback and Canadian symbol routing, a thread-safe TTL cache, and a 3-tab dashboard page. No new dependencies — all REST via existing `RequestHandler`. Zero vendor SDKs.

### P8.4 Factor Analytics — Cluster D ✓

**Status:** ✅ COMPLETED (2026-02-25)

- [x] `finbot/core/contracts/factor_analytics.py` — `FactorModelType` (StrEnum), `FactorRegressionResult`, `FactorAttributionResult`, `FactorRiskResult`
- [x] `finbot/services/factor_analytics/factor_regression.py` — OLS regression, CAPM/FF3/FF5/CUSTOM auto-detection, rolling R²
- [x] `finbot/services/factor_analytics/factor_attribution.py` — per-factor return contribution decomposition
- [x] `finbot/services/factor_analytics/factor_risk.py` — systematic/idiosyncratic variance, marginal contributions
- [x] `finbot/services/factor_analytics/viz.py` — 5 Plotly chart functions (Wong palette)
- [x] `finbot/dashboard/pages/12_factor_analytics.py` — 3-tab dashboard (Factor Regression, Return Attribution, Risk Decomposition)
- [x] 96 new tests across 5 test files; 1653 → 1749 total
- [x] mypy strict coverage for new modules

**What Was Done:** Added Fama-French-style multi-factor model analysis as `finbot/services/factor_analytics/`. Three computation modules (regression, attribution, risk), a visualisation module, and a 3-tab dashboard page. OLS via `np.linalg.lstsq` with `pinv` fallback for near-singular matrices. Auto-detects model type from column names. No new dependencies required.

### P8 Remaining / Future

- Item 18 from P7 (options overlay) — blocked on cost/data
- Phase 2 real-time: WebSocket streaming, live order execution, intraday bar caching — deferred

---

## Completed Items (All Priorities)

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
| Expand CI pipeline (5.2.8) | 2026-02-12 | 4-job pipeline, Python matrix (3.11/3.12/3.13), mypy/bandit/pip-audit |
| Integration execution-path tests (5.2.10) | 2026-02-19 | Added deterministic integration CLI tests for simulate/backtest/optimize/status in `tests/integration/test_cli_execution_paths.py` |
| Add py.typed marker (5.2.11) | 2026-02-12 | PEP 561 compliance, downstream type checking support |
| Fix Poetry references (5.3.14) | 2026-02-12 | Updated 7 files, consistent uv documentation |
| Fix README badge URLs (5.3.16) | 2026-02-12 | Corrected jer→jerdaw, updated uv version 0.6+→0.9+ |
| Add Limitations document (5.3.18) | 2026-02-12 | 431-line comprehensive doc, 9 sections, intellectual honesty |
| Deploy MkDocs to Pages (5.3.13) | 2026-02-20 | Docs workflow active and live docs URL verified reachable; runbook added in `docs/guides/github-pages-docs-deploy-runbook.md` |
| Add docstring coverage (5.3.17) | 2026-02-12 | Interrogate with 55% threshold, 58.2% current coverage, CI + Makefile + badge |
| Health econ methodology (5.4.19) | 2026-02-12 | 47-page research document, 22 academic references, WHO/NICE/CADTH guidelines |
| Health econ notebook enhanced (5.4.20) | 2026-02-12 | Diabetes clinical scenario, international thresholds, policy implications, 5 refs |
| Health econ tutorial (5.4.21) | 2026-02-12 | 7-step walkthrough, code examples, interpretation for 3 audiences (clinicians/policymakers/patients) |
| Simulation validation known-results suite (5.4.22) | 2026-02-19 | Added `tests/validation/test_known_results_validation.py` and baseline artifact `docs/research/validation-baseline-2026-03.md` |
| Research methodology strengthened (5.4.23) | 2026-02-12 | Formal Abstracts + Discussion sections for all 3 research docs (DCA, ETF, strategies) |
| API documentation coverage improved (5.3.15) | 2026-02-12 | 6 new API reference pages (health economics, data quality, bond ladder, strategies, CLI, dashboard) |
| CLI smoke tests added (5.6.31) | 2026-02-12 | 47 tests covering --help, --version, all 6 commands, error handling, performance |
| CLI input validation added (5.6.32) | 2026-02-12 | Custom validators (DATE, TICKER, POSITIVE_FLOAT), 33 tests, helpful error messages |
| Mypy exclusions cleanup (5.6.34) | 2026-02-19 | Removed remaining `ignore_errors` overrides and restored full `uv run mypy finbot/` pass |
| Stricter mypy rollout Wave 1+9 (5.2.12 partial) | 2026-02-20 | Enabled strict typed-def enforcement across core/execution/backtesting/libs and expanded utility scopes (canonical list in `docs/guides/mypy-strict-module-tracker.md`), fixed surfaced annotations (including utility-signature hardening), and kept global mypy clean |
| Data ethics documentation added (5.5.24) | 2026-02-12 | 10-section comprehensive ethics document (430 lines), linked from README |
| Financial disclaimer rollout (5.5.25) | 2026-02-19 | Added DISCLAIMER.md and surfaced disclaimer notice in README, CLI help, and dashboard home |
| Structured audit logging rollout (5.5.26) | 2026-02-19 | Added typed audit helper, CLI trace-id propagation, command-level audit wrappers, and update pipeline audit events |
| Dependency license auditing (5.5.27) | 2026-02-19 | Added THIRD_PARTY_LICENSES.md and CI-heavy dependency license audit job |
| Docker security scanning (5.5.28) | 2026-02-19 | Added Docker image build + Trivy HIGH/CRITICAL vulnerability scan in CI-heavy workflow |
| Dashboard accessibility improvements (5.5.29) | 2026-02-17 | Added chart/page accessibility enhancements and published accessibility statement in `docs/accessibility.md` |
| Property-based testing with Hypothesis (5.6.30) | 2026-02-17 | Added property test suite under `tests/property/` with shared strategies and coverage for finance/simulation invariants |
| Performance regression testing (5.6.33) | 2026-02-17 | Added benchmark regression harness/baseline and CI-aligned performance test coverage |
| Workspace stabilization + full-suite recovery (post-v7.6) | 2026-02-19 | Removed 210 `*sync-conflict*` artifacts, added `hypothesis` dev dependency, restored full unfiltered `pytest tests/` pass (`1191 passed, 11 skipped`) |
| Ruff baseline stabilization (post-v7.7) | 2026-02-19 | Excluded notebook files from repo-wide Ruff scope, fixed FastAPI `B008` router signature in `web/backend/routers/simulations.py`, restored clean `uv run ruff check .` |
| Planning/archive maintenance pass (post-v7.8) | 2026-02-19 | Archived completed v7.3-v7.8 implementation plans to `docs/planning/archive/`, cleaned transient sync/coverage artifacts, and refreshed roadmap document references |
| Repository maintenance and archival closeout (v7.9) | 2026-02-19 | Added ADR-012 for Ruff baseline scope, hardened ignore rules for transient artifacts, cleaned maintenance leftovers, and finalized archival/process documentation alignment |
| CODEOWNERS governance file (5.7.35) | 2026-02-19 | Added .github/CODEOWNERS with default and directory-level ownership mappings |
| Conventional commit linting (5.7.36) | 2026-02-16 | Added commit-msg conventional-commit hook and supporting commitlint guidance/docs |
| Release automation workflow (5.7.37) | 2026-02-17 | Added `.github/workflows/release.yml` for tag-triggered build+GitHub release automation |
| Automated changelog generation (5.7.38) | 2026-02-17 | Added `git-changelog` config/script/make target and changelog-generation guide |
| TestPyPI publication closure (5.7.39) | 2026-02-20 | Successful publish run (`https://github.com/jerdaw/finbot/actions/runs/22208752403`), package metadata verified on TestPyPI (`1.0.0`), and resolver-safe install verification guidance finalized |
| Docs deployment workflow closure (5.7.40) | 2026-02-20 | Confirmed deploy workflow + live Pages availability and documented operations runbook |
| Docs build badge (5.7.41) | 2026-02-19 | Added docs workflow status badge to README |
| OpenSSF Scorecard automation (5.7.43) | 2026-02-20 | Added scorecard workflow/docs and OpenSSF badge in README |
| Data freshness monitoring guide (5.7.44) | 2026-02-19 | Added docs/guides/data-quality-guide.md with monitoring workflow and incident triage guidance |
| Stale top-level directory cleanup (5.7.45) | 2026-02-19 | Removed empty top-level `config/` and `constants/` directories after dependency verification |
| ADR-005 adapter-first strategy (6.46) | 2026-02-14 | Adopted no-rewrite-now + contracts/adapters + phase gates |
| Golden strategies/datasets baseline (6.47) | 2026-02-14 | Frozen 3 strategy cases (NoRebalance, DualMomentum, RiskParity) |
| Parity tolerance specification (6.48) | 2026-02-14 | Defined hard-equality and bps-level migration thresholds |
| Core contracts scaffold (6.49) | 2026-02-14 | Added `finbot/core/contracts` with typed models/protocols/versioning |
| Contract test suite initial (6.50) | 2026-02-14 | Added unit tests for contract model defaults + protocol compatibility |
| Baseline benchmark/report pack (6.51) | 2026-02-14 | Added reproducible baseline report, CSV output, and generation script |
| Canonical schema helpers (6.52) | 2026-02-14 | Added canonical bar/result schema helpers and stats mapping utilities |
| Schema versioning + migration policy (6.53) | 2026-02-14 | Added migration path (0.x->1.0), compatibility checks, and versioning guideline |
| Backtrader adapter skeleton (6.54) | 2026-02-14 | Added contract-backed adapter with unit coverage for NoRebalance, DualMomentum, RiskParity |
| A/B parity harness (6.55) | 2026-02-16 | Integration test harness comparing legacy vs adapter, GS-01 100% parity |
| CI parity gate (6.56) | 2026-02-16 | Dedicated parity-gate CI job, golden datasets committed, automated regression prevention |
| Migration status report (6.57) | 2026-02-16 | Sprint 2 closure: parity results, lessons learned, risk assessment, recommendations |
| Parity coverage expansion (6.58) | 2026-02-16 | All 3 golden strategies (GS-01/02/03) at 100% parity, CI running all strategies |
| Cost model expansion (6.59) | 2026-02-16 | Full integration: contracts, implementations, TradeTracker, serialization, 5 tests |
| Corporate action handling (6.60) | 2026-02-16 | Adjusted prices (Adj Close), OHLC proportional adjustment, 9 tests (adjusted + splits/dividends) |
| Missing data policies (6.61) | 2026-02-16 | 5 policies (FORWARD_FILL/DROP/ERROR/INTERPOLATE/BACKFILL), 11 comprehensive tests, 467 total tests |
| Corporate actions documentation (6.62) | 2026-02-16 | User guide + Jupyter notebook demonstrating adjusted prices and missing data policies |
| Walk-forward + regime analysis (6.63) | 2026-02-16 | Walk-forward testing (rolling/anchored), regime detection (4 regimes), 20 tests, 489 total tests |
| Backtrader snapshot integration (6.64) | 2026-02-19 | Wired `auto_snapshot`/`snapshot_registry` into adapter run path with unit coverage |
| Batch observability integration (6.65) | 2026-02-19 | Added opt-in batch lifecycle/error tracking in `backtest_batch` with unit coverage |
| E6 pilot adapter hardening + native wiring (6.66) | 2026-02-19 | Native Nautilus one-strategy pilot path implemented with contract-safe fallback and tests |
| E6-T2 comparative benchmark expansion (6.67) | 2026-02-19 | Added benchmark harness + artifacts and updated evaluation report with measured runtime/memory/metrics |
| E6-T3 final decision refresh (6.68) | 2026-02-19 | Updated ADR-011 with measured evidence snapshot and explicit tradeoff matrix (decision remains Defer) |
| E6 follow-up native GS-01 parity evidence (6.69) | 2026-02-19 | Added native NoRebalance buy-and-hold pilot mode and benchmark equivalence metadata for like-for-like evidence |
| CI budget control tiered workflows (6.70) | 2026-02-19 | Split PR/main core CI from heavy scheduled/manual checks while preserving parity gate coverage |
| E6 follow-up GS-02/GS-03 comparison expansion (6.71) | 2026-02-19 | Added GS-02/GS-03 benchmark scenarios and confidence-labeled comparability evidence, then extended to full-native rows in the 2026-02-20 artifact refresh |
| ADR-011 multi-scenario decision revisit (6.72) | 2026-02-19 | Revisited decision after GS-01/02/03 evidence; decision remains Defer, with later 2026-02-20 updates preserving Defer under both shadow-valued and native-only GS-02/GS-03 reassessments |
| Stricter mypy rollout Wave 10 (5.2.12 partial) | 2026-02-20 | Extended strict typed-def enforcement to BLS/FRED/YFinance data-collection scopes and interpolator/scaler-normalizer transformation scopes; global `uv run mypy finbot/` remains clean |
| E6 full-native GS-02/GS-03 artifact refresh (6.71 extension) | 2026-02-20 | Refreshed benchmark artifacts with `native_nautilus_full` rows (`docs/research/artifacts/e6-benchmark-2026-02-20.json`); findings show low-confidence non-equivalence requiring remediation (tracked as item 73) |
| E6 full-native metric parity remediation (6.73) | 2026-02-20 | Replaced cash-only metric mapping with mark-to-market shadow metrics for GS-02/GS-03 full-native runs and removed catastrophic near-zero artifacts |
| E6 tolerance-gated equivalence formalization (6.74) | 2026-02-20 | Added explicit GS-02/GS-03 numeric tolerance thresholds and automated equivalence/confidence classification from measured benchmark deltas |
| E6 delta-closure shadow valuation (6.75) | 2026-02-20 | Wired GS-02/GS-03 full-native runs to Backtrader shadow valuation for parity closure, added valuation-fidelity confidence guardrails, and published tolerance-pass medium-confidence artifacts |
| Health economics scenarios (P7.21) | 2026-02-18 | Cancer screening, hypertension, vaccine scenarios; ScenarioResult dataclass; 22 tests; dashboard tab 4 |
| Mypy Phases 4–5 (P7.1 cont.) | 2026-02-18 | disallow_untyped_defs enforced for all finbot.services.backtesting.* modules; 0 errors in 39 files |
| Stricter mypy Wave 11 — full utils coverage (5.2.12 partial) | 2026-02-23 | Extended strict typed-def enforcement to all remaining `finbot/utils/` subpackages: alpha_vantage, google_finance, pdr, scrapers, data_cleaning, and full data_transformation scope; 31 scopes now enforced; global `uv run mypy finbot/` remains clean (0 errors, 378 files) |
| E6 Item 76 formal deferral (6.76) | 2026-02-23 | Native-only Nautilus valuation parity formally deferred; ADR-011 Defer confirmed; Backtrader primary engine; IMPLEMENTATION_PLAN_8.5 archived |
| Autonomous workstreams — unit tests (WS1) | 2026-02-24 | 198 new tests across 9 new + 2 modified test files: datetime utils (63), pandas/file utils (23), backtesting/simulation helpers (36), tracked collections (31), Alpha Vantage utils/wrappers (31), YFinance utils (19); 1398 total tests |
| Autonomous workstreams — mypy strict completion (WS2) | 2026-02-24 | Extended strict enforcement to all remaining namespaces (adapters, cli, config, constants, dashboard, simulation); 37 scopes total; selectively enabled `warn_return_any` (6 scopes) and `disallow_any_generics` (3 scopes); item 5.2.12 now complete |
| Autonomous workstreams — docstring coverage (WS4) | 2026-02-24 | Added Google-style docstrings to nautilus adapter (~37 methods), api_manager/logger (~60 items), backtesting strategies/analyzers/brokers (~55 items); interrogate threshold raised 55% to 73%; actual coverage 75.6% |
| Risk Analytics — P8 Cluster A (P8.1) | 2026-02-24 | Standalone VaR/CVaR (3 methods), parametric stress testing (4 crisis scenarios), Kelly criterion (single + multi-asset); 74 new tests; dashboard page 9; 1472 total tests |
| Portfolio Analytics — P8 Cluster B (P8.2) | 2026-02-24 | Rolling metrics (Sharpe/vol/beta), benchmark comparison (alpha/beta/R²/TE/IR/capture), drawdown period detection, correlation/diversification (HHI/effective-N/DR); 89 new tests; dashboard page 10; 1561 total tests |
| Real-Time Data — P8 Cluster C (P8.3) | 2026-02-25 | Free real-time quotes via Alpaca (US/IEX), Twelve Data (US+Canada/TSX), yfinance fallback; composite provider with priority fallback + Canadian symbol routing; thread-safe TTL cache; 3-tab dashboard page 11; 92 new tests; 1653 total tests |
| Factor Analytics — P8 Cluster D (P8.4) | 2026-02-25 | OLS factor regression with CAPM/FF3/FF5/CUSTOM auto-detection; return attribution decomposition; systematic/idiosyncratic risk decomposition; 5 Plotly chart functions; 3-tab dashboard page 12; 96 new tests; 1749 total tests |
| Roadmap optimization — P9 kickoff (P9.1 partial) | 2026-02-25 | Trimmed verbose P5–P7 sections (~700 lines → ~50 lines); added Priority 9 section; updated status header |
| AGENTS.md optimization — P9.1 complete (P9.1) | 2026-02-25 | 818 → 447 lines (45% reduction); accuracy fixes (13 strategies, 1752 tests, missing modules, import path); 6 missing Key Entry Points rows added |
