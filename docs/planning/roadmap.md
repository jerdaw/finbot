# Finbot Roadmap

**Created:** 2026-02-10
**Last Updated:** 2026-02-17
**Status:** Priority 0-6 substantially complete (P5: 93.3%, P6: 100%). Production-ready. Priority 7 in progress (23/27 items, 85%). Batch 3 complete — see `docs/planning/priority-7-batch3-implementation-plan.md` (v1.0).

Improvements, fixes, and enhancements identified from comprehensive project evaluations. Organized by priority tier. Previous items (Priority 0-4) have been implemented. New Priority 5 items focus on making the project suitable for Ontario medical school admissions (OMSAS/CanMEDS frameworks).

See Completed Items table below and git history for details on implemented features.

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

## Priority 5: Admissions-Focused Improvements (OMSAS/CanMEDS) ✅ 93.3%

**Status:** 42/45 items complete — Substantially Complete ✅
**Completed:** 2026-02-17 | **Focus:** OMSAS/CanMEDS alignment for medical school admissions

| Category | Status |
|----------|--------|
| 5.1 Governance & Professionalism | 7/7 ✅ |
| 5.2 Quality & Reliability | 4/5 (Item 12 deferred) |
| 5.3 Documentation & Communication | 6/6 ✅ |
| 5.4 Health Economics & Scholarship | 4/5 (Item 22 requires data) |
| 5.5 Ethics, Privacy & Security | 6/6 ✅ |
| 5.6 Additional Quality & Testing | 5/5 ✅ |
| 5.7 Professional Polish & Deployment | 10/11 (Item 42 requires design) |

**Key achievements:** Coverage 54.54% → 59.20% (+114 tests) · Full governance suite · 7-job CI/CD · Health economics research (22+ citations) · OpenSSF Scorecard ready (8.0-8.5/10)

**Remaining (3 items — not blocking):**
- Item 12: Stricter mypy Phase 1 annotation audit (deferred to P7.1)
- Item 22: Simulation validation against known results (requires historical data files)
- Item 42: Project logo/branding (requires human design approval)

**Detail:** `docs/planning/priority-5-6-completion-status.md` · Archived plans in `docs/planning/archive/`

---

## Priority 6: Backtesting-to-Live Readiness ✅ 100%

**Status:** 18/18 items complete — Complete ✅
**Completed:** 2026-02-16 | **Focus:** Adapter-first architecture for future live trading

| Epic | Status |
|------|--------|
| E0: Baseline and Decision Framing | ✅ |
| E1: Contracts and Schema Layer | ✅ |
| E2: Backtrader Adapter and Parity Harness | ✅ |
| E3: Fidelity Improvements (cost models, corporate actions, walk-forward, regime) | ✅ |
| E4: Reproducibility (experiment tracking, snapshots, batch observability) | ✅ |
| E5: Live-Readiness (orders, latency simulation, risk controls, checkpoints) | ✅ |
| E6: NautilusTrader Pilot and Decision Gate | ✅ |

**Key achievements:** 100% parity on GS-01/02/03 · CI parity gate active · Engine-agnostic contract layer · Hybrid Backtrader + Nautilus approach adopted · Walk-forward and regime analysis complete

**Detail:** `docs/planning/backtesting-live-readiness-backlog.md` · `docs/planning/priority-5-6-completion-status.md` · Archived in `docs/planning/archive/`

---

## Priority 7: External Impact & Advanced Capabilities

New priority tier defined 2026-02-17 to maximize project impact and visibility while adding advanced technical capabilities. Focus on external communication, application readiness, and strategic enhancements.

**Status:** 🟡 In Progress (23/27 items complete, 85%)
**Implementation Plan:** `docs/planning/priority-7-implementation-plan.md` (v1.1); Batch 3 complete — `docs/planning/priority-7-batch3-implementation-plan.md` (v1.0)
**Quick Reference:** `docs/planning/priority-7-quick-reference.md`

### 7.1 Completion & Polish (4 items)

**Goal:** Complete Priority 5 to 100%, increase test coverage to 60%+.

1. **Complete Item 5.12 - Stricter mypy Phase 1** (M: 1 week)
   - **CanMEDS:** Professional (quality standards)
   - **What:** Annotation audit only (Phases 3-7 deferred)
   - **Status:** ✅ Complete (2026-02-17) — 355 Mode A errors catalogued; phased roadmap published in `docs/planning/mypy-phase1-audit-report.md`

