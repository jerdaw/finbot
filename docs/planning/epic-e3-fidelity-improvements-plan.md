# Epic E3: Backtesting Fidelity Improvements - Implementation Plan

**Created:** 2026-02-16
**Epic:** E3 (Weeks 17-26 from master plan)
**Status:** Active - Sprint 4 in progress
**Previous Epic:** E2 (Backtrader Adapter and Parity Harness) - Complete with 100% parity

---

## Epic Overview

**Objective:** Improve backtesting simulation realism without breaking parity on golden strategies.

**Key Principle:** Fidelity improvements are additive enhancements with default settings that maintain current behavior. All changes must pass parity tests with default parameters before adding cost models.

---

## E3-T1: Cost Model Expansion

**Effort:** M (3-5 days)
**Status:** In progress

### Objectives

1. Create parameterized cost model components (commission, spread, slippage, borrow)
2. Integrate cost models into backtesting contracts
3. Maintain 100% parity with default (zero-cost) settings
4. Add unit tests for each cost component
5. Document cost model usage and configuration

### Design Principles

**Backwards Compatibility:**
- Default cost models match current behavior (zero costs)
- Parity tests continue to pass with defaults
- Cost models are opt-in via configuration

**Extensibility:**
- Cost models are pluggable components
- Easy to add new cost types (market impact, exchange fees, etc.)
- Support both flat and percentage-based costs

**Transparency:**
- All costs tracked separately in results
- Cost breakdowns available for analysis
- Clear documentation of cost assumptions

### Architecture

**Cost Model Contract:**

```python
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

class CostType(StrEnum):
    """Types of trading costs."""
    COMMISSION = "commission"
    SPREAD = "spread"
    SLIPPAGE = "slippage"
    BORROW = "borrow"
    MARKET_IMPACT = "market_impact"

@dataclass(frozen=True)
class CostEvent:
    """Single cost event during backtesting."""
    timestamp: pd.Timestamp
    symbol: str
    cost_type: CostType
    amount: float  # Dollar amount
    basis: str  # Description of how cost was calculated

class CostModel(Protocol):
    """Interface for cost calculation models."""

    def calculate_cost(
        self,
        symbol: str,
        quantity: float,
        price: float,
        timestamp: pd.Timestamp,
        **kwargs
    ) -> float:
        """Calculate cost for a trade."""
        ...
```

**Cost Model Components:**

1. **CommissionModel** - Trading commissions
   - `FlatCommission(per_share: float)` - Current default
   - `PercentageCommission(rate: float, min_cost: float)`
   - `TieredCommission(tiers: list[tuple[float, float]])`

2. **SpreadModel** - Bid-ask spread costs
   - `ZeroSpread()` - Default (assumes mid-price execution)
   - `FixedSpread(bps: float)` - Fixed basis points
   - `ProportionalSpread(base_bps: float, volatility_multiplier: float)`

3. **SlippageModel** - Market impact and execution slippage
   - `ZeroSlippage()` - Default
   - `FixedSlippage(bps: float)`
   - `SqrtSlippage(coefficient: float)` - Square-root market impact

4. **BorrowCostModel** - Costs for leverage/margin
   - `ZeroBorrowCost()` - Default
   - `FixedBorrowRate(annual_rate: float)`
   - `TieredBorrowRate(tiers: dict[float, float])`

### Implementation Steps

#### Step 1: Create Cost Model Contracts (Day 1)

**Files to create:**
- `finbot/core/contracts/costs.py` - Cost model interfaces and base classes
- `finbot/services/backtesting/costs/` - Cost model implementations
  - `__init__.py`
  - `commission.py`
  - `spread.py`
  - `slippage.py`
  - `borrow.py`

**Tasks:**
- Define `CostModel` protocol
- Define `CostEvent` dataclass
- Define `CostType` enum
- Create base implementations for each cost type

#### Step 2: Add Default Cost Models (Day 1-2)

**Tasks:**
- Implement `FlatCommission` (matches current `FixedCommissionScheme`)
- Implement `ZeroSpread`, `ZeroSlippage`, `ZeroBorrowCost`
- Add unit tests for each model
- Verify calculations are deterministic

#### Step 3: Integrate Cost Tracking into Adapter (Day 2-3)

**Files to modify:**
- `finbot/core/contracts/models.py` - Add cost tracking to `BacktestRunResult`
- `finbot/services/backtesting/adapters/backtrader_adapter.py` - Track costs
- `finbot/services/backtesting/backtest_runner.py` - Pass cost models

**Tasks:**
- Add `costs: list[CostEvent]` to `BacktestRunResult`
- Add `total_commission`, `total_spread`, `total_slippage`, `total_borrow_cost` to metrics
- Implement cost event capture during backtest
- Update schema version (bump to v2)

#### Step 4: Verify Parity with Default Costs (Day 3)

