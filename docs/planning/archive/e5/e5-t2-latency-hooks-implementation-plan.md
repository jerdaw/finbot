# E5-T2: Order Lifecycle and Latency Hooks Implementation Plan

**Created:** 2026-02-16
**Epic:** E5 - Live Execution Interfaces
**Task:** E5-T2
**Estimated Effort:** M (3-5 days)

## Overview

Add latency simulation capabilities to the order execution system to model realistic order processing delays. This enables more accurate paper trading simulations and prepares the system for live trading conditions.

## Current State

**Already Implemented (E5-T1):**
- ✅ Order lifecycle states (NEW → SUBMITTED → PARTIALLY_FILLED → FILLED/REJECTED/CANCELLED)
- ✅ Order execution tracking
- ✅ ExecutionSimulator for paper trading
- ✅ Order validation and rejection

**What's Missing:**
- Latency simulation for order submission
- Latency simulation for order fills
- Latency simulation for order cancellations
- Configurable latency profiles (fast/normal/slow/custom)
- Time-based order processing queue

## Goals

1. **Submission latency** - Simulate delay between order creation and submission
2. **Fill latency** - Simulate delay between market data arrival and order fill
3. **Cancellation latency** - Simulate delay for order cancellation processing
4. **Configurable profiles** - Pre-configured latency profiles for different trading environments
5. **Testing** - Verify latency behavior matches configuration

## Design Decisions

**Latency Types:**
```python
- Submission latency: Time from submit_order() call to status=SUBMITTED
- Fill latency: Time from price update to execution
- Cancellation latency: Time from cancel request to status=CANCELLED
```

**Latency Profiles:**
```python
INSTANT:     0ms submission, 0ms fill, 0ms cancel (current behavior)
FAST:        10ms submission, 50ms fill, 20ms cancel
NORMAL:      50ms submission, 100-200ms fill, 50ms cancel
SLOW:        100ms submission, 500-1000ms fill, 100ms cancel
CUSTOM:      User-defined latencies
```

**Implementation Approach:**
- Use `timedelta` for latency configuration
- Track "effective time" vs "wall clock time"
- Process pending actions when time advances
- Support both deterministic and random latencies

## Implementation

### Step 1: Latency Configuration Contracts (1 hour)

**File:** `finbot/core/contracts/latency.py`

```python
@dataclass(frozen=True, slots=True)
class LatencyConfig:
    """Latency simulation configuration.

    Attributes:
        submission_latency: Delay from submit to SUBMITTED status
        fill_latency_min: Minimum delay from price update to fill
        fill_latency_max: Maximum delay from price update to fill
        cancel_latency: Delay from cancel request to CANCELLED status
    """
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

### Step 2: Pending Action Queue (1-2 hours)

**File:** `finbot/services/execution/pending_actions.py`

```python
class ActionType(StrEnum):
    """Type of pending action."""
    SUBMIT = "submit"
    FILL = "fill"
    CANCEL = "cancel"


@dataclass
class PendingAction:
    """Action waiting to be processed at future time."""
    action_type: ActionType
    order_id: str
    scheduled_time: datetime
    data: dict[str, Any]  # Action-specific data


class PendingActionQueue:
    """Queue for time-based action processing."""

    def __init__(self):
        self.actions: list[PendingAction] = []

    def add_action(self, action: PendingAction) -> None:
        """Add action to queue."""
        # Insert in sorted order by scheduled_time

    def get_due_actions(self, current_time: datetime) -> list[PendingAction]:
        """Get all actions due by current time."""
        # Return and remove actions with scheduled_time <= current_time

    def cancel_order_actions(self, order_id: str) -> None:
        """Remove all pending actions for an order."""
```

### Step 3: Update ExecutionSimulator with Latency (2-3 hours)

**File:** `finbot/services/execution/execution_simulator.py` (update)

```python
class ExecutionSimulator:
    def __init__(
        self,
        initial_cash: Decimal,
        slippage_bps: Decimal = Decimal("5"),
        commission_per_share: Decimal = Decimal("0"),
        latency_config: LatencyConfig = LATENCY_INSTANT,
    ):
        # ... existing fields ...
        self.latency_config = latency_config
        self.action_queue = PendingActionQueue()
        self.current_time = datetime.now()

    def submit_order(self, order: Order) -> Order:
        """Submit order with latency simulation."""
        # 1. Validate immediately
        # 2. If valid, schedule submission action
        # 3. Return order with status=NEW (not yet SUBMITTED)

    def process_market_data(
        self,
        symbol: str,
        price: Decimal,
        timestamp: datetime | None = None,
    ) -> list[OrderExecution]:
        """Process market data and handle pending actions."""
        # 1. Update current_time
        # 2. Process all due actions (submissions, cancellations)
        # 3. For matching orders, schedule fill actions with latency
        # 4. Process due fill actions
        # 5. Return executions

    def cancel_order(self, order_id: str) -> Order | None:
        """Cancel order with latency simulation."""
        # 1. Schedule cancel action with latency
        # 2. Return order (still in original status until cancel processes)
```

### Step 4: Tests (2-3 hours)

**File:** `tests/unit/test_latency_simulation.py`

```python
class TestLatencyProfiles:
    """Test pre-configured latency profiles."""

    def test_instant_profile():
        """INSTANT profile has zero latency."""

    def test_fast_profile():
        """FAST profile has 10/50/20ms latencies."""

    def test_normal_profile():
        """NORMAL profile has 50/100-200/50ms latencies."""

    def test_slow_profile():
        """SLOW profile has 100/500-1000/100ms latencies."""


