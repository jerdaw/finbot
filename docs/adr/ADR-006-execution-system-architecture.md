# ADR-006: Execution System Architecture

**Status:** Accepted
**Date:** 2026-02-16
**Deciders:** Development team
**Epic:** E5 (Live-Readiness Without Production Live)

## Context

We need a paper trading execution simulator that can:
1. Realistically simulate order submission, fills, and cancellations
2. Enforce risk controls (position limits, exposure limits, drawdown protection)
3. Support disaster recovery via state checkpoints
4. Work independently or integrate with backtesting engines
5. Eventually support live trading with minimal changes

The system must be **engine-agnostic** to work with both Backtrader (current) and potentially NautilusTrader (E6) or other backends.

## Decision

We will build a **standalone execution simulator** (`ExecutionSimulator`) with:

1. **Typed order contracts** for engine-agnostic order lifecycle
2. **Pluggable risk controls** via composable `RiskConfig`
3. **Latency simulation** with configurable delay profiles
4. **State persistence** via JSON checkpoints with versioning
5. **Clean separation** from backtesting engines

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Backtesting Engine                        │
│                  (Backtrader / Nautilus)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Uses contracts
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  finbot/core/contracts/                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   orders.py  │  │  latency.py  │  │   risk.py    │      │
│  │   (Order,    │  │ (LatencyConf)│  │ (RiskConfig) │      │
│  │  OrderStatus)│  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐                                           │
│  │checkpoint.py │  Typed, versioned, immutable              │
│  │(Execution    │  contracts for portability               │
│  │ Checkpoint)  │                                           │
│  └──────────────┘                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Implements
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              finbot/services/execution/                      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          ExecutionSimulator                           │  │
│  │                                                        │  │
│  │  • submit_order()                                     │  │
│  │  • process_market_data()                              │  │
│  │  • cancel_order()                                     │  │
│  │  • get_position()                                     │  │
│  │  • enable/disable_trading()                           │  │
│  └────────┬─────────────────────────┬───────────────────┘  │
│           │                         │                       │
│           ↓                         ↓                       │
│  ┌────────────────┐      ┌──────────────────┐             │
│  │  RiskChecker   │      │ PendingActionQue │             │
│  │                │      │                  │             │
│  │ • check_order()│      │ • add_action()   │             │
│  │ • update_state│      │ • process_until()│             │
│  └────────────────┘      └──────────────────┘             │
│                                                              │
│  ┌────────────────────────────────────────────────┐        │
│  │       CheckpointManager                         │        │
│  │                                                  │        │
│  │  • create_checkpoint()                          │        │
│  │  • save_checkpoint()                            │        │
│  │  • load_checkpoint()                            │        │
│  │  • restore_simulator()                          │        │
│  └────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. ExecutionSimulator

**Responsibilities:**
- Accept order submissions
- Validate orders before acceptance
- Check risk limits before acceptance
- Simulate latency delays (submission, fill, cancel)
- Execute fills based on market data
- Track positions and cash
- Maintain order history

**Not Responsible For:**
- Strategy logic (handled by backtesting engine)
- Market data generation (provided by engine)
- Performance metrics (handled by engine/analytics)

#### 2. Typed Contracts

**Order Lifecycle:**
```python
@dataclass(frozen=True, slots=True)
class Order:
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    status: OrderStatus
    limit_price: Decimal | None = None
    filled_quantity: Decimal = Decimal("0")
    avg_fill_price: Decimal = Decimal("0")
    executions: list[OrderExecution] = field(default_factory=list)
    # ... timestamps, rejection info, etc.
```

**Latency Configuration:**
```python
@dataclass(frozen=True, slots=True)
class LatencyConfig:
    submission_latency: timedelta
    fill_latency_min: timedelta
    fill_latency_max: timedelta
    cancel_latency: timedelta
```

**Risk Configuration:**
```python
@dataclass
class RiskConfig:
    position_limit: PositionLimitRule | None = None
    exposure_limit: ExposureLimitRule | None = None
    drawdown_limit: DrawdownLimitRule | None = None
    trading_enabled: bool = True
```

#### 3. Pending Action Queue

**Purpose:** Simulate realistic delays for order operations

**Design:**
- Binary search insertion for O(log n) performance
- Time-ordered queue of pending actions
- Process actions when `current_time >= scheduled_time`

**Action Types:**
- SUBMIT: Order submission (after submission_latency)
- FILL: Order execution (after fill_latency)
- CANCEL: Order cancellation (after cancel_latency)

#### 4. Risk Checker

**Purpose:** Enforce risk limits before order acceptance

**Rules:**
- Position limits: Max shares/value per position
- Exposure limits: Gross/net exposure as % of portfolio
- Drawdown limits: Daily/total drawdown from peak
- Kill-switch: Enable/disable trading

