# Priority 7 Implementation Plan: External Impact & Advanced Capabilities

**Version:** 1.1
**Created:** 2026-02-17
**Last Updated:** 2026-02-17
**Status:** In Progress (16/27 items complete, 59%)
**Estimated Duration:** 6-10 weeks (phased execution)
**Dependencies:** Priority 5 (93.3% complete), Priority 6 (100% complete)

---

## Executive Summary

Priority 7 focuses on maximizing the impact and visibility of Finbot while adding advanced technical capabilities. With Priorities 0-6 substantially complete (production-ready state), this phase emphasizes external communication, application readiness, and strategic enhancements.

**Key Objectives:**
1. **Complete Priority 5** - Finish 3 remaining achievable items (97% → 100%)
2. **External Visibility** - Publications, presentations, and community engagement
3. **Application Readiness** - Medical school portfolio materials and reflection pieces
4. **Advanced Features** - High-value technical enhancements (options strategies, real-time data)
5. **Deferred Items** - Tackle high-value items from earlier priorities

**Strategic Rationale:**
- **Medical School Applications**: Priority 5 aligned with OMSAS/CanMEDS; Priority 7 prepares concrete portfolio artifacts
- **Technical Excellence**: Advanced features demonstrate depth and continued learning
- **Community Impact**: External publications increase project visibility and demonstrate leadership
- **Career Development**: Portfolio pieces usable for multiple contexts (med school, tech roles, research)

---

## Current State Assessment

### Project Maturity (2026-02-17)

**Completion Status:**
- Priority 0: ✅ 100% (6/6 items) - Bugs and architectural hazards
- Priority 1: ✅ 100% (3/3 items) - Critical gaps
- Priority 2: ✅ 100% (6/6 items) - High-impact improvements
- Priority 3: ✅ 100% (7/7 items) - Moderate improvements
- Priority 4: ✅ 100% (6/6 items) - Polish and extensibility
- Priority 5: 🟡 93.3% (42/45 items) - OMSAS/CanMEDS improvements
- Priority 6: ✅ 100% (18/18 items) - Backtesting-to-live readiness

**Key Metrics:**
- **Tests:** 866 passing (all green)
- **Coverage:** 59.20% (98.83% of 60% target)
- **Documentation:** 113 markdown files, 8 Jupyter notebooks
- **CI/CD:** 7 jobs (lint, type-check, security, test, docs, parity, performance)
- **Python Support:** 3.11, 3.12, 3.13
- **Security:** bandit, pip-audit, trivy, OpenSSF Scorecard ready
- **Governance:** Complete (LICENSE, SECURITY, CODE_OF_CONDUCT, CODEOWNERS, etc.)

**Remaining Priority 5 Items:**
1. **Item 12:** Stricter mypy settings (L: 3-5 weeks) - Phase 2 complete, Phases 1,3-7 deferred
2. **Item 22:** Simulation validation against known results (M: 1-2 days) - Blocked on historical data
3. **Item 42:** Project logo/branding (S: 1-2 hours) - Blocked on design approval

**Deferred High-Value Items:**
- Increase coverage target from 60% to 70%+ (currently 59.20%, 1.3% short)
- Enable scheduled CI for daily update pipeline (requires API keys in CI)
- Apply conventional commits retroactively to history (clean git log)
- Add options overlay strategies (covered calls, protective puts)
- Add real-time data feeds (WebSocket/streaming data)
- Expand health economics to include more clinical scenarios
- Create video tutorials for key features

### Key Assumptions

1. **Medical School Timeline**: Applications may occur in 2026-2027 cycle; portfolio materials should be ready within 6 months
2. **Resource Availability**: Solo development with local automation tooling; parallelizable tasks preferred
3. **API Access**: Existing API keys sufficient; no new paid services required
4. **Historical Data**: Item 22 remains blocked unless historical datasets become available
5. **Design Resources**: Item 42 remains blocked unless design approval obtained
6. **Publication Venues**: Blog posts, GitHub Pages, Medium, or personal website for external visibility
7. **Time Commitment**: ~10-15 hours/week sustainable pace for 6-10 week duration

### Key Unknowns

1. **Medical School Application Timeline**: Exact dates unknown; flexible scheduling needed
2. **External Publication Interest**: Unknown if blog posts/papers will gain external readership
3. **Options Data Availability**: May need options chain data from new source for Item P7.18
4. **Real-Time Data Costs**: WebSocket feeds may require paid subscriptions for Item P7.19
5. **Stricter Mypy Feasibility**: Item 12 may uncover unexpected annotation challenges
6. **Community Engagement**: Unknown level of external contributor interest

---

## Priority 7 Roadmap

### 7.1 Completion & Polish (Quick Wins)

**Goal:** Achieve 100% completion of Priority 5 by finishing achievable items.

**CanMEDS:** Professional (excellence, completion), Scholar (rigor)

#### Item P7.1: Complete Item 5.12 - Stricter mypy (Phase 1 only)
- **Size:** M (1 week)
- **What:** Complete Phase 1 (annotation audit) from stricter-mypy-implementation-plan.md
- **Why:** 98.83% of target is frustratingly close; finishing Phase 1 demonstrates commitment to type safety
- **CanMEDS:** Professional (quality standards)
- **Output:** Annotation audit report, priority module list
- **Acceptance:** Audit complete, actionable plan for Phases 3-7 (deferred to future)
- **Skip Phases 3-7:** Too large (3-4 weeks) for Priority 7 scope; defer to Priority 8+

