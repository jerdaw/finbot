# E6: NautilusTrader Pilot Implementation Plan

**Created:** 2026-02-16
**Epic:** E6 - NautilusTrader Pilot and Decision Gate
**Estimated Effort:** M-L (5-10 days)

## Overview

Pilot NautilusTrader integration to evaluate it as an alternative/complementary backtesting engine to Backtrader. This is a **build vs buy decision gate** - we will implement a minimal viable pilot, evaluate it, and decide whether to proceed with full Nautilus integration or stick with Backtrader.

## Current State

**Already Implemented (E0-E5):**
- ✅ Engine-agnostic contracts (`finbot/core/contracts/`)
- ✅ ExecutionSimulator with orders, latency, risk, checkpoints
- ✅ Backtrader adapter with parity testing
- ✅ 645 tests passing

**What's Missing:**
- NautilusTrader adapter implementation
- Execution integration (ExecutionSimulator ↔ Nautilus)
- Parity testing (Nautilus vs Backtrader)
- Evaluation and decision documentation

## Goals

1. **Minimal Viable Pilot** - Get one strategy running via Nautilus
2. **Evaluation** - Compare Nautilus to Backtrader on key metrics
3. **Decision** - Make informed build/buy/hybrid decision
4. **Documentation** - Record findings and rationale

## Decision Criteria

**Technical:**
- Can Nautilus match Backtrader parity within tolerance?
- Does Nautilus integrate cleanly with ExecutionSimulator?
- Is the learning curve acceptable?
- Are there deal-breaking limitations?

**Operational:**
- What's the integration effort (hours/days)?
- What's the ongoing maintenance burden?
- Does Nautilus provide sufficient value for complexity?
- Can we leverage Nautilus's unique features?

**Strategic:**
- Does Nautilus enable live trading more easily?
- Is the ecosystem/community healthy?
- Are we vendor-locked or can we switch later?

## Tasks

### E6-T1: Single-Strategy Pilot Adapter (M - 3-5 days)

**Goal:** Get one simple strategy (Rebalance) running via NautilusTrader

**Scope:**
- Install and configure NautilusTrader
- Create minimal NautilusAdapter implementing BacktestEngine interface
- Adapt one strategy (Rebalance) to Nautilus
- Run basic backtest and verify it produces results
- Document setup and integration points

**Out of scope:**
- Full feature parity with Backtrader
- All 12 strategies
- Production deployment
- Performance optimization

**Acceptance:**
- Nautilus installed and configured
- NautilusAdapter exists and implements BacktestEngine
- Rebalance strategy runs via Nautilus path
- Basic BacktestRunResult returned (even if incomplete)
- Setup documented

### E6-T2: Comparative Evaluation Report (S - 1-2 days)

**Goal:** Document Nautilus vs Backtrader comparison

**Output:** `docs/research/nautilus-pilot-evaluation.md`

**Evaluation Dimensions:**
1. **Fill Realism:** How realistic are fills? Slippage modeling?
2. **Latency Fit:** Does Nautilus support our latency simulation needs?
3. **Integration Cost:** Hours spent, complexity encountered
4. **Ops Complexity:** Setup, configuration, debugging experience
5. **Feature Comparison:** What Nautilus has/lacks vs Backtrader
6. **Performance:** Speed, memory usage
7. **Ecosystem:** Documentation quality, community support, maintenance

**Format:**
- Comparative table (Backtrader vs Nautilus)
- Quantified metrics where possible
- Subjective assessment where quantification not feasible
- Code examples showing integration differences

**Acceptance:**
- Comprehensive comparison document
- Quantified metrics (integration hours, performance)
- Clear pros/cons for each dimension
- Honest assessment of pain points

### E6-T3: Go/No-Go Decision Memo (S - 1 day)

**Goal:** Make and document the build/buy decision

**Output:** ADR documenting the decision

**Options:**
1. **Go with Nautilus:** Full integration, deprecate Backtrader over time
2. **No-Go on Nautilus:** Stick with Backtrader, abandon Nautilus
3. **Hybrid:** Support both engines, let users choose
4. **Defer:** Need more evaluation, extend pilot

**Decision Memo Contents:**
- Decision statement (which option)
- Rationale (why this decision)
- Quantified tradeoffs (effort, benefits, costs)
- Risk assessment
- Implementation roadmap (if Go)
- Exit criteria (if Defer)

**Acceptance:**
- Clear decision recorded
- Rationale documented with evidence from T2
- Team alignment (or documented disagreement)
- Next steps defined

## Implementation Approach

### Phase 1: Setup and Familiarization (E6-T1 Part 1)

**Goal:** Get NautilusTrader installed and running basic examples

**Steps:**
1. Research NautilusTrader documentation
   - Installation requirements
   - Basic architecture (Actor model, event-driven)
   - Data feed setup
   - Strategy API
2. Install NautilusTrader
   - Add to `pyproject.toml`
   - Handle dependencies
   - Verify installation with basic example
