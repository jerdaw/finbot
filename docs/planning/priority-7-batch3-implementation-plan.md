# Priority 7 — Batch 3 Implementation Plan

**Version:** 1.0
**Created:** 2026-02-18
**Status:** In Progress
**Scope:** 4 phases — mypy hardening, performance test fix, multi-objective optimization, doc cleanup
**Parent plan:** `docs/planning/priority-7-batch2-implementation-plan.md` (v1.2)

---

## 1. Executive Summary

Batch 2 closed 5 major features (P7.15/16/22/23/1). Batch 3 addresses the remaining
**code-implementable** items: a known runtime bug, type-safety enforcement, test
reliability, and the one large deferred feature (P7.17 multi-objective optimization).

| Phase | Item | Size | Priority |
|-------|------|------|----------|
| 1 | Fix 44 mypy errors + mypy_path + Phase 3 overrides | S | Critical |
| 2 | Harden performance regression test | S | High |
| 3 | Multi-objective Pareto optimizer (P7.17) | L | High |
| 4 | Documentation reconciliation | XS | Low |

---

## 2. Phase 1 — Mypy Hardening

**Goal:** Eliminate all 44 current-config mypy errors (including a real runtime bug),
fix a hardcoded local path that breaks CI on non-WSL machines, and enable stricter
enforcement on the already-annotated `core.*` and `services.execution.*` packages.

**Deliverables:**
- `pyproject.toml` — fix `mypy_path`, add Phase 3 overrides
- 12 source files patched (44 errors → 0)
- No regressions in existing tests

### 2.1 Files to fix (44 errors across 13 files)

| File | Errors | Nature |
|------|--------|--------|
| `utils/data_collection_utils/fred/correlate_fred_to_price.py` | 10 | numpy/pandas type narrowing |
| `services/backtesting/regime.py` | 8 | pandas `Hashable` index issue |
| `dashboard/utils/experiment_comparison.py` | 4 | `any` used as type, unreachable |
| `cli/validators.py` | 4 | Click callback returns `None` (should be `str \| None`) |
| `dashboard/pages/8_walkforward.py` | 3 | missing module stub, assignment type |
| `services/execution/execution_simulator.py` | 2 | re-def + `datetime.timedelta` **runtime bug** |
| `libs/audit/audit_schema.py` | 2 | assignment type mismatch |
| `libs/api_manager/_resource_groups/api_resource_groups.py` | 2 | limits library arg type |
| `utils/audit_log_utils.py` | 2 | `None` used as dict key |
| `core/contracts/versioning.py` | 2 | `in` operator on `Any | None` |
| `core/contracts/serialization.py` | 1 | assignment type mismatch |
| `dashboard/pages/7_experiments.py` | 1 | Series not callable |
| `adapters/nautilus/nautilus_adapter.py` | 1 | `Hashable` attr access |

**Critical fix:** `execution_simulator.py:356` — `datetime.timedelta` is used but
the module is imported as `import datetime`, not `from datetime import timedelta`.
This will raise `NameError` at runtime on that code path.

### 2.2 pyproject.toml changes

**Fix hardcoded path:**
```toml
# Before (breaks CI on any non-WSL machine):
mypy_path = "/home/jer/localsync/finbot"

# After (resolved via editable install):
# (remove the mypy_path line entirely)
```

**Add Phase 3 overrides:**
```toml
[[tool.mypy.overrides]]
module = ["finbot.core.*", "finbot.services.execution.*"]
disallow_untyped_defs = true
disallow_incomplete_defs = true
```

### 2.3 Validation

```bash
uv run mypy finbot/ 2>&1 | tail -3   # Should show 0 errors
uv run pytest tests/ -q              # No regressions
```

---

## 3. Phase 2 — Performance Test Hardening

**Goal:** Eliminate the timing-flakiness that caused a spurious failure in Batch 2's
final test run. The test now has a ~24% coefficient of variation but a 20% threshold —
statistically guaranteed to fail periodically even with no regressions.

**Deliverables:**
- `tests/performance/test_performance_regression.py` — add `@pytest.mark.slow`
- `tests/performance/benchmark_runner.py` — increase n_runs, switch to median
- `pyproject.toml` — add `slow` to markers (already there), exclude from default run

### 3.1 Changes

**`benchmark_runner.py`:**
- Increase `n_runs` from 5 → 10 for `fund_simulator`, 3 → 7 for `backtest_adapter`
- Use **median** instead of mean for comparison (more robust to outliers)
- Add `duration_median_ms` field alongside existing `duration_mean_ms` in baseline

**`test_performance_regression.py`:**
- Add `@pytest.mark.slow` decorator
- Compare against median (more robust)
- Widen threshold to 30% (still catches real regressions; eliminates noise failures)
- Add explicit check: if `backtest_adapter` benchmark was skipped, skip the test
  rather than vacuously passing

**`pyproject.toml` addopts:**
```toml
addopts = "-v --tb=short -m 'not slow'"
```
This excludes slow tests from default `pytest` runs; CI can run with `-m slow` explicitly.

### 3.2 Validation

```bash
uv run pytest tests/performance/ -v -m slow  # Must pass
uv run pytest tests/ -q                       # No regressions; faster (skips slow tests)
```

---

## 4. Phase 3 — Multi-Objective Pareto Optimizer (P7.17)

**Goal:** Implement a Pareto-frontier optimizer for portfolio strategies — the last
major deferred technical feature. Given `pyportfolioopt` is already in deps, this
builds on the existing `dca_optimizer.py` pattern and the existing `BacktestRunResult`
contracts.