**Tasks:**
- Run all 3 golden strategy parity tests with default cost models
- Ensure 100% parity maintained
- If parity breaks, debug and fix
- Update parity tolerance if needed (should not be necessary)

#### Step 5: Add Advanced Cost Models (Day 4)

**Tasks:**
- Implement `PercentageCommission`
- Implement `FixedSpread` and `ProportionalSpread`
- Implement `FixedSlippage` and `SqrtSlippage`
- Implement `FixedBorrowRate`
- Add comprehensive unit tests

#### Step 6: Add Cost Model Examples and Documentation (Day 5)

**Tasks:**
- Create example notebook: `notebooks/cost_model_examples.ipynb`
- Document cost model API in `docs_site/api/services/backtesting/costs.md`
- Add cost model configuration guide
- Update migration status report with cost model results

### Testing Strategy

**Unit Tests (`tests/unit/test_cost_models.py`):**
- Test each cost model with known inputs/outputs
- Verify edge cases (zero quantity, zero price, etc.)
- Test cost event creation and serialization

**Integration Tests:**
- Add cost-aware parity tests (optional, if time permits)
- Verify cost tracking in end-to-end backtest
- Test cost aggregation in results

**Parity Tests:**
- All existing parity tests must pass with default cost models
- No tolerance changes should be needed

### Acceptance Criteria

- [ ] All cost model components implemented and unit-tested
- [ ] Default cost models match current behavior (zero costs)
- [ ] All 3 golden strategy parity tests pass with defaults
- [ ] Cost events tracked in `BacktestRunResult`
- [ ] Cost metrics included in result summary
- [ ] Documentation complete (API docs + examples)
- [ ] No regressions in existing test suite

---

## E3-T2: Corporate Action + Calendar Correctness

**Effort:** M (3-5 days)
**Status:** Not started
**Dependencies:** E3-T1 (cost models should be stable first)

### Objectives

1. Validate split/dividend handling in price data
2. Add trading calendar/session control
3. Implement missing-data policies
4. Test event correctness with synthetic data

### Scope

**In Scope:**
- Validate that current data handling is correct for splits/dividends
- Add calendar-aware date filtering
- Add configurable missing-data policies (ffill, drop, error)

**Out of Scope (for now):**
- Live corporate action feeds
- Real-time event handling
- Complex derivative actions (spinoffs, etc.)

### Implementation Approach

(Detailed plan TBD - will create after E3-T1 complete)

---

## E3-T3: Walk-Forward + Regime Evaluation

**Effort:** M (3-5 days)
**Status:** Not started
**Dependencies:** E3-T1, E3-T2

### Objectives

1. Add walk-forward analysis helper functions
2. Implement regime-segmented performance metrics
3. Create unified stats path using shared metrics contract

### Scope

**In Scope:**
- Walk-forward parameter optimization framework
- Regime detection and segmentation utilities
- Cohort comparison tools

**Out of Scope:**
- Automated hyperparameter tuning
- Machine learning-based regime detection

### Implementation Approach

(Detailed plan TBD - will create after E3-T2 complete)

---

## Epic E3 Success Criteria

**Technical:**
- [ ] All fidelity improvements parameterized and test-covered
- [ ] 100% parity maintained on golden strategies with defaults
- [ ] No performance regressions (backtests run at same speed)
- [ ] Documentation complete for all new features

**Quality:**
- [ ] Unit test coverage >80% for new code
- [ ] Integration tests for key workflows
- [ ] Examples notebooks demonstrating usage

**Process:**
- [ ] All changes reviewed and documented
- [ ] Planning docs kept up-to-date
- [ ] Migration status report updated with findings

---

## Risk Mitigation

**Risk: Cost models break parity**
- Mitigation: Default models match current behavior, parity tests run continuously

**Risk: Performance degradation from cost tracking**
- Mitigation: Cost tracking is optional, benchmark before/after

**Risk: Scope creep into live trading**
- Mitigation: Strict adherence to Epic E3 scope, no live trading interfaces

**Risk: Breaking changes to contracts**
- Mitigation: Schema versioning, migration path for v1→v2

---

## Next Steps After Epic E3

**Epic E4: Research Reproducibility and Observability** (Weeks 27-36)
- Experiment registry
- Snapshot-based reproducibility
- Batch observability instrumentation

**Epic E5: Live-Readiness Interfaces** (Weeks 37-44)
- Broker-neutral execution interfaces
- Paper trading simulator
- Risk control interfaces
- State checkpoint/recovery

**Epic E6: NautilusTrader Pilot** (Weeks 45-52)
- Single-strategy pilot
- Comparative evaluation
- Go/no-go decision

---

## References

- Master plan: `docs/planning/backtesting-live-readiness-implementation-plan.md`
- Backlog: `docs/planning/backtesting-live-readiness-backlog.md`
- ADR-005: `docs/adr/ADR-005-adapter-first-backtesting-live-readiness.md`
- Parity spec: `docs/planning/parity-tolerance-spec.md`
