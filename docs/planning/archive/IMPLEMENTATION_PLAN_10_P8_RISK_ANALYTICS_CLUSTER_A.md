# Implementation Plan 10: P8 Cluster A — Risk Analytics Module

**Status:** ✅ COMPLETE
**Completed:** 2026-02-24
**Tests added:** 74 (1398 → 1472 total)

## Context

Finbot is fully through P0–P7. Priority 8 adds three standalone risk analytics capabilities not previously in the codebase:

1. **VaR / CVaR** — parametric, historical, and Monte Carlo Value at Risk + Expected Shortfall
2. **Stress testing** — parametric crisis scenarios (2008, COVID, dot-com, Black Monday) applied to any portfolio
3. **Kelly criterion** — fractional Kelly sizing (full/half/quarter) and multi-asset correlation-adjusted Kelly weights

`compute_stats.py` already computes Kelly and CVaR as single numbers via quantstats tied to a completed backtest run. These new modules provide **standalone** analysis on any returns/price series, multiple methods, and multiple confidence levels. `scipy` was already in `pyproject.toml` — no new dependencies required.

## Files Created

| File | Purpose |
|------|---------|
| `finbot/core/contracts/risk_analytics.py` | 8 frozen dataclasses with `__post_init__` validation |
| `finbot/services/risk_analytics/__init__.py` | Public API surface (15 symbols) |
| `finbot/services/risk_analytics/var.py` | VaR / CVaR computation (3 methods) |
| `finbot/services/risk_analytics/stress.py` | Stress testing with 4 named scenarios |
| `finbot/services/risk_analytics/kelly.py` | Kelly criterion (single + multi-asset) |
| `finbot/services/risk_analytics/viz.py` | 6 Plotly chart functions |
| `finbot/dashboard/pages/9_risk_analytics.py` | 3-tab dashboard page |
| `tests/unit/test_var.py` | 19 tests |
| `tests/unit/test_stress_testing.py` | 16 tests |
| `tests/unit/test_kelly.py` | 18 tests |
| `tests/unit/test_risk_analytics_viz.py` | 7 smoke tests |
| `tests/unit/test_risk_analytics_contracts.py` | 14 tests |

## Files Edited

| File | Change |
|------|--------|
| `finbot/core/contracts/__init__.py` | Import + re-export 8 new types |
| `pyproject.toml` | Add `[[tool.mypy.overrides]]` strict block |

## Key Formulas Implemented

- **Historical VaR:** `-percentile(returns, (1-confidence)*100) * sqrt(horizon_days)`
- **Parametric VaR:** `-norm.ppf(1-confidence) * std(returns) * sqrt(horizon_days)`
- **Monte Carlo VaR:** percentile of simulated cumulative path returns
- **CVaR:** mean loss in the tail beyond the VaR threshold
- **Single-asset Kelly:** `f* = win_rate - (1 - win_rate) / win_loss_ratio`
- **Multi-asset Kelly:** `f* = Σ⁻¹ μ` (covariance-solve), clipped to `[0,1]` and normalised

## Verification

```
uv run pytest tests/unit/test_var.py tests/unit/test_stress_testing.py \
    tests/unit/test_kelly.py tests/unit/test_risk_analytics_viz.py \
    tests/unit/test_risk_analytics_contracts.py -v
# 74 passed in 1.12s

uv run pytest tests/ -q
# 1472 passed, 10 skipped, 6 deselected

uv run mypy finbot/services/risk_analytics/ finbot/core/contracts/risk_analytics.py
# Success: no issues found in 6 source files

uv run ruff check finbot/services/risk_analytics/ ...
# All checks passed!
```
