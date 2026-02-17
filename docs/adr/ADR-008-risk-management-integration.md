# ADR-008: Risk Management Integration

**Status:** Accepted
**Date:** 2026-02-16
**Deciders:** Development team
**Epic:** E5-T3 (Risk Controls Implementation)

## Context

The ExecutionSimulator needs comprehensive risk management to prevent excessive losses and enforce trading discipline. Without risk controls, paper trading and eventual live trading would expose portfolios to:

1. **Over-concentration:** Too many shares/value in a single symbol
2. **Excessive leverage:** Total exposure exceeding capital
3. **Runaway losses:** Large drawdowns without automatic halt
4. **Emergency situations:** No kill-switch for immediate trading halt
5. **Silent failures:** Orders accepted that violate risk rules

Real trading systems require pre-trade risk checks to reject orders before execution. The system must be:
- **Proactive:** Check before order acceptance, not after fills
- **Configurable:** Different strategies need different risk profiles
- **Composable:** Multiple risk rules work together
- **Transparent:** Clear rejection reasons when orders fail risk checks
- **Stateful:** Track peak values and daily performance for drawdown limits

## Decision

We will implement a **pluggable risk control system** with:

1. **RiskConfig dataclass** containing composable risk rules
2. **RiskChecker class** that validates orders against all enabled rules
3. **Pre-execution risk checks** integrated into ExecutionSimulator
4. **Risk state tracking** for peak value and daily performance
5. **Typed violation messages** for clear rejection feedback

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Order Submission                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    RiskChecker                               │
│                                                              │
│  1. Kill-Switch Check                                       │
│     ↓ (enabled)                                             │
│  2. Position Limit Check (per symbol)                       │
│     ↓ (pass)                                                │
│  3. Exposure Limit Check (portfolio)                        │
│     ↓ (pass)                                                │
│  4. Drawdown Limit Check (daily/total)                      │
│     ↓ (pass)                                                │
│  Return: None (approved) or (RejectionReason, message)      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              Order Validation                                │
│              (quantity, buying power)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              Order Execution                                 │
│              (with latency simulation)                       │
└─────────────────────────────────────────────────────────────┘
```

### Risk Rule Types

#### 1. Position Limit Rule

**Purpose:** Prevent over-concentration in single symbols

**Configuration:**
```python
@dataclass(frozen=True, slots=True)
class PositionLimitRule:
    max_shares: Decimal | None = None      # Max shares per symbol
    max_value: Decimal | None = None        # Max dollar value per symbol
```

**Behavior:**
- Checks only apply to BUY orders (sells always allowed to reduce position)
- Calculates new position after order fill
- Rejects if new position would exceed either limit
- Uses current market price for value check

**Example:**
```python
position_limit = PositionLimitRule(
    max_shares=Decimal("1000"),     # Max 1000 shares per symbol
    max_value=Decimal("50000"),     # Max $50K per symbol
)
```

#### 2. Exposure Limit Rule

**Purpose:** Control total portfolio leverage and risk

**Configuration:**
```python
@dataclass(frozen=True, slots=True)
class ExposureLimitRule:
    max_gross_exposure_pct: Decimal = Decimal("100")  # Sum of abs(positions)
    max_net_exposure_pct: Decimal = Decimal("100")    # Net long/short
```

**Behavior:**
- Gross exposure = sum of absolute position values
- Net exposure = algebraic sum of position values
- Calculated as percentage of total portfolio value
- Allows leveraged strategies (e.g., 150% gross for 1.5x leverage)

**Example:**
```python
exposure_limit = ExposureLimitRule(
    max_gross_exposure_pct=Decimal("150"),  # 150% = 1.5x leverage allowed
    max_net_exposure_pct=Decimal("100"),    # Net long must be <= 100%
)
```

#### 3. Drawdown Limit Rule

**Purpose:** Halt trading on excessive losses

**Configuration:**
```python
@dataclass(frozen=True, slots=True)
class DrawdownLimitRule:
    max_daily_drawdown_pct: Decimal | None = None    # Daily loss limit
    max_total_drawdown_pct: Decimal | None = None    # Loss from peak
```

**Behavior:**
- Daily drawdown: (current_value - daily_start_value) / daily_start_value
- Total drawdown: (peak_value - current_value) / peak_value
- Rejects ALL orders (buy/sell) when limit exceeded
- Requires manual intervention to resume trading

**Example:**
```python
drawdown_limit = DrawdownLimitRule(
    max_daily_drawdown_pct=Decimal("5"),   # Stop if down 5% today
    max_total_drawdown_pct=Decimal("20"),  # Stop if down 20% from peak
)
```

#### 4. Kill-Switch (Trading Enabled Flag)

**Purpose:** Emergency trading halt

**Configuration:**
```python
@dataclass
class RiskConfig:
    trading_enabled: bool = True  # False = all trading disabled
