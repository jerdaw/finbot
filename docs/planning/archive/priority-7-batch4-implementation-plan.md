# Priority 7 Batch 4 Implementation Plan
**Version:** 1.0.0
**Date:** 2026-02-18
**Status:** Complete

---

## Overview

This plan covers the final implementable work in Priority 7, plus two phases of mypy hardening (Phases 4 and 5) progressing through the backtesting services layer. It is organized into 4 sequential phases with clear goals and deliverables.

**New tests added:** 22 (health economics clinical scenarios)
**Mypy errors resolved:** ~66 Mode A errors (Phase 4: ~20, Phase 5: ~46)
**Completion impact:** P7 → 24/27 items (89%)

---

## Context

### State Before Batch 4
- P7: 23/27 items complete (85%)
- 1 code-implementable P7 item remained: **P7.21** (health economics clinical scenarios)
- 3 user-action-only items remaining (P7.8 video, P7.9 poster, P7.20 video tutorials)
- Mypy Phase 3 overrides applied for `finbot.core.*` and `finbot.services.execution.*`
- ~66 Mode A mypy errors in `finbot.services.backtesting.*`

### Health Economics Infrastructure (pre-existing)
- `finbot/services/health_economics/qaly_simulator.py`: `simulate_qalys()` → `dict`
- `finbot/services/health_economics/cost_effectiveness.py`: `cost_effectiveness_analysis()` → `dict`
- `finbot/services/health_economics/treatment_optimizer.py`: `optimize_treatment()` → `pd.DataFrame`
- 25 pre-existing passing tests in `tests/unit/test_health_economics.py`

---

## Phase 1: P7.21 — Health Economics Clinical Scenarios ✅

**Goal:** Implement 3 real-world clinical scenarios composing existing health economics modules into narrative, reproducible analyses. Add a 4th tab to the health economics dashboard page.

### Files Created

| File | Description |
|------|-------------|
| `finbot/services/health_economics/scenarios/__init__.py` | Package init; exports `ScenarioResult` |
| `finbot/services/health_economics/scenarios/models.py` | `ScenarioResult` frozen dataclass |
| `finbot/services/health_economics/scenarios/cancer_screening.py` | Mammography vs no screening (10-year horizon) |
| `finbot/services/health_economics/scenarios/hypertension.py` | ACE inhibitor vs lifestyle modification (5-year) |
| `finbot/services/health_economics/scenarios/vaccine.py` | Flu vaccine vs no vaccination, elderly ≥65 (1-year) |
| `tests/unit/test_health_economics_scenarios.py` | 22 new tests |

### Files Modified

| File | Change |
|------|--------|
| `finbot/services/health_economics/__init__.py` | Added 4 exports: 3 scenario functions + `ScenarioResult` |
| `finbot/dashboard/pages/6_health_economics.py` | Added 4th "Clinical Scenarios" tab |

### ScenarioResult Fields

```python
@dataclasses.dataclass(frozen=True)
class ScenarioResult:
    scenario_name: str
    description: str
    intervention_name: str
    comparator_name: str
    icer: float | None          # Cost per QALY gained; None if dominated
    nmb: float                  # Net monetary benefit at base WTP
    is_cost_effective: bool     # NMB > 0
    qaly_gain: float            # Mean QALYs gained vs comparator
    cost_difference: float      # Mean cost difference vs comparator
    n_simulations: int
    summary_stats: dict[str, float]
```

### Acceptance Criteria Met
- [x] All 22 new scenario tests pass
- [x] All 25 existing health economics tests still pass
- [x] `ruff check` clean on all new files
- [x] `mypy` 0 errors on all new files
- [x] Dashboard renders 4th tab

---

## Phase 2: Mypy Phase 4 — Backtesting Core Annotations ✅

**Goal:** Add full type annotations to backtesting core files and enforce `disallow_untyped_defs = true` for those modules via pyproject.toml override block.

### Files Annotated

| File | Key additions |
|------|---------------|
| `analyzers/cv_tracker.py` | `notify_cashvalue`, `get_analysis` return types |
| `analyzers/trade_tracker.py` | `bt.Order`, `bt.Trade` parameter types |
| `compute_stats.py` | Full parameter types; removed stale `# type: ignore` comments |
| `run_backtest.py` | `*args: Any, **kwargs: Any -> pd.DataFrame` |
| `rebalance_optimizer.py` | `**kwargs: Any -> pd.DataFrame` |
| `backtest_batch.py` | `_get_starts_from_steps` and `backtest_batch` signatures |
| `gen_rebal_proportions.py` | `gen_rebal_proportions` and `_parse_prods` signatures |
| `print_and_save_backtest.py` | `-> None` return type |
| `brokers/fixed_commission_scheme.py` | `_getcommission(size, price, pseudoexec) -> float` |
| `brokers/commission_schemes.py` | `_getcommission` signature |

