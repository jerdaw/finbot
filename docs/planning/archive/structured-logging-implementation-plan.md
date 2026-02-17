# Structured Logging for Audit Trails Implementation Plan

**Created:** 2026-02-17
**Priority:** Priority 5, Item 26
**Category:** 5.5 Ethics, Privacy & Security
**Status:** ✅ COMPLETE (2026-02-17)
**CanMEDS:** Professional (governance, accountability)

## Overview

Enhance the existing queue-based logging system to ensure all critical operations are logged with structured JSON format, enabling audit trails for debugging, compliance, and accountability.

## Background

**Current State:**
- Queue-based async logging implemented (`finbot/libs/logger/`)
- Dual output: colored console + JSON file
- Rotating file handlers (5MB, 3 backups)
- Basic structured logging already present

**Goal:**
- Ensure ALL critical operations have structured audit logs
- Standardize audit log format
- Document audit trail usage
- Add utilities for querying audit logs

## Task Breakdown

### Task 1: Audit Current Logging Coverage

**What:** Identify gaps in logging coverage for critical operations

**Operations to audit:**
1. Backtesting operations (strategy execution, results)
2. Simulation operations (fund simulation, Monte Carlo)
3. Data collection operations (API calls, data updates)
4. Optimization operations (DCA, rebalancing)
5. CLI operations (command execution)
6. Health economics operations (QALY simulation, CEA)
7. Execution simulator operations (orders, fills, risk events)

**Output:** List of operations missing structured logging

### Task 2: Define Audit Log Schema

**What:** Create standardized schema for audit logs

**Schema fields:**
```python
{
    "timestamp": "ISO 8601",
    "level": "INFO|WARNING|ERROR",
    "operation": "operation_name",
    "operation_type": "backtest|simulation|data_collection|optimization|cli|health_economics|execution",
    "parameters": {
        # Operation-specific parameters
    },
    "result": {
        # Operation outcome
        "status": "success|failure|partial",
        "metrics": {},
        "errors": []
    },
    "duration_ms": 0,
    "user": "system",  # For future multi-user support
    "context": {
        # Additional context (env, version, etc.)
    }
}
```

**Output:** Schema definition module

### Task 3: Create Audit Logging Utilities

**What:** Build helper functions for structured audit logging

**Components:**
1. `AuditLogger` class wrapping existing logger
2. Context managers for operation tracking
3. Decorators for automatic operation logging
4. Schema validation

**File:** `finbot/libs/logger/audit_logger.py`

**Example usage:**
```python
from finbot.libs.logger.audit_logger import audit_operation

@audit_operation(operation_type="backtest")
def run_backtest(...):
    # Function code
    pass
```

### Task 4: Add Audit Logging to Critical Operations

**What:** Integrate audit logging into existing operations

**Priority operations:**
1. **Backtesting** (`finbot/services/backtesting/`)
   - `backtest_runner.py`: Log strategy runs
   - `backtest_batch.py`: Log batch executions
   - `rebalance_optimizer.py`: Log optimization runs

2. **Simulation** (`finbot/services/simulation/`)
   - `fund_simulator.py`: Log fund simulations
   - `monte_carlo_simulator.py`: Log MC runs
   - `bond_ladder_simulator.py`: Log bond ladder construction

3. **Data Collection** (`finbot/utils/data_collection_utils/`)
   - `yfinance/`: Log price history fetches
   - `fred/`: Log FRED data fetches
   - API calls with rate limiting

4. **CLI** (`finbot/cli/main.py`)
   - Log all command executions

5. **Execution Simulator** (`finbot/services/execution/`)
   - Log order submissions, fills, risk events
   - Already has structured logging (verify completeness)

### Task 5: Create Audit Log Query Utilities

**What:** Build tools for querying and analyzing audit logs

**Components:**
1. `audit_log_reader.py`: Read and parse JSON logs
2. Query by operation type, time range, status
3. Generate summary reports
4. Export to CSV/parquet for analysis

**File:** `finbot/utils/audit_log_utils.py`

**Example usage:**
```python
from finbot.utils.audit_log_utils import AuditLogReader

reader = AuditLogReader()
failed_backtests = reader.query(
    operation_type="backtest",
    status="failure",
    start_time="2024-01-01",
    end_time="2024-12-31"
)
```

### Task 6: Documentation

**What:** Document audit trail usage and best practices

**Documents:**
1. `docs/guides/audit-trails.md` - User guide
   - What is logged
   - How to query logs
   - Example use cases
   - Privacy/security considerations

2. Update `CLAUDE.md` - Add audit logging section
3. Update `README.md` - Mention audit capability

### Task 7: Testing

**What:** Comprehensive tests for audit logging

**Test files:**
1. `tests/unit/test_audit_logger.py`
   - Schema validation
   - Context managers
   - Decorators
   - Error handling

2. `tests/unit/test_audit_log_utils.py`
   - Log reading
   - Querying
   - Report generation

3. `tests/integration/test_audit_trails.py`
   - End-to-end operation tracking
   - Verify critical operations are logged

## Deliverables

### New Files Created

1. `finbot/libs/logger/audit_logger.py` - Audit logging utilities
2. `finbot/libs/logger/audit_schema.py` - Schema definitions
3. `finbot/utils/audit_log_utils.py` - Query utilities
4. `docs/guides/audit-trails.md` - User guide
5. `tests/unit/test_audit_logger.py` - Unit tests
6. `tests/unit/test_audit_log_utils.py` - Utility tests
7. `tests/integration/test_audit_trails.py` - Integration tests

### Files Modified

1. `finbot/services/backtesting/backtest_runner.py` - Add audit logging
2. `finbot/services/backtesting/backtest_batch.py` - Add audit logging
3. `finbot/services/simulation/fund_simulator.py` - Add audit logging
4. `finbot/cli/main.py` - Add command audit logging
5. `CLAUDE.md` - Document audit logging
6. `README.md` - Mention audit capability
7. Multiple other service files as needed

## Acceptance Criteria

- [ ] Audit logger utilities created and tested
- [ ] All critical operations log structured audit events
- [ ] Audit log schema documented
- [ ] Query utilities implemented and tested
- [ ] User guide created
- [ ] Tests pass (unit + integration)
- [ ] Documentation updated

## Timeline

**Estimated Effort:** 6-8 hours (1 day)
**Target Completion:** 2026-02-17

## Implementation Strategy

**Phase 1: Foundation** (2 hours)
- Create audit logger utilities
- Define schema
- Write unit tests

**Phase 2: Integration** (3 hours)
- Add logging to critical operations
- Test integration

**Phase 3: Utilities & Docs** (2 hours)
- Create query utilities
- Write documentation
- Integration tests

**Phase 4: Verification** (1 hour)
- Run all tests
- Verify coverage
- Update roadmap

## Success Metrics

- All critical operations have audit logs
- Audit logs queryable and analyzable
- Documentation clear and comprehensive
- Tests pass
- Roadmap updated with completion checkmark

## Notes

- Build on existing logger infrastructure
- Don't break existing logging behavior
- Keep performance impact minimal (async logging already implemented)
- Consider privacy: don't log sensitive data (API keys, credentials)
- Future: Could add audit log rotation policy, retention, analysis dashboard
