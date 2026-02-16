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
**Status:** In progress (Step 1 complete - adjusted prices)
**Dependencies:** E3-T1 (cost models should be stable first) ✅

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

### Current State Analysis

**YFinance Data Structure:**
- Data includes: Open, High, Low, Close, Adj Close, Volume, Dividends, Stock Splits
- "Adj Close" accounts for splits and dividends (backward-adjusted)
- "Close" is unadjusted raw price
- Current backtest code uses "Close" (unadjusted) → **Issue to fix**

**Current Warning:**
```python
if any("adj" in c.lower() and "close" in c.lower() for c in v.columns):
    warnings.warn(f"price_histories entry {data_name} is not using adjusted returns.")
```
This correctly warns when Adj Close is available but not being used.

**Trading Calendar:**
- YFinance only returns trading days (implicit calendar handling)
- No explicit validation that dates are valid trading days
- No holiday/early-close awareness

**Missing Data:**
- No explicit policy for handling gaps
- Pandas default behavior (NaN propagation)
- No user configuration

### Implementation Steps

#### Step 1: Use Adjusted Prices (Day 1)

**Problem:** Current code uses raw "Close" prices, not "Adj Close". This means splits and dividends are NOT properly accounted for, leading to incorrect returns and performance metrics.

**Solution:**
1. Modify data preparation to rename "Adj Close" → "Close" before feeding to Backtrader
2. Keep original Close as "Close_Unadjusted" for reference
3. Update warning logic to confirm adjusted prices are being used
4. Document the adjustment in assumptions

**Files to modify:**
- `finbot/services/backtesting/backtest_runner.py` - Adjust price column mapping
- `finbot/core/contracts/schemas.py` - Update bar validation to accept adj_close

**Acceptance:**
- Backtrader uses adjusted prices by default
- Warning removed or changed to confirm adjustment
- Parity tests still pass (may need tolerance adjustment if this changes results)

#### Step 2: Add Corporate Action Tests (Day 2)

**Create synthetic data with known splits/dividends:**
1. Generate price series with split event
2. Generate price series with dividend event
3. Verify backtest correctly handles both

**Files to create:**
- `tests/unit/test_corporate_actions.py` - Unit tests for split/dividend handling
- `tests/integration/test_adjusted_prices.py` - Integration test verifying adj prices used

**Test cases:**
- 2:1 stock split (price halves, shares double)
- Dividend payment (price drops by dividend amount on ex-date)
- Combined split + dividend scenario

**Acceptance:**
- Tests verify correct handling of splits and dividends
- Portfolio value remains consistent through corporate actions

#### Step 3: Add Trading Calendar Validation (Day 2-3)

**Add explicit trading calendar support:**
1. Create `TradingCalendar` abstraction
2. Implement US stock market calendar (NYSE/NASDAQ)
3. Add validation that backtest dates are trading days
4. Add holiday calendar data

**Files to create:**
- `finbot/core/contracts/calendar.py` - Trading calendar interface
- `finbot/services/backtesting/calendars/us_stock.py` - US market calendar
- `tests/unit/test_trading_calendar.py` - Calendar tests

**Features:**
- Validate start/end dates are trading days
- Skip non-trading days in date ranges
- Handle early closes (half days)
- Configurable calendar per market

**Acceptance:**
- Backtest rejects invalid (non-trading) start/end dates
- Calendar-aware date filtering available
- Tests verify common holidays excluded

#### Step 4: Missing Data Policies (Day 3-4)

**Add configurable missing data handling:**
1. Define `MissingDataPolicy` enum (FORWARD_FILL, DROP, ERROR)
2. Implement policy handlers
3. Add policy parameter to BacktraderAdapter
4. Test each policy behavior

**Files to modify/create:**
- `finbot/core/contracts/models.py` - Add MissingDataPolicy enum
- `finbot/services/backtesting/adapters/backtrader_adapter.py` - Add policy parameter
- `tests/unit/test_missing_data_policies.py` - Policy tests

**Policies:**
- `FORWARD_FILL`: Use last known price (current default)
- `DROP`: Remove symbols with missing data
- `ERROR`: Raise exception on missing data
- `INTERPOLATE`: Linear interpolation (advanced)

**Acceptance:**
- All policies implemented and tested
- User can configure policy per backtest
- Policy choice recorded in assumptions

#### Step 5: Documentation and Validation (Day 4-5)

**Create comprehensive documentation:**
1. Document adjusted price handling in ADR or guide
2. Add corporate action handling guide
3. Update API docs for calendar and missing data features
4. Add examples to notebooks

**Files to create/modify:**
- `docs/guides/corporate-actions-and-calendars.md` - User guide
- `notebooks/corporate_action_examples.ipynb` - Examples notebook
- Update roadmap and backlog

**Acceptance:**
- All features documented with examples
- User guide explains why adjusted prices matter
- Notebooks demonstrate calendar and policy usage

### Testing Strategy

**Unit Tests:**
- Adjusted price column mapping
- Trading calendar date validation
- Missing data policy handlers
- Corporate action event detection

**Integration Tests:**
- Full backtest with split event
- Full backtest with dividend event
- Calendar validation in adapter
- Missing data policy in real backtest

**Parity Tests:**
- Re-run all 3 golden strategies
- Adjust tolerances if needed (adjusted prices may change results slightly)
- Document any parity changes

### Risk Mitigation

**Risk: Adjusted prices break parity**
- Mitigation: Test with golden strategies, adjust tolerances if needed
- Rationale: Adjusted prices are MORE correct, so parity may shift

**Risk: Calendar validation too strict**
- Mitigation: Make calendar validation optional/configurable
- Allow bypass for non-standard data sources

**Risk: Missing data policies change results**
- Mitigation: Default to FORWARD_FILL (current behavior)
- Make policy explicit in assumptions

### Progress Tracking

**Step 1: Use Adjusted Prices** ✅ Complete (2026-02-16)
- ✅ Backtrader uses Adj Close when available
- ✅ OHLC adjusted proportionally to maintain relationships
- ✅ Original prices preserved as Close_Unadjusted
- ✅ 3 unit tests added and passing
- ✅ All 3 golden strategy parity tests pass (100% parity maintained)
- ✅ 458 tests passing total

**Step 2: Corporate Action Tests** ✅ Complete (2026-02-16)
- ✅ Synthetic data generators for splits and dividends
- ✅ Test 2:1 stock split handling
- ✅ Test 3:1 stock split handling
- ✅ Test dividend payment handling
- ✅ Test multiple dividends
- ✅ Test combined split + dividend scenarios
- ✅ Test reverse split (1:5)
- ✅ 6 comprehensive tests added and passing
- ✅ 464 tests passing total
**Step 3: Trading Calendar Validation** - Not started
**Step 4: Missing Data Policies** - Not started
**Step 5: Documentation** - Not started

### Acceptance Criteria

- [x] Backtrader uses adjusted prices (Adj Close) by default
- [x] Corporate action tests pass (splits, dividends)
- [ ] Trading calendar validation implemented
- [ ] Missing data policies configurable
- [x] All unit tests pass
- [x] Golden strategy parity maintained (with adjusted tolerances if needed)
- [ ] Documentation complete

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