class TestSubmissionLatency:
    """Test order submission latency."""

    def test_order_not_submitted_immediately():
        """Order status is NEW immediately after submit."""

    def test_order_submitted_after_latency():
        """Order becomes SUBMITTED after latency period."""

    def test_submission_latency_configurable():
        """Custom submission latency works."""


class TestFillLatency:
    """Test order fill latency."""

    def test_order_not_filled_immediately():
        """Order doesn't fill immediately when price matches."""

    def test_order_filled_after_latency():
        """Order fills after latency period."""

    def test_fill_latency_random_range():
        """Fill latency varies between min and max."""


class TestCancellationLatency:
    """Test order cancellation latency."""

    def test_order_not_cancelled_immediately():
        """Order remains active immediately after cancel request."""

    def test_order_cancelled_after_latency():
        """Order becomes CANCELLED after latency period."""

    def test_pending_fills_cancelled():
        """Pending fill actions are cancelled when order cancelled."""
```

### Step 5: Integration and Documentation (1 hour)

- Add LatencyConfig to contracts exports
- Update ExecutionSimulator docstrings with latency examples
- Add example in implementation plan

## Acceptance Criteria

- [x] Latency configuration contracts (LatencyConfig, profiles) ✅
- [x] Pending action queue for time-based processing ✅
- [x] Submission latency in ExecutionSimulator ✅
- [x] Fill latency in ExecutionSimulator ✅
- [x] Cancellation latency in ExecutionSimulator ✅
- [x] Pre-configured latency profiles (INSTANT/FAST/NORMAL/SLOW) ✅
- [x] Tests for all latency scenarios ✅
- [x] Integration with existing execution system ✅
- [x] Documentation ✅

**All acceptance criteria met!** E5-T2 is complete.

## Out of Scope (Future Work)

- Network jitter simulation
- Order queue prioritization (FIFO vs price-time priority)
- Partial fill latencies (multiple executions over time)
- Reject latencies
- Market impact latencies

## Risk Mitigation

**Complexity:** Time-based simulation can be complex
- Solution: Start with simple deterministic latencies, add randomness later

**Testing:** Hard to test time-based behavior
- Solution: Use controlled timestamps, not wall clock time

**Backward compatibility:** Existing code expects instant execution
- Solution: Default to LATENCY_INSTANT profile (zero latency)

## Timeline

- Step 1: Latency configuration contracts (1 hour)
- Step 2: Pending action queue (1-2 hours)
- Step 3: Update ExecutionSimulator (2-3 hours)
- Step 4: Tests (2-3 hours)
- Step 5: Integration (1 hour)
- Total: 7-10 hours (~1-2 days)

## Implementation Status

### Completed (2026-02-16)

- [x] Step 1: Latency configuration contracts ✅
  - Created `finbot/core/contracts/latency.py`
  - Contracts: `LatencyConfig` dataclass
  - Pre-configured profiles: `LATENCY_INSTANT`, `LATENCY_FAST`, `LATENCY_NORMAL`, `LATENCY_SLOW`
  - Support for submission, fill (min/max range), and cancellation latencies

- [x] Step 2: Pending action queue ✅
  - Created `finbot/services/execution/pending_actions.py`
  - `ActionType` enum: SUBMIT, FILL, CANCEL
  - `PendingAction` dataclass for scheduled actions
  - `PendingActionQueue` class with sorted queue management:
    - Binary search insertion for O(log n) adds
    - `get_due_actions()` removes and returns actions due by current time
    - `cancel_order_actions()` removes all pending actions for an order
    - Helper methods: `get_pending_count()`, `get_pending_for_order()`, `clear()`

- [x] Step 3: Update ExecutionSimulator with latency ✅
  - Updated `finbot/services/execution/execution_simulator.py`
  - Added `latency_config` parameter (defaults to LATENCY_INSTANT for backward compatibility)
  - Added `action_queue` and `current_time` tracking
  - Updated `submit_order()` for submission latency:
    - Instant: status=SUBMITTED immediately
    - Delayed: status=NEW, scheduled for later
  - Updated `process_market_data()` for fill latency:
    - Processes all due actions first
    - Schedules fill actions with random latency between min/max
    - Instant fills work as before
  - Updated `cancel_order()` for cancellation latency:
    - Cancels pending fill actions immediately
    - Schedules cancellation action with latency
  - Internal methods use `action.scheduled_time` for accurate timestamps

- [x] Step 4: Tests ✅
  - Created `tests/unit/test_latency_simulation.py`
  - 17 comprehensive tests covering:
    - Latency profiles (4 tests - INSTANT/FAST/NORMAL/SLOW)
    - Pending action queue (3 tests - sorting, due actions, cancellation)
    - Submission latency (3 tests - instant, delayed, after latency)
    - Fill latency (3 tests - instant, delayed, after latency)
    - Cancellation latency (4 tests - instant, delayed, after latency, cancel pending fills)
  - All tests passing
  - 615 tests total (613 passed, 2 skipped) - up from 598

- [x] Step 5: Integration ✅
  - Added to `finbot/core/contracts/__init__.py`:
    - `LatencyConfig`, `LATENCY_INSTANT`, `LATENCY_FAST`, `LATENCY_NORMAL`, `LATENCY_SLOW`
  - All existing tests still pass (backward compatible)
  - No linting errors