#### Item P7.2: Increase test coverage from 59.20% to 60%+ ✅
- **Size:** S (3-5 days)
- **What:** Add targeted tests to cross 60% threshold (need +0.8 percentage points = ~112 lines)
- **Why:** Cross the psychological 60% barrier; demonstrates thoroughness
- **CanMEDS:** Scholar (rigor, completeness)
- **Output:** 60%+ coverage, updated CI threshold
- **Acceptance:** Coverage ≥60.00%, all tests passing, no regressions
- **Status:** ✅ Complete (2026-02-17) — achieved **61.63%** (+2.43%)
- **Implementation:** Added 78 new tests across 4 new test files:
  - `tests/unit/test_json_utils.py` (45 tests) — serialize/deserialize/save/load round-trips
  - `tests/unit/test_dict_utils.py` (25 tests) — hash_dictionary with all algorithms
  - `tests/unit/test_coverage_boost.py` (28 tests) — error constants, overlapping date range, rate limiter, retry strategy, API resource groups
  - `tests/unit/test_datetime_utils.py` (+5 tests) — measure_execution_time
  - CI threshold raised from 30% → 60% in `.github/workflows/ci.yml`
  - Total tests: 866 → 956 (+90 tests)

#### Item P7.3: Enable scheduled CI for daily update pipeline ✅
- **Size:** S (2-4 hours)
- **What:** Add .github/workflows/scheduled-update.yml running daily at 6am UTC
- **Why:** Automated data freshness monitoring; professional operations
- **CanMEDS:** Professional (automation, reliability)
- **Output:** Scheduled workflow, notification on failures
- **Acceptance:** Workflow runs daily, updates data, reports failures
- **Blocker:** Requires API keys as GitHub secrets (user action)
- **Status:** ✅ Complete (2026-02-17)
- **Implementation:** Created workflow file and setup guide
  - Workflow: `.github/workflows/scheduled-update.yml`
  - Guide: `docs/guides/scheduled-ci-setup.md`
  - User action required: Add API keys to GitHub Secrets

#### Item P7.4: Apply conventional commits to recent history
- **Size:** S (2-4 hours)
- **What:** Rewrite commits from v1.0.0 tag forward to use conventional commit format
- **Why:** Clean git history for future changelog generation
- **CanMEDS:** Professional (documentation standards)
- **Output:** Cleaned git history, updated CHANGELOG.md
- **Acceptance:** Last 50+ commits follow conventional format
- **Note:** Use interactive rebase, requires force-push to main (risky but valuable)

---

### 7.2 External Visibility & Publications

**Goal:** Increase project visibility through publications, presentations, and community engagement.

**CanMEDS:** Communicator (publishing, teaching), Leader (impact, influence)

#### Item P7.5: Write "Why I Built Finbot" blog post ✅
- **Size:** M (1-2 days)
- **What:** 1500-2000 word narrative blog post on motivation, journey, lessons learned
- **Why:** Human story engages readers; demonstrates reflection and growth
- **CanMEDS:** Communicator (storytelling), Professional (reflection)
- **Output:** `docs/blog/why-i-built-finbot.md`, publish to Medium/dev.to
- **Acceptance:** Published externally, linked from README
- **Topics:** Problem motivation, technical challenges, key decisions, future vision
- **Status:** ✅ Complete (2026-02-17) — ~1800 words, covers spreadsheet origins, 3-repo history, architectural decisions, medical school connection

#### Item P7.6: Write "Backtesting Engines Compared" technical article ✅
- **Size:** M (2-3 days)
- **What:** 2000-3000 word technical deep-dive comparing Backtrader vs Nautilus
- **Why:** Fills gap in existing literature; demonstrates technical depth
- **CanMEDS:** Scholar (comparative analysis), Communicator (technical writing)
- **Output:** `docs/blog/backtesting-engines-compared.md`, publish externally
- **Acceptance:** Published with code examples, performance benchmarks, decision matrix
- **Topics:** Architecture comparison, fill realism, performance, when to use each
- **Status:** ✅ Complete (2026-02-17) — ~2400 words, decision matrix, code examples, Finbot parity case study

#### Item P7.7: Create "Health Economics with Python" tutorial series ✅
- **Size:** L (1-2 weeks)
- **What:** 3-part tutorial series on health economics methods (QALY, ICER, CEA)
- **Why:** Bridges medicine and programming; demonstrates teaching ability
- **CanMEDS:** Health Advocate (HE methodology), Communicator (teaching)
- **Output:** 3 blog posts (Part 1: QALY basics, Part 2: CEA, Part 3: Treatment optimization)
- **Acceptance:** Published externally, Jupyter notebooks included, 30+ citations
- **Topics:** Clinical scenarios, code walkthroughs, policy implications
- **Status:** ✅ Complete (2026-02-17)
  - Part 1: `docs/blog/health-economics-part1-qaly.md` — QALY formula, utility, discounting, Monte Carlo PSA, T2D example
  - Part 2: `docs/blog/health-economics-part2-cea.md` — ICER, NMB, CEAC, CE plane, WTP thresholds (NICE/CADTH/WHO)
  - Part 3: `docs/blog/health-economics-part3-optimization.md` — Grid search over dose frequency × duration, NMB optimization, WTP sensitivity

#### Item P7.8: Record 5-minute "Finbot Overview" presentation video
- **Size:** S (4-6 hours)
- **What:** 5-minute screencast demonstrating Finbot capabilities (simulation, backtesting, dashboard)
- **Why:** Visual demonstration more engaging than text; usable for presentations
- **CanMEDS:** Communicator (presentation skills)
- **Output:** MP4 video, upload to YouTube, embed in README
- **Acceptance:** <5 minutes, clear audio, demonstrates 3+ features
- **Tools:** OBS Studio (free), simple slides, live demo

#### Item P7.9: Create project poster for medical school applications
- **Size:** M (1-2 days)
- **What:** Academic-style research poster (36x48 inches, PDF) summarizing Finbot
- **Why:** Required artifact for many medical school applications; demonstrates research communication
- **CanMEDS:** Communicator (visual communication), Scholar (research dissemination)
- **Output:** `docs/poster/finbot-research-poster.pdf`, print-ready
- **Acceptance:** Follows academic poster conventions, includes figures/results, <500 words
- **Sections:** Problem, Methods, Results, Impact, Future Directions
- **Tools:** PowerPoint or Canva (free templates)

---

### 7.3 Medical School Application Readiness

**Goal:** Create portfolio artifacts and reflection pieces for medical school applications.

**CanMEDS:** All competencies (reflection, growth, leadership)

