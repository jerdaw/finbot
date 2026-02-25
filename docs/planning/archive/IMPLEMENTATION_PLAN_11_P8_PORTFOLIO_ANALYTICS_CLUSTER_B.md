# Implementation Plan 11: P8 Cluster B — Portfolio Analytics

**Status:** ✅ COMPLETE
**Completed:** 2026-02-24
**Tests added:** 89 (1472 → 1561 total)

---

## What Was Done

Added standalone portfolio analytics as `finbot/services/portfolio_analytics/`. Four computation modules (rolling, benchmark, drawdown, correlation), a visualisation module (6 Plotly charts), and a 4-tab dashboard page. All result types are immutable frozen dataclasses with `__post_init__` validation. No new dependencies required — scipy/numpy/pandas were already present. 89 new tests, all passing. mypy strict registered for all new modules.

## Context

P8 Cluster A (Risk Analytics) added standalone VaR, stress testing, and Kelly criterion.
Cluster B adds four complementary analytics that are absent from the existing quantstats-powered
`compute_stats` output:

1. **Rolling Metrics** — rolling Sharpe, vol, beta over configurable windows
2. **Benchmark Comparison** — alpha, beta, R², tracking error, information ratio, up/down capture
3. **Drawdown Analysis** — full period detection (start/trough/recovery), underwater curve, aggregate stats
4. **Correlation & Diversification** — HHI, effective N, diversification ratio, pairwise correlation

**What this does NOT duplicate:** `compute_stats.py` via quantstats already gives max_drawdown (single
value), CAGR, Sharpe, Sortino, CVaR, Kelly, and volatility. Cluster B adds multi-period drawdown
decomposition, rolling time-series metrics, relative benchmark statistics, and portfolio-level
diversification measures — all absent from the existing output.

**No new dependencies:** scipy/numpy/pandas already in `pyproject.toml`.

---

## Files to Create

| File | Purpose |
|------|---------|
| `finbot/core/contracts/portfolio_analytics.py` | 5 frozen dataclasses with `__post_init__` validation |
| `finbot/services/portfolio_analytics/__init__.py` | Public API surface (re-exports + `__all__`) |
| `finbot/services/portfolio_analytics/rolling.py` | `compute_rolling_metrics()` |
| `finbot/services/portfolio_analytics/benchmark.py` | `compute_benchmark_comparison()` |
| `finbot/services/portfolio_analytics/drawdown.py` | `compute_drawdown_analysis()` |
| `finbot/services/portfolio_analytics/correlation.py` | `compute_diversification_metrics()` |
| `finbot/services/portfolio_analytics/viz.py` | 6 Plotly chart functions |
| `finbot/dashboard/pages/10_portfolio_analytics.py` | 4-tab Streamlit dashboard page |
| `tests/unit/test_portfolio_analytics_contracts.py` | Contract `__post_init__` validation (~15 tests) |
| `tests/unit/test_rolling_metrics.py` | Rolling window math (~15 tests) |
| `tests/unit/test_benchmark.py` | Alpha/beta/TE/IR (~15 tests) |
| `tests/unit/test_drawdown_analysis.py` | Period detection + underwater curve (~15 tests) |
| `tests/unit/test_correlation_diversification.py` | HHI/effective-N/DR (~12 tests) |
| `tests/unit/test_portfolio_analytics_viz.py` | `go.Figure` smoke tests (~5 tests) |

## Files to Edit

| File | Change |
|------|--------|
| `finbot/core/contracts/__init__.py` | Import + re-export 5 new types |
| `pyproject.toml` | Add `[[tool.mypy.overrides]]` strict block |
| `CLAUDE.md` / `AGENTS.md` | Update P8 section + key entry points table |
| `docs/planning/roadmap.md` | Mark Cluster B complete |

---

## Contracts (`finbot/core/contracts/portfolio_analytics.py`)

### `RollingMetricsResult`
```python
@dataclass(frozen=True, slots=True)
class RollingMetricsResult:
    window: int                         # rolling window bars (>= 2)
    n_obs: int                          # total observations (>= window)
    sharpe: tuple[float, ...]           # length == n_obs; NaN for first (window-1) bars
    volatility: tuple[float, ...]       # annualized vol; same length as sharpe
    beta: tuple[float, ...] | None      # rolling beta vs benchmark; None if not provided
    dates: tuple[str, ...]              # length == n_obs; ISO strings or "0","1","2"
    annualization_factor: int           # default 252
```
**Validation:** window >= 2; n_obs >= window; all tuples same length; beta length matches if not None.

