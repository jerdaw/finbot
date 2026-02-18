# ADR-011: NautilusTrader Adoption Decision

**Status:** DECIDED - Hybrid Approach
**Date:** 2026-02-17
**Deciders:** Technical Team (based on E6-T2 comprehensive evaluation)
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

- **Live trading enablement**: Nautilus provides built-in live trading path with unified backtest/live codebase
- **Integration effort vs value**: 15 hours actual integration time (beat 12-26h estimate), feasibility proven
- **Backtesting fidelity**: Nautilus provides superior fill simulation (order queues, realistic slippage) vs Backtrader
- **Migration cost**: Full strategy migration would require 20-40 hours additional work (12 strategies)
- **Adapter pattern validation**: No contract changes needed, proving ADR-005 architecture works
- **Strategic flexibility**: Hybrid approach allows gradual migration without breaking existing workflows

## Considered Options

### Option 1: Go with Nautilus (Full Adoption)

**Description:** Adopt NautilusTrader as primary backtesting engine, deprecate Backtrader over 6-12 months.

**Pros:**
- Enables live trading with unified backtest/live codebase (same strategy code runs in both modes)
- Superior backtesting fidelity (order queues, realistic fills, probabilistic slippage)
- Excellent performance (Rust core, <1s backtest execution, ~50MB memory)
- Active development and growing ecosystem (v1.222.0, professional support available)
- Modern event-driven architecture more realistic than bar-based

