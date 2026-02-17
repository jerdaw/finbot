# ADR-007: Checkpoint and Recovery Design

**Status:** Accepted
**Date:** 2026-02-16
**Deciders:** Development team
**Epic:** E5-T4 (State Checkpoint and Recovery)

## Context

The ExecutionSimulator needs state persistence for:

1. **Disaster Recovery:** Recover from system crashes, network failures, power outages
2. **State Replay:** Resume paper trading sessions from exact state
3. **Debugging:** Inspect historical simulator state at specific points
4. **Testing:** Create reproducible test scenarios from saved states
5. **Long-Running Simulations:** Safely interrupt and resume multi-day backtests

### Requirements

**Must Have:**
- Capture complete simulator state (cash, positions, orders, risk state, config)
- Restore simulator to exact state from checkpoint
- Detect incompatible checkpoint versions
- Support multiple checkpoints per simulator
- Human-readable format for debugging

**Nice to Have:**
- Compact storage
- Fast serialization/deserialization
- Version migration support
- Checkpoint compression

**Constraints:**
- Must preserve Decimal precision (no float rounding)
- Must handle datetime serialization
- Must be language/system independent (JSON compatible)
- Must support schema evolution

## Decision

We will use **JSON-based checkpoints** with:

1. **Versioned schema** (`CHECKPOINT_VERSION`) for compatibility checking
2. **String serialization** for Decimal values (preserve precision)
3. **ISO format** for datetime values (portable)
4. **Timestamped files** for checkpoint history
5. **`latest.json` symlink** for easy access to most recent

### Storage Structure

```
checkpoints/
├── {simulator_id}/
│   ├── latest.json                      # Copy of most recent
│   ├── 20260216_103045_123456.json      # Timestamped checkpoint
│   ├── 20260216_143022_789012.json
│   └── 20260216_183011_345678.json
```

**Filename format:** `YYYYMMDD_HHMMSS_microseconds.json`

### Checkpoint Schema

```json
{
  "version": "1.0.0",
  "simulator_id": "sim-abc12345",
  "checkpoint_timestamp": "2026-02-16T10:30:45.123456",

  "cash": "95000.50",
  "initial_cash": "100000.00",

  "positions": {
    "AAPL": "100",
    "SPY": "50.5"
  },

  "pending_orders": [
    {
      "order_id": "ord-001",
      "symbol": "MSFT",
      "side": "buy",
      "order_type": "limit",
      "quantity": "50",
      "limit_price": "300.00",
      "status": "submitted",
      "created_at": "2026-02-16T10:25:00.000000",
      "submitted_at": "2026-02-16T10:25:00.050000",
      "filled_quantity": "0",
      "avg_fill_price": "0",
      "total_commission": "0",
      "executions": []
    }
  ],

  "completed_orders": [
    {
      "order_id": "ord-000",
      "symbol": "AAPL",
      "side": "buy",
      "order_type": "market",
      "quantity": "100",
      "status": "filled",
      "created_at": "2026-02-16T10:20:00.000000",
      "submitted_at": "2026-02-16T10:20:00.050000",
      "filled_quantity": "100",
      "avg_fill_price": "150.25",
      "total_commission": "1.00",
      "executions": [
        {
          "execution_id": "exec-000",
          "order_id": "ord-000",
          "timestamp": "2026-02-16T10:20:00.150000",
          "quantity": "100",
          "price": "150.25",
          "commission": "1.00",
          "is_partial": false
        }
      ]
    }
  ],

  "peak_value": "110000.00",
  "daily_start_value": "105000.00",
  "trading_enabled": true,

  "slippage_bps": "5",
  "commission_per_share": "0.01",
  "latency_config_name": "NORMAL",

  "risk_config_data": {
    "trading_enabled": true,
    "position_limit": {
      "max_shares": "1000",
      "max_value": "50000.00"
    },
    "exposure_limit": {
      "max_gross_exposure_pct": "150",
      "max_net_exposure_pct": "100"
    },
    "drawdown_limit": {
      "max_daily_drawdown_pct": "5",
      "max_total_drawdown_pct": "20"
    }
  }
}
```

