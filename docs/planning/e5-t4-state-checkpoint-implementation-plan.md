# E5-T4: State Checkpoint and Recovery Implementation Plan

**Created:** 2026-02-16
**Epic:** E5 - Live Execution Interfaces
**Task:** E5-T4
**Estimated Effort:** M (3-5 days)

## Overview

Implement state checkpoint and recovery capabilities to enable system restarts, disaster recovery, and state replay. This is critical for live trading where systems must recover gracefully from failures.

## Current State

**Already Implemented (E5-T1, E5-T2, E5-T3):**
- ✅ Order lifecycle and execution tracking
- ✅ ExecutionSimulator with full state (cash, positions, orders)
- ✅ Latency simulation
- ✅ Risk controls
- ✅ Order registry for persistence

**What's Missing:**
- State checkpoint contracts
- ExecutionSimulator state serialization
- State restoration with validation
- Checkpoint versioning
- Recovery testing

## Goals

1. **State capture** - Serialize ExecutionSimulator state to disk
2. **State restoration** - Rebuild ExecutionSimulator from checkpoint
3. **Validation** - Verify restored state integrity
4. **Versioning** - Handle checkpoint schema evolution
5. **Testing** - Verify checkpoint/restore cycles work correctly

## Design Decisions

**Checkpoint Contents:**
```python
- Checkpoint metadata (version, timestamp, simulator_id)
- Cash balance
- Positions (symbol -> quantity)
- Pending orders (full Order objects)
- Completed orders (full Order objects)
- Risk state (peak_value, daily_start_value, trading_enabled)
- Configuration (slippage, commission, latency_config, risk_config)
```

**Checkpoint Format:**
- JSON for human readability and version control compatibility
- Decimal serialized as strings for precision
- Datetime serialized as ISO format

**Checkpoint Storage:**
```
checkpoints/
├── {simulator_id}/
│   ├── latest.json
│   └── {timestamp}.json
```

**Recovery Strategy:**
- Restore all state fields
- Validate state consistency
- Rebuild pending action queue (latency simulation)
- Resume from where left off

## Implementation

### Step 1: Checkpoint Contracts (1-2 hours)

**File:** `finbot/core/contracts/checkpoint.py`

```python
@dataclass(frozen=True, slots=True)
class ExecutionCheckpoint:
    """Snapshot of ExecutionSimulator state."""

    # Metadata
    version: str
    simulator_id: str
    checkpoint_timestamp: datetime

    # Account state
    cash: Decimal
    initial_cash: Decimal
    positions: dict[str, Decimal]

    # Orders
    pending_orders: list[Order]
    completed_orders: list[Order]

    # Risk state (optional)
    peak_value: Decimal | None = None
    daily_start_value: Decimal | None = None
    trading_enabled: bool = True

    # Configuration
    slippage_bps: Decimal = Decimal("5")
    commission_per_share: Decimal = Decimal("0")
    latency_config_name: str = "INSTANT"  # INSTANT/FAST/NORMAL/SLOW
    risk_config_data: dict | None = None


CHECKPOINT_VERSION = "1.0.0"
```

### Step 2: Checkpoint Manager (2-3 hours)

**File:** `finbot/services/execution/checkpoint_manager.py`

```python
class CheckpointManager:
    """Manages ExecutionSimulator state checkpoints."""

    def __init__(self, checkpoint_dir: Path):
        self.checkpoint_dir = checkpoint_dir

    def create_checkpoint(
        self,
        simulator: ExecutionSimulator,
        simulator_id: str,
    ) -> ExecutionCheckpoint:
        """Create checkpoint from simulator state."""
        # Extract all state
        # Create ExecutionCheckpoint
        # Return checkpoint

    def save_checkpoint(
        self,
        checkpoint: ExecutionCheckpoint,
    ) -> Path:
        """Save checkpoint to disk."""
        # Create directory for simulator_id
        # Save to timestamped file
        # Update latest.json symlink/copy

    def load_checkpoint(
        self,
        simulator_id: str,
        timestamp: datetime | None = None,
    ) -> ExecutionCheckpoint:
        """Load checkpoint from disk."""
        # Load latest if timestamp=None
        # Load specific timestamp otherwise
        # Deserialize and return

    def restore_simulator(
        self,
        checkpoint: ExecutionCheckpoint,
    ) -> ExecutionSimulator:
        """Restore ExecutionSimulator from checkpoint."""
        # Validate checkpoint version
        # Recreate simulator with config
        # Restore state (cash, positions, orders)
        # Restore risk state
        # Return simulator

    def list_checkpoints(
        self,
        simulator_id: str,
    ) -> list[tuple[datetime, Path]]:
        """List available checkpoints for simulator."""
```

