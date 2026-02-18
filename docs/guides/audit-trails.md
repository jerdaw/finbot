# Audit Trails Guide

**Last Updated:** 2026-02-17

## Overview

Finbot provides comprehensive audit logging for all critical operations, enabling debugging, compliance tracking, and operational accountability. All audit logs are stored in structured JSON format for easy querying and analysis.

## What Is Logged

Finbot automatically logs the following information for audited operations:

- **Operation name and type** (backtest, simulation, data collection, etc.)
- **Timestamp** (ISO 8601 format with timezone)
- **Status** (success, failure, partial, in_progress)
- **Parameters** (input parameters, sanitized for sensitive data)
- **Results** (operation outcomes and key metrics)
- **Duration** (operation execution time in milliseconds)
- **Errors** (error messages if operation failed)
- **Context** (additional metadata like environment, version)

## Audited Operations

The following operations are automatically logged:

### Backtesting
- Strategy backtests (`BacktestRunner.run_backtest()`)
- Batch backtests
- Strategy optimization runs

### Simulation
- Fund simulations (`fund_simulator()`)
- Bond ladder simulations
- Monte Carlo simulations
- Index simulations

### Data Collection
- API calls (with rate limiting)
- Data fetch operations
- Cache hits/misses

### Optimization
- DCA optimization runs
- Rebalance optimization

### Health Economics
- QALY simulations
- Cost-effectiveness analyses
- Treatment optimizations

### Execution
- Order submissions
- Order fills
- Risk control events

## Log File Locations

Audit logs are written to:

```
finbot/data/logs/finbot.log.jsonl
```

This is a JSON Lines file where each line is a complete JSON object representing one log entry.

**Retention:** Rotating file handler with 5MB max size, 3 backups (15MB total)

## Querying Audit Logs

### Basic Usage

```python
from finbot.utils.audit_log_utils import AuditLogReader, AuditLogQuery

# Create reader
reader = AuditLogReader()

# Read all audit logs
all_logs = reader.read_all()

# Query with filters
query = AuditLogQuery(
    operation_type="backtest",
    status="failure",
    start_time="2024-01-01"
)
failed_backtests = reader.query(query)

# Alternative: pass filters as kwargs
failed_backtests = reader.query(
    operation_type="backtest",
    status="failure",
    start_time="2024-01-01"
)
```

### Query Options

Available filter parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `operation_type` | str | Filter by operation type (backtest, simulation, etc.) |
| `operation` | str | Filter by specific operation name |
| `status` | str | Filter by status (success, failure, partial) |
| `start_time` | str/datetime | Filter by start time (ISO format) |
| `end_time` | str/datetime | Filter by end time (ISO format) |
| `user` | str | Filter by user (default: "system") |
| `min_duration_ms` | float | Minimum duration in milliseconds |
| `max_duration_ms` | float | Maximum duration in milliseconds |
| `has_errors` | bool | Filter to entries with errors only |

### Generate Summary Statistics

```python
from finbot.utils.audit_log_utils import AuditLogReader

reader = AuditLogReader()

# Generate summary for all backtests
summary = reader.generate_summary(operation_type="backtest")

print(f"Total operations: {summary.total_operations}")
print(f"Success rate: {summary.successful_operations / summary.total_operations:.1%}")
print(f"Average duration: {summary.avg_duration_ms:.0f}ms")
print(f"Operations by type: {summary.operations_by_type}")
print(f"Error messages: {summary.error_messages}")
```

### Convert to DataFrame for Analysis

```python
import pandas as pd
from finbot.utils.audit_log_utils import AuditLogReader

reader = AuditLogReader()

# Convert to DataFrame
df = reader.to_dataframe()

# Analyze by operation type
df.groupby("operation_type")["duration_ms"].agg(["mean", "median", "max"])

# Success rate by operation
df.groupby("operation_type")["status"].value_counts(normalize=True)

# Time series of operations
df.set_index("timestamp").resample("1D")["operation"].count().plot()
```

### Export to Files

```python
from finbot.utils.audit_log_utils import AuditLogReader

reader = AuditLogReader()

# Export to CSV
reader.export_to_csv("failed_operations.csv", status="failure")

# Export to parquet
reader.export_to_parquet("audit_logs.parquet")
```

