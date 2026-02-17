# State Checkpoint and Recovery Implementation Plan

**Epic:** E5-T4
**Backlog Item:** Backtesting Live-Readiness Epic E5 Task 4
**Size:** M (3-5 days)
**Status:** In Progress
**Date Started:** 2026-02-17

## Overview

Implement state checkpoint and recovery capabilities to enable:
- Resuming interrupted backtests/paper trading
- Reproducing exact state at any point in time
- Disaster recovery for live trading (future)
- Testing state transitions and edge cases

## What is State Checkpoint and Recovery?

**State Checkpoint:** Serializable snapshot of:
- Portfolio state (positions, cash, equity)
- Strategy state (internal variables, indicators)
- Order state (pending orders, fills)
- Timestamp and sequence number

**Recovery:** Ability to:
- Load a checkpoint and continue from that exact point
- Validate state consistency after load
- Handle checkpoint format migrations

## Use Cases

1. **Resume Interrupted Runs:**
   - Long backtest crashes midway
   - Load checkpoint and continue without recomputing

2. **Debugging:**
   - Checkpoint before a known failure point
   - Repeatedly test fix from same state

3. **Testing:**
   - Create synthetic checkpoints for edge cases
   - Test recovery logic in isolation

4. **Future Live Trading:**
   - Checkpoint state every N minutes
   - Recover from process crashes
   - Survive machine reboots

## Design Principles

1. **Immutability:** Checkpoints are immutable once created
2. **Content-Addressed:** Checkpoint ID is hash of content
3. **Versioned:** Schema version for forward compatibility
4. **Minimal:** Only serialize essential state, not derived values
5. **Validated:** Verify checkpoint integrity on load
6. **Backward Compatible:** Old code doesn't break with new checkpoints

## Implementation Phases

### Phase 1: Checkpoint Contract ✅
Create contracts for checkpoint data structure:
- StateCheckpoint model (portfolio, orders, strategy, timestamp)
- Checkpoint metadata (version, created_at, strategy_name)
- Serialization/deserialization logic

### Phase 2: Checkpoint Registry ✅
File-based registry for storing/loading checkpoints:
- Create checkpoint with content-addressable ID
- Load checkpoint by ID
- List checkpoints with filters (strategy, date range)
- Delete old checkpoints

### Phase 3: State Extraction ✅
Extract checkpointable state from running system:
- Portfolio state extraction (positions, cash, value)
- Order state extraction (pending orders, recent fills)
- Strategy state extraction (indicators, internal vars)
- Timestamp and sequence tracking

### Phase 4: State Restoration ✅
Restore state from checkpoint:
- Validate checkpoint integrity
- Restore portfolio state
- Restore order state
- Restore strategy state (if supported)
- Verify state consistency

### Phase 5: Integration with BacktraderAdapter
Add checkpoint support to adapter:
- save_checkpoint() method
- load_checkpoint() method
- Auto-checkpoint at intervals (optional)
- Integration tests

### Phase 6: Testing and Documentation
- Unit tests for checkpoint/restore
- Integration tests for resume scenarios
- User guide with examples
- API documentation

## Acceptance Criteria

- [x] StateCheckpoint contract defined
- [x] Checkpoint registry with CRUD operations
- [x] Can create checkpoint from portfolio/order state
- [x] Can restore state from checkpoint
- [x] Checkpoints are content-addressed (same state → same ID)
- [x] Checkpoint integrity validated on load
- [ ] BacktraderAdapter integration (deferred for parity)
- [x] Unit tests cover core functionality
- [ ] Integration tests verify resume scenarios (deferred)
- [ ] User guide with examples (deferred)

## Implementation Plan

### Step 1: Contract Definition
Create `finbot/core/contracts/checkpoint.py`:
- StateCheckpoint dataclass
  - checkpoint_id: str (SHA256 of content)
  - version: str
  - created_at: datetime
  - strategy_name: str
  - timestamp: datetime (point in backtest/live time)
  - portfolio_state: dict (cash, positions, equity)
  - order_state: dict (pending orders, recent fills)
  - strategy_state: dict | None (custom strategy data)
  - metadata: dict (custom key-value pairs)

### Step 2: Registry Implementation
Create `finbot/core/contracts/checkpoint_registry.py`:
- CheckpointRegistry class
  - create_checkpoint(state, strategy_name, ...)
  - load_checkpoint(checkpoint_id)
  - list_checkpoints(strategy_name?, start_date?, end_date?)
  - delete_checkpoint(checkpoint_id)
  - cleanup_old_checkpoints(days_to_keep)

Storage format: JSON files in data/checkpoints/{year}/{month}/

### Step 3: State Extraction Helpers
Create helper functions for state extraction:
- extract_portfolio_state(cerebro) → dict
- extract_order_state(cerebro) → dict
- extract_strategy_state(strategy) → dict | None

### Step 4: State Restoration Helpers
Create helper functions for state restoration:
- validate_checkpoint(checkpoint) → bool
- restore_portfolio_state(cerebro, state)
- restore_order_state(cerebro, state)
- restore_strategy_state(strategy, state)

### Step 5: Testing
Unit tests:
- Checkpoint creation and hashing
- Registry CRUD operations
- State extraction from minimal portfolio
- State restoration validation
- Checkpoint integrity checks

Integration tests (deferred to avoid parity impact):
- Full checkpoint/resume cycle
- Resume from mid-backtest
- Handle incompatible checkpoints gracefully

## Estimated Time

- Phase 1: Contract definition - 2 hours
- Phase 2: Registry implementation - 3 hours
- Phase 3: State extraction - 2 hours
- Phase 4: State restoration - 2 hours
- Phase 5: Adapter integration - 3 hours (DEFERRED)
- Phase 6: Testing and docs - 4 hours (partial deferred)

**Total:** ~16 hours (2 days) for core functionality

## Deferred Work

To maintain 100% parity on golden strategies:
- BacktraderAdapter integration (Phase 5)
- Full integration tests with adapter (Phase 6)
- User guide with resume examples (Phase 6)

These can be added later without affecting existing functionality.

## File Plan

### New Files:
- `finbot/core/contracts/checkpoint.py` (models)
- `finbot/core/contracts/checkpoint_registry.py` (storage)
- `tests/unit/test_checkpoint.py` (unit tests)

### Modified Files:
- `finbot/core/contracts/__init__.py` (exports)
- `docs/planning/backtesting-live-readiness-backlog.md` (mark E5-T4 complete)

## Success Metrics

- All unit tests pass
- Checkpoint can be created from minimal state
- Checkpoint can be loaded and validated
- Content-addressed IDs work correctly
- No parity regression on golden strategies
- Documentation explains checkpoint/recovery workflow

## Resources

- Pickle security concerns: https://docs.python.org/3/library/pickle.html#module-pickle
- Content-addressed storage: Git-like hashing approach
- State machine patterns for validation

## Notes

- Use JSON for checkpoints (not pickle) for security and compatibility
- Checkpoint IDs are SHA256 of canonical JSON (sorted keys)
- Registry is file-based for simplicity (no database dependency)
- Strategy state is optional (strategies may not be serializable)
- Adapter integration deferred to avoid breaking parity tests