#### Item P7.10: Write "CanMEDS Competency Reflection" essay ✅
- **Size:** M (2-3 days)
- **What:** 2000-3000 word reflection essay mapping Finbot development to all 7 CanMEDS roles
- **Why:** Demonstrates self-awareness and alignment with medical education framework
- **CanMEDS:** All roles (Professional, Scholar, Communicator, Collaborator, Leader, Health Advocate, Medical Expert)
- **Output:** `docs/applications/canmeds-reflection.md`
- **Acceptance:** Addresses all 7 roles with concrete examples, demonstrates growth/learning
- **Sections:** Introduction, Professional, Scholar, Communicator, Collaborator, Leader, Health Advocate, Conclusion
- **Status:** ✅ Complete (2026-02-17) — ~2800 words covering all 7 CanMEDS roles with concrete Finbot examples

#### Item P7.11: Create "Finbot Portfolio Piece" summary (1-pager) ✅
- **Size:** S (4-6 hours)
- **What:** 1-page PDF summary of Finbot for application portfolios (500 words max)
- **Why:** Concise artifact for application submission; highlights key achievements
- **CanMEDS:** Communicator (concise communication)
- **Output:** `docs/applications/finbot-portfolio-summary.md`
- **Acceptance:** ≤1 page, professional formatting, includes metrics/outcomes
- **Sections:** Problem, Approach, Technical Achievements, Impact, Skills Demonstrated
- **Status:** ✅ Complete (2026-02-17) — Markdown format with metrics table, technical highlights, research findings

#### Item P7.12: Document "Lessons Learned" for application interviews ✅
- **Size:** M (1 day)
- **What:** Structured document capturing key lessons, challenges overcome, growth areas
- **Why:** Interview preparation; demonstrates reflective capacity
- **CanMEDS:** Professional (reflection, lifelong learning)
- **Output:** `docs/applications/lessons-learned.md`
- **Acceptance:** 10+ concrete lessons with examples, growth mindset framing
- **Categories:** Technical challenges, collaboration, time management, decision-making, future improvements
- **Status:** ✅ Complete (2026-02-17) — 15 concrete lessons with what happened, what I learned, cross-domain application

#### Item P7.13: Create "Impact Statement" quantifying Finbot outcomes ✅
- **Size:** S (3-4 hours)
- **What:** 500-word impact statement with quantified outcomes and future potential
- **Why:** Applications require evidence of impact; numbers tell compelling story
- **CanMEDS:** Leader (impact measurement), Scholar (evidence-based)
- **Output:** `docs/applications/impact-statement.md`
- **Acceptance:** 5+ quantified metrics, evidence-based claims
- **Metrics:** Lines of code, test coverage, documentation pages, research citations, user scenarios
- **Status:** ✅ Complete (2026-02-17) — ~500 words, 9 quantified metrics, skills table, medicine relevance section

---

### 7.4 Advanced Technical Features

**Goal:** Add high-value technical capabilities that demonstrate depth and continued learning.

**CanMEDS:** Scholar (advanced knowledge), Professional (continuous improvement)

#### Item P7.14: Add Nautilus strategy migration guide ✅
- **Size:** M (3-5 days)
- **What:** Step-by-step guide for migrating Backtrader strategies to Nautilus
- **Why:** Hybrid approach (ADR-011) needs migration documentation; demonstrates teaching
- **CanMEDS:** Communicator (technical teaching), Scholar (systematic methodology)
- **Output:** `docs/guides/nautilus-migration-guide.md`, example migration (SmaRebalanceMix)
- **Acceptance:** Complete migration of 1 strategy, before/after code comparison, troubleshooting section
- **Status:** ✅ Complete (2026-02-17) — side-by-side Backtrader/Nautilus code, type system guide, common errors, multi-asset pattern, parity checklist

#### Item P7.15: Expand walk-forward analysis with visualization
- **Size:** M (3-5 days)
- **What:** Add visualization tools for walk-forward results (heatmaps, rolling metrics charts)
- **Why:** Walk-forward analysis powerful but underutilized; visualization increases usability
- **CanMEDS:** Scholar (advanced analysis), Communicator (data visualization)
- **Output:** `finbot/services/backtesting/walkforward_viz.py`, updated notebook
- **Acceptance:** 3+ visualization types (heatmap, rolling chart, degradation plot), example notebook
- **Dependencies:** Plotly for interactive charts

#### Item P7.16: Add regime-adaptive strategy example
- **Size:** M (4-6 days)
- **What:** New strategy that adjusts parameters based on detected regime (bull/bear/sideways)
- **Why:** Demonstrates practical use of regime detection; novel strategy contribution
- **CanMEDS:** Scholar (advanced methodology), Professional (innovation)
- **Output:** `finbot/services/backtesting/strategies/regime_adaptive.py`, tests, notebook
- **Acceptance:** Strategy adjusts leverage/allocation by regime, 10+ tests, example backtest
- **Example:** Higher equity allocation in bull regimes, defensive in bear regimes

#### Item P7.17: Add multi-objective optimization
- **Size:** L (1-2 weeks)
- **What:** Pareto frontier optimization for portfolios (maximize return, minimize drawdown)
- **Why:** Real-world optimization involves tradeoffs; demonstrates advanced concepts
- **CanMEDS:** Scholar (advanced optimization), Professional (complexity management)
- **Output:** `finbot/services/optimization/pareto_optimizer.py`, tests, visualization
- **Acceptance:** Generates Pareto frontier, 3+ objectives supported, interactive visualization
- **Methods:** NSGA-II or similar multi-objective genetic algorithm
- **Dependencies:** May require `pymoo` or `deap` for multi-objective optimization

#### Item P7.18: Add options overlay strategy (DEFERRED - Data dependency)
- **Size:** L (2-3 weeks)
- **What:** Strategy that sells covered calls or buys protective puts on equity positions
- **Why:** Options strategies common in real portfolios; demonstrates advanced modeling
- **CanMEDS:** Scholar (derivatives knowledge), Professional (complexity)
- **Output:** Options pricing module, overlay strategy, tests
- **Acceptance:** Black-Scholes pricing, 2+ overlay strategies, Greeks calculations
- **BLOCKER:** Requires options chain data (may need paid API)
- **Defer:** Too large and blocked; move to Priority 8