**Deliverables:**
- `finbot/services/optimization/pareto_optimizer.py` — core optimizer
- `finbot/core/contracts/optimization.py` — typed contracts (ParetoPoint, ParetoResult)
- `tests/unit/test_pareto_optimizer.py` — 15+ tests
- Update `finbot/services/optimization/__init__.py`

### 4.1 Design

**Core concept:** Given a set of strategy/parameter combinations and their backtest
results, identify the Pareto-optimal front — the set of strategies where no other
strategy dominates on BOTH objectives simultaneously.

**Objectives (user-configurable):**
- Primary: maximize CAGR (annualized return)
- Secondary: maximize Sharpe, minimize max_drawdown, minimize volatility
- Default pair: (CAGR, -max_drawdown) — return vs. risk

**Typed contracts (`finbot/core/contracts/optimization.py`):**

```python
@dataclass(frozen=True, slots=True)
class ParetoPoint:
    strategy_name: str
    params: dict[str, object]          # Strategy parameters
    metrics: dict[str, float]          # All backtest metrics for this point
    objective_a: float                 # Value on objective A (e.g., CAGR)
    objective_b: float                 # Value on objective B (e.g., -max_drawdown)
    is_pareto_optimal: bool


@dataclass(frozen=True, slots=True)
class ParetoResult:
    objective_a_name: str              # e.g., "cagr"
    objective_b_name: str              # e.g., "max_drawdown" (negated internally)
    all_points: tuple[ParetoPoint, ...]
    pareto_front: tuple[ParetoPoint, ...]   # Subset of all_points
    dominated_points: tuple[ParetoPoint, ...]
    n_evaluated: int
```

**Core algorithm (`pareto_optimizer.py`):**

```python
def compute_pareto_front(
    results: Sequence[BacktestRunResult],
    objective_a: str = "cagr",
    objective_b: str = "max_drawdown",
    *,
    maximize_a: bool = True,
    maximize_b: bool = False,   # max_drawdown: lower is better → minimize
) -> ParetoResult:
    """Identify Pareto-optimal strategies from a set of backtest results.

    A point P dominates Q if P is at least as good as Q on both objectives
    AND strictly better on at least one.

    Returns:
        ParetoResult with full classification of all points.
    """
```

```python
def _is_dominated(
    point: tuple[float, float],
    candidates: Sequence[tuple[float, float]],
    *,
    maximize: tuple[bool, bool],
) -> bool:
    """Return True if point is dominated by any candidate."""
```

```python
def plot_pareto_front(
    result: ParetoResult,
    *,
    title: str | None = None,
    show_dominated: bool = True,
) -> go.Figure:
    """Scatter plot of all evaluated strategies with Pareto front highlighted."""
```

### 4.2 Tests (`tests/unit/test_pareto_optimizer.py`)

Helper: `_make_result(cagr, max_drawdown, **extra_metrics)` builds a
`BacktestRunResult` from synthetic values.

| Test | What it asserts |
|------|-----------------|
| `test_pareto_single_point` | 1 point → 1 Pareto-optimal point |
| `test_pareto_two_points_one_dominates` | [0.15, -0.10] dominates [0.08, -0.20] |
| `test_pareto_two_points_tradeoff` | [0.15, -0.20] vs [0.08, -0.05] → both optimal |
| `test_pareto_front_not_dominated` | No point in front is dominated by another |
| `test_dominated_points_excluded` | All dominated points in `dominated_points` |
| `test_all_points_classified` | `len(pareto_front) + len(dominated)` == `n_evaluated` |
| `test_pareto_maximize_both` | Works with `maximize_b=True` |
| `test_pareto_minimize_both` | Works with `maximize_a=False, maximize_b=False` |
| `test_missing_metric_raises` | `KeyError` for unknown objective |
| `test_empty_results_raises` | `ValueError` for empty input |
| `test_single_dominated_cluster` | All same values → all Pareto-optimal |
| `test_large_set_returns_correct_front` | 100 synthetic points; front is correct |
| `test_plot_returns_figure` | `plot_pareto_front()` returns `go.Figure` |
| `test_plot_has_two_traces` | Pareto front trace + dominated trace |
| `test_pareto_result_is_frozen` | `ParetoResult` is immutable |

### 4.3 Validation

```bash
uv run pytest tests/unit/test_pareto_optimizer.py -v  # All 15+ tests pass
uv run ruff check finbot/services/optimization/pareto_optimizer.py
uv run mypy finbot/services/optimization/pareto_optimizer.py
```

---

## 5. Phase 4 — Documentation Reconciliation

**Goal:** Fix discrepancy where CLAUDE.md and roadmap.md "summary" section still
shows 17/27 (63%) while the detailed sections and header show 22/27 (81%).

**Deliverables:**
- `CLAUDE.md` — update delivery status block
- `docs/planning/roadmap.md` — reconcile summary section

---

## 6. Acceptance Criteria

- [ ] `uv run mypy finbot/ 2>&1 | tail -1` shows `Found 0 errors`
- [ ] Phase 3 overrides in `pyproject.toml` (core.*, services.execution.*)
- [ ] `mypy_path` hardcoded path removed from `pyproject.toml`
- [ ] `test_performance_regression` marked `@pytest.mark.slow`
- [ ] Performance test uses median, 30% threshold, 10 runs
- [ ] `finbot/services/optimization/pareto_optimizer.py` — Pareto front algorithm
- [ ] `finbot/core/contracts/optimization.py` — typed contracts
- [ ] `tests/unit/test_pareto_optimizer.py` — 15+ tests passing
- [ ] Full test suite: 1080+ tests passing
- [ ] CLAUDE.md + roadmap.md updated to 23/27 (85%) after P7.17 completion
- [ ] `uv run ruff check .` — 0 errors

---

## 7. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-18 | Initial draft — 4 phases |