2. **Increase test coverage to 60%+** (S: 3-5 days)
   - **CanMEDS:** Scholar (rigor, completeness)
   - **What:** Add ~112 lines of test coverage (+0.8 percentage points)
   - **Status:** ✅ Complete (2026-02-17) — achieved 61.63% (+2.43%), 866 → 956 tests, CI threshold raised 30% → 60%

3. **Enable scheduled CI for daily updates** (S: 2-4 hours)
   - **CanMEDS:** Professional (automation, reliability)
   - **What:** Add .github/workflows/scheduled-update.yml
   - **Status:** ✅ Complete (2026-02-17)
   - **Implementation:** Created workflow + setup guide (user action required: add API keys to GitHub Secrets)

4. **Apply conventional commits to recent history** (S: 2-4 hours)
   - **CanMEDS:** Professional (documentation standards)
   - **What:** Rewrite last 50+ commits to conventional format
   - **Status:** 🟡 Guide created — user action required
   - **Guide:** `docs/guides/conventional-commits-rewrite-guide.md` (step-by-step walkthrough)

### 7.2 External Visibility & Publications (5 items)

**Goal:** Increase project visibility through publications, presentations, community engagement.

5. **Write "Why I Built Finbot" blog post** (M: 1-2 days)
   - **CanMEDS:** Communicator (storytelling), Professional (reflection)
   - **What:** 1500-2000 word narrative blog post
   - **Status:** ✅ Complete (2026-02-17) — `docs/blog/why-i-built-finbot.md`

6. **Write "Backtesting Engines Compared" technical article** (M: 2-3 days)
   - **CanMEDS:** Scholar (comparative analysis), Communicator
   - **What:** 2000-3000 word technical deep-dive
   - **Status:** ✅ Complete (2026-02-17) — `docs/blog/backtesting-engines-compared.md`

7. **Create "Health Economics with Python" tutorial series** (L: 1-2 weeks)
   - **CanMEDS:** Health Advocate (HE methodology), Communicator (teaching)
   - **What:** 3-part tutorial series (QALY, CEA, Treatment optimization)
   - **Status:** ✅ Complete (2026-02-17) — `docs/blog/health-economics-part1-qaly.md`, `docs/blog/health-economics-part2-cea.md`, `docs/blog/health-economics-part3-optimization.md`

8. **Record 5-minute "Finbot Overview" video** (S: 4-6 hours)
   - **CanMEDS:** Communicator (presentation skills)
   - **What:** Screencast demo uploaded to YouTube
   - **Status:** ⬜ Not started

9. **Create project poster for medical school applications** (M: 1-2 days)
   - **CanMEDS:** Communicator (visual), Scholar (research dissemination)
   - **What:** 36x48 academic poster (PDF)
   - **Status:** ⬜ Not started

### 7.3 Medical School Application Readiness (4 items)

**Goal:** Create portfolio artifacts and reflection pieces for applications.

10. **Write "CanMEDS Competency Reflection" essay** (M: 2-3 days)
    - **CanMEDS:** All roles (reflection, growth, leadership)
    - **What:** 2000-3000 word reflection mapping to all 7 CanMEDS roles
    - **Status:** ✅ Complete (2026-02-17) — `docs/applications/canmeds-reflection.md` (~2800 words, all 7 roles)

11. **Create "Finbot Portfolio Piece" summary** (S: 4-6 hours)
    - **CanMEDS:** Communicator (concise communication)
    - **What:** 1-page PDF for application portfolios
    - **Status:** ✅ Complete (2026-02-17) — `docs/applications/finbot-portfolio-summary.md`

12. **Document "Lessons Learned"** (M: 1 day)
    - **CanMEDS:** Professional (reflection, lifelong learning)
    - **What:** Structured lessons document for interviews
    - **Status:** ✅ Complete (2026-02-17) — `docs/applications/lessons-learned.md` (15 concrete lessons)

13. **Create "Impact Statement"** (S: 3-4 hours)
    - **CanMEDS:** Leader (impact measurement), Scholar
    - **What:** 500-word impact statement with quantified outcomes
    - **Status:** ✅ Complete (2026-02-17) — `docs/applications/impact-statement.md` (9 quantified metrics)

### 7.4 Advanced Technical Features (6 items, 3 deferred)

**Goal:** Add high-value technical capabilities demonstrating depth and continued learning.