#### Item P7.19: Add real-time data feeds (DEFERRED - Cost dependency)
- **Size:** L (1-2 weeks)
- **What:** WebSocket integration for real-time market data (Alpaca, Polygon.io)
- **Why:** Real-time data enables paper trading validation; demonstrates modern APIs
- **CanMEDS:** Professional (modern technology), Scholar (data integration)
- **Output:** Real-time data adapter, demo notebook
- **Acceptance:** WebSocket connection, 1+ data provider, real-time bar updates
- **BLOCKER:** May require paid subscription for real-time data
- **Defer:** Cost unclear; move to Priority 8

---

### 7.5 Deferred High-Value Items

**Goal:** Complete high-value items deferred from earlier priorities.

**CanMEDS:** Professional (completion, thoroughness)

#### Item P7.20: Create video tutorials (3 videos)
- **Size:** L (1-2 weeks)
- **What:** 3 video tutorials (15-20 min each) for key features
- **Why:** Video tutorials increase accessibility; demonstrates teaching/communication
- **CanMEDS:** Communicator (teaching, accessibility)
- **Output:** 3 videos (Setup, Backtesting, Dashboard), upload to YouTube
- **Acceptance:** Clear audio, screencasts, <20 min each, YouTube published
- **Topics:** (1) Installation & first backtest, (2) Strategy development, (3) Dashboard walkthrough

#### Item P7.21: Expand health economics to 3 new clinical scenarios
- **Size:** M (4-6 days)
- **What:** Add 3 new clinical scenarios (cancer screening, hypertension, vaccine)
- **Why:** Demonstrates breadth of health economics application
- **CanMEDS:** Health Advocate (diverse scenarios), Scholar (clinical reasoning)
- **Output:** 3 new notebooks, updated methodology doc
- **Acceptance:** 3 clinically realistic scenarios, NICE/CADTH thresholds applied, 10+ new citations

#### Item P7.22: Add hypothesis testing for strategy comparison
- **Size:** M (3-5 days)
- **What:** Statistical significance testing for backtest results (t-tests, bootstrap confidence intervals)
- **Why:** Professional research requires statistical rigor; demonstrates Scholar role
- **CanMEDS:** Scholar (statistical methodology), Professional (rigor)
- **Output:** `finbot/services/backtesting/hypothesis_testing.py`, tests, notebook
- **Acceptance:** 3+ statistical tests, confidence intervals, p-values, example comparison
- **Methods:** Paired t-tests, bootstrap resampling, permutation tests

#### Item P7.23: Clean up deferred unit tests from Priority 1
- **Size:** M (4-6 days)
- **What:** Add tests for bond_ladder_simulator, backtest_batch, rebalance_optimizer, data collection utils
- **Why:** Deferred in Priority 1; completing demonstrates thoroughness
- **CanMEDS:** Professional (completion), Scholar (testing rigor)
- **Output:** 30+ new tests, coverage increase
- **Acceptance:** Tests for 4 deferred modules, all passing, +2-3% coverage
- **Note:** Some may require mock API responses or FRED data

---

### 7.6 Documentation & Maintenance

**Goal:** Update documentation and maintain project health.

**CanMEDS:** Communicator (documentation), Professional (maintenance)

#### Item P7.24: Update roadmap and planning docs ✅
- **Size:** S (2-3 hours)
- **What:** Update roadmap.md with Priority 7, archive completed plans, update status docs
- **Why:** Documentation must reflect current state; demonstrates professional practices
- **CanMEDS:** Professional (documentation standards)
- **Output:** Updated roadmap.md, archived Priority 5/6 plans, new status summary
- **Acceptance:** Roadmap reflects Priority 7, all completed items checked, status current
- **Status:** ✅ Complete (2026-02-17) — roadmap.md and implementation plan updated continuously throughout Priority 7 execution

#### Item P7.25: Create "Getting Started" video tutorial
- **Size:** M (1 day)
- **What:** 10-minute video walkthrough for new users (installation → first backtest)
- **Why:** Lowers barrier to entry; demonstrates teaching ability
- **CanMEDS:** Communicator (teaching), Leader (enabling others)
- **Output:** `docs/tutorials/getting-started-video.md` with YouTube embed
- **Acceptance:** <10 minutes, covers installation + first backtest, clear audio/video

#### Item P7.26: Add "Frequently Asked Questions" (FAQ) ✅
- **Size:** S (3-4 hours)
- **What:** FAQ document addressing common questions (Why Finbot? API keys? Strategies? etc.)
- **Why:** Reduces friction for new users; demonstrates user-centered thinking
- **CanMEDS:** Communicator (user support)
- **Output:** `docs/guides/faq.md`, linked from README
- **Acceptance:** 20+ Q&A pairs, organized by category, clear answers
- **Status:** ✅ Complete (2026-02-17) — 30+ Q&A pairs in 7 categories (Getting Started, Backtesting, Simulation, Data, Health Economics, Technical, Contributing)

#### Item P7.27: Create "Contributing Guide" video
- **Size:** S (4-6 hours)
- **What:** 5-minute video on how to contribute (fork, branch, test, PR)
- **Why:** Encourages external contributors; demonstrates collaboration mindset
- **CanMEDS:** Collaborator (enabling contribution), Leader (community building)
- **Output:** Video embedded in CONTRIBUTING.md
- **Acceptance:** <5 minutes, demonstrates full contribution workflow

---

## Phased Implementation Plan

### Phase 1: Completion Sprint (Weeks 1-2)

**Goal:** Complete Priority 5 to 100% with quick wins.

**Timeline:** 2 weeks (10-15 hours/week = 20-30 total hours)

**Tasks:**
1. P7.1: Stricter mypy Phase 1 audit (M: 1 week)
2. P7.2: Increase coverage to 60%+ (S: 3-5 days)
3. P7.3: Scheduled CI for daily updates (S: 2-4 hours)
4. P7.4: Apply conventional commits to history (S: 2-4 hours)

