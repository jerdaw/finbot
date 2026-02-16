# E5-T3: Risk Controls Interface Implementation Plan

**Created:** 2026-02-16
**Epic:** E5 - Live Execution Interfaces
**Task:** E5-T3
**Estimated Effort:** M (3-5 days)

## Overview

Implement risk management controls to prevent excessive losses and enforce trading limits. This adds a critical safety layer to the execution system, essential for live trading preparation.

## Current State

**Already Implemented (E5-T1, E5-T2):**
- ✅ Order lifecycle and execution tracking
- ✅ ExecutionSimulator with position and cash tracking
- ✅ Order validation (quantity, buying power)
- ✅ Latency simulation

**What's Missing:**
- Position size limits (per symbol, total)
- Exposure limits (sector, market value)
- Drawdown limits (daily, total)
- Kill-switch (emergency trading halt)
- Risk rule framework
- Pre-trade risk checks

## Goals

1. **Position limits** - Prevent over-concentration in single symbols
2. **Exposure limits** - Control total portfolio risk
3. **Drawdown protection** - Stop trading on excessive losses
4. **Kill-switch** - Emergency halt capability
5. **Configurable rules** - Flexible risk rule system
6. **Testing** - Verify risk controls work correctly

## Design Decisions

**Risk Rule Types:**
```python
- PositionLimit: Max shares/value per symbol
- ExposureLimit: Max total portfolio exposure (% of capital)
- DrawdownLimit: Max loss from peak (daily, total)
- KillSwitch: Manual emergency halt
```

**Risk Check Flow:**
```
Order submission → Risk checks → Validation → Execution
                     ↓ (fail)
                  Rejection
```

**Risk State Tracking:**
```python
- Peak portfolio value (for drawdown calculation)
- Daily start value (for daily drawdown)
- Position sizes by symbol
- Trading enabled/disabled (kill-switch)
```

**Implementation Approach:**
- Abstract RiskRule interface for extensibility
- RiskChecker aggregates multiple rules
- Integrate with ExecutionSimulator
- Clear rejection reasons for failed risk checks

## Implementation

### Step 1: Risk Control Contracts (1-2 hours)

**File:** `finbot/core/contracts/risk.py`

```python
class RiskRuleType(StrEnum):
    """Type of risk rule."""
    POSITION_LIMIT = "position_limit"
    EXPOSURE_LIMIT = "exposure_limit"
    DRAWDOWN_LIMIT = "drawdown_limit"
    KILL_SWITCH = "kill_switch"


@dataclass(frozen=True, slots=True)
class RiskViolation:
    """Risk rule violation details."""
    rule_type: RiskRuleType
    message: str
    current_value: Decimal
    limit_value: Decimal


@dataclass(frozen=True, slots=True)
class PositionLimitRule:
    """Limit position size per symbol."""
    max_shares: Decimal | None = None
    max_value: Decimal | None = None


@dataclass(frozen=True, slots=True)
class ExposureLimitRule:
    """Limit total portfolio exposure."""
    max_gross_exposure_pct: Decimal = Decimal("100")  # 100% = fully invested
    max_net_exposure_pct: Decimal = Decimal("100")


@dataclass(frozen=True, slots=True)
class DrawdownLimitRule:
    """Limit portfolio drawdown."""
    max_daily_drawdown_pct: Decimal | None = None
    max_total_drawdown_pct: Decimal | None = None


@dataclass
class RiskConfig:
    """Risk control configuration."""
    position_limit: PositionLimitRule | None = None
    exposure_limit: ExposureLimitRule | None = None
    drawdown_limit: DrawdownLimitRule | None = None
    trading_enabled: bool = True  # Kill-switch
```

### Step 2: Risk Checker (2-3 hours)

**File:** `finbot/services/execution/risk_checker.py`