3. Run Nautilus examples
   - Understand event loop
   - Understand data handling
   - Understand order execution model
4. Document findings
   - Installation notes
   - Architecture overview
   - Key differences vs Backtrader

**Time Estimate:** 4-8 hours

### Phase 2: Minimal Adapter (E6-T1 Part 2)

**Goal:** Create NautilusAdapter skeleton

**Steps:**
1. Create `finbot/adapters/nautilus/` directory
2. Create `nautilus_adapter.py` implementing `BacktestEngine`
3. Implement minimal interface methods:
   - `run_backtest()` - main entry point
   - Data feed construction
   - Strategy instantiation
   - Result extraction
4. Stub out incomplete functionality
   - Log TODOs for missing features
   - Return minimal BacktestRunResult

**Files Created:**
- `finbot/adapters/nautilus/__init__.py`
- `finbot/adapters/nautilus/nautilus_adapter.py`
- `finbot/adapters/nautilus/strategy_adapter.py` (if needed)
- `finbot/adapters/nautilus/data_feed_builder.py` (if needed)

**Time Estimate:** 6-10 hours

### Phase 3: Strategy Adaptation (E6-T1 Part 3)

**Goal:** Get Rebalance strategy working

**Steps:**
1. Understand Nautilus strategy API
   - How strategies subscribe to data
   - How strategies submit orders
   - How strategies track positions
2. Adapt Rebalance strategy
   - Map Backtrader API → Nautilus API
   - Handle timing (Nautilus is event-driven, not bar-based)
   - Handle rebalancing logic
3. Test with simple data
   - 2-asset portfolio (SPY + TLT)
   - Short time period (1 year)
   - Verify execution
4. Debug and iterate
   - Fix errors
   - Handle edge cases
   - Verify basic correctness

**Time Estimate:** 6-12 hours

### Phase 4: Evaluation (E6-T2)

**Goal:** Document findings

**Steps:**
1. Measure integration effort
   - Track time spent on each phase
   - Document pain points
   - Document pleasant surprises
2. Run comparison tests
   - Same strategy, same data, Backtrader vs Nautilus
   - Compare results (returns, trades, metrics)
   - Measure performance (speed, memory)
3. Write evaluation report
   - Fill out comparison table
   - Document findings
   - Make preliminary recommendation

**Time Estimate:** 8-12 hours

### Phase 5: Decision (E6-T3)

**Goal:** Make the call

**Steps:**
1. Review evaluation with stakeholders (if applicable)
2. Consider strategic factors
3. Draft decision memo
4. Record as ADR
5. Define next steps

**Time Estimate:** 4-8 hours

## Key Unknowns and Risks

### Unknown: Nautilus Learning Curve

**Risk:** Nautilus has a steeper learning curve than expected

**Mitigation:**
- Allocate extra time for learning (Phase 1)
- Engage with Nautilus community for help
- Document learning process for future reference

**Exit Criteria:** If learning takes >16 hours, consider No-Go

### Unknown: Contract Compatibility

**Risk:** Nautilus results don't map cleanly to our contracts

**Mitigation:**
- Start with minimal contract compliance
- Document gaps and workarounds
- Evaluate if gaps are deal-breakers

**Decision Point:** If contract compatibility requires major refactoring, lean toward No-Go

### Unknown: Performance

**Risk:** Nautilus is slower than Backtrader

**Mitigation:**
- Measure performance in Phase 4
- Consider if slowness is acceptable tradeoff for other features

**Threshold:** If >5x slower, document as significant cost

### Unknown: Execution Integration

**Risk:** ExecutionSimulator doesn't integrate with Nautilus

**Mitigation:**
- This is actually out of scope for pilot
- Document as future work if Go decision made

**Note:** Don't block pilot on ExecutionSimulator integration

## Success Metrics

**Must Achieve:**
- [ ] Nautilus installed and working
- [ ] One strategy runs via Nautilus
- [ ] Results returned in BacktestRunResult format
- [ ] Evaluation report completed
- [ ] Decision documented

**Nice to Have:**
- [ ] Parity with Backtrader results (within tolerance)
- [ ] Performance comparable or better
- [ ] ExecutionSimulator integration (stretch goal)
- [ ] Multiple strategies working

## Timeline

**Optimistic:** 5 days (40 hours)
**Realistic:** 7-10 days (56-80 hours)
**Pessimistic:** 12-15 days (96-120 hours)

**Breakdown:**
- E6-T1 Phase 1: 4-8 hours
- E6-T1 Phase 2: 6-10 hours
- E6-T1 Phase 3: 6-12 hours
- E6-T2: 8-12 hours
- E6-T3: 4-8 hours
- **Total: 28-50 hours (realistic 40 hours)**

## Deliverables

1. **Code:**
   - `finbot/adapters/nautilus/` (minimal adapter)
   - Tests (basic smoke tests)

2. **Documentation:**
   - `docs/research/nautilus-pilot-evaluation.md` (evaluation)
   - ADR documenting decision
   - Setup/installation notes

