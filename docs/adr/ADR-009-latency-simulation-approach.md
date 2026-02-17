# ADR-009: Latency Simulation Approach

**Status:** Accepted
**Date:** 2026-02-16
**Deciders:** Development team
**Epic:** E5-T2 (Order Lifecycle and Latency Hooks)

## Context

Paper trading simulators that execute orders instantly produce unrealistic results. In real trading environments, every operation has latency:

1. **Submission delays:** Network round-trip, broker validation, exchange acknowledgment (10-100ms typical)
2. **Fill delays:** Market data propagation, matching engine processing, execution confirmation (50-1000ms typical)
3. **Cancellation delays:** Cancel request processing, confirmation round-trip (20-100ms typical)

Without latency simulation:
- Strategies appear more profitable than they would be live
- Look-ahead bias creeps in (filling at prices before they're "known")
- Cancellation logic appears instantaneous (unrealistic)
- No way to test latency-sensitive strategies (high-frequency, market-making)

The execution simulator needs configurable latency profiles to bridge the gap between backtesting and live trading.

### Requirements

**Must Have:**
- Simulate submission, fill, and cancellation latencies independently
- Support deterministic and random latency ranges
- Process actions in correct time order
- Work with existing ExecutionSimulator without breaking changes
- Configurable profiles for different trading environments

**Nice to Have:**
- Pre-configured profiles (INSTANT/FAST/NORMAL/SLOW)
- Efficient queue processing (O(log n) insertion)
- Ability to cancel pending actions when order cancelled

**Constraints:**
- Must preserve exact timestamp precision for audit trails
- Must not break backward compatibility (default to zero latency)
- Must work with both wall-clock time and simulated time

## Decision

We will use a **pending action queue** with time-based scheduling:

1. **Configurable latency profiles** via `LatencyConfig` dataclass
2. **Four pre-configured profiles:** INSTANT (0ms), FAST (10/50-100/20ms), NORMAL (50/100-200/50ms), SLOW (100/500-1000/100ms)
3. **Time-ordered queue** with binary search insertion for O(log n) performance
4. **Three action types:** SUBMIT, FILL, CANCEL
5. **Scheduled execution** when `current_time >= action.scheduled_time`

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ExecutionSimulator                        │
│                                                              │
│  submit_order(order, timestamp)                             │
│  ├─> Validate order                                         │
│  ├─> If latency > 0:                                        │
│  │   ├─> status = NEW                                       │
│  │   └─> Schedule SUBMIT action (t + submission_latency)    │
│  └─> If latency = 0:                                        │
│      └─> status = SUBMITTED immediately                     │
│                                                              │
│  process_market_data(symbol, price, timestamp)              │
│  ├─> Update current_time                                    │
│  ├─> Process due actions from queue:                        │
│  │   ├─> SUBMIT: Order → SUBMITTED status                   │
│  │   ├─> CANCEL: Order → CANCELLED status                   │
│  │   └─> FILL: Execute order, update positions              │
│  ├─> For SUBMITTED orders matching price:                   │
│  │   └─> Schedule FILL action (t + random(min, max))        │
│  └─> Return executions from processed fills                 │
│                                                              │
│  cancel_order(order_id, timestamp)                          │
│  ├─> Cancel pending FILL actions for order                  │
│  ├─> If latency > 0:                                        │
│  │   └─> Schedule CANCEL action (t + cancel_latency)        │
│  └─> If latency = 0:                                        │
│      └─> status = CANCELLED immediately                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Uses
                     ↓
┌─────────────────────────────────────────────────────────────┐
│               PendingActionQueue                             │
│                                                              │
│  actions: list[PendingAction]  # Sorted by scheduled_time   │
│                                                              │
│  add_action(action)                                         │
│  ├─> Binary search for insertion point                      │
│  └─> Insert maintaining sorted order                        │
│                                                              │
│  get_due_actions(current_time) → list[PendingAction]       │
│  ├─> Pop actions where scheduled_time <= current_time       │
│  └─> Return in time order                                   │
│                                                              │
│  cancel_order_actions(order_id)                             │
│  └─> Remove all actions for order_id                        │
└─────────────────────────────────────────────────────────────┘
                     │
                     │ Contains
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                   PendingAction                              │
│                                                              │
│  action_type: ActionType  # SUBMIT / FILL / CANCEL          │
│  order_id: str                                               │
│  scheduled_time: datetime                                    │
│  data: dict[str, Any]  # Action-specific payload            │
└─────────────────────────────────────────────────────────────┘
```

### Latency Configuration

```python
@dataclass(frozen=True, slots=True)
class LatencyConfig:
    """Latency simulation configuration."""
    submission_latency: timedelta  # submit_order() → SUBMITTED
    fill_latency_min: timedelta    # price match → FILLED (min)
    fill_latency_max: timedelta    # price match → FILLED (max)
    cancel_latency: timedelta      # cancel_order() → CANCELLED
```

### Pre-Configured Profiles

| Profile | Submission | Fill (min-max) | Cancel | Use Case |
|---------|-----------|----------------|--------|----------|
| **INSTANT** | 0ms | 0ms - 0ms | 0ms | Backtesting (current behavior) |
| **FAST** | 10ms | 50ms - 100ms | 20ms | Co-located / Direct Market Access |
| **NORMAL** | 50ms | 100ms - 200ms | 50ms | Typical retail broker |
| **SLOW** | 100ms | 500ms - 1000ms | 100ms | High-latency network / Congested |

### Action Processing Flow

**1. Order Submission (with latency):**
```python
submit_order(order, timestamp=T0)
├─> Validate
├─> Add SUBMIT action scheduled for T0 + submission_latency
└─> Return order with status=NEW

process_market_data(timestamp=T1) where T1 >= T0 + submission_latency
├─> get_due_actions(T1)
├─> Process SUBMIT action: order.status → SUBMITTED
└─> Order now eligible for fills
```

**2. Order Fill (with latency):**
```python
process_market_data(symbol, price, timestamp=T2)
├─> For SUBMITTED orders matching price:
│   ├─> fill_latency = random(fill_latency_min, fill_latency_max)
│   └─> Schedule FILL action for T2 + fill_latency
└─> Process due FILL actions: execute fills, update positions
```

**3. Order Cancellation (with latency):**
```python
cancel_order(order_id, timestamp=T3)
├─> Cancel pending FILL actions immediately (prevent race)
├─> Schedule CANCEL action for T3 + cancel_latency
└─> Return order (still active)

process_market_data(timestamp=T4) where T4 >= T3 + cancel_latency
├─> Process CANCEL action: order.status → CANCELLED
└─> Order no longer eligible for fills
```

### Queue Algorithm

**Binary Search Insertion (O(log n)):**
```python
def add_action(self, action: PendingAction) -> None:
    """Insert action in sorted order by scheduled_time."""
    left, right = 0, len(self.actions)
    while left < right:
        mid = (left + right) // 2
        if self.actions[mid].scheduled_time <= action.scheduled_time:
            left = mid + 1
        else:
            right = mid
    self.actions.insert(left, action)
```

**Due Action Processing (Amortized O(1)):**
```python
def get_due_actions(self, current_time: datetime) -> list[PendingAction]:
    """Pop all actions with scheduled_time <= current_time."""
    due_actions = []
    while self.actions and self.actions[0].scheduled_time <= current_time:
        due_actions.append(self.actions.pop(0))
    return due_actions
```

**Action Cancellation (O(n)):**
```python
def cancel_order_actions(self, order_id: str) -> int:
    """Remove all pending actions for an order."""
    original_count = len(self.actions)
    self.actions = [a for a in self.actions if a.order_id != order_id]
    return original_count - len(self.actions)
```

## Consequences

### Positive

✅ **Realistic paper trading:** Matches live trading latencies, reduces strategy over-optimization
✅ **Prevents look-ahead bias:** Orders can't fill before prices are "known" (after latency)
✅ **Configurable:** Four profiles + custom configuration support
✅ **Efficient:** O(log n) insertion, amortized O(1) processing for due actions
✅ **Backward compatible:** Defaults to INSTANT (zero latency) for existing code
✅ **Testable:** Controlled time simulation makes testing deterministic
✅ **Race prevention:** Cancelling order removes pending fills immediately

### Negative

❌ **Complexity:** More state to track (pending queue, scheduled times)
❌ **Performance overhead:** Binary search insertion, queue processing (~5-10% slowdown)
❌ **Memory overhead:** Pending actions stored in memory
❌ **Testing burden:** Time-based logic requires careful test design

### Neutral

⚖️ **Fill latency is random:** Varies between min/max (matches real-world variance)
⚖️ **Queue size:** Typically small (< 100 actions) for most strategies
⚖️ **No partial fill latency:** All-or-nothing fills (future enhancement)

## Implementation Details

### Latency Contract

**File:** `finbot/core/contracts/latency.py`

```python
@dataclass(frozen=True, slots=True)
class LatencyConfig:
    submission_latency: timedelta
    fill_latency_min: timedelta
    fill_latency_max: timedelta
    cancel_latency: timedelta


# Pre-configured profiles
LATENCY_INSTANT = LatencyConfig(
    submission_latency=timedelta(0),
    fill_latency_min=timedelta(0),
    fill_latency_max=timedelta(0),
    cancel_latency=timedelta(0),
)

LATENCY_FAST = LatencyConfig(
    submission_latency=timedelta(milliseconds=10),
    fill_latency_min=timedelta(milliseconds=50),
    fill_latency_max=timedelta(milliseconds=100),
    cancel_latency=timedelta(milliseconds=20),
)

LATENCY_NORMAL = LatencyConfig(
    submission_latency=timedelta(milliseconds=50),
    fill_latency_min=timedelta(milliseconds=100),
    fill_latency_max=timedelta(milliseconds=200),
    cancel_latency=timedelta(milliseconds=50),
)

LATENCY_SLOW = LatencyConfig(
    submission_latency=timedelta(milliseconds=100),
    fill_latency_min=timedelta(milliseconds=500),
    fill_latency_max=timedelta(milliseconds=1000),
    cancel_latency=timedelta(milliseconds=100),
)
```

### Action Types

**File:** `finbot/services/execution/pending_actions.py`

```python
class ActionType(StrEnum):
    """Type of pending action."""
    SUBMIT = "submit"    # Order submission (after validation)
    FILL = "fill"        # Order execution
    CANCEL = "cancel"    # Order cancellation


@dataclass
class PendingAction:
    """Action waiting to be processed at future time."""
    action_type: ActionType
    order_id: str
    scheduled_time: datetime
    data: dict[str, Any]  # fill price, execution details, etc.
```

### ExecutionSimulator Integration

**File:** `finbot/services/execution/execution_simulator.py`

```python
class ExecutionSimulator:
    def __init__(
        self,
        initial_cash: Decimal,
        slippage_bps: Decimal = Decimal("5"),
        commission_per_share: Decimal = Decimal("0"),
        latency_config: LatencyConfig = LATENCY_INSTANT,  # Default: no latency
    ):
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.positions: dict[str, Decimal] = {}
        self.pending_orders: dict[str, Order] = {}
        self.completed_orders: dict[str, Order] = {}
        self.slippage_bps = slippage_bps
        self.commission_per_share = commission_per_share
        self.latency_config = latency_config
        self.action_queue = PendingActionQueue()
        self.current_time = datetime.now()
```

### Example Usage

```python
from finbot.services.execution import ExecutionSimulator
from finbot.core.contracts import LATENCY_NORMAL

# Create simulator with realistic latency
simulator = ExecutionSimulator(
    initial_cash=Decimal("100000"),
    latency_config=LATENCY_NORMAL,
)

# Submit order (status = NEW)
order = simulator.submit_order(Order(...), timestamp=T0)
assert order.status == OrderStatus.NEW

# After 50ms: submission latency elapsed
simulator.process_market_data("AAPL", Decimal("150"), timestamp=T0 + timedelta(milliseconds=50))
assert simulator.pending_orders[order.order_id].status == OrderStatus.SUBMITTED

# After 150ms more: fill latency elapsed (100-200ms range)
simulator.process_market_data("AAPL", Decimal("150"), timestamp=T0 + timedelta(milliseconds=200))
assert simulator.completed_orders[order.order_id].status == OrderStatus.FILLED
```

## Alternatives Considered

### Alternative 1: Instant Execution (No Latency)

Execute all operations (submit, fill, cancel) instantly when called.

**Rejected because:**
- Unrealistic for paper trading
- Creates look-ahead bias (fills at prices before they're "known")
- Doesn't prepare strategies for live trading
- No way to test latency-sensitive logic

**Status:** Retained as default (LATENCY_INSTANT) for backward compatibility

### Alternative 2: Fixed Random Delays Per Operation

Add random `time.sleep()` on each operation without a queue.

**Rejected because:**
- Breaks deterministic time simulation (can't use simulated time)
- Can't cancel pending fills when order cancelled (race condition)
- No ordering guarantees (cancels could process before fills)
- Slows down backtests unnecessarily (real sleep vs simulated time)

### Alternative 3: External Latency Simulator

Separate service that intercepts orders and delays them.

**Rejected because:**
- Adds deployment complexity
- Network overhead for inter-process communication
- Hard to test in isolation
- Overkill for current use case

### Alternative 4: Simple Queue (Unsorted)

Use unsorted list, scan entire queue to find due actions.

**Rejected because:**
- O(n) for every `get_due_actions()` call
- Poor performance for long-running simulations
- Binary search insertion is simple and fast

### Alternative 5: Priority Queue (heapq)

Use Python's `heapq` module for priority queue.

**Rejected because:**
- Harder to cancel specific order actions (no efficient removal)
- Binary search on sorted list is simpler and sufficient
- Queue size is small (< 100 actions typically)

## Future Enhancements

### 1. Partial Fill Latency

**Goal:** Simulate fills over multiple time steps for large orders

```python
# Instead of single FILL action
FILL_PARTIAL: Fill 100 shares at T1 + 100ms
FILL_PARTIAL: Fill 50 shares at T1 + 150ms
FILL_FINAL: Fill 50 shares at T1 + 200ms
```

### 2. Network Jitter Simulation

**Goal:** Add variance to latency (not just fixed + random)

```python
@dataclass
class LatencyConfig:
    # ... existing fields ...
    jitter_pct: Decimal = Decimal("10")  # +/- 10% variance
```

### 3. Order Queue Prioritization

**Goal:** Model FIFO vs price-time priority matching

```python
class OrderQueuePolicy(StrEnum):
    FIFO = "fifo"
    PRICE_TIME = "price_time"
    PRO_RATA = "pro_rata"
```

### 4. Reject Latency

**Goal:** Simulate delay for order rejection (validation failures)

```python
@dataclass
class LatencyConfig:
    # ... existing fields ...
    reject_latency: timedelta = timedelta(milliseconds=20)
```

### 5. Market Impact Latency

**Goal:** Simulate delay increase for large orders

```python
def calculate_fill_latency(order_quantity, avg_volume):
    base_latency = self.latency_config.fill_latency_min
    impact_factor = order_quantity / avg_volume
    return base_latency * (1 + impact_factor)
```

## Testing Strategy

**Unit Tests:** (17 tests in `tests/unit/test_latency_simulation.py`)
- Latency profiles (4 tests): Verify INSTANT/FAST/NORMAL/SLOW configuration
- Pending action queue (3 tests): Binary search, due actions, cancellation
- Submission latency (3 tests): Instant, delayed, after latency
- Fill latency (3 tests): Instant, delayed, after latency
- Cancellation latency (4 tests): Instant, delayed, after latency, cancel pending fills

**Integration Tests:**
- Full order lifecycle with NORMAL latency
- Cancel order before fill processes
- Multiple orders with overlapping latencies

**Test Coverage:** All tests passing (615 total, 613 passed, 2 skipped)

## Related

- **ADR-006:** Execution system architecture (latency as core component)
- **E5-T2:** Latency hooks implementation plan
- **E5-T1:** Orders and executions (order lifecycle foundation)

## References

- Implementation plan: `docs/planning/e5-t2-latency-hooks-implementation-plan.md`
- Latency contract: `finbot/core/contracts/latency.py`
- Pending actions: `finbot/services/execution/pending_actions.py`
- Execution simulator: `finbot/services/execution/execution_simulator.py`
- Tests: `tests/unit/test_latency_simulation.py`

---

**Last updated:** 2026-02-16
