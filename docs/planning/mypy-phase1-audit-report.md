# Mypy Phase 1 Annotation Audit Report

**Date:** 2026-02-17
**Scope:** `finbot/` (370 source files)
**Purpose:** Establish a baseline of un-annotated functions and type errors under
progressively stricter mypy settings, and define an actionable phased roadmap for
future tightening — without modifying any production code in this phase.

---

## 1. Executive Summary

| Mode | Flags | Errors |
|------|-------|--------|
| **Current config** (pyproject.toml) | `disallow_untyped_calls = false`, `ignore_missing_imports = true` | **44** |
| **Mode A** — Unannotated functions | `--disallow-untyped-defs --disallow-incomplete-defs` | **355** |
| **Mode B** — Missing return types + generics | Mode A + `--disallow-any-generics --warn-return-any` | **484** |
| **Mode C** — Full strict | `--strict` | **631** |

Key finding: **311 additional errors** (Mode A − current) are purely from unannotated
function signatures. The majority live in `finbot/utils/` (43%) and `finbot/services/`
(29%), where annotation coverage is lowest. The `finbot/core/contracts/` package is
already well-annotated (only 4 Mode A errors) and is the natural starting point for
stricter enforcement.

---

## 2. Error Distribution by Package (Mode A — 355 errors)

| Package | Mode A Errors | % of Total | Priority |
|---------|--------------|-----------|----------|
| `finbot/utils/` | 154 | 43% | Medium — large surface, less critical path |
| `finbot/services/` | 102 | 29% | High — core backtest/simulation logic |
| `finbot/libs/` | 51 | 14% | High — infrastructure used by everything |
| `finbot/adapters/` | 12 | 3% | High — Nautilus adapter specifically |
| `finbot/dashboard/` | 10 | 3% | Low — UI layer |
| `finbot/constants/` | 9 | 3% | Medium — widely imported |
| `finbot/exceptions.py` | 5 | 1% | High — simple to fix |
| `finbot/core/` | 4 | 1% | **Low** — already well-annotated |
| `finbot/config/` | 4 | 1% | Medium |
| `finbot/cli/` | 4 | 1% | Low |

---

## 3. Top 25 Files by Error Count (Mode A)

These are the highest-impact files for phased annotation work:

| File | Errors | Category |
|------|--------|----------|
| `utils/data_collection_utils/scrapers/msci/_utils.py` | 24 | Data collection |
| `services/simulation/sim_specific_funds.py` | 18 | Simulation |
| `libs/api_manager/_utils/api_manager.py` | 12 | Infrastructure |
| `adapters/nautilus/nautilus_adapter.py` | 12 | Adapter layer |
| `utils/data_collection_utils/fred/correlate_fred_to_price.py` | 11 | Data collection |
| `utils/audit_log_utils.py` | 9 | Infrastructure |
| `services/backtesting/regime.py` | 9 | Backtesting |
| `libs/api_manager/_utils/api_resource_group.py` | 9 | Infrastructure |
| `libs/api_manager/_utils/api.py` | 9 | Infrastructure |
| `libs/logger/utils.py` | 7 | Infrastructure |
| `utils/request_utils/request_handler.py` | 6 | Infrastructure |
| `utils/data_science_utils/data_analysis/telltale_data_processor.py` | 6 | Analysis |
| `services/backtesting/analyzers/cv_tracker.py` | 6 | Backtesting |
| `libs/audit/audit_schema.py` | 5 | Infrastructure |
| `utils/function_utils/log_with_header_footer.py` | 5 | Utilities |
| `exceptions.py` | 5 | Core |
| `utils/data_collection_utils/bls/_bls_utils.py` | 5 | Data collection |
| `dashboard/utils/experiment_comparison.py` | 5 | Dashboard |
| `libs/audit/audit_logger.py` | 4 | Infrastructure |
| `utils/data_collection_utils/google_finance/_utils.py` | 4 | Data collection |
| `constants/host_constants.py` | 4 | Constants |
| `cli/validators.py` | 4 | CLI |
| `services/backtesting/analyzers/trade_tracker.py` | 4 | Backtesting |
| `dashboard/pages/8_walkforward.py` | 3 | Dashboard |
| `config/project_config.py` | 3 | Configuration |