### `BenchmarkComparisonResult`
```python
@dataclass(frozen=True, slots=True)
class BenchmarkComparisonResult:
    alpha: float                        # Jensen's alpha, annualized
    beta: float                         # systematic beta (OLS slope)
    r_squared: float                    # goodness of fit in [0, 1]
    tracking_error: float               # annualized std(portfolio - benchmark); >= 0
    information_ratio: float            # alpha / tracking_error; may be ±inf
    up_capture: float                   # avg port return / avg bench return on up-bench days
    down_capture: float                 # avg port return / avg bench return on down-bench days
    benchmark_name: str                 # label for display
    n_observations: int                 # >= 2
    annualization_factor: int
```
**Validation:** r_squared in [0,1]; tracking_error >= 0; n_observations >= 2.

### `DrawdownPeriod`
```python
@dataclass(frozen=True, slots=True)
class DrawdownPeriod:
    start_idx: int                      # bar index of peak (drawdown begins)
    trough_idx: int                     # bar index of maximum loss
    end_idx: int | None                 # bar of recovery; None if still in drawdown
    depth: float                        # positive fraction (0.20 = 20% drawdown)
    duration_bars: int                  # peak→trough bars
    recovery_bars: int | None           # trough→recovery bars; None if unrecovered
```
**Validation:** trough_idx >= start_idx; end_idx >= trough_idx when not None; depth >= 0.

### `DrawdownAnalysisResult`
```python
@dataclass(frozen=True, slots=True)
class DrawdownAnalysisResult:
    periods: tuple[DrawdownPeriod, ...]  # sorted by depth desc, up to top_n
    underwater_curve: tuple[float, ...]  # signed fractions (negative); length == n_observations
    n_periods: int                       # == len(periods)
    max_depth: float                     # >= 0
    avg_depth: float                     # >= 0
    avg_duration_bars: float
    avg_recovery_bars: float | None      # None if no period has been recovered
    current_drawdown: float              # >= 0; 0 if at all-time high
    n_observations: int
```
**Validation:** n_periods == len(periods); len(underwater_curve) == n_observations; max_depth >= 0.

### `DiversificationResult`
```python
@dataclass(frozen=True, slots=True)
class DiversificationResult:
    n_assets: int                                    # >= 2
    weights: dict[str, float]                        # sum to 1.0
    herfindahl_index: float                          # HHI = sum(w²) in (0, 1]
    effective_n: float                               # 1/HHI; >= 1.0
    diversification_ratio: float                     # weighted_avg_vol / portfolio_vol
    avg_pairwise_correlation: float                  # mean off-diagonal correlation
    correlation_matrix: dict[str, dict[str, float]]  # nested dict, JSON-safe
    individual_vols: dict[str, float]                # per-asset annualized vol
    portfolio_vol: float                             # weighted portfolio annualized vol; >= 0
    n_observations: int
    annualization_factor: int
```
**Validation:** n_assets >= 2; HHI in (0,1]; effective_n >= 1; weights sum to 1.0 ±1e-9.

---

## Service Layer

### `rolling.py` — `compute_rolling_metrics`

```python
def compute_rolling_metrics(
    returns: np.ndarray,
    window: int = 63,
    benchmark_returns: np.ndarray | None = None,
    risk_free_rate: float = 0.0,
    annualization_factor: int = 252,
) -> RollingMetricsResult
```

**Algorithm:**
1. Validate: len >= 30, window >= 2, benchmark same length if provided
2. `rf_per_bar = risk_free_rate / annualization_factor`
3. Initialize sharpe/vol/beta with `np.nan`
4. Loop `i in range(window-1, n)`: compute window excess returns
   - `sigma = std(excess[i-window+1:i+1], ddof=1)`
   - `sharpe[i] = mean(excess_window) / sigma * sqrt(annFactor)` (0 if sigma=0)
   - `vol[i] = sigma * sqrt(annFactor)`
   - If benchmark: `beta[i] = cov(window_excess, window_bench) / var(bench)` (0 if var=0)
5. Convert to tuples; return `RollingMetricsResult`