```

**Behavior:**
- When `trading_enabled=False`, ALL orders rejected immediately
- Checked first before any other risk rules
- Can be toggled programmatically or manually
- Useful for:
  - Emergency halt during market events
  - End-of-day cutoff
  - Manual risk override

**Example:**
```python
# Activate kill-switch
simulator.disable_trading()

# Clear kill-switch
simulator.enable_trading()
```

### RiskConfig: Composable Configuration

**Design:**
```python
@dataclass
class RiskConfig:
    """Risk control configuration.

    All rules are optional - only enabled rules are checked.
    """
    position_limit: PositionLimitRule | None = None
    exposure_limit: ExposureLimitRule | None = None
    drawdown_limit: DrawdownLimitRule | None = None
    trading_enabled: bool = True
```

**Usage:**
```python
# Conservative risk profile
conservative_risk = RiskConfig(
    position_limit=PositionLimitRule(
        max_shares=Decimal("500"),
        max_value=Decimal("25000"),
    ),
    exposure_limit=ExposureLimitRule(
        max_gross_exposure_pct=Decimal("100"),  # No leverage
        max_net_exposure_pct=Decimal("100"),
    ),
    drawdown_limit=DrawdownLimitRule(
        max_daily_drawdown_pct=Decimal("2"),    # Tight daily limit
        max_total_drawdown_pct=Decimal("10"),   # Tight total limit
    ),
    trading_enabled=True,
)

# Aggressive risk profile
aggressive_risk = RiskConfig(
    position_limit=PositionLimitRule(
        max_shares=Decimal("2000"),
        max_value=Decimal("100000"),
    ),
    exposure_limit=ExposureLimitRule(
        max_gross_exposure_pct=Decimal("200"),  # 2x leverage
        max_net_exposure_pct=Decimal("150"),
    ),
    drawdown_limit=DrawdownLimitRule(
        max_daily_drawdown_pct=Decimal("10"),
        max_total_drawdown_pct=Decimal("30"),
    ),
    trading_enabled=True,
)

# Position limits only
position_only_risk = RiskConfig(
    position_limit=PositionLimitRule(max_shares=Decimal("1000")),
    # exposure_limit and drawdown_limit are None (disabled)
)

# No risk controls (testing only)
no_risk = None  # Pass None to ExecutionSimulator
```

### RiskChecker: Validation Engine

**Responsibilities:**
- Check orders against all enabled risk rules
- Track risk state (peak value, daily start value)
- Return typed violations on failure
- Update state after successful fills

**API:**
```python
class RiskChecker:
    def check_order(
        self,
        order: Order,
        current_positions: dict[str, Decimal],
        current_prices: dict[str, Decimal],
        cash: Decimal,
    ) -> tuple[RejectionReason, str] | None:
        """Check order against all risk rules.

        Returns:
            (rejection_reason, message) if violated, None if passed
        """

    def update_state(
        self,
        portfolio_value: Decimal,
        is_new_day: bool = False,
    ) -> None:
        """Update risk state after trades."""

    def enable_trading(self) -> None:
        """Enable trading (clear kill-switch)."""

    def disable_trading(self) -> None:
        """Disable trading (activate kill-switch)."""

    def reset_daily_tracking(self, current_value: Decimal) -> None:
        """Reset daily drawdown tracking."""
```

### Integration with ExecutionSimulator

**Initialization:**
```python
from finbot.services.execution import ExecutionSimulator
from finbot.core.contracts import RiskConfig, PositionLimitRule

risk_config = RiskConfig(
    position_limit=PositionLimitRule(max_shares=Decimal("1000")),
)

simulator = ExecutionSimulator(
    initial_cash=Decimal("100000"),
    risk_config=risk_config,  # Optional - pass None for no risk controls
)
```

**Order Submission Flow:**
```python
def submit_order(self, order: Order, timestamp: datetime | None = None) -> Order:
    """Submit order with risk checks."""

    # 1. Risk checks (if enabled)
    if self.risk_checker:
        violation = self.risk_checker.check_order(
            order=order,
            current_positions=self.positions,
            current_prices=self.latest_prices,
            cash=self.cash,
        )
        if violation:
            rejection_reason, message = violation
            return order.reject(rejection_reason, message)

    # 2. Validation (quantity, buying power)
    # 3. Queue for submission with latency
    # ...