```python
class RiskChecker:
    """Checks orders against risk rules."""

    def __init__(self, risk_config: RiskConfig):
        self.risk_config = risk_config
        self.peak_value: Decimal = Decimal("0")
        self.daily_start_value: Decimal = Decimal("0")
        self.trading_enabled = risk_config.trading_enabled

    def check_order(
        self,
        order: Order,
        current_positions: dict[str, Decimal],
        current_prices: dict[str, Decimal],
        cash: Decimal,
    ) -> RiskViolation | None:
        """Check order against all risk rules."""
        # 1. Check kill-switch
        # 2. Check position limits
        # 3. Check exposure limits
        # 4. Check drawdown limits
        # Return first violation or None

    def update_state(
        self,
        portfolio_value: Decimal,
        is_new_day: bool = False,
    ) -> None:
        """Update risk state after trades."""
        # Update peak value
        # Reset daily tracking if new day

    def enable_trading(self) -> None:
        """Enable trading (clear kill-switch)."""

    def disable_trading(self) -> None:
        """Disable trading (activate kill-switch)."""

    def reset_daily_tracking(self, current_value: Decimal) -> None:
        """Reset daily drawdown tracking."""
```

### Step 3: Integrate Risk Checks into ExecutionSimulator (1-2 hours)

**File:** `finbot/services/execution/execution_simulator.py` (update)

```python
class ExecutionSimulator:
    def __init__(
        self,
        initial_cash: Decimal,
        slippage_bps: Decimal = Decimal("5"),
        commission_per_share: Decimal = Decimal("0"),
        latency_config: LatencyConfig = LATENCY_INSTANT,
        risk_config: RiskConfig | None = None,
    ):
        # ... existing fields ...
        self.risk_checker = RiskChecker(risk_config) if risk_config else None

    def submit_order(self, order: Order, timestamp: datetime | None = None) -> Order:
        """Submit order with risk checks."""
        # 1. Risk checks (if enabled)
        # 2. Validation
        # 3. Submit with latency
```

### Step 4: Update Order Rejection Reasons (30 min)

**File:** `finbot/core/contracts/orders.py` (update)

```python
class RejectionReason(StrEnum):
    # ... existing reasons ...
    RISK_POSITION_LIMIT = "risk_position_limit"
    RISK_EXPOSURE_LIMIT = "risk_exposure_limit"
    RISK_DRAWDOWN_LIMIT = "risk_drawdown_limit"
    RISK_TRADING_DISABLED = "risk_trading_disabled"
```

### Step 5: Tests (2-3 hours)

**File:** `tests/unit/test_risk_controls.py`

```python
class TestPositionLimits:
    """Test position size limits."""

    def test_position_limit_shares():
        """Order rejected when shares exceed limit."""

    def test_position_limit_value():
        """Order rejected when value exceeds limit."""

    def test_position_limit_allows_reduce():
        """Sell orders allowed even if over limit."""


class TestExposureLimits:
    """Test portfolio exposure limits."""

    def test_gross_exposure_limit():
        """Order rejected when gross exposure exceeds limit."""

    def test_net_exposure_limit():
        """Order rejected when net exposure exceeds limit."""


class TestDrawdownLimits:
    """Test drawdown protection."""

    def test_daily_drawdown_limit():
        """Trading halted when daily loss exceeds limit."""

    def test_total_drawdown_limit():
        """Trading halted when total loss exceeds limit."""

    def test_drawdown_reset_on_new_day():
        """Daily tracking resets on new day."""


class TestKillSwitch:
    """Test emergency trading halt."""

    def test_kill_switch_blocks_orders():
        """All orders rejected when kill-switch active."""

    def test_kill_switch_enable_disable():
        """Kill-switch can be toggled."""
```

### Step 6: Integration and Documentation (1 hour)

- Add RiskConfig, RiskViolation, risk rules to contracts exports
- Update ExecutionSimulator docstrings with risk examples
- Add example in implementation plan

## Acceptance Criteria