## Adding Audit Logging to Your Code

### Method 1: Using the Decorator (Recommended)

```python
from finbot.libs.audit.audit_logger import audit_operation
from finbot.libs.audit.audit_schema import OperationType

@audit_operation(operation_type=OperationType.SIMULATION)
def my_simulation_function(param1: str, param2: int):
    # Your code here
    result = do_simulation()
    return result

# Function calls are automatically logged
my_simulation_function("test", 42)
```

### Method 2: Using the Context Manager

```python
from finbot.config import logger
from finbot.libs.audit.audit_logger import AuditLogger
from finbot.libs.audit.audit_schema import OperationType

def my_operation():
    audit = AuditLogger(logger)

    with audit.log_operation(
        operation="my_custom_operation",
        operation_type=OperationType.DATA_COLLECTION,
        parameters={"source": "api", "symbol": "SPY"}
    ) as entry:
        # Perform operation
        data = fetch_data()

        # Update result
        entry.update_result({"rows": len(data), "columns": data.shape[1]})

        return data
```

### Method 3: Manual Event Logging

```python
from finbot.config import logger
from finbot.libs.audit.audit_logger import AuditLogger
from finbot.libs.audit.audit_schema import OperationType, OperationStatus

def quick_operation():
    audit = AuditLogger(logger)

    # Log single event
    audit.log_event(
        operation="cache_hit",
        operation_type=OperationType.DATA_COLLECTION,
        status=OperationStatus.SUCCESS,
        parameters={"key": "SPY_2024"},
        result={"cached": True, "age_hours": 2}
    )
```

## Operation Types

Available operation types (from `OperationType` enum):

- `BACKTEST` - Backtesting operations
- `SIMULATION` - Simulation operations
- `DATA_COLLECTION` - Data fetching and storage
- `OPTIMIZATION` - Portfolio optimization
- `CLI` - Command-line interface operations
- `HEALTH_ECONOMICS` - Health economics analyses
- `EXECUTION` - Order execution and trading
- `EXPERIMENT` - Experiment tracking

## Privacy and Security

### Automatic Sanitization

Sensitive information is automatically redacted from logs. The following parameter keys are masked:

- `api_key`
- `password`
- `secret`
- `token`
- `credential`
- `auth`

**Example:**
```python
# This parameter
{"api_key": "sk-12345", "symbol": "SPY"}

# Becomes
{"api_key": "***REDACTED***", "symbol": "SPY"}
```

### Best Practices

1. **Don't log sensitive data manually** - Avoid adding sensitive data to result dictionaries
2. **Use operation_type correctly** - Helps with querying and analysis
3. **Keep parameters simple** - Log simple types (str, int, float) when possible
4. **Update results incrementally** - Use `entry.update_result()` during long operations
5. **Log errors** - Always include error information on failures

## Example Use Cases

### Debug a Failed Backtest

```python
from finbot.utils.audit_log_utils import AuditLogReader

reader = AuditLogReader()

# Find failed backtests from today
import datetime
today = datetime.date.today().isoformat()

failed = reader.query(
    operation_type="backtest",
    status="failure",
    start_time=today
)

# Print error details
for entry in failed:
    print(f"Operation: {entry['operation']}")
    print(f"Parameters: {entry['parameters']}")
    print(f"Errors: {entry['errors']}")
    print("-" * 80)
```

### Identify Slow Operations

```python
from finbot.utils.audit_log_utils import AuditLogReader

reader = AuditLogReader()

# Find operations taking > 10 seconds
slow_ops = reader.query(min_duration_ms=10000)

# Convert to DataFrame and analyze
import pandas as pd
df = reader.to_dataframe(min_duration_ms=10000)
print(df.nlargest(10, "duration_ms")[["operation", "duration_ms", "status"]])
```

### Monitor Success Rates

```python
from finbot.utils.audit_log_utils import AuditLogReader

reader = AuditLogReader()

# Get summary by operation type
for op_type in ["backtest", "simulation", "data_collection"]:
    summary = reader.generate_summary(operation_type=op_type)
    success_rate = summary.successful_operations / summary.total_operations
    print(f"{op_type}: {success_rate:.1%} success rate ({summary.total_operations} operations)")
```