### Step 3: Serialization Helpers (1-2 hours)

**File:** `finbot/services/execution/checkpoint_serialization.py`

```python
def serialize_checkpoint(checkpoint: ExecutionCheckpoint) -> dict:
    """Convert checkpoint to JSON-compatible dict."""
    # Handle Decimal -> str
    # Handle datetime -> ISO string
    # Handle nested objects (Order, RiskConfig)

def deserialize_checkpoint(data: dict) -> ExecutionCheckpoint:
    """Convert dict to ExecutionCheckpoint."""
    # Handle str -> Decimal
    # Handle ISO string -> datetime
    # Rebuild nested objects
```

### Step 4: Add Checkpoint Methods to ExecutionSimulator (1 hour)

**File:** `finbot/services/execution/execution_simulator.py` (update)

```python
class ExecutionSimulator:
    def __init__(
        self,
        # ... existing params ...
        simulator_id: str | None = None,
    ):
        self.simulator_id = simulator_id or f"sim-{uuid.uuid4().hex[:8]}"
        # ... existing init ...

    def get_checkpoint_data(self) -> dict:
        """Get current state for checkpointing."""
        return {
            "cash": self.cash,
            "initial_cash": self.initial_cash,
            "positions": self.positions.copy(),
            "pending_orders": list(self.pending_orders.values()),
            "completed_orders": list(self.completed_orders.values()),
            # ... risk state, config ...
        }
```

### Step 5: Tests (2-3 hours)

**File:** `tests/unit/test_checkpoint_recovery.py`

```python
class TestCheckpointCreation:
    """Test checkpoint creation."""

    def test_create_checkpoint_basic():
        """Create checkpoint from simulator."""

    def test_checkpoint_includes_all_state():
        """Checkpoint contains all required fields."""


class TestCheckpointSerialization:
    """Test checkpoint serialization."""

    def test_serialize_deserialize_roundtrip():
        """Checkpoint survives serialize/deserialize."""

    def test_decimal_precision_preserved():
        """Decimal values maintain precision."""

    def test_datetime_preserved():
        """Datetime values preserved correctly."""


class TestStateRestoration:
    """Test state restoration."""

    def test_restore_cash_and_positions():
        """Cash and positions restored correctly."""

    def test_restore_pending_orders():
        """Pending orders restored and can execute."""

    def test_restore_completed_orders():
        """Completed orders history preserved."""

    def test_restore_risk_state():
        """Risk state (peak, daily) restored."""

    def test_restore_with_latency():
        """Latency simulation continues after restore."""


class TestCheckpointVersioning:
    """Test checkpoint version handling."""

    def test_version_mismatch_detected():
        """Incompatible versions detected."""
```

### Step 6: Integration and Documentation (1 hour)

- Add ExecutionCheckpoint to contracts exports
- Document checkpoint/restore workflow
- Add example usage

## Acceptance Criteria

- [x] Checkpoint contracts (ExecutionCheckpoint, version)
- [x] CheckpointManager for save/load
- [x] Serialization with Decimal/datetime handling
- [x] ExecutionSimulator restoration
- [x] State validation on restore
- [x] Tests for checkpoint/restore cycles (18 tests, all passing)
- [x] Versioning support
- [x] Integration with existing execution system
- [x] Documentation

## Out of Scope (Future Work)

- Automatic checkpoint scheduling (periodic saves)
- Checkpoint compression
- Remote checkpoint storage (S3, etc.)
- Checkpoint diff/delta encoding
- Checkpoint encryption

## Risk Mitigation

**Data loss:** Checkpoint corruption could lose state
- Solution: Atomic writes, keep multiple checkpoints

**Version incompatibility:** Schema changes break old checkpoints
- Solution: Version checking, migration support

**Performance:** Large checkpoints slow down saves
- Solution: JSON is reasonably fast, optimize later if needed

## Timeline

- Step 1: Checkpoint contracts (1-2 hours)
- Step 2: Checkpoint manager (2-3 hours)
- Step 3: Serialization helpers (1-2 hours)
- Step 4: ExecutionSimulator integration (1 hour)
- Step 5: Tests (2-3 hours)
- Step 6: Integration (1 hour)
- Total: 8-12 hours (~1-2 days)

## Implementation Status

- [x] Step 1: Checkpoint contracts
- [x] Step 2: Checkpoint manager
- [x] Step 3: Serialization helpers
- [x] Step 4: ExecutionSimulator integration
- [x] Step 5: Tests
- [x] Step 6: Integration
