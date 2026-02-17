# ADR-011: NautilusTrader Adoption Decision

**Status:** TEMPLATE - Fill in after E6-T2 evaluation complete
**Date:** TBD (after E6-T1 and E6-T2 completion)
**Deciders:** [Project Lead, Technical Team]
**Epic:** E6 - NautilusTrader Pilot and Decision Gate

## Context and Problem Statement

We have a working backtesting system built on Backtrader with engine-agnostic contracts. We piloted NautilusTrader integration (E6-T1) and evaluated it comprehensively (E6-T2). Now we must decide whether to:

1. **Go** - Adopt Nautilus, deprecate Backtrader over time
2. **No-Go** - Stick with Backtrader, abandon Nautilus
3. **Hybrid** - Support both engines for different use cases
4. **Defer** - Need more evaluation before deciding

This decision affects:
- Live trading readiness timeline
- Backtesting fidelity and realism
- Development complexity and maintenance burden
- Long-term strategic flexibility

## Decision Drivers

- [FILL IN: Most important factors from evaluation]
- [FILL IN: Integration effort vs value provided]
- [FILL IN: Live trading enablement timeline]
- [FILL IN: Ecosystem health and longevity]
- [FILL IN: Team learning curve and maintenance burden]

## Considered Options

### Option 1: Go with Nautilus (Full Adoption)

**Description:** Adopt NautilusTrader as primary backtesting engine, deprecate Backtrader over 6-12 months.

**Pros:**
- [FILL IN: e.g., Enables live trading with same codebase]
- [FILL IN: e.g., More realistic fill simulation]
- [FILL IN: e.g., Better performance]
- [FILL IN: e.g., Active development and growing ecosystem]

**Cons:**
- [FILL IN: e.g., Steeper learning curve]
- [FILL IN: e.g., Migration effort for existing strategies]
- [FILL IN: e.g., Less mature documentation]
- [FILL IN: e.g., Rust dependency complicates deployment]

**Effort Estimate:** [X] person-weeks
**Risk:** [Low/Medium/High]

### Option 2: No-Go on Nautilus (Stick with Backtrader)

**Description:** Continue with Backtrader as sole backtesting engine, abandon Nautilus integration.

**Pros:**
- [FILL IN: e.g., No migration effort]
- [FILL IN: e.g., Team already familiar]
- [FILL IN: e.g., Simpler deployment]
- [FILL IN: e.g., Mature, stable codebase]

**Cons:**
- [FILL IN: e.g., No built-in live trading path]
- [FILL IN: e.g., Less realistic fill simulation]
- [FILL IN: e.g., Limited ongoing development]
- [FILL IN: e.g., Potential future technical debt]

**Effort Estimate:** 0 (no change)
**Risk:** [Low/Medium/High]

### Option 3: Hybrid Approach (Support Both)

**Description:** Maintain both Backtrader and Nautilus adapters, let users/strategies choose.

**Pros:**
- [FILL IN: e.g., Flexibility to use best tool for each job]
- [FILL IN: e.g., Gradual migration path]
- [FILL IN: e.g., De-risk single-engine dependency]
- [FILL IN: e.g., Leverage Nautilus for live, Backtrader for backtesting]

**Cons:**
- [FILL IN: e.g., Maintain two engines doubles complexity]
- [FILL IN: e.g., Parity testing burden]
- [FILL IN: e.g., Confusing for new developers]
- [FILL IN: e.g., Neither engine gets full optimization]

**Effort Estimate:** [X] person-weeks
**Risk:** [Low/Medium/High]

### Option 4: Defer Decision (Extended Evaluation)

**Description:** Need more data before deciding. Extend pilot with additional scenarios.

**Pros:**
- [FILL IN: e.g., More confidence in final decision]
- [FILL IN: e.g., Time to evaluate upcoming Nautilus features]
- [FILL IN: e.g., Reduce risk of wrong choice]