### Track API Usage

```python
from finbot.utils.audit_log_utils import AuditLogReader
import pandas as pd

reader = AuditLogReader()

# Get all data collection operations
df = reader.to_dataframe(operation_type="data_collection")

# Count by date
daily_calls = df.set_index("timestamp").resample("1D")["operation"].count()
print(f"API calls per day:")
print(daily_calls)

# Check for rate limit errors
errors = reader.query(operation_type="data_collection", has_errors=True)
print(f"Errors: {len(errors)}")
```

## Audit Log Schema

Each audit log entry contains:

```json
{
  "timestamp": "2024-02-17T10:30:45.123456-05:00",
  "level": "INFO",
  "name": "finbot",
  "message": "Completed backtest operation: run_backtest (1234.56ms) - success",
  "audit_log": true,
  "operation": "run_backtest",
  "operation_type": "backtest",
  "audit_timestamp": "2024-02-17T10:30:43.888900-05:00",
  "status": "success",
  "parameters": {
    "symbols": ["SPY", "TLT"],
    "strategy": "Rebalance",
    "initial_cash": 100000
  },
  "result": {
    "total_return_pct": 15.4,
    "sharpe_ratio": 1.2,
    "max_drawdown_pct": -8.5,
    "num_trades": 24
  },
  "duration_ms": 1234.56,
  "user": "system",
  "context": {},
  "errors": []
}
```

## Compliance and Retention

### Log Retention Policy

- **Retention:** Logs are retained for the duration of 3 backup files (15MB total)
- **Rotation:** Files rotate at 5MB
- **Archival:** Old logs are automatically deleted by the rotating file handler

### Compliance Considerations

Audit logs can support:

- **Regulatory compliance** - Track all operations for audit purposes
- **Debugging** - Trace operation history and failures
- **Performance monitoring** - Identify bottlenecks and slow operations
- **Security** - Track API usage and detect anomalies
- **Accountability** - Record who did what and when

## Advanced Usage

### Custom Operation Types

While the predefined operation types cover most use cases, you can pass any string to `operation_type` if needed:

```python
with audit.log_operation(
    operation="custom_analysis",
    operation_type="analytics",  # Custom type
    parameters={"dataset": "market_data"}
):
    # Your code
    pass
```

### Multi-User Tracking

For future multi-user support, set the `user` parameter:

```python
with audit.log_operation(
    operation="run_backtest",
    operation_type=OperationType.BACKTEST,
    user="analyst@company.com"
):
    # Your code
    pass
```

### Progressive Result Updates

For long-running operations, update results incrementally:

```python
with audit.log_operation(
    operation="batch_simulation",
    operation_type=OperationType.SIMULATION
) as entry:
    for i, item in enumerate(items):
        process(item)
        # Update progress
        entry.update_result({"processed": i+1, "total": len(items)})
```

## Troubleshooting

### Log File Not Found

**Error:** `FileNotFoundError: Log file not found: /path/to/finbot.log.jsonl`

**Solution:** Ensure the application has run at least once to create log files. Check that `LOGS_DIR` exists.

### Parsing Errors

**Issue:** Some log entries fail to parse

**Solution:** The reader automatically skips malformed JSON lines. To see which lines failed, check the raw file:

```bash
cat finbot/data/logs/finbot.log.jsonl | jq . > /dev/null
```

### Large Log Files

**Issue:** Query operations are slow with large log files

**Solution:**
1. Use specific filters to reduce the result set
2. Export to parquet for faster analysis
3. Archive old logs periodically

## See Also

- [Data Quality Guide](data-quality-guide.md) - Data freshness monitoring
- [Backtesting Guide](../user-guide/backtesting.md) - Backtesting operations
- [Health Economics Tutorial](../user-guide/health-economics-tutorial.md) - Health economics operations

## References

- **Code:** `finbot/libs/audit/audit_logger.py`, `finbot/utils/audit_log_utils.py`
- **Tests:** `tests/unit/test_audit_logger.py`, `tests/integration/test_audit_trails.py`
- **Schema:** `finbot/libs/audit/audit_schema.py`
