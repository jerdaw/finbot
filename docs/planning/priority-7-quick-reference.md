# Priority 7 Quick Reference

**Version:** 1.0
**Created:** 2026-02-17
**Full Plan:** `docs/planning/priority-7-implementation-plan.md`

---

## Overview

**Focus:** External Impact & Advanced Capabilities
**Duration:** 11 weeks (6 phases)
**Total Items:** 27 (20+ expected complete)

---

## Quick Summary by Category

### 7.1 Completion & Polish (4 items)
- Complete Priority 5 to 100%
- Increase coverage to 60%+
- Enable scheduled CI
- Clean git history

### 7.2 External Visibility (5 items)
- 3 blog posts (Why Finbot, Backtrader vs Nautilus, Health Economics series)
- 1 overview video
- 1 research poster

### 7.3 Application Readiness (4 items)
- CanMEDS reflection essay
- Portfolio 1-pager
- Lessons learned
- Impact statement

### 7.4 Advanced Features (6 items, 3 deferred)
- Nautilus migration guide
- Walk-forward visualization
- Regime-adaptive strategy
- Multi-objective optimization (partial)
- ~Options overlay (DEFERRED)~
- ~Real-time data (DEFERRED)~

### 7.5 Deferred Items (4 items)
- Video tutorials (3 videos)
- Health economics scenarios (+3)
- Hypothesis testing
- Deferred unit tests

### 7.6 Documentation (4 items)
- Roadmap updates
- Getting Started video
- FAQ (20+ Q&A)
- Contributing Guide video

---

## 6 Phases (11 weeks)

| Phase | Weeks | Focus | Deliverables |
|-------|-------|-------|--------------|
| **1. Completion Sprint** | 1-2 | Priority 5 → 100% | Coverage 60%+, scheduled CI, clean git history |
| **2. External Visibility** | 3-5 | Publications | 3 blog posts, 1 video, 1 poster |
| **3. Application Readiness** | 6-7 | Portfolio | 4 application documents |
| **4. Advanced Features 1** | 8-9 | Technical depth | Migration guide, visualizations, regime strategy |
| **5. Advanced Features 2** | 10 | Optimization | Hypothesis testing, multi-objective optimization |
| **6. Documentation** | 11 | Wrap-up | Videos, FAQ, roadmap updates |

---

## Key Milestones

- **M1 (Week 2):** Priority 5 at 100%, coverage ≥60%
- **M2 (Week 5):** 3+ blog posts published, 1 video, 1 poster
- **M3 (Week 7):** 4 application documents ready
- **M4 (Week 9):** 3 advanced features delivered
- **M5 (Week 11):** Priority 7 complete, documentation updated

---

## Decision Gates

**Gate 1 (Week 2):** Continue to Phase 2 or focus on applications?
- **Go:** Priority 5 complete, tests passing, coverage ≥60%
- **No-Go:** If P5 takes >2 weeks, defer Phase 2

**Gate 2 (Week 5):** Prioritize applications or continue features?
- **Accelerate Phase 3:** If med school deadline <2 months out
- **Continue:** If timeline comfortable

**Gate 3 (Week 9):** Extend Phase 5 or wrap up?
- **Extend:** If multi-objective optimization nearly done (+1 week)
- **Defer:** If incomplete, move to Priority 8

---

## Priority Matrix (by value/effort)

### High Value, Low Effort (DO FIRST)
- P7.2: Coverage to 60%+ (S, 3-5 days)
- P7.3: Scheduled CI (S, 2-4 hours)
- P7.11: Portfolio 1-pager (S, 4-6 hours)
- P7.13: Impact statement (S, 3-4 hours)
- P7.26: FAQ (S, 3-4 hours)

### High Value, Medium Effort (DO NEXT)
- P7.5: "Why I Built Finbot" blog (M, 1-2 days)
- P7.6: Backtrader vs Nautilus article (M, 2-3 days)
- P7.10: CanMEDS reflection (M, 2-3 days)
- P7.14: Nautilus migration guide (M, 3-5 days)
- P7.22: Hypothesis testing (M, 3-5 days)

### High Value, High Effort (PRIORITIZE CAREFULLY)
- P7.7: Health Economics tutorial series (L, 1-2 weeks)
- P7.17: Multi-objective optimization (L, 1-2 weeks) - **Partial delivery**