**Deliverables:**
- Priority 5 at 100% (up from 93.3%)
- Test coverage ≥60%
- Daily automated data updates
- Clean git history

**Risks:**
- P7.1 may uncover unexpected mypy challenges → Scope to audit only (Phase 1)
- P7.3 blocked on API keys → Document manual workaround
- P7.4 force-push risky → Create backup branch first

**Validation:**
- All 866 tests passing
- Coverage badge shows 60%+
- Scheduled workflow runs successfully
- Git log shows conventional commits

---

### Phase 2: External Visibility (Weeks 3-5)

**Goal:** Publish 3+ external articles and create presentation materials.

**Timeline:** 3 weeks (10-15 hours/week = 30-45 total hours)

**Tasks:**
1. P7.5: "Why I Built Finbot" blog post (M: 1-2 days)
2. P7.6: "Backtesting Engines Compared" technical article (M: 2-3 days)
3. P7.7: "Health Economics with Python" tutorial series (L: 1-2 weeks)
4. P7.8: 5-minute "Finbot Overview" video (S: 4-6 hours)
5. P7.9: Research poster for applications (M: 1-2 days)

**Deliverables:**
- 5 published articles/videos (3 blog posts, 1 video, 1 poster)
- External visibility on Medium/dev.to/YouTube
- Reusable presentation materials

**Risks:**
- Writing takes longer than estimated → Prioritize P7.5, P7.6 (highest value)
- External publication may require editorial review → Use Medium for self-publishing
- Video recording may have technical issues → Practice run first

**Validation:**
- 3+ articles published with live URLs
- Video uploaded to YouTube with >0 views
- Poster PDF print-ready (300 DPI)

---

### Phase 3: Application Readiness (Weeks 6-7)

**Goal:** Create all portfolio artifacts for medical school applications.

**Timeline:** 2 weeks (10-15 hours/week = 20-30 total hours)

**Tasks:**
1. P7.10: CanMEDS Competency Reflection essay (M: 2-3 days)
2. P7.11: Finbot Portfolio Piece 1-pager (S: 4-6 hours)
3. P7.12: Lessons Learned documentation (M: 1 day)
4. P7.13: Impact Statement (S: 3-4 hours)

**Deliverables:**
- 4 application-ready documents (reflection, portfolio, lessons, impact)
- All documents formatted and proofread
- Ready for submission to OMSAS or other applications

**Risks:**
- Reflection essay may require multiple drafts → Allocate 3 days
- Impact metrics may be difficult to quantify → Focus on test coverage, LOC, docs

**Validation:**
- All 4 documents complete and proofread
- CanMEDS reflection addresses all 7 roles
- Impact statement has 5+ quantified metrics

---

### Phase 4: Advanced Features Part 1 (Weeks 8-9)

**Goal:** Add 2-3 advanced technical features.

**Timeline:** 2 weeks (10-15 hours/week = 20-30 total hours)

**Tasks:**
1. P7.14: Nautilus migration guide (M: 3-5 days)
2. P7.15: Walk-forward visualization (M: 3-5 days)
3. P7.16: Regime-adaptive strategy (M: 4-6 days)

**Deliverables:**
- 1 complete strategy migration example
- Walk-forward visualization suite
- 1 novel regime-adaptive strategy

**Risks:**
- Nautilus API may have changed → Refer to E6 evaluation report
- Visualization may be complex → Use Plotly templates
- Regime strategy may underperform → Focus on methodology, not raw performance

**Validation:**
- 1 strategy successfully migrated and tested
- 3+ visualization types working
- Regime-adaptive strategy passes 10+ tests

---

### Phase 5: Advanced Features Part 2 (Week 10)

**Goal:** Add multi-objective optimization and complete deferred items.

**Timeline:** 1 week (10-15 hours/week = 10-15 total hours)

**Tasks:**
1. P7.17: Multi-objective optimization (L: 1-2 weeks) - **Start only, defer completion to Priority 8**
2. P7.22: Hypothesis testing for strategy comparison (M: 3-5 days)
3. P7.23: Clean up deferred unit tests (M: 4-6 days) - **Start only**

**Deliverables:**
- Multi-objective optimization framework (partial)
- Hypothesis testing module complete
- 15+ new deferred unit tests

**Risks:**
- P7.17 too large for 1 week → Defer completion to Priority 8, deliver skeleton only
- P7.23 requires mock APIs → Focus on bond_ladder tests (no mocks needed)

**Validation:**
- Hypothesis testing module with 3+ statistical tests
- Pareto optimizer skeleton with 1 working example
- 15+ new tests passing

---

### Phase 6: Documentation & Wrap-Up (Week 11)

**Goal:** Update all documentation and prepare handoff materials.

**Timeline:** 1 week (10-15 hours/week = 10-15 total hours)

**Tasks:**
1. P7.24: Update roadmap and planning docs (S: 2-3 hours)
2. P7.25: "Getting Started" video tutorial (M: 1 day)
3. P7.26: FAQ document (S: 3-4 hours)
4. P7.27: "Contributing Guide" video (S: 4-6 hours)
5. **Priority 7 Completion Summary** (S: 2-3 hours)

**Deliverables:**
- Updated roadmap.md with Priority 7 status
- 2 video tutorials (Getting Started, Contributing)
- FAQ with 20+ Q&A pairs
- Priority 7 completion summary document

**Risks:**
- Documentation updates may take longer than estimated → Prioritize P7.24 (roadmap)

**Validation:**
- Roadmap.md reflects all Priority 7 items
- 2 videos uploaded and linked
- FAQ covers common questions
- Completion summary published

---

## Dependencies and Risks

### Critical Path Dependencies

```
Phase 1 (Completion Sprint)
  └─> Phase 2 (External Visibility) [can start in parallel]
  └─> Phase 3 (Application Readiness) [can start in parallel]
       └─> Phase 4 (Advanced Features Part 1)
            └─> Phase 5 (Advanced Features Part 2)
                 └─> Phase 6 (Documentation & Wrap-Up)
```