**Strategy files** (all with 3 errors each — same pattern, annotatable in batch):
`sma_crossover.py`, `sma_crossover_double.py`, `sma_crossover_triple.py`,
`rebalance.py`, `no_rebalance.py`, `macd_single.py`, `macd_dual.py`,
`dual_momentum.py`, `dip_buy_stdev.py`, `dip_buy_sma.py` (30 total across 10 files)

**Cost model files** (3 errors each):
`costs/slippage.py`, `costs/commission.py` (6 total across 2 files)

---

## 4. Current Config Errors (44 errors — 13 files)

These errors exist under the current `pyproject.toml` settings and represent
the **immediate backlog** to clear before tightening anything:

| File | Approx. Errors | Error Type |
|------|---------------|------------|
| `utils/data_collection_utils/fred/correlate_fred_to_price.py` | 4 | Return-value incompatibility |
| Various (`services/`, `utils/`) | 40 | Scattered type incompatibilities |

These 44 errors are the minimum to resolve before any phased tightening begins.
However, they are non-blocking for production use (current CI passes with 0 blocking
mypy errors via `continue-on-error: true` in the CI config).

---

## 5. Well-Annotated Areas (Low Error Counts)

These packages already have strong annotation coverage and can have strict mode
enabled immediately with minimal work:

| Package | Mode A Errors | Notes |
|---------|--------------|-------|
| `finbot/core/contracts/` | ~0–2 | Frozen dataclasses, fully annotated |
| `finbot/core/contracts/models.py` | 0 | Fully annotated |
| `finbot/core/contracts/orders.py` | 0 | Fully annotated |
| `finbot/core/contracts/risk.py` | 0 | Fully annotated |
| `finbot/services/execution/` | ~0–2 | Well-annotated execution simulator |
| `finbot/services/backtesting/walkforward.py` | 0 | Fully annotated |
| `finbot/services/backtesting/hypothesis_testing.py` | 0 | Fully annotated (new) |
| `finbot/services/backtesting/walkforward_viz.py` | 0 | Fully annotated (new) |
| `finbot/services/backtesting/strategies/regime_adaptive.py` | 0 | Fully annotated (new) |

---

## 6. Effort Estimate

| Task | Estimated Functions | Estimated Days |
|------|---------------------|----------------|
| Resolve current 44 errors | ~15 fixes | 0.5–1 |
| Annotate `finbot/core/` (4 errors) | ~4 functions | 0.5 |
| Annotate `finbot/libs/` (51 errors) | ~51 functions | 1.5–2 |
| Annotate `finbot/services/backtesting/` (excl. strategies) | ~30 functions | 1–2 |
| Annotate backtesting strategies (10 files × 3 errors) | ~30 functions | 1 |
| Annotate `finbot/services/simulation/` | ~18 functions | 0.5–1 |
| Annotate `finbot/utils/` (154 errors) | ~154 functions | 4–6 |
| **Total** | **~280–310 functions** | **9–14 days** |

Annotation work is mechanical for most functions (add return type + arg types) and
can be partially automated with `monkeytype` or `pyright --writeexcludes`.

---

## 7. Phased Tightening Roadmap (Phases 3–7)

Each phase adds `[[tool.mypy.overrides]]` entries to `pyproject.toml` without
changing any source code. This is additive and fully reversible.

### Phase 3 (recommended next): `finbot/core/` + `finbot/services/execution/`

```toml
[[tool.mypy.overrides]]
module = ["finbot.core.*", "finbot.services.execution.*"]
disallow_untyped_defs = true
disallow_incomplete_defs = true
```

**Expected additional errors:** ~6 (minimal work, high-value packages)
**Rationale:** These are the most critical path modules (contracts, execution
simulator). They are already mostly annotated; this just enforces the standard.

### Phase 4: `finbot/services/backtesting/` (excluding strategies/)

```toml
[[tool.mypy.overrides]]
module = ["finbot.services.backtesting.*"]
disallow_untyped_defs = true
disallow_incomplete_defs = true
```