14. **Add Nautilus strategy migration guide** (M: 3-5 days)
    - **CanMEDS:** Communicator (technical teaching), Scholar
    - **What:** Step-by-step guide + example migration
    - **Status:** ✅ Complete (2026-02-17) — `docs/guides/nautilus-migration-guide.md` (side-by-side code, type system guide, checklist)

15. **Expand walk-forward analysis with visualization** (M: 3-5 days)
    - **CanMEDS:** Scholar (advanced analysis), Communicator
    - **What:** Heatmaps, rolling metrics charts, degradation plots
    - **Status:** ✅ Complete (2026-02-17) — `walkforward_viz.py` (5 chart functions) + `pages/8_walkforward.py` + 23 tests

16. **Add regime-adaptive strategy** (M: 4-6 days)
    - **CanMEDS:** Scholar (advanced methodology), Professional
    - **What:** Strategy that adjusts parameters by detected regime
    - **Status:** ✅ Complete (2026-02-17) — `strategies/regime_adaptive.py` + `segment_by_regime()` upgraded + 19 tests

17. **Add multi-objective optimization** (L: 1-2 weeks)
    - **CanMEDS:** Scholar (advanced optimization), Professional
    - **What:** Pareto frontier optimization (partial delivery)
    - **Status:** ✅ Complete (2026-02-18) — `pareto_optimizer.py` (Pareto frontier, NSGA-II-style ranking, dashboard integration) + tests

18. **Add options overlay strategy** (L: 2-3 weeks)
    - **CanMEDS:** Scholar (derivatives knowledge), Professional
    - **What:** Covered calls, protective puts
    - **Status:** ⬜ DEFERRED to Priority 8
    - **Blocker:** Requires options chain data (may need paid API)

19. **Add real-time data feeds** (L: 1-2 weeks)
    - **CanMEDS:** Professional (modern technology), Scholar
    - **What:** WebSocket integration (Alpaca, Polygon.io)
    - **Status:** ⬜ DEFERRED to Priority 8
    - **Blocker:** May require paid subscription

### 7.5 Deferred High-Value Items (4 items)

**Goal:** Complete high-value items deferred from earlier priorities.

20. **Create video tutorials** (L: 1-2 weeks)
    - **CanMEDS:** Communicator (teaching, accessibility)
    - **What:** 3 videos (Setup, Backtesting, Dashboard)
    - **Status:** ⬜ Not started

21. **Expand health economics to 3 new scenarios** (M: 4-6 days)
    - **CanMEDS:** Health Advocate, Scholar
    - **What:** Cancer screening, hypertension, vaccine
    - **Status:** ⬜ Not started

22. **Add hypothesis testing for strategy comparison** (M: 3-5 days)
    - **CanMEDS:** Scholar (statistical methodology), Professional
    - **What:** T-tests, bootstrap confidence intervals
    - **Status:** ✅ Complete (2026-02-17) — `hypothesis_testing.py` (6 functions, paired t-test, Mann-Whitney, permutation, bootstrap CI) + 24 tests

23. **Clean up deferred unit tests from Priority 1** (M: 4-6 days)
    - **CanMEDS:** Professional (completion), Scholar
    - **What:** Tests for bond_ladder, backtest_batch, rebalance_optimizer
    - **Status:** ✅ Complete (2026-02-17) — 39 new tests across 3 modules; `tests/conftest.py` added for ENV setup

### 7.6 Documentation & Maintenance (4 items)

**Goal:** Update documentation and maintain project health.

24. **Update roadmap and planning docs** (S: 2-3 hours)
    - **CanMEDS:** Professional (documentation standards)
    - **What:** Update roadmap.md with Priority 7, archive completed plans
    - **Status:** ✅ Complete (2026-02-17) — updated continuously throughout Priority 7 execution

25. **Create "Getting Started" video tutorial** (M: 1 day)
    - **CanMEDS:** Communicator (teaching), Leader
    - **What:** 10-minute video walkthrough (installation → first backtest)
    - **Status:** ⬜ Not started

26. **Add "Frequently Asked Questions" (FAQ)** (S: 3-4 hours)
    - **CanMEDS:** Communicator (user support)
    - **What:** 20+ Q&A pairs organized by category
    - **Status:** ✅ Complete (2026-02-17) — `docs/guides/faq.md` (30+ Q&A pairs, 7 categories)

27. **Create "Contributing Guide" video** (S: 4-6 hours)
    - **CanMEDS:** Collaborator, Leader
    - **What:** 5-minute video on contribution workflow
    - **Status:** ⬜ Not started

---

## Priority 7 Summary

