# Implementation Plan v7.3.0: Priority 5 Reliability, Validation, and Security Automation

**Created:** 2026-02-19
**Updated:** 2026-02-19
**Status:** Complete (implemented 2026-02-19)
**Roadmap Anchors:** Priority 5 items 10, 22, 26, 28, 34, 44, 45

## Current State Summary

- Priority 6 adapter-first cycle is complete and ADR-011 remains **Defer**.
- Core logging already writes JSONL records, but operation-level audit semantics were not standardized.
- CI heavy workflow already runs docstring/security/license checks; Docker image vulnerability scanning was not yet wired.
- Data quality service exists (`finbot/services/data_quality`), but there was no consolidated operator guide.

## Scope for This Batch

1. Add structured audit logging utilities and propagate trace IDs through CLI.
2. Instrument CLI command entrypoints and the daily update pipeline for operation-level audit events.
3. Add Docker container security scanning in CI heavy workflow.
4. Add operational documentation for audit logging and data quality monitoring.
5. Expand integration and validation testing with deterministic fixtures.
6. Remove remaining mypy `ignore_errors` exclusions and restore full type-check pass.
7. Remove stale top-level directories after dependency verification.

## Deliverables and Validation

### D1: Audit logging contracts and helper
- `finbot/libs/logger/audit.py`
- Status: [x] Complete
- Validation:
  - Deterministic parameter hashing.
  - Sensitive key redaction.
  - Success/failure event emission includes `trace_id`, `operation`, `component`, `duration_ms`, `parameters_hash`, `error_type`.

### D2: CLI trace propagation + audit instrumentation
- `finbot/cli/main.py`
- `finbot/cli/commands/backtest.py`
- `finbot/cli/commands/simulate.py`
- `finbot/cli/commands/optimize.py`
- `finbot/cli/commands/update.py`
- `finbot/cli/commands/status.py`
- `finbot/cli/commands/dashboard.py`
- Validation:
  - `--trace-id` accepted at root command.
  - Commands emit audit events on success/failure.
- Status: [x] Complete

### D3: Pipeline audit instrumentation
- `scripts/update_daily.py`
- Validation:
  - Pipeline-level audit event for run.
  - Step-level audit events for retries and final failures.
- Status: [x] Complete

### D4: Docker security scanning
- `.github/workflows/ci-heavy.yml`
- Validation:
  - Workflow builds Docker image and runs Trivy scan for HIGH/CRITICAL findings.
- Status: [x] Complete

### D5: Operations documentation
- `docs/guides/audit-logging-guide.md`
- `docs/guides/data-quality-guide.md`
- Validation:
  - Includes command examples, expected outputs, and incident triage flow.
- Status: [x] Complete

### D6: Integration tests for CLI execution paths (Item 10)
- `tests/integration/test_cli_execution_paths.py`
- Validation:
  - deterministic integration command tests for simulate/backtest/optimize/status.
  - no external network dependency.
- Status: [x] Complete

### D7: Validation known-results test suite (Item 22)
- `tests/validation/test_known_results_validation.py`
- `docs/research/validation-baseline-2026-03.md`
- Validation:
  - reference-value checks for `get_cgr`, `get_drawdown`, and `fund_simulator`.
- Status: [x] Complete

### D8: Mypy exclusion cleanup + stale-dir cleanup (Items 34, 45)
- `pyproject.toml` (remove `ignore_errors` overrides)
- `finbot/utils/request_utils/rate_limiter.py` (compat module)
- `finbot/utils/request_utils/retry_strategy.py` (compat module)
- top-level `config/` and `constants/` directories removed
- Validation:
  - `DYNACONF_ENV=development uv run mypy finbot/` passes.
  - no runtime dependency on removed top-level directories.
- Status: [x] Complete

## Risks and Mitigations

1. **Risk:** Added audit calls could introduce log volume noise.
   - **Mitigation:** Keep payload compact and hash parameters rather than logging full raw input.
2. **Risk:** Docker scan can be noisy/flaky on dependency DB refresh.
   - **Mitigation:** Use CI-heavy tier only and `ignore-unfixed` to reduce churn.
3. **Risk:** Command wrappers may alter CLI behavior.
   - **Mitigation:** Run existing CLI test suite after instrumentation.

## Milestones

1. M1: Audit helper + CLI root trace propagation. [x]
2. M2: Command and pipeline instrumentation complete. [x]
3. M3: CI docker security scan added. [x]
4. M4: Documentation + tests updated and passing. [x]
5. M5: Integration/validation/mypy cleanup + stale-dir cleanup. [x]

## Verification Snapshot

- `uv run ruff check ...` on touched files: passed
- `DYNACONF_ENV=development uv run mypy finbot/`: passed
- `DYNACONF_ENV=development uv run pytest tests/unit/test_audit_logging.py tests/unit/test_cli.py tests/integration/test_cli_execution_paths.py tests/validation/test_known_results_validation.py -v`: passed

## Rollout and Rollback

### Rollout
- Land as additive changes; existing CLI command syntax stays compatible.
- Keep security scanning in heavy workflow (not core PR gate).

### Rollback
- Remove command-level audit wrappers if operational noise is unacceptable.
- Disable Docker scan job independently without touching core CI checks.