### Checkpoint Components

#### 1. ExecutionCheckpoint Contract

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
    latency_config_name: str = "INSTANT"
    risk_config_data: dict | None = None
```

#### 2. CheckpointManager

**Responsibilities:**
- Create checkpoints from ExecutionSimulator
- Save checkpoints to disk (JSON)
- Load checkpoints from disk
- Restore ExecutionSimulator from checkpoint
- List available checkpoints
- Validate checkpoint versions

**API:**
```python
class CheckpointManager:
    def create_checkpoint(
        self,
        simulator: ExecutionSimulator,
        simulator_id: str | None = None,
    ) -> ExecutionCheckpoint:
        """Extract state from simulator."""

    def save_checkpoint(
        self,
        checkpoint: ExecutionCheckpoint,
    ) -> Path:
        """Save to checkpoints/{simulator_id}/{timestamp}.json."""

    def load_checkpoint(
        self,
        simulator_id: str,
        timestamp: datetime | None = None,
    ) -> ExecutionCheckpoint:
        """Load from disk (latest if timestamp=None)."""

    def restore_simulator(
        self,
        checkpoint: ExecutionCheckpoint,
    ) -> ExecutionSimulator:
        """Rebuild simulator from checkpoint."""

    def list_checkpoints(
        self,
        simulator_id: str,
    ) -> list[tuple[datetime, Path]]:
        """List available checkpoints."""
```

#### 3. Serialization Helpers

**Purpose:** Handle Decimal/datetime conversion for JSON

```python
def serialize_checkpoint(checkpoint: ExecutionCheckpoint) -> dict:
    """Convert to JSON-compatible dict.

    - Decimal → str (preserve precision)
    - datetime → ISO format string
    - Nested objects → recursive serialization
    """

def deserialize_checkpoint(data: dict) -> ExecutionCheckpoint:
    """Rebuild from dict.

    - str → Decimal
    - ISO string → datetime
    - Rebuild nested objects
    """
```

### Version Checking

**On Restore:**
```python
def restore_simulator(self, checkpoint: ExecutionCheckpoint) -> ExecutionSimulator:
    # Validate version
    if checkpoint.version != CHECKPOINT_VERSION:
        raise ValueError(
            f"Checkpoint version {checkpoint.version} incompatible "
            f"with current version {CHECKPOINT_VERSION}"
        )

    # ... restore state ...
```

**Version Evolution:**
- `CHECKPOINT_VERSION = "1.0.0"` (current)
- Future: Add migration functions for older versions
- Store version in every checkpoint
- Reject incompatible versions (fail fast)

### Restoration Flow

1. **Load checkpoint:**
   ```python
   checkpoint = manager.load_checkpoint("sim-001")
   ```

2. **Validate version:**
   ```python
   if checkpoint.version != CHECKPOINT_VERSION:
       raise ValueError("Incompatible version")
   ```

3. **Recreate simulator with config:**
   ```python
   simulator = ExecutionSimulator(
       initial_cash=checkpoint.initial_cash,
       slippage_bps=checkpoint.slippage_bps,
       commission_per_share=checkpoint.commission_per_share,
       latency_config=latency_config,
       risk_config=risk_config,
   )
   ```

4. **Restore state:**
   ```python
   simulator.cash = checkpoint.cash
   simulator.positions = checkpoint.positions.copy()
   simulator.pending_orders = {
       order.order_id: order
       for order in checkpoint.pending_orders
   }
   simulator.completed_orders = {
       order.order_id: order
       for order in checkpoint.completed_orders
   }
   ```

5. **Restore risk state:**
   ```python
   if simulator.risk_checker:
       simulator.risk_checker.peak_value = checkpoint.peak_value
       simulator.risk_checker.daily_start_value = checkpoint.daily_start_value
       simulator.risk_checker.trading_enabled = checkpoint.trading_enabled
   ```

6. **Return restored simulator:**
   ```python
   return simulator
   ```

## Consequences

### Positive

✅ **Human-readable:** JSON is easy to inspect and debug
✅ **Version control friendly:** Text format can be diffed, committed to git
✅ **Safe:** No pickle vulnerability, no code execution
✅ **Portable:** Works across systems, languages, platforms
✅ **Precise:** String serialization preserves Decimal precision
✅ **Debuggable:** Can manually edit checkpoints for testing
✅ **Versioned:** Schema evolution supported via version checking
✅ **History:** Multiple checkpoints enable state replay at any point

### Negative

❌ **File size:** JSON is larger than binary formats (protobuf, msgpack)
❌ **Performance:** JSON parsing slower than binary deserialization
❌ **No compression:** Files can grow large for complex state
❌ **No encryption:** Sensitive data stored in plain text

### Neutral

⚖️ **Storage cost:** ~1-10KB per checkpoint (acceptable for current scale)
⚖️ **Serialization speed:** ~1-5ms per checkpoint (not a bottleneck)
⚖️ **Manual cleanup:** Old checkpoints must be manually deleted
⚖️ **No automatic migration:** Version mismatches rejected (fail fast)

## Implementation Details

### Decimal Precision Preservation

**Problem:** JSON doesn't support Decimal natively

**Solution:** Convert to string during serialization

```python
# Serialize
"cash": str(checkpoint.cash)  # "95000.50"