**Expected additional errors:** ~50 (mainly analyzers, regime.py, run_backtest.py)
**Rationale:** Backtesting is the core value-add layer. Type safety here prevents
subtle bugs in CAGR/Sharpe calculations.

### Phase 5: `finbot/services/backtesting/strategies/` + cost models

```toml
[[tool.mypy.overrides]]
module = [
    "finbot.services.backtesting.strategies.*",
    "finbot.services.backtesting.costs.*",
]
disallow_untyped_defs = true
```

**Expected additional errors:** ~36 (10 strategy files × 3 + cost models)
**Rationale:** Strategies are leaf modules; annotation effort is low and uniform.

### Phase 6: `finbot/libs/` + `finbot/constants/` + `finbot/config/`

```toml
[[tool.mypy.overrides]]
module = ["finbot.libs.*", "finbot.constants.*", "finbot.config.*"]
disallow_untyped_defs = true
```

**Expected additional errors:** ~68 (primarily api_manager, logger utilities)
**Rationale:** Infrastructure is called from everywhere — type errors here propagate
throughout the codebase.

### Phase 7: `finbot/utils/` (largest surface area)

```toml
[[tool.mypy.overrides]]
module = ["finbot.utils.*"]
disallow_untyped_defs = true
```

**Expected additional errors:** ~154 (data collection, finance utilities, scrapers)
**Rationale:** Utils are the outer boundary of the system (I/O, scraping, data
collection). These are the least type-sensitive and highest annotation effort.

---

## 8. Recommended CI Integration Path

**Current state:** `mypy` job runs with `continue-on-error: true`. This allows
annotation work to proceed without blocking CI.

**Proposed progression:**

1. After Phase 3: Switch `core.*` and `services.execution.*` to hard-fail in CI
2. After Phase 4: Add `services.backtesting.*` to hard-fail list
3. After Phase 5–7: Move to full hard-fail (`continue-on-error: false`)

This ensures that new code in critical modules is annotated while legacy utils
are upgraded incrementally.

---

## 9. Blockers and Risks

| Blocker | Affected Files | Mitigation |
|---------|---------------|------------|
| `backtrader` has no type stubs | All strategy files | Use `# type: ignore` or `py.typed` stub package |
| `quantstats` has minimal stubs | `compute_stats.py` | Use `type: ignore[attr-defined]` for return types |
| `pandas` generic types (`DataFrame[...]`) require pandas-stubs | All files using DataFrames | Already have `pandas-stubs` in dev deps; confirm version |
| `numpy` generics in Python 3.13 | Numpy operations | numpy ≥ 2.0 has better built-in typing; already on compatible version |

---

## 10. Summary and Recommendations

**Immediate actions (no code changes required):**
1. Fix the 44 current-config errors — these are real bugs/imprecisions, not just
   annotation issues
2. Enable Phase 3 overrides in `pyproject.toml` for `core.*` and `services.execution.*`

**This batch (Phase 5 of Batch 2):**
- Audit complete; no code changes required in this phase
- Report serves as the authoritative baseline for all future annotation work

**Target state after full annotation (Phases 3–7):**
- 0 mypy errors under `--disallow-untyped-defs --disallow-incomplete-defs`
- Full strict mode (`--strict`) errors reduced from 631 to < 100 (primarily
  backtrader/quantstats stubs)
- `continue-on-error: false` in CI for the full codebase

---

## 11. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-17 | Finbot team | Initial Phase 1 audit |

---

*This report was generated by running mypy against commit `HEAD` on 2026-02-17.
Re-run the audit commands below to update after code changes:*

```bash
# Current config errors
uv run mypy finbot/ 2>&1 | tail -3

# Mode A (unannotated functions)
uv run mypy finbot/ --disallow-untyped-defs --disallow-incomplete-defs --no-error-summary \
  2>&1 | grep "error:" | wc -l

# Per-module breakdown
uv run mypy finbot/ --disallow-untyped-defs --disallow-incomplete-defs --no-error-summary \
  2>&1 | grep "error:" | sed 's|finbot/||' | cut -d'/' -f1 | sort | uniq -c | sort -rn

# Full strict
uv run mypy finbot/ --strict --no-error-summary 2>&1 | grep "error:" | wc -l
```