**Cons:**
- [FILL IN: e.g., Delays live trading roadmap]
- [FILL IN: e.g., Opportunity cost of deferred decision]
- [FILL IN: e.g., Evaluation fatigue]

**Exit Criteria:** [FILL IN: What would make us confident to decide?]
**Timeline:** [FILL IN: Defer until when?]

## Decision Outcome

**Chosen option:** [Go / No-Go / Hybrid / Defer]

**Rationale:**

[2-3 paragraphs explaining the decision based on evaluation evidence]

Example structure:
- "Based on E6-T2 evaluation, we found that..."
- "The key deciding factor was..."
- "While Option X had advantages Y, we chose Option Z because..."
- "This aligns with our strategic goal of..."

**Key Evidence from E6-T2:**

| Criterion | Backtrader Score | Nautilus Score | Winner | Weight | Impact |
| --- | --- | --- | --- | --- | --- |
| Ease of Use | [X] | [Y] | [?] | 20% | [?] |
| Backtesting Fidelity | [X] | [Y] | [?] | 25% | [?] |
| Performance | [X] | [Y] | [?] | 15% | [?] |
| Live Trading Support | [X] | [Y] | [?] | 15% | [?] |
| Documentation | [X] | [Y] | [?] | 10% | [?] |
| Community Support | [X] | [Y] | [?] | 5% | [?] |
| Maintenance Risk | [X] | [Y] | [?] | 5% | [?] |
| Integration Cost | [X] | [Y] | [?] | 5% | [?] |
| **Weighted Total** | **[X]** | **[Y]** | **[?]** | 100% | - |

**Quantified Tradeoffs:**

- **Integration Effort:** [X hours actual vs Y hours estimated]
- **Performance Gain:** [X% faster / slower]
- **Parity Results:** [Within tolerance? Yes/No - explain]
- **Live Trading Timeline Impact:** [+/- X months]

## Implementation Plan

**If Go:**

### Phase 1: Full Strategy Migration (E7)
- [ ] Migrate all 12 strategies to Nautilus
- [ ] Parity testing for each strategy
- [ ] Performance benchmarking
- Timeline: [X weeks]

### Phase 2: ExecutionSimulator Integration (E8)
- [ ] Integrate ExecutionSimulator with Nautilus
- [ ] Checkpoint/recovery support
- [ ] Risk controls integration
- Timeline: [X weeks]

### Phase 3: Production Readiness (E9)
- [ ] CI/CD for Nautilus path
- [ ] Documentation updates
- [ ] Deployment guide
- Timeline: [X weeks]

### Phase 4: Backtrader Deprecation (E10)
- [ ] Mark Backtrader adapter as legacy
- [ ] Maintain for 6 months
- [ ] Remove after transition complete
- Timeline: [X months]

**If No-Go:**

### Immediate Actions:
- [ ] Document learnings from pilot
- [ ] Apply insights to Backtrader improvements
- [ ] Focus on live trading via alternative path
- [ ] Consider custom execution layer

### Next Steps:
- Enhance Backtrader fill simulation
- Build live trading adapter using different approach
- Revisit decision in [X months] if needs change

**If Hybrid:**

### Phase 1: Establish Clear Use Cases
- [ ] Define when to use Backtrader vs Nautilus
- [ ] Document decision criteria
- Timeline: [X weeks]

### Phase 2: Parity Framework
- [ ] Automated parity testing across both engines
- [ ] Alert on divergence
- Timeline: [X weeks]

### Phase 3: Migration Path
- [ ] Strategy-by-strategy migration plan
- [ ] Gradual transition over [X months]

**If Defer:**

### Extended Evaluation Tasks:
- [ ] [FILL IN: Additional scenarios to test]
- [ ] [FILL IN: Features to wait for]
- [ ] [FILL IN: Information to gather]

### Decision Deadline: [Date]

### Exit Criteria:
- [FILL IN: What would trigger Go decision?]
- [FILL IN: What would trigger No-Go decision?]