**Raises:** ValueError if len < 30, window < 2, benchmark length mismatch, annFactor < 1.

### `benchmark.py` — `compute_benchmark_comparison`

```python
def compute_benchmark_comparison(
    portfolio_returns: np.ndarray,
    benchmark_returns: np.ndarray,
    risk_free_rate: float = 0.0,
    benchmark_name: str = "Benchmark",
    annualization_factor: int = 252,
) -> BenchmarkComparisonResult
```

**Algorithm:**
1. Validate: lengths equal, len >= 30
2. `scipy.stats.linregress(benchmark_excess, portfolio_excess)` → slope=beta, intercept=daily_alpha
3. `alpha = daily_alpha * annualization_factor` (annualized Jensen's alpha)
4. `r_squared = r_value ** 2`
5. `tracking_error = std(portfolio - benchmark, ddof=1) * sqrt(annFactor)`
6. `information_ratio = mean(portfolio - benchmark) * annFactor / tracking_error` (±inf if TE=0)
7. Up/down capture: `mean(portfolio[bench>0]) / mean(benchmark[bench>0])` (nan if no up/down days)

### `drawdown.py` — `compute_drawdown_analysis`

```python
def compute_drawdown_analysis(
    returns: np.ndarray,
    top_n: int = 5,
) -> DrawdownAnalysisResult
```

**Algorithm:**
1. `wealth = np.cumprod(1 + returns)`
2. `peak = np.maximum.accumulate(wealth)`
3. `uw = (wealth - peak) / peak` — underwater curve (negative or 0)
4. State-machine scan: track `in_drawdown`, `peak_idx`, `trough_idx`; emit `DrawdownPeriod` when uw crosses back to 0 (use `>= -1e-14` for float tolerance)
5. Append final unrecovered period with `end_idx=None` if still in drawdown
6. Sort all periods by depth desc, take `[:top_n]` for the result tuple
7. Compute aggregates from **all** detected periods (not just top_n)
8. `current_drawdown = max(-uw[-1], 0.0)`

### `correlation.py` — `compute_diversification_metrics`

```python
def compute_diversification_metrics(
    returns_df: pd.DataFrame,
    weights: dict[str, float] | None = None,
    annualization_factor: int = 252,
) -> DiversificationResult
```

**Algorithm:**
1. Validate: ncols >= 2, nrows >= 30, weights keys match columns, weights sum to 1 if provided
2. Equal weights if None: `w = np.ones(n) / n`
3. `sigma_i = std(arr, axis=0, ddof=1) * sqrt(annFactor)` — per-asset vols
4. `corr = np.corrcoef(arr, rowvar=False)` — correlation matrix
5. `avg_corr = mean(upper triangle of corr, k=1)`
6. `cov = np.cov(arr, rowvar=False, ddof=1)`
7. `portfolio_vol = sqrt(max(w @ cov @ w, 0) * annFactor)`
8. `diversification_ratio = (w @ sigma_i) / portfolio_vol` (1.0 if portfolio_vol=0)
9. `HHI = sum(w**2)`, `effective_n = 1 / HHI`

---

## Viz Module (`finbot/services/portfolio_analytics/viz.py`)

All 6 functions return `go.Figure`, never call `.show()`. Wong 2011 palette.

| Function | Chart type |
|----------|-----------|
| `plot_rolling_metrics(result)` | 2–3-row subplot (Sharpe / Vol / Beta), shared x-axis |
| `plot_benchmark_scatter(p_rets, b_rets, result)` | Scatter + OLS regression line + stats annotation |
| `plot_underwater_curve(result)` | Area chart, filled negative (red shading) |
| `plot_drawdown_periods(result, top_n=5)` | Horizontal bar chart by depth |
| `plot_correlation_heatmap(result)` | Annotated heatmap (RdBu, zmid=0) |
| `plot_diversification_weights(result)` | Bar chart of weights + effective_n annotation |

Use `plotly.subplots.make_subplots` for `plot_rolling_metrics`.
Color palette: `_BLUE="#0072B2"`, `_ORANGE="#D55E00"`, `_GREEN="#009E73"`, `_PINK="#CC79A7"`.

---

## Dashboard (`finbot/dashboard/pages/10_portfolio_analytics.py`)

4-tab page following `9_risk_analytics.py` exactly:

```python
st.set_page_config(page_title="Portfolio Analytics — Finbot", layout="wide")
show_sidebar_disclaimer()
show_sidebar_accessibility()
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Rolling Metrics", "🎯 Benchmark", "📉 Drawdown", "🔗 Correlation",
])
```

**Shared helper:**
```python
def _load_returns(ticker: str, start: str, end: str) -> np.ndarray | None:
    # Load parquet from PRICE_HISTORIES_DATA_DIR, pct_change, dropna, return array or None
```

| Tab | Sidebar inputs | Key outputs |
|-----|---------------|-------------|
| Rolling Metrics | ticker, optional benchmark ticker, window slider (21–252), risk_free_rate, dates | 3 metrics (mean Sharpe, mean vol, mean beta) + `plot_rolling_metrics()` |
| Benchmark | portfolio ticker, benchmark ticker (default "SPY"), dates | 6 metrics (alpha, beta, R², TE, IR, up/down capture) + `plot_benchmark_scatter()` |
| Drawdown | ticker, top_n slider (1–10), dates | 4 metrics (max depth, avg depth, n periods, current drawdown) + `plot_underwater_curve()` + `plot_drawdown_periods()` |
| Correlation | comma-separated tickers (≥2), optional weights input, dates | 4 metrics (HHI, effective N, DR, avg corr) + `plot_correlation_heatmap()` + `plot_diversification_weights()` |

Pattern: lazy imports inside `if run_btn:`, `st.session_state` caching, `st.spinner()`, `st.error()` + `st.stop()` for validation failures.

---

## `__init__.py` Public API

```python
from finbot.services.portfolio_analytics.benchmark import compute_benchmark_comparison
from finbot.services.portfolio_analytics.correlation import compute_diversification_metrics
from finbot.services.portfolio_analytics.drawdown import compute_drawdown_analysis
from finbot.services.portfolio_analytics.rolling import compute_rolling_metrics
from finbot.services.portfolio_analytics.viz import (
    plot_benchmark_scatter,
    plot_correlation_heatmap,
    plot_diversification_weights,
    plot_drawdown_periods,
    plot_rolling_metrics,
    plot_underwater_curve,
)

__all__ = [
    "compute_benchmark_comparison",
    "compute_diversification_metrics",
    "compute_drawdown_analysis",
    "compute_rolling_metrics",
    "plot_benchmark_scatter",
    "plot_correlation_heatmap",
    "plot_diversification_weights",
    "plot_drawdown_periods",
    "plot_rolling_metrics",
    "plot_underwater_curve",
]
```

---

## `pyproject.toml` mypy override (add after `finbot.services.optimization.*` block)

```toml
[[tool.mypy.overrides]]
module = [
    "finbot.core.contracts.portfolio_analytics",
    "finbot.services.portfolio_analytics",
    "finbot.services.portfolio_analytics.*",
]
disallow_untyped_defs = true
disallow_incomplete_defs = true
```

---

## Test Plan

All tests in `tests/unit/`. Seeded RNG: `RNG = np.random.default_rng(seed=42)`.

### `test_portfolio_analytics_contracts.py` (~15 tests)
- `TestRollingMetricsResult`: valid construction, window < 2 raises, tuple length mismatch raises
- `TestBenchmarkComparisonResult`: valid, r_squared > 1 raises, n_obs < 2 raises
- `TestDrawdownPeriod`: valid, trough < start raises, end < trough raises
- `TestDrawdownAnalysisResult`: valid, n_periods mismatch raises, underwater_curve length mismatch
- `TestDiversificationResult`: valid, n_assets < 2 raises, weights don't sum raises

### `test_rolling_metrics.py` (~15 tests)
- Returns `RollingMetricsResult`; sharpe shape == n_obs; first (window-1) values are NaN; higher-vol series → higher rolling vol; with benchmark → beta is not None; without benchmark → beta is None; len < 30 raises; window < 2 raises; benchmark length mismatch raises; zero-return series → Sharpe=0

### `test_benchmark.py` (~15 tests)
- Returns `BenchmarkComparisonResult`; perfect replication → beta≈1, alpha≈0, TE≈0; length mismatch raises; len < 30 raises; `benchmark_name` stored; `r_squared` in [0,1]; IR is finite when TE > 0; up/down capture computed; uncorrelated series → beta≈0

### `test_drawdown_analysis.py` (~15 tests)
- Returns `DrawdownAnalysisResult`; all-positive returns → n_periods=0, max_depth=0; known declining series → detects period; unrecovered drawdown → end_idx=None; len(underwater_curve) == n_observations; max_depth >= 0; current_drawdown=0 at peak; top_n limits periods returned; len < 2 raises

### `test_correlation_diversification.py` (~12 tests)
- Returns `DiversificationResult`; equal weights → HHI=1/n, effective_n=n; custom weights stored; weights-don't-sum raises; n_assets < 2 raises; zero-corr assets → diversification_ratio >= 1; perfect-corr assets → diversification_ratio ≈ 1; correlation matrix symmetric; avg_corr in [-1,1]

### `test_portfolio_analytics_viz.py` (~5 tests)
- `plot_rolling_metrics` returns `go.Figure`
- `plot_benchmark_scatter` returns `go.Figure`
- `plot_underwater_curve` returns `go.Figure`
- `plot_drawdown_periods` returns `go.Figure`
- `plot_correlation_heatmap` returns `go.Figure`

---

## Implementation Order

1. `finbot/core/contracts/portfolio_analytics.py` — all 5 dataclasses (foundation)
2. `finbot/core/contracts/__init__.py` — add exports
3. `finbot/services/portfolio_analytics/rolling.py`
4. `finbot/services/portfolio_analytics/benchmark.py`
5. `finbot/services/portfolio_analytics/drawdown.py`
6. `finbot/services/portfolio_analytics/correlation.py`
7. `finbot/services/portfolio_analytics/viz.py`
8. `finbot/services/portfolio_analytics/__init__.py`
9. `finbot/dashboard/pages/10_portfolio_analytics.py`
10. `tests/unit/test_portfolio_analytics_contracts.py`
11. `tests/unit/test_rolling_metrics.py`
12. `tests/unit/test_benchmark.py`
13. `tests/unit/test_drawdown_analysis.py`
14. `tests/unit/test_correlation_diversification.py`
15. `tests/unit/test_portfolio_analytics_viz.py`
16. `pyproject.toml` — add mypy override
17. `CLAUDE.md` / `AGENTS.md` — update P8 section
18. `docs/planning/roadmap.md` — mark Cluster B complete

---

## Key Formulas

| Metric | Formula |
|--------|---------|
| Rolling Sharpe | `mean(excess_window) / std(excess_window) * sqrt(annFactor)` |
| Rolling Beta | `cov(excess_window, bench_window) / var(bench_window)` |
| Jensen's Alpha | `OLS_intercept * annFactor` (annualized) |
| Tracking Error | `std(portfolio - benchmark, ddof=1) * sqrt(annFactor)` |
| Information Ratio | `mean(portfolio - benchmark) * annFactor / tracking_error` |
| Up Capture | `mean(portfolio[bench>0]) / mean(benchmark[bench>0])` |
| Underwater curve | `(wealth - cummax(wealth)) / cummax(wealth)` |
| HHI | `sum(w_i^2)` |
| Effective N | `1 / HHI` |
| Diversification Ratio | `(w · sigma_i) / portfolio_vol` |

---

## Verification

```bash
# 1. Type check — must stay at 0 errors
uv run mypy finbot/

# 2. Lint — must be clean
uv run ruff check . --fix
uv run ruff format .

# 3. New tests
uv run pytest tests/unit/test_portfolio_analytics_contracts.py \
               tests/unit/test_rolling_metrics.py \
               tests/unit/test_benchmark.py \
               tests/unit/test_drawdown_analysis.py \
               tests/unit/test_correlation_diversification.py \
               tests/unit/test_portfolio_analytics_viz.py -v

# 4. Full suite — must stay green (1472 → ~1549 passing)
uv run pytest tests/ -v

# 5. Import smoke
uv run python -c "
from finbot.services.portfolio_analytics import (
    compute_rolling_metrics, compute_benchmark_comparison,
    compute_drawdown_analysis, compute_diversification_metrics,
)
from finbot.core.contracts.portfolio_analytics import (
    RollingMetricsResult, BenchmarkComparisonResult,
    DrawdownPeriod, DrawdownAnalysisResult, DiversificationResult,
)
print('OK')
"
```