**Status:** 🟡 23/27 items complete (85%) — In Progress
**Date Started:** 2026-02-17
**Implementation Plan:** `docs/planning/priority-7-implementation-plan.md` (v1.1); Batch 3 — `docs/planning/priority-7-batch3-implementation-plan.md` (v1.0)

**Focus:** External impact, medical school application readiness, advanced capabilities

**Completed (23 items):**
- Coverage raised to 61.63% (+2.43%), 956 → 1063+ tests passing ✅
- Scheduled CI workflow for daily data updates ✅
- Conventional commits rewrite guide (user action needed) 🟡
- Blog: "Why I Built Finbot" (`docs/blog/why-i-built-finbot.md`) ✅
- Blog: "Backtesting Engines Compared" (`docs/blog/backtesting-engines-compared.md`) ✅
- Blog: 3-part "Health Economics with Python" tutorial series ✅
- CanMEDS Competency Reflection essay (`docs/applications/canmeds-reflection.md`) ✅
- Portfolio summary, lessons learned, impact statement (`docs/applications/`) ✅
- Nautilus strategy migration guide (`docs/guides/nautilus-migration-guide.md`) ✅
- FAQ document (`docs/guides/faq.md`, 30+ Q&A pairs) ✅
- Walk-forward visualization (`walkforward_viz.py`, 5 charts, dashboard page 8) ✅
- Regime-adaptive strategy (`strategies/regime_adaptive.py`, registered in adapter) ✅
- Multi-objective Pareto optimizer (`pareto_optimizer.py`, Pareto frontier + dashboard) ✅
- Statistical hypothesis testing (`hypothesis_testing.py`, 6 functions) ✅
- Deferred unit tests (39 new tests; backtest_batch, rebalance_optimizer, bond_ladder) ✅
- Mypy Phase 1 audit (`docs/planning/mypy-phase1-audit-report.md`, phased roadmap) ✅
- Roadmap and planning docs kept current ✅

**Remaining (4 items):**
- Items 8-9: Overview video + project poster (requires user recording/design)
- Item 20: Video tutorials (requires user recording)
- Item 21: New health economics scenarios (cancer screening, hypertension, vaccine)
- Items 25, 27: Getting Started video, Contributing Guide video

**Deferred to Priority 8:**
- Items 18-19 (options overlay, real-time data) — blocked on cost/data

**See:** `docs/planning/priority-7-batch3-implementation-plan.md` for detailed plan

---

## Completed Items (Priority 0-4)

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
| Add py.typed marker (5.2.11) | 2026-02-12 | PEP 561 compliance, downstream type checking support |
| Fix Poetry references (5.3.14) | 2026-02-12 | Updated 7 files, consistent uv documentation |
| Fix README badge URLs (5.3.16) | 2026-02-12 | Corrected jer→jerdaw, updated uv version 0.6+→0.9+ |
| Add Limitations document (5.3.18) | 2026-02-12 | 431-line comprehensive doc, 9 sections, intellectual honesty |
| Deploy MkDocs to Pages (5.3.13) | 2026-02-12 | Workflow created, awaiting user to enable Pages |
| Add docstring coverage (5.3.17) | 2026-02-12 | Interrogate with 55% threshold, 58.2% current coverage, CI + Makefile + badge |
| Health econ methodology (5.4.19) | 2026-02-12 | 47-page research document, 22 academic references, WHO/NICE/CADTH guidelines |
| Health econ notebook enhanced (5.4.20) | 2026-02-12 | Diabetes clinical scenario, international thresholds, policy implications, 5 refs |
| Health econ tutorial (5.4.21) | 2026-02-12 | 7-step walkthrough, code examples, interpretation for 3 audiences (clinicians/policymakers/patients) |
| Research methodology strengthened (5.4.23) | 2026-02-12 | Formal Abstracts + Discussion sections for all 3 research docs (DCA, ETF, strategies) |
| API documentation coverage improved (5.3.15) | 2026-02-12 | 6 new API reference pages (health economics, data quality, bond ladder, strategies, CLI, dashboard) |
| CLI smoke tests added (5.6.31) | 2026-02-12 | 47 tests covering --help, --version, all 6 commands, error handling, performance |
| CLI input validation added (5.6.32) | 2026-02-12 | Custom validators (DATE, TICKER, POSITIVE_FLOAT), 33 tests, helpful error messages |
| Data ethics documentation added (5.5.24) | 2026-02-12 | 10-section comprehensive ethics document (430 lines), linked from README |
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