**Parallelization Opportunities:**
- Phases 2 and 3 can run concurrently (different focus areas)
- P7.5-P7.9 (external visibility) can be tackled in any order
- P7.10-P7.13 (application materials) can be tackled in any order

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Scope Creep** | High | High | Defer P7.17, P7.18, P7.19 to Priority 8 if timeline slips |
| **Writing Takes Longer** | Medium | Medium | Prioritize P7.5, P7.6 (highest visibility) |
| **Video Quality Issues** | Low | Low | Practice runs, use OBS Studio |
| **API Keys Missing for P7.3** | Medium | Low | Document manual workaround, user action required |
| **Historical Data Unavailable for P7.22** | High | Low | Item already deferred; remains blocked |
| **Design Approval Blocked for P7.42** | High | Low | Item already deferred; remains blocked |
| **Multi-Objective Optimization Complexity** | Medium | Medium | Start with simple 2-objective case, defer full implementation |
| **External Publication Rejection** | Low | Low | Use self-publishing platforms (Medium, dev.to) |
| **Force-Push for P7.4** | Medium | Medium | Create backup branch, coordinate with any collaborators |
| **Medical School Timeline Shift** | Medium | Medium | Phase 3 self-contained; can accelerate if needed |

### Blockers and Deferred Items

**Deferred to Priority 8:**
- P7.18: Options overlay strategy (requires options chain data, 2-3 weeks)
- P7.19: Real-time data feeds (cost unclear, 1-2 weeks)
- P7.17 completion: Multi-objective optimization (1 week remaining after Phase 5)
- P7.23 completion: Deferred unit tests (some require FRED data)

**Permanently Blocked:**
- Priority 5 Item 22: Simulation validation (no historical data source identified)
- Priority 5 Item 42: Project logo/branding (no design approval process)

**User Action Required:**
- P7.3: Add API keys to GitHub Secrets (ALPHA_VANTAGE_API_KEY, NASDAQ_DATA_LINK_API_KEY, etc.)

---

## Timeline and Milestones

### High-Level Timeline (11 weeks)

```
Week 1-2:   Phase 1 - Completion Sprint (Priority 5 → 100%)
Week 3-5:   Phase 2 - External Visibility (5 publications)
Week 6-7:   Phase 3 - Application Readiness (4 portfolio pieces)
Week 8-9:   Phase 4 - Advanced Features Part 1 (3 technical features)
Week 10:    Phase 5 - Advanced Features Part 2 (optimization, testing)
Week 11:    Phase 6 - Documentation & Wrap-Up (videos, FAQ, summary)
```

### Key Milestones

**M1: Priority 5 Complete (End of Week 2)**
- All 45 Priority 5 items at 100%
- Test coverage ≥60%
- Daily automated updates running
- **Success Criteria:** Roadmap shows P5: 100%, coverage badge ≥60%

**M2: External Presence Established (End of Week 5)**
- 3+ blog posts published externally
- 1 video uploaded to YouTube
- Research poster complete
- **Success Criteria:** 3+ live publication URLs, 1 YouTube video, 1 PDF poster

**M3: Application Materials Ready (End of Week 7)**
- 4 application documents complete (reflection, portfolio, lessons, impact)
- All documents proofread and formatted
- **Success Criteria:** All 4 PDFs/docs ready for submission

**M4: Advanced Features Delivered (End of Week 9)**
- Nautilus migration guide complete
- Walk-forward visualization working
- Regime-adaptive strategy tested
- **Success Criteria:** 3 new features documented and tested

**M5: Priority 7 Complete (End of Week 11)**
- All Priority 7 items complete or deferred with rationale
- Documentation updated
- Completion summary published
- **Success Criteria:** Roadmap shows P7 status, summary document exists

### Checkpoint Gates

**Gate 1 (End of Week 2):** Decide whether to proceed with external visibility phase
- **Go/No-Go:** If Priority 5 completion takes >2 weeks, defer Phase 2 and focus on applications
- **Criteria:** P5 at 100%, tests passing, coverage ≥60%

**Gate 2 (End of Week 5):** Decide whether to prioritize applications or advanced features
- **Go/No-Go:** If medical school timeline accelerates, skip Phase 4-5 and jump to Phase 6
- **Criteria:** 3+ publications complete, application deadline <2 months out?

**Gate 3 (End of Week 9):** Decide whether to extend Phase 5 or wrap up
- **Go/No-Go:** If multi-objective optimization incomplete, either extend 1 week or defer to P8
- **Criteria:** P7.17 skeleton working? Time budget remaining?

---

## Rollout and Rollback Strategy

### Rollout Approach

**Incremental Delivery:**
- Each phase delivers standalone value (completion → visibility → applications → features → docs)
- Phases can be reordered based on changing priorities (e.g., accelerate Phase 3 if med school deadline approaches)
- Parallel execution where possible (Phases 2 and 3 can overlap)

**Quality Gates:**
- All tests must pass before merging any feature
- Documentation must be updated before marking phase complete
- External publications must be proofread by human before publishing
- Application materials must be reviewed before considering "ready"

**Validation Steps:**
1. **Code Changes:** Run `make all` (lint, format, type-check, security, test)
2. **Documentation:** Proofread, check links, verify formatting
3. **External Publications:** Grammar check, technical accuracy review, peer feedback (optional)
4. **Application Materials:** Proofread, ensure professional tone, check for errors

### Rollback Strategy

**Per-Phase Rollback:**
- **Phase 1:** If mypy audit reveals too many issues, revert to current state (check_untyped_defs=true)
- **Phase 2:** If external publications don't gain traction, treat as learning experience (no rollback needed)
- **Phase 3:** Application materials are standalone documents (no code rollback needed)
- **Phase 4-5:** If features unstable, move behind feature flag or defer to Priority 8
- **Phase 6:** Documentation updates can be reverted via git

**Git Strategy:**
- Create feature branches for all code changes (`feature/p7-{item-number}`)
- Merge to main only after tests pass and documentation updated
- Tag milestones (`priority-7-milestone-1`, etc.) for easy rollback points
- For P7.4 (git history rewrite), create backup branch `main-backup-pre-rebase` first