```

**Post-Fill Risk State Update:**
```python
def _execute_order(self, order: Order, timestamp: datetime) -> Order:
    """Execute fill and update risk state."""

    # ... execute fill ...

    # Update risk state after fill
    if self.risk_checker:
        portfolio_value = self._calculate_portfolio_value()
        self.risk_checker.update_state(portfolio_value)

    return filled_order
```

### Rejection Reasons

**New Rejection Reasons:**
```python
class RejectionReason(StrEnum):
    # ... existing reasons ...
    RISK_POSITION_LIMIT = "risk_position_limit"
    RISK_EXPOSURE_LIMIT = "risk_exposure_limit"
    RISK_DRAWDOWN_LIMIT = "risk_drawdown_limit"
    RISK_TRADING_DISABLED = "risk_trading_disabled"
```

**Usage:**
```python
rejected_order = simulator.submit_order(order)

if rejected_order.status == OrderStatus.REJECTED:
    print(f"Rejection: {rejected_order.rejection_reason}")
    print(f"Message: {rejected_order.rejection_message}")

    # Example output:
    # Rejection: risk_position_limit
    # Message: Position would exceed max shares: 1500 > 1000
```

## Consequences

### Positive

✅ **Safety:** Prevents catastrophic losses from over-concentration, excessive leverage, runaway drawdowns
✅ **Discipline:** Enforces trading rules automatically, removes emotional override
✅ **Flexibility:** Composable rules allow tailored risk profiles per strategy
✅ **Transparency:** Clear rejection reasons explain why orders fail
✅ **Testability:** Each rule type tested independently and in combination
✅ **Extensibility:** New rule types can be added without changing core architecture
✅ **Optional:** Risk controls are opt-in, backward compatible with existing code
✅ **Stateful:** Tracks peak/daily values for accurate drawdown calculations
✅ **Pre-emptive:** Checks before order acceptance, not after fills

### Negative

❌ **Overhead:** Risk checks add ~5-10% latency to order submission
❌ **Complexity:** More configuration surface area, more to understand
❌ **State management:** Requires careful tracking of peak/daily values
❌ **False rejections:** Conservative limits may reject valid trades
❌ **Testing burden:** Many edge cases (rule interactions, state transitions)

### Neutral

⚖️ **Optional:** Risk controls can be disabled for testing (pass `risk_config=None`)
⚖️ **Performance:** Risk checks are fast (simple math, early exit on first violation)
⚖️ **No automatic recovery:** Drawdown/kill-switch requires manual intervention

## Implementation Details

### Risk Check Flow

**1. Kill-Switch Check:**
```python
if not self.trading_enabled:
    return (
        RejectionReason.RISK_TRADING_DISABLED,
        "Trading is disabled (kill-switch active)",
    )
```

**2. Position Limit Check:**
```python
# Calculate new position after order
current_pos = current_positions.get(order.symbol, Decimal("0"))
new_pos = current_pos + order.quantity  # (buy orders only)

# Check shares limit
if rule.max_shares is not None and new_pos > rule.max_shares:
    return RiskViolation(...)

# Check value limit
if rule.max_value is not None:
    price = current_prices.get(order.symbol)
    new_value = new_pos * price
    if new_value > rule.max_value:
        return RiskViolation(...)
```

**3. Exposure Limit Check:**
```python
# Simulate new positions after order
new_positions = current_positions.copy()
if order.side == OrderSide.BUY:
    new_positions[symbol] += quantity
else:
    new_positions[symbol] -= quantity

# Calculate gross and net exposure
gross_exposure = sum(abs(qty) * price for symbol, qty in new_positions.items())
net_exposure = sum(qty * price for symbol, qty in new_positions.items())

# Convert to percentages
gross_pct = (gross_exposure / portfolio_value) * 100
net_pct = (abs(net_exposure) / portfolio_value) * 100

# Check limits
if gross_pct > rule.max_gross_exposure_pct:
    return RiskViolation(...)
if net_pct > rule.max_net_exposure_pct:
    return RiskViolation(...)
```

**4. Drawdown Limit Check:**
```python
# Daily drawdown
if rule.max_daily_drawdown_pct is not None:
    daily_return_pct = ((portfolio_value - daily_start_value) / daily_start_value) * 100
    if daily_return_pct < -rule.max_daily_drawdown_pct:
        return RiskViolation(...)

# Total drawdown from peak
if rule.max_total_drawdown_pct is not None:
    drawdown_pct = ((peak_value - portfolio_value) / peak_value) * 100
    if drawdown_pct > rule.max_total_drawdown_pct:
        return RiskViolation(...)
```

### State Tracking

**Peak Value:**
```python
def update_state(self, portfolio_value: Decimal, is_new_day: bool = False) -> None:
    # Update peak value (monotonically increasing)
    if portfolio_value > self.peak_value:
        self.peak_value = portfolio_value

    # Reset daily tracking if new day
    if is_new_day:
        self.reset_daily_tracking(portfolio_value)