# Deserialize
cash = Decimal(data["cash"])  # Decimal("95000.50")
```

**Why:** Avoids float rounding errors (e.g., `95000.50` → `95000.5000000001`)

### Datetime Serialization

**Format:** ISO 8601 with microseconds

```python
# Serialize
"checkpoint_timestamp": checkpoint.checkpoint_timestamp.isoformat()
# "2026-02-16T10:30:45.123456"

# Deserialize
timestamp = datetime.fromisoformat(data["checkpoint_timestamp"])
```

**Why:** Language-independent, timezone-aware, microsecond precision

### Latency Config Serialization

**Problem:** LatencyConfig is not JSON-serializable (timedelta)

**Solution:** Store config name as string, map back on restore

```python
# Serialize
latency_config_name = "NORMAL"  # Store name, not config

# Deserialize
latency_config = LATENCY_NORMAL  # Map name → config object
```

**Mapping:**
- "INSTANT" → `LATENCY_INSTANT`
- "FAST" → `LATENCY_FAST`
- "NORMAL" → `LATENCY_NORMAL`
- "SLOW" → `LATENCY_SLOW`

### Risk Config Serialization

**Problem:** RiskConfig contains nested dataclasses

**Solution:** Serialize to nested dict, reconstruct on deserialize

```python
# Serialize
def _serialize_risk_config(risk_config) -> dict:
    return {
        "trading_enabled": risk_config.trading_enabled,
        "position_limit": {
            "max_shares": str(risk_config.position_limit.max_shares),
            "max_value": str(risk_config.position_limit.max_value),
        } if risk_config.position_limit else None,
        # ... other rules ...
    }

# Deserialize
def _deserialize_risk_config(data: dict) -> RiskConfig:
    position_limit = PositionLimitRule(
        max_shares=Decimal(data["position_limit"]["max_shares"]),
        max_value=Decimal(data["position_limit"]["max_value"]),
    ) if data.get("position_limit") else None

    return RiskConfig(
        position_limit=position_limit,
        # ... other rules ...
    )
```

### Atomic Writes

**Problem:** Partial writes can corrupt checkpoints

**Solution:** Write to temp file, then atomic rename

```python
def save_checkpoint(self, checkpoint: ExecutionCheckpoint) -> Path:
    checkpoint_path = self.checkpoint_dir / checkpoint.simulator_id / f"{timestamp}.json"
    temp_path = checkpoint_path.with_suffix(".tmp")

    # Write to temp file
    with temp_path.open("w") as f:
        json.dump(checkpoint_data, f, indent=2)

    # Atomic rename
    temp_path.rename(checkpoint_path)

    return checkpoint_path