### Medium Value (DO IF TIME)
- P7.1: Stricter mypy Phase 1 (M, 1 week) - **Already started in P5**
- P7.15: Walk-forward visualization (M, 3-5 days)
- P7.16: Regime-adaptive strategy (M, 4-6 days)
- P7.20: Video tutorials (L, 1-2 weeks)
- P7.21: Health economics scenarios (M, 4-6 days)
- P7.23: Deferred unit tests (M, 4-6 days)

### Deferred to Priority 8
- P7.18: Options overlay (L, 2-3 weeks, blocked on data)
- P7.19: Real-time data (L, 1-2 weeks, cost unclear)

---

## Critical Success Factors

1. **Priority 5 Completion:** Must reach 100% in Phase 1 (weeks 1-2)
2. **External Publications:** At least 3 blog posts + 1 video in Phase 2 (weeks 3-5)
3. **Application Materials:** All 4 documents ready by end of Phase 3 (week 7)
4. **No Regressions:** All 866+ tests passing throughout
5. **Documentation Currency:** Roadmap and docs updated in Phase 6 (week 11)

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| **Scope creep** | Defer P7.17, P7.18, P7.19 to Priority 8 if needed |
| **Writing takes longer** | Prioritize P7.5, P7.6 (highest visibility) |
| **Med school deadline accelerates** | Skip Phases 4-5, jump to Phase 6 |
| **Force-push for P7.4** | Create backup branch first |
| **API keys missing for P7.3** | Document manual workaround |

---

## Quick Commands

```bash
# Phase 1: Completion Sprint
make test  # Verify all tests passing
make check  # Run code quality checks
uv run pytest --cov  # Check coverage

# Phase 2: External Visibility
# (Manual: write blog posts, record videos)

# Phase 3: Application Readiness
# (Manual: write reflection essays, portfolio pieces)

# Phase 4-5: Advanced Features
make test  # Run tests after each feature
make docs-serve  # Preview documentation

# Phase 6: Documentation
make changelog  # Generate changelog
make docs-build  # Build documentation
```

---

## Key Outputs

**Documents:**
- 5 external publications (blog posts, videos, poster)
- 4 application materials (reflection, portfolio, lessons, impact)
- 3 guides (migration, visualization, FAQ)
- 2 videos (Getting Started, Contributing)

**Code:**
- 3 advanced features (migration guide, visualizations, regime strategy)
- 1 optimization framework (partial)
- 1 hypothesis testing module
- 15+ new unit tests

**Metrics:**
- Priority 5: 93.3% → 100%
- Coverage: 59.20% → ≥60%
- Total tests: 866 → 900+
- Documentation files: 113 → 125+

---

## CanMEDS Coverage

✅ **Professional:** P7.1, P7.2, P7.3, P7.4, P7.10, P7.12, P7.13, P7.24
✅ **Scholar:** P7.2, P7.6, P7.7, P7.10, P7.15, P7.16, P7.17, P7.22, P7.23
✅ **Communicator:** P7.5, P7.6, P7.7, P7.8, P7.9, P7.11, P7.14, P7.25, P7.26, P7.27
✅ **Collaborator:** P7.4, P7.27
✅ **Leader:** P7.5, P7.8, P7.9, P7.13, P7.25, P7.27
✅ **Health Advocate:** P7.7, P7.9, P7.10, P7.21

All 7 CanMEDS roles represented.

---

## When to Use This Document

- **Planning:** Review before starting each phase
- **Daily:** Check current phase tasks and acceptance criteria
- **Weekly:** Review progress toward milestones
- **Decision Points:** Consult decision gates at end of Weeks 2, 5, 9
- **Handoff:** Share with collaborators or future self

---

## Related Documents

- **Full Plan:** `docs/planning/priority-7-implementation-plan.md` (this is the authoritative source)
- **Roadmap:** `docs/planning/roadmap.md` (overall project roadmap)
- **Prior Status:** `docs/planning/priority-5-6-completion-status.md`
- **Stricter Mypy Plan:** `docs/planning/stricter-mypy-implementation-plan.md` (for P7.1)

---

**Last Updated:** 2026-02-17
