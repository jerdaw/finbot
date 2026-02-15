# Backtesting Contract Schema Versioning

**Created:** 2026-02-14
**Status:** Active
**Scope:** `finbot/core/contracts/` payloads and result contracts

## Purpose

Define a stable compatibility policy for backtesting contract payloads so historical results remain readable as the platform evolves.

## Version Model

- Contract schema version: `CONTRACT_SCHEMA_VERSION` in `finbot/core/contracts/versioning.py`
- Result schema version: `BACKTEST_RESULT_SCHEMA_VERSION` in `finbot/core/contracts/versioning.py`
- Current major version: `1`

Compatibility rule:

- Payloads are considered compatible when major versions match.
- Minor/patch updates are backward-compatible by default.
- Major changes require migration functions and an ADR update.

## Required Result Payload Fields (v1)

- `schema_version`
- `metadata`:
  - `run_id`
  - `engine_name`
  - `engine_version`
  - `strategy_name`
  - `created_at`
  - `config_hash`
  - `data_snapshot_id`
  - optional `random_seed`
- `metrics` (canonical keys):
  - `starting_value`
  - `ending_value`
  - `roi`
  - `cagr`
  - `sharpe`
  - `max_drawdown`
  - `mean_cash_utilization`
- optional `assumptions`, `artifacts`, `warnings`

## Legacy Migration Policy

Legacy payloads without `schema_version` are treated as pre-1.0 and migrated through:

- `migrate_backtest_result_payload()` in `finbot/core/contracts/versioning.py`

Current built-in migration path:

- `0.x` legacy payloads -> `1.0.0` payload shape

The migration logic:

- normalizes metadata fields,
- maps legacy stats keys (`Starting Value`, `CAGR`, etc.) to canonical metric keys,
- sets `schema_version` to target version.

## Operational Guidance

- Serialization path:
  - `backtest_result_to_payload()` in `finbot/core/contracts/serialization.py`
- Deserialization path (with migration):
  - `backtest_result_from_payload()` in `finbot/core/contracts/serialization.py`
- BacktestRunner stats mapping:
  - `build_backtest_run_result_from_stats()` in `finbot/core/contracts/serialization.py`

## Change Management

When changing schema fields:

1. Update `finbot/core/contracts/models.py` and schema helpers.
2. Add migration support in `versioning.py`.
3. Add/extend tests in `tests/unit/test_core_contracts.py`.
4. Update this guideline and relevant ADRs.