### pyproject.toml Phase 4 Override Added

```toml
[[tool.mypy.overrides]]
module = [
    "finbot.services.backtesting.analyzers.*",
    "finbot.services.backtesting.compute_stats",
    "finbot.services.backtesting.run_backtest",
    "finbot.services.backtesting.rebalance_optimizer",
    "finbot.services.backtesting.backtest_batch",
    "finbot.services.backtesting.gen_rebal_proportions",
    "finbot.services.backtesting.print_and_save_backtest",
    "finbot.services.backtesting.brokers.*",
]
disallow_untyped_defs = true
```

### Acceptance Criteria Met
- [x] 0 mypy errors on all annotated files under Phase 4 override
- [x] All existing tests still pass
- [x] pyproject.toml override block added

---

## Phase 3: Mypy Phase 5 — Strategies, Costs, and Indicators ✅

**Goal:** Add full type annotations to 10 strategy files, 3 cost files, and 3 indicator files.

### Strategies Annotated

All strategy files received:
- `from __future__ import annotations`
- `from typing import Any`
- Typed `__init__` parameters and `-> None` return types
- `notify_order(self, order: bt.Order) -> None`
- `next(self) -> None`
- `self.order: Any = None` instance attribute annotation

Files: `rebalance.py`, `no_rebalance.py`, `sma_crossover.py`, `sma_crossover_double.py`, `sma_crossover_triple.py`, `macd_single.py`, `macd_dual.py`, `dip_buy_sma.py`, `dip_buy_stdev.py`, `dual_momentum.py`, `risk_parity.py`, `sma_rebal_mix.py`, `regime_adaptive.py`

### Costs Annotated

| File | Key change |
|------|-----------|
| `commission.py` | `**kwargs: object` |
| `spread.py` | `**kwargs: object` |
| `slippage.py` | `ZeroSlippage`/`FixedSlippage`: `**kwargs: object`; `SqrtSlippage`: `**kwargs: Any` (arithmetic on values) |

### Indicators Annotated

All indicator files (`returns.py`, `positive_returns.py`, `negative_returns.py`) received:
- `_plotlabel(self) -> list[int]`
- `__init__(self) -> None`

### pyproject.toml Phase 5 Override Added

```toml
[[tool.mypy.overrides]]
module = [
    "finbot.services.backtesting.strategies.*",
    "finbot.services.backtesting.costs.*",
    "finbot.services.backtesting.indicators.*",
]
disallow_untyped_defs = true
```

### Acceptance Criteria Met
- [x] 0 mypy errors on all annotated files under Phase 5 override
- [x] All existing strategy tests still pass
- [x] pyproject.toml Phase 5 override block added

---

## Phase 4: Documentation Reconciliation ✅

### Files Updated

| File | Change |
|------|--------|
| `docs/planning/roadmap.md` | P7.21 marked complete; P7 updated to 24/27 (89%); Batch 4 reference added |
| `CLAUDE.md` | P7 status to 24/27 (89%); P7.21 added to completed list; mypy Phase 4/5 status noted; plan reference updated |
| `docs/planning/priority-7-batch4-implementation-plan.md` | This document (created) |

---

## Implementation Notes

### `**kwargs: object` vs `**kwargs: Any`

The `object` type is correct when kwargs values are not used arithmetically (they're only passed through or ignored). Use `Any` when kwargs values are extracted and used in arithmetic operations — e.g., `SqrtSlippage.calculate_cost` extracts `daily_volume` and divides by it.

### Backtrader Type Stubs

Since `backtrader.*` has `ignore_missing_imports = true` in pyproject.toml, all types imported from it (`bt.Order`, `bt.feeds.PandasData`, `bt.Trade`) resolve to `Any`. The annotations satisfy `disallow_untyped_defs` without requiring actual stub packages.

### Quantstats Extension Methods

`quantstats` patches pandas `Series` with `.cagr()`, `.sharpe()`, etc. at import time. With `ignore_missing_imports = true` for quantstats, mypy sees all attribute accesses as `Any` — no `# type: ignore[attr-defined]` comments are needed. Previous comments of this kind were removed as they were flagged as unused ignores.

---

## Results

| Metric | Before Batch 4 | After Batch 4 |
|--------|---------------|---------------|
| P7 items complete | 23/27 (85%) | 24/27 (89%) |
| Test count | ~1084 | ~1106 |
| Mypy Mode A errors (backtesting) | ~66 | 0 |
| Mypy phases applied | 3 (core + execution) | 5 (+ backtesting core + strategies) |
