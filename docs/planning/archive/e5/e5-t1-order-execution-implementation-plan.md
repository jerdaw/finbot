# E5-T1: Order Execution Interface Implementation Plan

**Created:** 2026-02-16
**Epic:** E5 - Live Execution Interfaces
**Task:** E5-T1
**Estimated Effort:** M (3-5 days)

## Overview

Define contracts and interfaces for order execution to enable transitioning from backtesting to live trading. This task focuses on creating the abstractions needed for order management without implementing live broker connections.

## Current State

**Already Implemented:**
- ✅ `OrderRequest`, `OrderSide`, `OrderType` in contracts
- ✅ `FillEvent` for execution tracking
- ✅ BacktestEngine interface
- ✅ Cost models for transaction costs

**What's Missing:**
- Order lifecycle management (pending → submitted → filled/rejected)
- Order state tracking and persistence
- Order validation and rejection reasons
- Execution simulator interface (paper trading)
- Order book/queue management

## Goals

1. **Order lifecycle** - Track orders from creation through execution
2. **Order states** - Model state transitions (pending/submitted/filled/rejected/cancelled)
3. **Validation** - Pre-execution order validation
4. **Execution simulation** - Paper trading capability
5. **Persistence** - Order history tracking

## Design Decisions

**Order Lifecycle States:**
```
NEW → SUBMITTED → PARTIALLY_FILLED → FILLED
                → REJECTED
                → CANCELLED
```

**Order Validation:**
- Pre-flight checks before submission
- Sufficient buying power
- Valid symbol/quantity
- Market hours (if applicable)
- Risk limits (if configured)

**Execution Simulator:**
- Paper trading against market data
- Realistic fill simulation (slippage, partial fills)
- No real broker connection required
- Can replay historical data for testing

**Order Persistence:**
- All orders saved to registry
- Track full lifecycle
- Enable audit trail
- Support order replay/analysis

## Implementation

### Step 1: Order Lifecycle Contracts (1-2 hours)

**File:** `finbot/core/contracts/orders.py`

```python
class OrderStatus(StrEnum):
    """Order lifecycle status."""
    NEW = "new"                          # Created but not submitted
    SUBMITTED = "submitted"              # Sent to broker/simulator
    PARTIALLY_FILLED = "partially_filled"  # Partial execution
    FILLED = "filled"                    # Fully executed
    REJECTED = "rejected"                # Rejected by broker/validator
    CANCELLED = "cancelled"              # Cancelled by user/system


class RejectionReason(StrEnum):
    """Reasons for order rejection."""
    INSUFFICIENT_FUNDS = "insufficient_funds"
    INVALID_QUANTITY = "invalid_quantity"
    INVALID_SYMBOL = "invalid_symbol"
    MARKET_CLOSED = "market_closed"
    DUPLICATE_ORDER = "duplicate_order"
    RISK_LIMIT_EXCEEDED = "risk_limit_exceeded"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class OrderExecution:
    """Record of an order execution (fill)."""
    execution_id: str
    order_id: str
    timestamp: datetime
    quantity: Decimal
    price: Decimal
    commission: Decimal
    is_partial: bool


@dataclass
class Order:
    """Mutable order with lifecycle tracking."""
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal

    created_at: datetime
    status: OrderStatus = OrderStatus.NEW

    # Optional: limit price for limit orders
    limit_price: Decimal | None = None

    # Execution tracking
    submitted_at: datetime | None = None
    filled_quantity: Decimal = Decimal("0")
    avg_fill_price: Decimal = Decimal("0")
    total_commission: Decimal = Decimal("0")
    executions: list[OrderExecution] = field(default_factory=list)

    # Rejection tracking
    rejected_at: datetime | None = None
    rejection_reason: RejectionReason | None = None
    rejection_message: str | None = None

    # Cancellation tracking
    cancelled_at: datetime | None = None
```

### Step 2: Order Validator (1-2 hours)

**File:** `finbot/services/execution/order_validator.py`

```python
@dataclass
class ValidationResult:
    """Result of order validation."""
    is_valid: bool
    rejection_reason: RejectionReason | None = None
    message: str | None = None


class OrderValidator:
    """Validates orders before execution."""

    def validate(
        self,
        order: Order,
        account_balance: Decimal,
        positions: dict[str, Decimal],
    ) -> ValidationResult:
        """Validate order against account state."""
        # Check quantity
        # Check buying power
        # Check symbol validity
        # Return ValidationResult
```

### Step 3: Execution Simulator (2-3 hours)

**File:** `finbot/services/execution/execution_simulator.py`