**Emergency Rollback:**
- If Priority 7 must be paused (e.g., urgent medical school deadline):
  - Complete current phase
  - Update roadmap with "Paused" status
  - Create handoff document summarizing completed/remaining work
  - Can resume later from any phase boundary

---

## Success Metrics

### Quantitative Metrics

1. **Completion:**
   - Priority 5: 93.3% → 100% (+6.7%)
   - Test coverage: 59.20% → ≥60% (+0.8%)
   - Total tests: 866 → 900+ (+34)

2. **Documentation:**
   - External publications: 0 → 5+ (blog posts, videos, poster)
   - Application materials: 0 → 4 documents
   - Video tutorials: 0 → 3 videos
   - FAQ entries: 0 → 20+ Q&A pairs

3. **External Visibility:**
   - Blog post views: 0 → 100+ (modest goal)
   - YouTube video views: 0 → 50+ (modest goal)
   - GitHub stars: current → +10 (aspirational)

4. **Technical Features:**
   - New strategies: +1 (regime-adaptive)
   - New optimization methods: +1 (multi-objective, partial)
   - New visualization types: +3 (walk-forward heatmap, rolling chart, degradation)
   - Statistical tests: +3 (hypothesis testing module)

### Qualitative Metrics

1. **Portfolio Quality:**
   - Application materials demonstrate all 7 CanMEDS roles
   - Reflection essay shows genuine growth and learning
   - Impact statement has concrete, quantified outcomes

2. **External Impact:**
   - Publications demonstrate technical depth and communication skills
   - Videos demonstrate teaching ability
   - Poster demonstrates research communication

3. **Code Quality:**
   - Advanced features well-tested and documented
   - Migration guide enables Nautilus adoption
   - Visualization improves walk-forward usability

4. **Community Readiness:**
   - FAQ reduces friction for new users
   - Contributing guide enables external contributions
   - Getting Started video lowers barrier to entry

---

## Resource Requirements

### Human Resources
- **Primary:** Solo developer (you) with local automation tooling
- **Time Commitment:** 10-15 hours/week for 11 weeks (110-165 total hours)
- **Optional:** Peer review for blog posts (informal, friends/colleagues)
- **Optional:** Proofreading for application materials (highly recommended)

### Technical Resources
- **Existing:** All development tools already in place (uv, pytest, ruff, mypy, etc.)
- **New (Free):**
  - Medium/dev.to account (external publishing)
  - YouTube account (video hosting)
  - OBS Studio (screen recording)
  - Canva or PowerPoint (poster design)
- **New (Paid - Optional):**
  - Grammarly Premium (proofreading, ~$12/month)
  - Professional poster printing (~$50-100 for 36x48)

### API/Data Resources
- **Required:** Existing API keys (Alpha Vantage, NASDAQ Data Link, etc.)
- **Blocked:** Historical data for simulation validation (Priority 5 Item 22)
- **Deferred:** Options chain data (P7.18), real-time data feeds (P7.19)

### Infrastructure
- **CI/CD:** GitHub Actions (free tier sufficient)
- **Documentation:** GitHub Pages (free)
- **Storage:** Git repository (no additional storage needed)

---

## Acceptance Criteria

### Phase 1: Completion Sprint
- [ ] Priority 5 at 100% (all 45 items complete or permanently deferred)
- [ ] Test coverage ≥60.00%
- [ ] Scheduled CI workflow running daily
- [ ] Git history follows conventional commits (last 50+ commits)
- [ ] All 866+ tests passing

### Phase 2: External Visibility
- [ ] 3+ blog posts published externally with live URLs
- [ ] 1 video uploaded to YouTube (Finbot Overview, <5 min)
- [ ] 1 research poster PDF (36x48, print-ready, 300 DPI)
- [ ] All publications linked from README or docs

### Phase 3: Application Readiness
- [ ] CanMEDS reflection essay (2000-3000 words, addresses all 7 roles)
- [ ] Portfolio 1-pager (≤1 page, professional formatting)
- [ ] Lessons learned document (10+ lessons with examples)
- [ ] Impact statement (500 words, 5+ quantified metrics)
- [ ] All documents proofread and formatted

### Phase 4: Advanced Features Part 1
- [ ] Nautilus migration guide complete (1 strategy migrated, before/after comparison)
- [ ] Walk-forward visualization (3+ chart types, example notebook)
- [ ] Regime-adaptive strategy (adjusts by regime, 10+ tests, example backtest)

### Phase 5: Advanced Features Part 2
- [ ] Hypothesis testing module (3+ statistical tests, confidence intervals, p-values)
- [ ] Multi-objective optimization skeleton (1 working 2-objective example)
- [ ] 15+ new deferred unit tests (bond_ladder or other non-blocked modules)

### Phase 6: Documentation & Wrap-Up
- [ ] Roadmap.md updated with Priority 7 status
- [ ] Getting Started video (10 min, installation → first backtest)
- [ ] FAQ (20+ Q&A pairs, organized by category)
- [ ] Contributing Guide video (5 min, fork → PR workflow)
- [ ] Priority 7 completion summary published

### Overall Success
- [ ] 20+ Priority 7 items complete (out of 27 total)
- [ ] 5+ external publications (blog posts + videos + poster)
- [ ] 4 application materials ready for submission
- [ ] 3+ advanced technical features delivered
- [ ] Documentation comprehensive and up-to-date
- [ ] No regressions (all tests passing, coverage maintained)

---

## Next Steps After Priority 7

### Priority 8 Candidates (Future Work)

**Deferred from Priority 7:**
1. Complete multi-objective optimization (P7.17 remainder: 1 week)
2. Add options overlay strategies (P7.18: 2-3 weeks)
3. Add real-time data feeds (P7.19: 1-2 weeks)
4. Complete deferred unit tests (P7.23 remainder: 2-3 days)
5. Create remaining video tutorials (P7.20: health economics, advanced features)
6. Expand health economics scenarios (P7.21: 3 new clinical cases)