3. **Decision:**
   - Go/No-Go/Hybrid/Defer clearly stated
   - Next steps defined

## Out of Scope (Explicitly Deferred)

- Full feature parity with Backtrader
- All 12 strategies
- Production deployment
- Live trading integration
- Performance optimization
- ExecutionSimulator integration (stretch goal only)
- Walk-forward analysis via Nautilus
- Regime detection via Nautilus
- Cost model integration
- Corporate actions handling

## Next Steps After E6

**If Go:**
- E7: Full Nautilus integration (all strategies)
- E8: ExecutionSimulator integration
- E9: Production readiness

**If No-Go:**
- Continue with Backtrader as primary engine
- Consider Backtrader enhancements
- Focus on live trading via Backtrader path

**If Hybrid:**
- Maintain both adapters
- Define which strategies use which engine
- Plan migration strategy

**If Defer:**
- Define what additional information is needed
- Plan extended pilot
- Set decision deadline

## Open Questions

1. **Nautilus Version:** Which version should we target? Latest stable?
2. **Python Compatibility:** Does Nautilus support Python 3.13?
3. **Data Format:** Can we use our existing data format or do we need conversion?
4. **Strategy Pattern:** Event-driven vs bar-based - is adaptation straightforward?
5. **Backtest Mode:** Does Nautilus support true backtesting or just simulation?

## References

- NautilusTrader docs: https://nautilustrader.io/
- NautilusTrader GitHub: https://github.com/nautechsystems/nautilus_trader
- Our contracts: `finbot/core/contracts/`
- Backtrader adapter: `finbot/adapters/backtrader/`
- E5 execution system: `finbot/services/execution/`

---

## Implementation Status

### Phase 1: Setup and Familiarization ✅ COMPLETE
- [x] Research NautilusTrader documentation
- [x] Document installation requirements (Python 3.12-3.14, uv compatible)
- [x] Document architecture overview (BacktestEngine, event-driven)
- [x] Create setup guide (`e6-nautilus-setup-guide.md`)
- [x] Document key differences vs Backtrader

**Time Spent:** ~2 hours (research and documentation)

### Phase 2: Minimal Adapter - IN PROGRESS
- [x] Create `finbot/adapters/nautilus/` directory
- [x] Create adapter skeleton (`nautilus_adapter.py`)
- [x] Document all required methods with TODOs
- [ ] **REQUIRES MANUAL WORK:** Implement TODOs (cannot be automated)
- [ ] **REQUIRES MANUAL WORK:** Test implementation

**Files Created:**
- `finbot/adapters/nautilus/__init__.py` ✅
- `finbot/adapters/nautilus/nautilus_adapter.py` ✅ (skeleton with TODOs)

**Next Steps:** See `e6-t1-implementation-guide.md` for detailed manual implementation guide

**Status:** Automated work complete, manual implementation required
**Next:** User must install Nautilus and implement TODOs

### E6-T2: Comparative Evaluation Report ✅ TEMPLATE READY
- [x] Create comprehensive evaluation template
- [x] Define evaluation dimensions (8 categories)
- [x] Create comparison matrices
- [x] Define quantified scoring system
- [x] Document decision factors (Go/No-Go/Hybrid/Defer)
- [ ] **REQUIRES MANUAL WORK:** Fill in template after E6-T1 completes

**Files Created:**
- `docs/research/nautilus-pilot-evaluation.md` ✅ (comprehensive template)

**Status:** Template ready, awaiting E6-T1 completion to fill in

### E6-T3: Go/No-Go Decision Memo ✅ TEMPLATE READY
- [x] Create ADR template for decision
- [x] Define 4 decision options (Go/No-Go/Hybrid/Defer)
- [x] Create implementation plans for each option
- [x] Define quantified tradeoff framework
- [x] Create risk assessment structure
- [x] Define validation criteria
- [ ] **REQUIRES MANUAL WORK:** Fill in template after E6-T2 completes

**Files Created:**
- `docs/adr/ADR-011-nautilus-decision.md` ✅ (decision template)

**Status:** Template ready, awaiting E6-T2 evaluation to fill in

---

## E6 Preparation Summary

**Automated Work:** ✅ COMPLETE
- Research and documentation (Phase 1)
- Adapter skeleton creation (Phase 2)
- Evaluation framework (E6-T2 template)
- Decision framework (E6-T3 template)

**Manual Work Required:**
1. **E6-T1:** Install Nautilus, implement adapter, run tests (12-26 hours)
2. **E6-T2:** Fill in evaluation template with findings (8-12 hours)
3. **E6-T3:** Make and document decision (4-8 hours)

**Ready to Proceed:**
- Implementation guide: `docs/planning/e6-t1-implementation-guide.md`
- Setup guide: `docs/planning/e6-nautilus-setup-guide.md`
- Evaluation template: `docs/research/nautilus-pilot-evaluation.md`
- Decision template: `docs/adr/ADR-011-nautilus-decision.md`
- Adapter skeleton: `finbot/adapters/nautilus/nautilus_adapter.py`