**Integration:**
- Runs before order validation
- Returns (rejection_reason, message) on violation
- Updates risk state after fills

#### 5. Checkpoint Manager

**Purpose:** State persistence for disaster recovery

**Checkpoint Contents:**
- Metadata: version, simulator_id, timestamp
- Account state: cash, positions
- Orders: pending, completed
- Risk state: peak_value, daily_start_value, trading_enabled
- Configuration: slippage, commission, latency, risk

**Storage:** JSON files at `checkpoints/{simulator_id}/{timestamp}.json`

**Versioning:** `CHECKPOINT_VERSION` with migration support

## Consequences

### Positive

✅ **Engine-agnostic:** Works with any backtesting engine (Backtrader, Nautilus, custom)
✅ **Testable:** Each component (validator, risk checker, latency queue) testable in isolation
✅ **Realistic:** Latency simulation and risk controls mirror real trading
✅ **Recoverable:** Checkpoints enable disaster recovery and state replay
✅ **Flexible:** Pluggable risk rules, configurable latency profiles
✅ **Type-safe:** Full mypy compliance, catch errors early
✅ **Portable:** JSON contracts work across systems/languages

### Negative

❌ **Complexity:** More moving parts than simple backtesting
❌ **Overhead:** Latency simulation adds computational cost
❌ **Storage:** Checkpoint files can grow large for long-running simulations
❌ **Testing burden:** More components = more tests needed

### Neutral

⚖️ **No live trading yet:** This is paper trading only, live execution deferred to future
⚖️ **Performance:** Latency simulation adds ~5-10% overhead, acceptable for paper trading
⚖️ **Checkpoint size:** JSON is larger than binary, but human-readable is worth it

## Implementation Notes

### Order Flow

1. **Submission:**
   ```python
   order = Order(...)
   simulator.submit_order(order, timestamp)
   → Risk check → Validation → Add to pending queue (delayed)
   → SUBMITTED status (after submission_latency)
   ```

2. **Filling:**
   ```python
   simulator.process_market_data(current_time, prices)
   → Process pending actions up to current_time
   → Execute fills for submitted orders
   → Add fill to pending queue (delayed)
   → FILLED status (after fill_latency)
   ```

3. **Cancellation:**
   ```python
   simulator.cancel_order(order_id, timestamp)
   → Add cancel to pending queue (delayed)
   → CANCELLED status (after cancel_latency)
   ```

### Risk Check Flow

1. Order submitted
2. Risk checker evaluates:
   - Would this exceed position limits?
   - Would this exceed exposure limits?
   - Would this violate drawdown limits?
   - Is trading enabled?
3. If violation: Reject with typed reason
4. If pass: Proceed to validation

### Checkpoint/Restore Flow

**Save:**
```python
manager = CheckpointManager("checkpoints")
checkpoint = manager.create_checkpoint(simulator)
path = manager.save_checkpoint(checkpoint)
# Writes to checkpoints/{simulator_id}/{timestamp}.json
```

**Restore:**
```python
checkpoint = manager.load_checkpoint(simulator_id)
simulator = manager.restore_simulator(checkpoint)
# Validates version, rebuilds state
```

## Alternatives Considered

### Alternative 1: Engine-Embedded Execution

Embed execution logic directly in Backtrader/Nautilus adapters.

**Rejected because:**
- Duplicates logic across engines
- Hard to test in isolation
- Tightly couples execution to specific engine
- Can't share risk controls across engines

### Alternative 2: Simple Instant Execution

No latency simulation, instant fills on order submission.

**Rejected because:**
- Unrealistic for paper trading
- Can't test latency-dependent strategies
- Doesn't prepare for live trading

### Alternative 3: Binary Checkpoints (Pickle)

Use pickle for checkpoint serialization.

**Rejected because:**
- Security risk (pickle vulnerability)
- Not human-readable
- Not version control friendly
- Harder to debug

### Alternative 4: Database Storage for Checkpoints

Store checkpoints in SQLite/Postgres.

**Rejected for now because:**
- Adds deployment complexity
- Overkill for current scale
- JSON files are simpler and sufficient
- Can migrate to DB later if needed

## Related

- **ADR-005:** Engine-agnostic architecture (contracts decision)
- **ADR-007:** Checkpoint and recovery design
- **E5-T1:** Orders and executions implementation
- **E5-T2:** Latency hooks implementation
- **E5-T3:** Risk controls implementation
- **E5-T4:** State checkpoint implementation

## References

- Epic E5 backlog: `docs/planning/backtesting-live-readiness-backlog.md`
- Implementation plans: `docs/planning/e5-t*-implementation-plan.md`
- Execution simulator code: `finbot/services/execution/execution_simulator.py`
- Contracts code: `finbot/core/contracts/orders.py`, `latency.py`, `risk.py`, `checkpoint.py`

---

**Last updated:** 2026-02-16