- [x] Risk control contracts (RiskConfig, rules, RiskViolation) ✅
- [x] Position limit enforcement (shares and value) ✅
- [x] Exposure limit enforcement (gross and net) ✅
- [x] Drawdown limit enforcement (daily and total) ✅
- [x] Kill-switch functionality ✅
- [x] Risk checker integration with ExecutionSimulator ✅
- [x] Updated rejection reasons for risk violations ✅
- [x] Tests for all risk controls ✅
- [x] Integration with existing execution system ✅
- [x] Documentation ✅

**All acceptance criteria met!** E5-T3 is complete.

## Out of Scope (Future Work)

- Sector/industry exposure limits
- VaR/CVaR limits
- Correlation-based limits
- Dynamic position sizing
- Risk analytics dashboard
- Risk limit breach notifications

## Risk Mitigation

**Complexity:** Risk rules can interact in complex ways
- Solution: Test each rule independently, then combinations

**State management:** Tracking peak/daily values across time
- Solution: Clear state update methods, explicit reset for new days

**Performance:** Risk checks on every order
- Solution: Simple checks, early exit on first violation

## Timeline

- Step 1: Risk control contracts (1-2 hours)
- Step 2: Risk checker (2-3 hours)
- Step 3: ExecutionSimulator integration (1-2 hours)
- Step 4: Update rejection reasons (30 min)
- Step 5: Tests (2-3 hours)
- Step 6: Integration (1 hour)
- Total: 7.5-11.5 hours (~1-2 days)

## Implementation Status

### Completed (2026-02-16)

- [x] Step 1: Risk control contracts ✅
  - Created `finbot/core/contracts/risk.py`
  - Contracts: `RiskRuleType` enum, `RiskViolation` dataclass
  - Risk rules: `PositionLimitRule`, `ExposureLimitRule`, `DrawdownLimitRule`
  - `RiskConfig` aggregates all risk rules + kill-switch

- [x] Step 2: Risk checker ✅
  - Created `finbot/services/execution/risk_checker.py`
  - `RiskChecker` class with comprehensive checking:
    - Kill-switch check (trading_enabled)
    - Position limits (max shares, max value per symbol)
    - Exposure limits (gross and net as % of capital)
    - Drawdown limits (daily and total from peak)
  - State tracking: `peak_value`, `daily_start_value`
  - Methods: `check_order()`, `update_state()`, `enable/disable_trading()`, `reset_daily_tracking()`

- [x] Step 3: ExecutionSimulator integration ✅
  - Updated `finbot/services/execution/execution_simulator.py`
  - Added `risk_config` parameter (optional, defaults to None)
  - Created `risk_checker` instance if risk_config provided
  - Risk checks performed before validation in `submit_order()`
  - Risk state updated after successful fills in `_execute_order()`
  - Convenience methods: `enable_trading()`, `disable_trading()`, `reset_daily_risk_tracking()`

- [x] Step 4: Update rejection reasons ✅
  - Updated `finbot/core/contracts/orders.py`
  - Added risk-specific rejection reasons:
    - `RISK_POSITION_LIMIT`
    - `RISK_EXPOSURE_LIMIT`
    - `RISK_DRAWDOWN_LIMIT`
    - `RISK_TRADING_DISABLED`

- [x] Step 5: Tests ✅
  - Created `tests/unit/test_risk_controls.py`
  - 14 comprehensive tests covering:
    - Position limits (4 tests - shares/value/within limit/sell allowed)
    - Exposure limits (2 tests - gross/net)
    - Drawdown limits (3 tests - daily/total/reset)
    - Kill-switch (3 tests - blocks orders/toggle/no controls)
    - Risk state tracking (2 tests - peak updates)
  - All tests passing
  - 629 tests total (627 passed, 2 skipped) - up from 615

- [x] Step 6: Integration ✅
  - Added to `finbot/core/contracts/__init__.py`:
    - `RiskConfig`, `RiskRuleType`, `RiskViolation`
    - `PositionLimitRule`, `ExposureLimitRule`, `DrawdownLimitRule`
  - Fully backward compatible (risk controls are optional)
  - No linting errors