```

**Why:** Prevents corrupted checkpoints if write is interrupted

## Alternatives Considered

### Alternative 1: Pickle Serialization

Store checkpoints using Python's pickle module.

**Rejected because:**
- Security vulnerability (code execution)
- Not human-readable
- Not portable across Python versions
- Breaks with class structure changes

### Alternative 2: Protocol Buffers (protobuf)

Use protobuf for compact binary serialization.

**Rejected because:**
- Requires schema definition files (.proto)
- Not human-readable
- Overkill for current scale
- Harder to debug

### Alternative 3: MessagePack

Use MessagePack for efficient binary JSON.

**Rejected because:**
- Not human-readable
- Marginal space savings
- Adds dependency
- Debugging harder

### Alternative 4: SQLite Database

Store checkpoints in SQLite database.

**Rejected for now because:**
- Adds deployment complexity
- Overkill for current use case
- File-based storage is simpler
- Can migrate later if needed

### Alternative 5: Compression (gzip)

Compress JSON files with gzip.

**Deferred because:**
- Adds complexity
- Files are small enough (< 100KB typically)
- Can add later if needed
- Debugging harder (must decompress first)

## Future Enhancements

### 1. Automatic Migration

**Goal:** Support checkpoint version upgrades

```python
def migrate_checkpoint(old_checkpoint: dict) -> dict:
    if old_checkpoint["version"] == "1.0.0":
        # Migrate to 1.1.0
        new_checkpoint = old_checkpoint.copy()
        new_checkpoint["version"] = "1.1.0"
        new_checkpoint["new_field"] = default_value
        return new_checkpoint
    # ... more migrations ...
```

### 2. Checkpoint Compression

**Goal:** Reduce storage for large checkpoints

```python
import gzip

def save_checkpoint_compressed(checkpoint: ExecutionCheckpoint) -> Path:
    path = self.checkpoint_dir / f"{timestamp}.json.gz"
    with gzip.open(path, "wt") as f:
        json.dump(checkpoint_data, f)
```

### 3. Checkpoint Encryption

**Goal:** Protect sensitive trading data

```python
from cryptography.fernet import Fernet

def save_checkpoint_encrypted(checkpoint: ExecutionCheckpoint, key: bytes) -> Path:
    data = json.dumps(checkpoint_data).encode()
    encrypted = Fernet(key).encrypt(data)
    path.write_bytes(encrypted)
```

### 4. Checkpoint Cleanup Policy

**Goal:** Automatically remove old checkpoints

```python
def cleanup_old_checkpoints(
    self,
    simulator_id: str,
    keep_last_n: int = 10,
):
    """Keep only the N most recent checkpoints."""
    checkpoints = self.list_checkpoints(simulator_id)
    for timestamp, path in checkpoints[keep_last_n:]:
        path.unlink()
```

### 5. Remote Storage

**Goal:** Store checkpoints in S3/cloud storage

```python
def save_checkpoint_remote(
    self,
    checkpoint: ExecutionCheckpoint,
    s3_bucket: str,
) -> str:
    """Upload checkpoint to S3."""
    data = serialize_checkpoint(checkpoint)
    s3_key = f"checkpoints/{checkpoint.simulator_id}/{timestamp}.json"
    s3_client.put_object(Bucket=s3_bucket, Key=s3_key, Body=json.dumps(data))
    return s3_key
```

## Testing Strategy

**Unit Tests:**
- Checkpoint creation from simulator
- Serialization roundtrip (Decimal, datetime preservation)
- Save/load from disk
- Version mismatch detection
- Restoration to identical state

**Integration Tests:**
- Full checkpoint/restore cycle
- Checkpoint with complex state (many orders, positions)
- Restoration continues execution correctly

**Test Coverage:** 18 tests in `test_checkpoint_recovery.py`

## Related

- **ADR-006:** Execution system architecture
- **E5-T4:** State checkpoint implementation plan
- **CHECKPOINT_VERSION:** `finbot/core/contracts/checkpoint.py`

## References

- Implementation plan: `docs/planning/e5-t4-state-checkpoint-implementation-plan.md`
- Checkpoint contract: `finbot/core/contracts/checkpoint.py`
- CheckpointManager: `finbot/services/execution/checkpoint_manager.py`
- Serialization: `finbot/services/execution/checkpoint_serialization.py`

---

**Last updated:** 2026-02-16