```

**Daily Tracking:**
```python
def reset_daily_tracking(self, current_value: Decimal) -> None:
    """Called at start of each trading day."""
    self.daily_start_value = current_value
```

**Integration:**
```python
# At start of each trading day (in backtesting loop or live trading)
simulator.reset_daily_risk_tracking(current_portfolio_value)

# After each fill
if simulator.risk_checker:
    portfolio_value = simulator.get_total_value()
    simulator.risk_checker.update_state(portfolio_value)
```

### Example: Complete Risk Setup

```python
from decimal import Decimal
from finbot.services.execution import ExecutionSimulator
from finbot.core.contracts import (
    RiskConfig,
    PositionLimitRule,
    ExposureLimitRule,
    DrawdownLimitRule,
    Order,
    OrderSide,
    OrderType,
)

# Define risk profile
risk_config = RiskConfig(
    position_limit=PositionLimitRule(
        max_shares=Decimal("1000"),
        max_value=Decimal("50000"),
    ),
    exposure_limit=ExposureLimitRule(
        max_gross_exposure_pct=Decimal("150"),  # 1.5x leverage allowed
        max_net_exposure_pct=Decimal("100"),
    ),
    drawdown_limit=DrawdownLimitRule(
        max_daily_drawdown_pct=Decimal("5"),
        max_total_drawdown_pct=Decimal("20"),
    ),
    trading_enabled=True,
)

# Create simulator with risk controls
simulator = ExecutionSimulator(
    initial_cash=Decimal("100000"),
    risk_config=risk_config,
)

# Initialize risk state
simulator.risk_checker.peak_value = Decimal("100000")
simulator.risk_checker.daily_start_value = Decimal("100000")

# Submit order (will be checked against all risk rules)
order = Order.create_market_order(
    symbol="AAPL",
    side=OrderSide.BUY,
    quantity=Decimal("1500"),  # Exceeds max_shares=1000
)

result = simulator.submit_order(order)

# Check result
if result.status == OrderStatus.REJECTED:
    print(f"Rejected: {result.rejection_reason}")
    print(f"Message: {result.rejection_message}")
    # Output: Rejected: risk_position_limit
    #         Message: Position would exceed max shares: 1500 > 1000
```

## Alternatives Considered

### Alternative 1: Hard-Coded Risk Limits

Embed risk limits as constructor parameters on ExecutionSimulator.

**Example:**
```python
simulator = ExecutionSimulator(
    initial_cash=100000,
    max_shares_per_position=1000,
    max_value_per_position=50000,
    max_daily_drawdown_pct=5,
)
```

**Rejected because:**
- Not extensible (hard to add new rule types)
- Not composable (can't disable individual rules)
- Clutters ExecutionSimulator API
- Harder to serialize/deserialize configurations

### Alternative 2: External Risk Service

Create separate RiskService that ExecutionSimulator calls via API/IPC.

**Rejected because:**
- Adds deployment complexity (another process)
- Adds latency (network/IPC overhead)
- Overkill for current scale
- Harder to test (requires mocking service)

### Alternative 3: Post-Fill Risk Checks

Check risk limits after fills, reject future orders if violated.

**Rejected because:**
- Reactive, not proactive (damage already done)
- Order already filled, can't undo
- Less safe for live trading
- Industry standard is pre-trade risk checks

### Alternative 4: Rule Engine Pattern

Use generic rule engine (e.g., durable-rules, business-rules).

**Rejected because:**
- Adds dependency
- Overkill for simple checks
- Harder to type-check
- Custom implementation is clearer and simpler

### Alternative 5: Separate RiskRule Classes

Create abstract `RiskRule` base class with subclasses for each rule type.

**Rejected because:**
- More boilerplate (multiple classes)
- Harder to serialize (class hierarchy)
- Dataclasses are simpler and sufficient
- Current design is extensible enough

## Related

- **ADR-006:** Execution system architecture (ExecutionSimulator design)
- **E5-T3:** Risk controls implementation plan (detailed task breakdown)
- **ADR-005:** Engine-agnostic contracts (typed order lifecycle)

## References

- Implementation plan: `docs/planning/e5-t3-risk-controls-implementation-plan.md`
- Risk contracts: `finbot/core/contracts/risk.py`
- Risk checker: `finbot/services/execution/risk_checker.py`
- Execution simulator: `finbot/services/execution/execution_simulator.py`
- Tests: `tests/unit/test_risk_controls.py`

---

**Last updated:** 2026-02-16