**Cons:**
- Steeper learning curve (type system complexity, API learning: 2h vs Backtrader's simplicity)
- Migration effort for 12 existing strategies (20-40 hours estimated)
- Documentation gaps (API reference incomplete, requires source code diving)
- Python 3.12+ requirement (forced dropping 3.11 support)
- Type system rigidity (Money/Currency/enums instead of simple floats/strings)

**Effort Estimate:** 5-10 person-weeks (1.5 weeks pilot + 3-8 weeks full migration)
**Risk:** Medium (complexity, but adapter pattern de-risks)

### Option 2: No-Go on Nautilus (Stick with Backtrader)

**Description:** Continue with Backtrader as sole backtesting engine, abandon Nautilus integration.

**Pros:**
- Zero migration effort (keep existing 12 strategies as-is)
- Team already familiar with Backtrader API
- Simpler deployment (pure Python, no Rust dependency, Python 3.11+ support)
- Mature, stable codebase (Backtrader v1.9.78.123)
- Excellent documentation and examples
- Adequate for current backtesting-only use case

**Cons:**
- No built-in live trading path (would need separate live trading system)
- Less realistic fill simulation (simplified instant fills, basic slippage)
- Limited ongoing development (mature but quiet community)
- Potential future technical debt if live trading becomes priority
- Performance lower than Nautilus (pure Python vs Rust core)
- Bar-based model less realistic than event-driven

**Effort Estimate:** 0 (no change)
**Risk:** Low (status quo, but limits future options)

### Option 3: Hybrid Approach (Support Both)

**Description:** Maintain both Backtrader and Nautilus adapters, let users/strategies choose.

**Pros:**
- Flexibility to use best tool for each job (Nautilus for live, Backtrader for quick research)
- Gradual migration path (migrate strategies one-by-one as needed, 0 upfront cost)
- De-risk single-engine dependency (adapter pattern already supports this)
- Low risk (keep working Backtrader while learning Nautilus)
- Best of both worlds (Backtrader's ease + Nautilus's power when needed)
- Adapter pattern explicitly designed for this (ADR-005 validation)

**Cons:**
- Maintain two engines (doubles maintenance complexity)
- Parity testing burden (need CI to validate strategies that support both)
- Potentially confusing for new developers (which engine to use when?)
- Neither engine gets full optimization/focus
- Incremental migration cost over time (may exceed "big bang" in total hours)

**Effort Estimate:** 2-3 person-weeks initial setup + ongoing maintenance
**Risk:** Low (pragmatic, reversible, aligns with adapter architecture)

### Option 4: Defer Decision (Extended Evaluation)

**Description:** Need more data before deciding. Extend pilot with additional scenarios.

**Pros:**
- More confidence in final decision (test real strategies, not just minimal adapter)
- Time to evaluate upcoming Nautilus features (documentation improvements, API stability)
- Reduce risk of wrong choice (wait for community/ecosystem maturity)
- Nautilus may improve docs/API in next 6 months

**Cons:**
- Delays live trading roadmap (if live trading is 3-6 months out, evaluation blocks progress)
- Opportunity cost of deferred decision (pilot already provides good data)
- Evaluation fatigue (15 hours already invested, diminishing returns on more testing)
- Strategy parity already untested (only minimal strategy tested in pilot)

**Exit Criteria:** Migrate 1-2 real strategies (e.g., Rebalance, SMA Crossover), validate parity within tolerance
**Timeline:** Defer 1-2 months for extended evaluation

## Decision Outcome

**Chosen option:** **Hybrid Approach** (with lean toward Nautilus for live trading strategies)

**Rationale:**

Based on E6-T2 evaluation, we found that NautilusTrader integration is technically feasible (15 hours actual vs 12-26h estimated), provides significant value for live trading (unified backtest/live codebase), and delivers superior backtesting fidelity (order queues, realistic fills). The quantified comparison shows Nautilus scoring 3.95 vs Backtrader's 3.30, with particularly strong wins in high-priority categories: backtesting fidelity (5 vs 3), performance (5 vs 3), and live trading support (5 vs 1).

The key deciding factor was the **live trading timeline uncertainty**. If live trading is 3-6 months away, adopting Nautilus now makes sense to build expertise gradually. If live trading is 12+ months away or uncertain, the 20-40 hour migration cost for all 12 strategies is not justified given Backtrader works well for pure backtesting. The hybrid approach offers the best risk/reward ratio: keep Backtrader operational for existing workflows while adopting Nautilus for new strategies targeting live trading.

While Option 1 (Full Go) had advantages in simplicity (single engine) and long-term cleanliness, we chose Option 3 (Hybrid) because the adapter pattern explicitly supports multiple engines with zero additional infrastructure cost. This allows incremental migration, validates real strategy parity over time, and avoids a risky "big bang" migration. The 15-hour pilot investment is preserved, and we can reassess at 6-month intervals based on live trading progress and Nautilus ecosystem maturity. This aligns with our strategic goals of engine-agnostic backtesting (ADR-005) and live trading readiness while minimizing risk.

**Key Evidence from E6-T2:**

| Criterion | Backtrader Score | Nautilus Score | Winner | Weight | Impact |
| --- | --- | --- | --- | --- | --- |
| Ease of Use | 4 | 2 | Backtrader | 20% | 0.80 vs 0.40 |
| Backtesting Fidelity | 3 | 5 | Nautilus | 25% | 0.75 vs 1.25 |
| Performance | 3 | 5 | Nautilus | 15% | 0.45 vs 0.75 |
| Live Trading Support | 1 | 5 | Nautilus | 15% | 0.15 vs 0.75 |
| Documentation | 5 | 3 | Backtrader | 10% | 0.50 vs 0.30 |
| Community Support | 4 | 3 | Backtrader | 5% | 0.20 vs 0.15 |
| Maintenance Risk | 4 | 4 | Tie | 5% | 0.20 vs 0.20 |
| Integration Cost | 5 | 3 | Backtrader | 5% | 0.25 vs 0.15 |
| **Weighted Total** | **3.30** | **3.95** | **Nautilus** | 100% | **+19.7%** |

**Quantified Tradeoffs:**

- **Integration Effort:** 15 hours actual vs 12-26h estimated (beat lower end of range)
  - Installation: 0.5h (fast, prebuilt wheels)
  - Learning Nautilus: 2h (API complexity)
  - Data Conversion: 3h (type system learning curve)
  - Adapter Implementation: 5h (147 lines of adapter code)
  - Testing & Debugging: 4h (iterative refinement)
- **Performance Gain:** <1s backtest execution vs Backtrader baseline, ~50MB memory footprint (Rust core delivers)
- **Parity Results:** Not tested on real strategies (pilot used minimal pass-through strategy only)
  - Recommendation: Validate parity on 1-2 real strategies (Rebalance, SMA Crossover) before full migration
- **Live Trading Timeline Impact:** Enables immediate live trading development (unified backtest/live codebase)
  - Hybrid approach: 0 months delay (start Nautilus for new strategies now)
  - Full migration: 1-2 months delay (20-40h for 12 strategies)

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

**If Hybrid (CHOSEN):**

### Phase 1: Establish Clear Use Cases (Week 1)
- [ ] Document Nautilus as officially supported engine in CLAUDE.md
- [ ] Create "when to use which engine" guide
  - **Use Backtrader for:** Quick research, existing strategies, simple backtesting-only workflows
  - **Use Nautilus for:** Live trading strategies, high-fidelity simulation, performance-critical backtests
- [ ] Update README.md with Nautilus quick start
- Timeline: 1 week (2-4 hours documentation work)

### Phase 2: Parity Validation (Month 1-2)
- [ ] Migrate 1-2 simple strategies to Nautilus as learning exercise (Rebalance, SMA Crossover)
- [ ] Create E2-T2 A/B parity harness (`tests/integration/test_backtest_parity_ab.py`)
- [ ] Run parallel backtests (Backtrader vs Nautilus) on golden dataset
- [ ] Validate parity within tolerance (±0.1% total return, ±0.05% CAGR, exact trade count)
- [ ] Set up CI parity gate for strategies supporting both engines
- Timeline: 4-8 weeks (includes parity harness development)

### Phase 3: Migration Path (Month 3-6)
- [ ] **Decision gate at Month 3:** Assess live trading timeline clarity
  - If live trading confirmed within 6 months: migrate remaining strategies to Nautilus
  - If live trading deferred or uncertain: keep hybrid approach, reassess at Month 6
- [ ] Strategy-by-strategy migration plan (priority order):
  1. Rebalance (simplest, good baseline)
  2. SMA Crossover (timing strategy validation)
  3. DualMomentum (complex logic validation)
  4. RiskParity (portfolio construction validation)
  5. Remaining 8 strategies as needed
- [ ] Gradual transition over 3-6 months (migrate on-demand based on live trading priority)

### Phase 4: Long-term Decision Gate (Month 6)
- [ ] **If >80% of strategies on Nautilus and live trading active/imminent:** Deprecate Backtrader
- [ ] **If <50% of strategies migrated and live trading uncertain:** Keep hybrid indefinitely
- [ ] **Otherwise:** Continue gradual migration, reassess at Month 12

**If Defer (Not Chosen):**

This option was considered but not selected. If live trading timeline remains unclear after Month 3 decision gate, could reconsider deferral, but current plan is to proceed with hybrid approach and reassess at regular intervals.

## Consequences

### Positive Consequences

**Hybrid (Chosen):**
- **Flexibility and optionality**: Use best tool for each job (Backtrader for quick research, Nautilus for live trading)
- **Risk mitigation**: Keep working Backtrader while building Nautilus expertise, no "big bang" risk
- **Gradual migration**: Migrate strategies one-by-one based on live trading priority, 0 upfront cost
- **Live trading path clear**: Can start Nautilus development for new strategies immediately
- **Adapter pattern validated**: ADR-005 architecture proven to work exactly as intended
- **Reversible decision**: Can pivot to full Nautilus or full Backtrader at any 6-month gate based on data
- **Strategy parity testing**: CI-enforced parity for strategies supporting both engines ensures correctness

**If Had Chosen Full Go:**
- Single engine simplicity (no "which engine?" confusion)
- Full team expertise on Nautilus (no split knowledge)
- Cleaner long-term architecture (no dual maintenance)

**If Had Chosen No-Go:**
- Zero migration effort (keep existing workflows)
- Maintain team expertise on familiar Backtrader
- Focus development effort elsewhere (avoid Nautilus learning curve)

### Negative Consequences

**Hybrid (Chosen):**
- **Doubled maintenance burden**: Must maintain both Backtrader and Nautilus adapters
- **Parity testing overhead**: Need CI to validate strategies supporting both engines, adds test complexity
- **Potentially confusing for new developers**: "Which engine should I use?" decision burden
- **Neither engine gets full optimization**: Split focus may mean neither engine is fully leveraged
- **Incremental migration cost**: May exceed "big bang" migration in total hours if done inefficiently
- **Decision fatigue**: Repeated 6-month decision gates require ongoing assessment effort

**If Had Chosen Full Go:**
- 20-40 hour upfront migration cost for 12 strategies
- Steeper learning curve for entire team (not gradual)
- Python 3.11 support dropped (affects deployment environments)
- Higher risk if Nautilus ecosystem changes significantly

**If Had Chosen No-Go:**
- No built-in live trading path (need separate live trading system)
- Less realistic backtesting fidelity (miss out on order queues, realistic fills)
- Potential regret if Nautilus ecosystem thrives and becomes industry standard
- Performance lower than possible (pure Python vs Rust core)

### Risks and Mitigations

**Risk 1:** Nautilus development slows down or breaking changes introduced
- **Probability:** Low (active development, v1.222.0 is mature)
- **Impact:** Medium (would need to fork or migrate back to Backtrader)
- **Mitigation:**
  - Hybrid approach keeps Backtrader operational as fallback
  - Pin Nautilus version in pyproject.toml
  - Monitor release notes and community activity
  - Can pivot to Backtrader-only at any 6-month gate if Nautilus stalls

**Risk 2:** Strategy migration takes longer than 20-40 hours estimated
- **Probability:** Medium (only tested minimal strategy, real strategies more complex)
- **Impact:** Medium (delays live trading timeline)
- **Mitigation:**
  - Gradual migration limits blast radius (migrate 1-2 strategies first, learn patterns)
  - Parity harness catches issues early (CI validation)
  - Create migration playbook after first 2 strategies to standardize process
  - Decision gate at Month 3 allows reassessment if effort exceeds estimate

**Risk 3:** Parity issues discovered post-migration (strategies behave differently)
- **Probability:** Medium (order execution model differs, fills may not match exactly)
- **Impact:** High (incorrect backtest results, loss of confidence in strategies)
- **Mitigation:**
  - E2-T2 A/B parity harness with tight tolerances (±0.1% return, exact trade count)
  - CI parity gate blocks merges if divergence detected
  - Run parallel backtests (both engines) for migrated strategies for 3-6 months
  - Golden dataset baseline with reproducible results (already exists from Priority 6)
  - Start with simple strategies (Rebalance, SMA Crossover) to validate parity before complex ones

**Risk 4:** Maintenance burden of two engines becomes unsustainable
- **Probability:** Low (adapter pattern isolates engine-specific code)
- **Impact:** Medium (slows development velocity)
- **Mitigation:**
  - Adapter pattern minimizes shared code changes (only BacktestEngine interface)
  - Decision gates at 6-month intervals to assess if hybrid is sustainable
  - Can pivot to single-engine (either direction) if burden too high
  - Track maintenance hours to quantify burden and inform decision gates

**Risk 5:** Team splits expertise across two engines, mastery in neither
- **Probability:** Medium (learning curve for Nautilus is steep)
- **Impact:** Low (both engines well-documented, community support available)
- **Mitigation:**
  - Create internal "when to use which engine" guide (Phase 1)
  - Designate Nautilus expert(s) who lead migration efforts
  - Document learnings from first 2 strategy migrations
  - Consider full migration to Nautilus if >80% of strategies migrated (simplify to single engine)

## Validation and Review

**Validation Criteria:**

Hybrid (Chosen):
- [ ] Use case boundaries clearly defined (Backtrader for research, Nautilus for live trading)
- [ ] "When to use which engine" guide documented
- [ ] 1-2 simple strategies migrated successfully (Rebalance, SMA Crossover)
- [ ] Parity testing automated via E2-T2 A/B harness
- [ ] CI parity gate enforces tolerance (±0.1% return, exact trade count)
- [ ] Parallel backtests run for 3-6 months on migrated strategies
- [ ] Maintenance plan sustainable (track hours, assess at 6-month gates)
- [ ] Decision gates at Month 3, 6, 12 to reassess hybrid vs single-engine

**Review Schedule:**

- **Month 1 (March 2026):** Phase 1 complete (documentation, use case guide)
- **Month 2 (April 2026):** Phase 2 in progress (1-2 strategies migrated, parity harness created)
- **Month 3 (May 2026):** Decision Gate 1 - Assess live trading timeline clarity
  - If live trading within 6 months: accelerate migration
  - If uncertain: maintain hybrid, reassess at Month 6
- **Month 6 (August 2026):** Decision Gate 2 - Evaluate hybrid sustainability
  - If >80% strategies on Nautilus + live trading active: deprecate Backtrader
  - If <50% strategies migrated + live trading uncertain: keep hybrid indefinitely
  - Otherwise: continue gradual migration, reassess at Month 12
- **Month 12 (February 2027):** Full retrospective and final decision (single-engine vs hybrid long-term)

**Success Metrics:**

- **Live trading readiness:** Nautilus path validated, can launch live trading within 1 month of decision
- **Backtest fidelity:** Parity within tolerance (±0.1% return, ±0.05% CAGR, exact trade count) for migrated strategies
- **Development velocity:** Maintained or improved (hybrid approach should not slow overall progress)
- **Migration quality:** Zero critical bugs from migration, all parity tests passing in CI
- **Maintenance hours:** <5 hours/month dual-engine overhead (tracked and reported at decision gates)
- **Strategy coverage:** At least 2 strategies successfully migrated by Month 2, 50%+ by Month 6 if live trading confirmed

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

**Decision Date:** 2026-02-17
**Decision Maker:** Technical Team (based on comprehensive E6-T2 evaluation)
**Approvers:** Project Lead
**Reviewers:** Development Team

**Status:** DECIDED - Hybrid approach adopted, Phase 1 begins immediately
**Next Review:** Month 1 (March 2026) - Phase 1 completion check