```python
class ExecutionSimulator:
    """Simulates order execution for paper trading."""

    def __init__(
        self,
        initial_cash: Decimal,
        slippage_bps: Decimal = Decimal("5"),
    ):
        self.cash = initial_cash
        self.positions: dict[str, Decimal] = {}
        self.slippage_bps = slippage_bps

    def submit_order(self, order: Order) -> Order:
        """Submit order for execution."""
        # Validate order
        # Update order status to SUBMITTED
        # Add to pending orders

    def process_market_data(
        self,
        symbol: str,
        price: Decimal,
    ) -> list[OrderExecution]:
        """Process market data and execute pending orders."""
        # Find pending orders for symbol
        # Simulate fills with slippage
        # Update order state
        # Update positions and cash
        # Return executions
```

### Step 4: Order Registry (2-3 hours)

**File:** `finbot/services/execution/order_registry.py`

```python
class OrderRegistry:
    """Persistent storage for order history."""

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir

    def save_order(self, order: Order) -> None:
        """Save order to registry."""

    def load_order(self, order_id: str) -> Order:
        """Load order by ID."""

    def list_orders(
        self,
        symbol: str | None = None,
        status: OrderStatus | None = None,
        since: datetime | None = None,
        limit: int | None = None,
    ) -> list[Order]:
        """List orders matching criteria."""

    def get_executions(
        self,
        order_id: str,
    ) -> list[OrderExecution]:
        """Get all executions for an order."""
```

### Step 5: Tests (2-3 hours)

**File:** `tests/unit/test_order_lifecycle.py`
- Order state transitions
- Validation logic
- Execution simulation
- Registry persistence

### Step 6: Integration Points (1 hour)

- Update `ExecutionSimulator` interface in contracts
- Add examples in docstrings
- Document order lifecycle

## Acceptance Criteria

- [x] Order lifecycle contracts (OrderStatus, Order, OrderExecution) ✅
- [x] Rejection handling (RejectionReason) ✅
- [x] Order validator ✅
- [x] Execution simulator for paper trading ✅
- [x] Order registry for persistence ✅
- [x] State transition validation ✅
- [x] Tests for all components ✅
- [x] Documentation ✅

**All acceptance criteria met!** E5-T1 is complete.

## Out of Scope (Future Work)

- Live broker connections (Interactive Brokers, Alpaca, etc.)
- Real-time market data integration
- Advanced order types (stop-loss, trailing stop, etc.)
- Order routing logic
- Multi-leg orders (spreads, combos)

## Risk Mitigation

**Complexity:** Order management is complex
- Solution: Start with simple market/limit orders only

**State consistency:** Tracking state across components
- Solution: Single source of truth (Order object), immutable executions

**Testing:** Hard to test without live data
- Solution: Execution simulator with synthetic data

## Timeline

- Step 1: Order lifecycle contracts (1-2 hours)
- Step 2: Order validator (1-2 hours)
- Step 3: Execution simulator (2-3 hours)
- Step 4: Order registry (2-3 hours)
- Step 5: Tests (2-3 hours)
- Step 6: Integration (1 hour)
- Total: 9-14 hours (~1.5-2.5 days)

## Implementation Status

### Completed (2026-02-16)

- [x] Step 1: Order lifecycle contracts ✅
  - Created `finbot/core/contracts/orders.py`
  - Contracts: `OrderStatus`, `RejectionReason`, `OrderExecution`, `Order`
  - Order lifecycle methods: `is_complete()`, `remaining_quantity()`, `add_execution()`

- [x] Step 2: Order validator ✅
  - Created `finbot/services/execution/order_validator.py`
  - `ValidationResult` dataclass for validation outcomes
  - `OrderValidator` class with comprehensive validation:
    - Quantity validation (positive, min/max limits)
    - Buying power checks for buy orders
    - Position checks for sell orders
    - Support for both market and limit orders

- [x] Step 3: Execution simulator ✅
  - Created `finbot/services/execution/execution_simulator.py`
  - `ExecutionSimulator` class for paper trading:
    - Order submission with validation
    - Market and limit order execution
    - Configurable slippage (basis points)
    - Commission per share
    - Position and cash tracking
    - Order cancellation
    - Realistic fill simulation

- [x] Step 4: Order registry ✅
  - Created `finbot/services/execution/order_registry.py`
  - `OrderRegistry` class for persistent storage:
    - Date-organized file structure (YYYY/MM/DD/)
    - JSON serialization with Decimal support
    - Query by symbol, status, date range, limit
    - Execution history retrieval
    - Order deletion

- [x] Step 5: Tests ✅
  - Created `tests/unit/test_order_lifecycle.py`
  - 21 comprehensive tests covering:
    - Order creation and lifecycle (3 tests)
    - Order validator (6 tests)
    - Execution simulator (6 tests)
    - Order registry (6 tests)
  - All tests passing
  - 598 tests total (596 passed, 2 skipped)

- [x] Step 6: Integration ✅
  - Added order contracts to `finbot/core/contracts/__init__.py`
  - Exported: `Order`, `OrderExecution`, `OrderStatus`, `RejectionReason`
  - All components follow existing patterns
  - No linting errors