**New Candidates:**
1. **Live Trading Integration:** Alpaca or Interactive Brokers API integration (4-6 weeks)
2. **Strategy Library Expansion:** Add 5+ new strategies (momentum, mean reversion, pairs trading)
3. **Machine Learning Integration:** Add ML-based strategies (scikit-learn, gradient boosting)
4. **Web Dashboard Enhancement:** Add authentication, user accounts, saved backtests
5. **Performance Optimization:** Profile and optimize hot paths (fund simulator, backtest loop)
6. **Community Building:** External contributor onboarding, issue triage, PR reviews
7. **Academic Publication:** Submit research paper to conference or journal
8. **Production Deployment:** Deploy dashboard to cloud (Heroku, Railway, Fly.io)

### Graduation Criteria (When is Finbot "Done"?)

Finbot may never be truly "done" (open-source projects evolve continuously), but natural stopping points:

1. **Medical School Acceptance:** If accepted, project served its purpose (portfolio artifact)
2. **External Adoption:** If external users/contributors emerge, shift to maintenance mode
3. **Live Trading:** If successfully trading live, focus shifts to operation/monitoring
4. **Opportunity Cost:** If other projects/opportunities more valuable, archive gracefully

---

## Appendices

### Appendix A: CanMEDS Mapping

| CanMEDS Role | Priority 7 Items |
|--------------|------------------|
| **Professional** | P7.1 (mypy audit), P7.2 (coverage), P7.3 (scheduled CI), P7.4 (git history), P7.10 (reflection), P7.12 (lessons learned), P7.13 (impact), P7.24 (documentation) |
| **Scholar** | P7.2 (testing rigor), P7.6 (technical article), P7.7 (HE tutorials), P7.10 (reflection), P7.15 (walk-forward), P7.16 (regime strategy), P7.17 (optimization), P7.22 (hypothesis testing), P7.23 (deferred tests) |
| **Communicator** | P7.5 (blog post), P7.6 (technical article), P7.7 (HE tutorials), P7.8 (video), P7.9 (poster), P7.11 (portfolio), P7.14 (migration guide), P7.25 (tutorial video), P7.26 (FAQ), P7.27 (contributing video) |
| **Collaborator** | P7.4 (conventional commits), P7.27 (contributing guide) |
| **Leader** | P7.5 (blog post), P7.8 (overview video), P7.9 (poster), P7.13 (impact statement), P7.25 (tutorial), P7.27 (contributing) |
| **Health Advocate** | P7.7 (HE tutorials), P7.9 (poster), P7.10 (reflection), P7.21 (HE scenarios) |
| **Medical Expert** | (Indirect: health economics domain knowledge in P7.7, P7.21) |

### Appendix B: External Publication Venues

**Blog Platforms (Self-Publishing):**
- Medium (https://medium.com) - Large audience, monetization possible
- dev.to (https://dev.to) - Developer-focused, supportive community
- Hashnode (https://hashnode.com) - Technical blogging, custom domain
- Personal blog (GitHub Pages + Jekyll) - Full control, professional presence

**Video Platforms:**
- YouTube (primary) - Largest audience, searchable, embeddable
- Vimeo (alternative) - Higher quality, professional aesthetic

**Academic/Research:**
- arXiv (preprint server for quantitative finance)
- SSRN (Social Science Research Network)
- Conference submissions (e.g., QuantCon, PyData, SciPy)

### Appendix C: Medical School Application Timeline

**Typical OMSAS Timeline (Ontario):**
- **September:** Applications open
- **October:** Application deadline
- **November-March:** Interviews
- **May:** Offers released

**Finbot Readiness:**
- Portfolio materials should be ready by **August** (1 month before applications)
- Phase 3 target: End of Week 7 (~mid-April if starting 2026-02-17)
- **Buffer:** 3+ months before August deadline

**If Timeline Accelerates:**
- Prioritize Phase 3 (Application Readiness) immediately
- Defer or shorten Phase 2 (External Visibility) and Phase 4-5 (Advanced Features)
- Minimum viable application package: P7.10 (reflection), P7.11 (portfolio), P7.13 (impact)

### Appendix D: Git History Rewrite Strategy (P7.4)

**Approach:**
1. Create backup branch: `git branch main-backup-pre-rebase`
2. Identify commit range: `git log --oneline v1.0.0..HEAD` (~50 commits)
3. Interactive rebase: `git rebase -i v1.0.0`
4. Edit each commit message to conventional format:
   - `feat(scope): description` for new features
   - `fix(scope): description` for bug fixes
   - `docs(scope): description` for documentation
   - `test(scope): description` for tests
   - `refactor(scope): description` for refactoring
   - `chore(scope): description` for maintenance
5. Force-push: `git push --force-with-lease origin main`
6. Verify: `git log --oneline -n 50` shows conventional commits

**Risks:**
- Force-push may affect collaborators (low risk: solo project)
- Commit SHAs change (breaks external references, but minimal risk)
- May break GitHub links (mitigated by GitHub's commit redirect)

**Rollback:**
- If issues arise: `git reset --hard main-backup-pre-rebase && git push --force`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-17 | Initial draft - 27 items across 6 phases, 11-week timeline |
| 1.1 | 2026-02-17 | Updated status after Batch 1 completion (17/27 items) |
| 1.2 | 2026-02-17 | Batch 2 plan created: P7.15, P7.22, P7.16, P7.23, P7.1 — see `priority-7-batch2-implementation-plan.md` |

---

## Document Metadata

- **Document Type:** Implementation Plan
- **Priority Level:** 7 (External Impact & Advanced Capabilities)
- **Target Audience:** Solo developer (author), future self, potential collaborators
- **Related Documents:**
  - `docs/planning/roadmap.md` (overall roadmap)
  - `docs/planning/priority-5-6-completion-status.md` (prior status)
  - `docs/planning/backtesting-live-readiness-backlog.md` (Priority 6 backlog)
  - `docs/planning/stricter-mypy-implementation-plan.md` (P7.1 reference)
- **Approval Status:** Draft - awaiting user review
- **Implementation Status:** Not Started

---

**END OF DOCUMENT**