## Consequences

### Positive Consequences

**If Go:**
- [FILL IN: e.g., Live trading path clear]
- [FILL IN: e.g., More realistic backtests]
- [FILL IN: e.g., Better performance]

**If No-Go:**
- [FILL IN: e.g., Avoid migration complexity]
- [FILL IN: e.g., Focus development effort elsewhere]
- [FILL IN: e.g., Maintain team expertise]

**If Hybrid:**
- [FILL IN: e.g., Flexibility and optionality]
- [FILL IN: e.g., Risk mitigation]

**If Defer:**
- [FILL IN: e.g., Higher confidence in eventual decision]

### Negative Consequences

**If Go:**
- [FILL IN: e.g., Migration effort]
- [FILL IN: e.g., Learning curve]
- [FILL IN: e.g., Deployment complexity]

**If No-Go:**
- [FILL IN: e.g., No built-in live trading]
- [FILL IN: e.g., Potential regret if Nautilus ecosystem thrives]

**If Hybrid:**
- [FILL IN: e.g., Doubled maintenance burden]
- [FILL IN: e.g., Parity testing overhead]

**If Defer:**
- [FILL IN: e.g., Live trading timeline delay]
- [FILL IN: e.g., Opportunity cost]

### Risks and Mitigations

**Risk 1:** [FILL IN: e.g., Nautilus development slows down]
- **Probability:** [Low/Medium/High]
- **Impact:** [Low/Medium/High]
- **Mitigation:** [FILL IN]

**Risk 2:** [FILL IN: e.g., Migration takes longer than expected]
- **Probability:** [Low/Medium/High]
- **Impact:** [Low/Medium/High]
- **Mitigation:** [FILL IN]

**Risk 3:** [FILL IN: e.g., Parity issues discovered post-migration]
- **Probability:** [Low/Medium/High]
- **Impact:** [Low/Medium/High]
- **Mitigation:** [FILL IN]

## Validation and Review

**Validation Criteria:**

If Go:
- [ ] All 12 strategies migrate successfully
- [ ] Parity within tolerance for golden dataset
- [ ] Performance meets or exceeds Backtrader
- [ ] Live trading path validated

If No-Go:
- [ ] Alternative live trading path identified
- [ ] Backtrader improvements planned
- [ ] Team aligned on decision

If Hybrid:
- [ ] Use case boundaries clearly defined
- [ ] Parity testing automated
- [ ] Maintenance plan sustainable

If Defer:
- [ ] Extended evaluation plan approved
- [ ] Decision deadline set
- [ ] Exit criteria agreed

**Review Schedule:**

- **3 months:** Review progress against implementation plan
- **6 months:** Assess if decision still correct
- **12 months:** Full retrospective

**Success Metrics:**

- [FILL IN: e.g., Live trading launched within X months]
- [FILL IN: e.g., Backtest fidelity improved by X%]
- [FILL IN: e.g., Development velocity maintained/improved]
- [FILL IN: e.g., Zero critical bugs from migration]

## References

- **E6-T1 Implementation:** `docs/planning/e6-nautilus-pilot-implementation-plan.md`
- **E6-T2 Evaluation Report:** `docs/research/nautilus-pilot-evaluation.md`
- **NautilusTrader Docs:** https://nautilustrader.io/
- **BacktestEngine Interface:** `finbot/core/contracts/interfaces.py`
- **Backtrader Adapter:** `finbot/adapters/backtrader/`
- **Nautilus Adapter:** `finbot/adapters/nautilus/`
- **ADR-005:** Adapter-first backtesting architecture
- **ADR-006:** Execution system architecture

---

**Decision Date:** [TBD]
**Decision Maker:** [Name]
**Approvers:** [Names]
**Reviewers:** [Names]

**Status:** TEMPLATE - To be filled after E6-T2 completion
**Next Review:** [After decision implementation begins]
