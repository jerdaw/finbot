# Priority 7 — Batch 2 Implementation Plan: Advanced Technical Features

**Version:** 1.0
**Created:** 2026-02-17
**Status:** Complete — All 5 phases delivered
**Scope:** P7.15 · P7.22 · P7.16 · P7.23 · P7.1 (5 items)
**Estimated Duration:** 2–3 weeks (~14–21 development days)
**Parent Plan:** `docs/planning/priority-7-implementation-plan.md` (v1.1)

---

## 1. Executive Summary

This document covers the next executable batch of Priority 7 work: five codeable,
non-blocked technical items that build directly on the existing P5/P6 infrastructure.
They are grouped to maximize code reuse and minimize context-switching:

| Item | Title | Size | Phase |
|------|-------|------|-------|
| **P7.15** | Walk-forward visualization | M | 1 |
| **P7.22** | Statistical hypothesis testing | M | 2 |
| **P7.16** | Regime-adaptive strategy | M | 3 |
| **P7.23** | Deferred unit tests | M | 4 |
| **P7.1**  | Mypy Phase 1 annotation audit | S | 5 |

Items **excluded** from this batch (blocked or require human action):
- P7.4 — Conventional commits rewrite (requires force-push decision by user)
- P7.8/9/20/25/27 — Videos and poster (require recording equipment/design tools)
- P7.17 — Multi-objective optimization (large; deferred to P8)
- P7.18/19 — Options / real-time data (blocked on external data/cost)
- P7.21 — Clinical HE scenarios (content-heavy; separate effort)

---

## 2. Current State Assessment

### 2.1 Repository snapshot (2026-02-17)

**Test suite:** 956 tests (all green, 11 skipped)
**Coverage:** 61.63% (CI threshold: 60%)
**CI/CD:** 7 jobs — lint, type-check, security, test, docs, parity, performance
**mypy:** 0 errors under current (permissive) settings
**Python:** 3.11 / 3.12 / 3.13

### 2.2 Relevant infrastructure already in place

#### Walk-forward (P7.15)
- **Contracts:** `finbot/core/contracts/walkforward.py` — `WalkForwardConfig`,
  `WalkForwardWindow`, `WalkForwardResult` (frozen dataclasses, fully validated)
- **Service:** `finbot/services/backtesting/walkforward.py` — `generate_windows()`,
  `run_walk_forward()`, `_calculate_summary_metrics()` (all working, tested)
- **Tests:** `tests/unit/test_walkforward.py` — 7 tests (window generation, execution,
  summary metrics)
- **Gap:** Zero visualization code exists; `summary_metrics` dict is rich but unrendered

#### Regime detection (P7.16)
- **Contracts:** `finbot/core/contracts/regime.py` — `MarketRegime` (BULL/BEAR/SIDEWAYS/
  VOLATILE), `RegimeConfig`, `RegimePeriod`, `RegimeMetrics`
- **Service:** `finbot/services/backtesting/regime.py` — `SimpleRegimeDetector.detect()`
  (working, threshold-based); `segment_by_regime()` (documented placeholder, returns
  `metrics={}`)
- **Tests:** `tests/unit/test_regime.py` — 10 tests
- **Gap:** No strategy uses regime detection; `segment_by_regime()` does not compute
  actual per-regime strategy metrics

#### Statistical testing (P7.22)
- **Dependencies:** `scipy>=1.11`, `statsmodels>=0.14.1` already in `pyproject.toml`
- **Gap:** No `hypothesis_testing.py` module exists; no `test_hypothesis_testing.py`

#### Charts convention (all phases)
- **Pattern:** `finbot/dashboard/components/charts.py` — all functions return `go.Figure`,
  no `.show()`, use Wong 2011 color palette (`#0072B2`, `#D55E00`, `#009E73`, etc.),
  call `_add_accessibility_features()` before returning
- **Dashboard pages:** `finbot/dashboard/pages/1_simulations.py` through
  `7_experiments.py` — next available number is `8`

#### Deferred tests (P7.23)
- **backtest_batch.py:** Uses `process_map` from tqdm; takes `**kwargs` with tuple/list
  coercion; no existing unit tests
- **rebalance_optimizer.py:** Gradient-descent portfolio optimizer; uses `process_map`;
  no existing unit tests
- **bond_ladder_simulator:** Comprehensive 6-file module; no end-to-end test for the
  full pipeline without FRED data; can be tested with synthetic yield data

### 2.3 Key assumptions

1. No new Python packages required — all needed libraries already in `pyproject.toml`
   (`scipy`, `statsmodels`, `plotly`, `numpy`, `pandas`)
2. Walk-forward visualization will be importable standalone (not Streamlit-only) so it
   can be tested with `go.Figure` assertions
3. Regime-adaptive strategy will compute regime inline in Backtrader's `next()` — it
   will not import `SimpleRegimeDetector` (avoids coupling the strategy to the service
   layer); regime classification logic is ~10 lines of arithmetic
4. Deferred unit tests must not require live API calls — synthetic data only
5. mypy Phase 1 is an audit only — no code changes, only a report

### 2.4 Key unknowns / risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| `rebalance_optimizer` uses `process_map` — subprocess issues in CI | Low | Medium | Patch with `max_workers=1` in tests |
| `bond_ladder_simulator` yield-curve construction may have hidden FRED deps | Medium | Low | Trace imports; mock or use synthetic flat yield curve |
| Walk-forward viz tests may be slow if they run full backtests | Medium | Low | Pre-build `WalkForwardResult` from synthetic data; no actual backtests in viz tests |
| Regime-adaptive strategy may underperform — reduces credibility | Low | Low | Tests check logic, not performance; document that it is a demonstration, not recommendation |
| mypy audit under strict flags may surface 100+ errors | High | Low | Audit is read-only; report categorizes errors; no fixes required in this batch |

---

## 3. Phase 1 — Walk-Forward Visualization (P7.15)

**Goal:** Provide a reusable, Streamlit-compatible visualization module for
`WalkForwardResult` objects, plus a new dashboard page that exposes it.

**Estimated duration:** 3–4 days
**Deliverables:**
- `finbot/services/backtesting/walkforward_viz.py` (5 chart functions)
- `finbot/dashboard/pages/8_walkforward.py` (Streamlit page)
- `tests/unit/test_walkforward_viz.py` (12+ tests)

### 3.1 New module: `finbot/services/backtesting/walkforward_viz.py`

All functions follow the `charts.py` convention: accept structured inputs, return
`go.Figure`, call `_add_accessibility_features()` before returning.

#### Function 1: `plot_rolling_metric`

```python
def plot_rolling_metric(
    result: WalkForwardResult,
    metric: str = "cagr",
    *,
    include_train: bool = False,
    title: str | None = None,
) -> go.Figure:
```

- X-axis: window test-period end date (one point per window)
- Y-axis: per-window metric value from `result.test_results[i].metrics[metric]`
- Trace 1 (always): test-period metric — solid line, `#0072B2`
- Trace 2 (if `include_train` and `result.train_results`): train-period metric —
  dashed line, `#D55E00`
- Horizontal dashed line at `result.summary_metrics[f"{metric}_mean"]`
- Y-axis formatted as percentage for CAGR/returns; 2dp for Sharpe
- Hover: window ID, date range, metric value

#### Function 2: `plot_metric_heatmap`

```python
def plot_metric_heatmap(
    result: WalkForwardResult,
    metrics: list[str] | None = None,
    *,
    title: str = "Walk-Forward Metric Heatmap",
) -> go.Figure:
```

- If `metrics` is None, defaults to: `["cagr", "sharpe", "sortino", "max_drawdown",
  "volatility"]`
- Rows: metrics; Columns: window IDs (0, 1, 2, …)
- Colorscale: `RdYlGn` (red = low, green = high)
- Cell annotations show numeric values (2dp)
- Uses `go.Heatmap`
- Note: max_drawdown is negated for colorscale (lower = worse = red)

#### Function 3: `plot_train_test_scatter`

```python
def plot_train_test_scatter(
    result: WalkForwardResult,
    metric: str = "cagr",
    *,
    title: str | None = None,
) -> go.Figure:
```

- Requires `result.train_results` to be non-empty; raises `ValueError` otherwise
- X-axis: in-sample (train) metric per window
- Y-axis: out-of-sample (test) metric per window
- Each point labeled "W{window_id}"
- Diagonal reference line (y=x): dashed `#888888` — points above = train overfit
- Colorscale: window_id (0 = light blue, last = dark blue) showing temporal order
- Quadrant annotations: "IS > OOS" / "OOS > IS" in grey

#### Function 4: `plot_window_timeline`

```python
def plot_window_timeline(
    result: WalkForwardResult,
    *,
    title: str = "Walk-Forward Window Timeline",
) -> go.Figure:
```

- Gantt-style horizontal bar chart
- Each row is one window (y = "Window {i}")
- Two bars per window: train period (`#56B4E9`, lighter blue) and test period
  (`#0072B2`, darker blue)
- Hover: exact start/end dates, number of days
- X-axis: dates (pd.Timestamp)
- Uses `go.Bar` with `orientation="h"` and base

#### Function 5: `plot_summary_boxplot`

```python
def plot_summary_boxplot(
    result: WalkForwardResult,
    metrics: list[str] | None = None,
    *,
    title: str = "Walk-Forward Metric Distribution",
) -> go.Figure:
```

- Box plots showing distribution of per-window metric values
- One box per metric; x-axis = metric name
- Uses `go.Box` with `boxpoints="all"` (show individual window dots)
- Color: Wong palette cycling
- Overlaid with mean marker (diamond)
- If `metrics` is None, defaults to `["cagr", "sharpe", "max_drawdown"]`

### 3.2 Dashboard page: `finbot/dashboard/pages/8_walkforward.py`

Streamlit page structure:
1. **Sidebar controls:** strategy selector (dropdown of strategy names),
   date range pickers (start/end), train window (slider 126–504 days),
   test window (slider 21–252 days), step size (slider 21–126 days),
   anchored toggle
2. **"Run Walk-Forward" button:** triggers `run_walk_forward()` via
   `BacktraderAdapter` with synthetic or cached price data
3. **Results section** (tabs):
   - Tab 1: "Rolling Metrics" → `plot_rolling_metric()` for CAGR and Sharpe
   - Tab 2: "Heatmap" → `plot_metric_heatmap()`
   - Tab 3: "Train vs Test" → `plot_train_test_scatter()` (only if `include_train`)
   - Tab 4: "Timeline" → `plot_window_timeline()`
   - Tab 5: "Distribution" → `plot_summary_boxplot()`
4. **Summary table:** `pd.DataFrame` of `summary_metrics` (mean/min/max/std per metric)

Note: The page will show a demo using cached results or a warning if no price data
is available — the existing dashboard pages follow this pattern.

### 3.3 Tests: `tests/unit/test_walkforward_viz.py`

All tests build `WalkForwardResult` directly from synthetic data (no actual backtest
engine calls). Helper `_make_wf_result(n_windows, with_train)` creates the fixture.

| Test | What it asserts |
|------|-----------------|
| `test_plot_rolling_metric_returns_figure` | Return type is `go.Figure` |
| `test_plot_rolling_metric_has_correct_trace_count` | 2 traces (test + mean line) |
| `test_plot_rolling_metric_with_train` | 3 traces when `include_train=True` |
| `test_plot_rolling_metric_missing_metric_raises` | `KeyError` for unknown metric |
| `test_plot_metric_heatmap_returns_figure` | Return type is `go.Figure` |
| `test_plot_metric_heatmap_default_metrics` | Heatmap has 5 rows (default metrics) |
| `test_plot_metric_heatmap_custom_metrics` | Heatmap has N rows for N metrics |
| `test_plot_train_test_scatter_returns_figure` | Return type is `go.Figure` |
| `test_plot_train_test_scatter_no_train_raises` | `ValueError` when no train results |
| `test_plot_window_timeline_returns_figure` | Return type is `go.Figure` |
| `test_plot_window_timeline_bar_count` | `2 * n_windows` bars |
| `test_plot_summary_boxplot_returns_figure` | Return type is `go.Figure` |
| `test_plot_summary_boxplot_custom_metrics` | One box per requested metric |

### 3.4 Validation

- `uv run pytest tests/unit/test_walkforward_viz.py -v` → all 13 tests pass
- `uv run ruff check finbot/services/backtesting/walkforward_viz.py`
- `uv run mypy finbot/services/backtesting/walkforward_viz.py`
- Dashboard page renders without error when imported: `python -c "import finbot.dashboard.pages"`

---

## 4. Phase 2 — Statistical Hypothesis Testing (P7.22)

**Goal:** Provide a rigorous statistical comparison module for backtest results,
enabling users to ask "Is strategy A significantly better than strategy B?" with
proper p-values and confidence intervals.

**Estimated duration:** 3–4 days
**Deliverables:**
- `finbot/services/backtesting/hypothesis_testing.py` (6 functions + 2 dataclasses)
- `tests/unit/test_hypothesis_testing.py` (18+ tests)
- Update `finbot/services/backtesting/__init__.py` to export new functions

### 4.1 New module: `finbot/services/backtesting/hypothesis_testing.py`

#### Data contracts (local dataclasses, not in `core/contracts`)

```python
@dataclass(frozen=True, slots=True)
class HypothesisTestResult:
    test_name: str            # "paired_t_test", "permutation_test", etc.
    statistic: float          # Test statistic value
    p_value: float            # Two-tailed p-value
    significant: bool         # p_value < alpha
    alpha: float              # Significance level used (default 0.05)
    n_samples: int            # Number of observations
    notes: str                # Human-readable interpretation


@dataclass(frozen=True, slots=True)
class BootstrapCI:
    metric: str               # Metric name
    estimate: float           # Point estimate (mean of bootstrap samples)
    lower: float              # Lower bound of CI
    upper: float              # Upper bound of CI
    confidence_level: float   # e.g., 0.95
    n_bootstrap: int          # Number of bootstrap iterations
```

#### Function signatures

```python
def paired_t_test(
    results_a: Sequence[BacktestRunResult],
    results_b: Sequence[BacktestRunResult],
    metric: str = "cagr",
    *,
    alpha: float = 0.05,
) -> HypothesisTestResult:
    """Paired t-test comparing metric values across matched windows.

    Suitable for: comparing two strategies run over identical walk-forward windows.
    Null hypothesis: E[metric_A - metric_B] = 0
    Requires: len(results_a) == len(results_b) >= 2

    Uses: scipy.stats.ttest_rel
    """
```

```python
def mannwhitney_test(
    results_a: Sequence[BacktestRunResult],
    results_b: Sequence[BacktestRunResult],
    metric: str = "cagr",
    *,
    alpha: float = 0.05,
) -> HypothesisTestResult:
    """Mann-Whitney U test (non-parametric strategy comparison).

    Suitable for: comparing strategies without normality assumption.
    Uses: scipy.stats.mannwhitneyu (alternative="two-sided")
    """
```

```python
def permutation_test(
    results_a: Sequence[BacktestRunResult],
    results_b: Sequence[BacktestRunResult],
    metric: str = "cagr",
    *,
    n_permutations: int = 1000,
    alpha: float = 0.05,
    random_seed: int = 42,
) -> HypothesisTestResult:
    """Permutation test for strategy comparison.

    Label-permutation approach: randomly swap strategy labels, recompute
    difference in means, build null distribution.
    Suitable for: small samples where parametric assumptions may not hold.
    """
```

```python
def bootstrap_confidence_interval(
    results: Sequence[BacktestRunResult],
    metric: str = "cagr",
    *,
    confidence_level: float = 0.95,
    n_bootstrap: int = 10_000,
    random_seed: int = 42,
) -> BootstrapCI:
    """Bootstrap percentile confidence interval for a metric.

    Uses numpy resampling with replacement; returns BCa-style interval.
    Suitable for: estimating uncertainty in a single strategy's performance.
    """
```

```python
def compare_strategies(
    strategies: dict[str, Sequence[BacktestRunResult]],
    metric: str = "cagr",
    *,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """Pairwise comparison of N strategies using paired t-tests.

    Returns a DataFrame with rows=strategy_pairs, columns=[statistic, p_value,
    significant, winner].  Suitable for: comparing all strategy pairs from a
    walk-forward batch run.
    """
```

```python
def summarize_walk_forward_significance(
    result: WalkForwardResult,
    benchmark_metric_value: float,
    metric: str = "cagr",
    *,
    alpha: float = 0.05,
) -> HypothesisTestResult:
    """One-sample t-test: does the strategy significantly beat a benchmark?

    Tests H0: mean(per_window_metric) == benchmark_metric_value
    Uses: scipy.stats.ttest_1samp
    Example: does mean CAGR across walk-forward windows differ from 0.07 (7% benchmark)?
    """
```

#### Implementation notes

- All functions extract the `metric` value from each `BacktestRunResult.metrics` dict
- Missing metric keys raise a descriptive `KeyError` with the metric name
- `n_samples < 2` raises `ValueError("Need at least 2 results for hypothesis testing")`
- `scipy.stats` is the only new import (already a dependency)
- All p-values are two-tailed unless otherwise noted in the docstring
- `HypothesisTestResult.notes` contains plain-English interpretation, e.g.:
  `"p=0.032 < α=0.05: reject H0. Strategy A significantly outperforms B (paired t-test, n=8)"`

### 4.2 Tests: `tests/unit/test_hypothesis_testing.py`

Helper: `_make_results(values, metric)` — creates `BacktestRunResult` list from a
list of floats (one result per value, metric injected into `metrics` dict).

| Test | What it asserts |
|------|-----------------|
| `test_paired_t_test_significant` | Returns `significant=True` for clearly different distributions |
| `test_paired_t_test_not_significant` | Returns `significant=False` for identical distributions |
| `test_paired_t_test_insufficient_data_raises` | `ValueError` for n=1 |
| `test_paired_t_test_mismatched_lengths_raises` | `ValueError` for unequal-length inputs |
| `test_paired_t_test_result_structure` | All fields present and typed |
| `test_mannwhitney_significant` | Correct result for separated distributions |
| `test_mannwhitney_not_significant` | Correct result for overlapping distributions |
| `test_permutation_test_deterministic` | Same seed → same p-value |
| `test_permutation_test_significant` | Large effect size → small p-value |
| `test_bootstrap_ci_contains_true_mean` | 95% CI contains the known mean |
| `test_bootstrap_ci_deterministic` | Same seed → same CI bounds |
| `test_bootstrap_ci_structure` | `lower < estimate < upper` |
| `test_compare_strategies_output_shape` | DataFrame rows = N*(N-1)/2 pairs |
| `test_compare_strategies_winner_column` | Winner column has correct strategy name |
| `test_summarize_wf_significance` | Correct H0 rejection for known data |
| `test_missing_metric_raises` | `KeyError` on unknown metric name |
| `test_custom_alpha` | Respects alpha parameter |
| `test_notes_field_nonempty` | `notes` string is non-empty and contains p-value |

### 4.3 Validation

- `uv run pytest tests/unit/test_hypothesis_testing.py -v` → all 18 tests pass
- `uv run ruff check finbot/services/backtesting/hypothesis_testing.py`
- `uv run mypy finbot/services/backtesting/hypothesis_testing.py`
- Coverage delta: +1–2% expected

---

## 5. Phase 3 — Regime-Adaptive Strategy (P7.16)

**Goal:** Deliver a production-quality Backtrader strategy that dynamically adjusts
equity allocation based on the current market regime (BULL/BEAR/SIDEWAYS/VOLATILE),
and simultaneously complete the `segment_by_regime()` implementation so it returns
real per-regime performance metrics.

**Estimated duration:** 4–5 days
**Deliverables:**
- `finbot/services/backtesting/strategies/regime_adaptive.py`
- Enhanced `finbot/services/backtesting/regime.py` (`segment_by_regime()` upgrade)
- `tests/unit/test_regime_adaptive.py` (14+ tests)
- Updated `finbot/services/backtesting/adapters/backtrader_adapter.py` (register new strategy)

### 5.1 Strategy design: `RegimeAdaptive`

The strategy is intentionally simple and pedagogically clear — demonstrating the
regime detection concept rather than optimising for returns.

**Core idea:**
- At each rebalance period, estimate the current market regime from the lookback
  window of daily returns (inline, no external class import)
- Apply pre-configured equity allocation weights per regime:
  - BULL: `bull_equity_pct` (default 0.90) → aggressive equity
  - SIDEWAYS: `sideways_equity_pct` (default 0.60) → moderate equity
  - VOLATILE: `volatile_equity_pct` (default 0.30) → defensive
  - BEAR: `bear_equity_pct` (default 0.10) → near-cash

**Data feeds:**
- `datas[0]`: Equity asset (e.g., SPY)
- `datas[1]`: Safe asset / bond proxy (e.g., TLT, IEF) — holds the non-equity portion

**Parameters (all via Backtrader `params` convention, but defined in `__init__`):**

```python
class RegimeAdaptive(bt.Strategy):
    def __init__(
        self,
        lookback: int = 252,             # Rolling window for regime classification (days)
        rebal_interval: int = 21,         # Rebalance every N bars
        bull_threshold: float = 0.15,     # Ann. return threshold for BULL
        bear_threshold: float = -0.10,    # Ann. return threshold for BEAR
        vol_threshold: float = 0.25,      # Ann. vol threshold for VOLATILE
        bull_equity_pct: float = 0.90,    # Equity allocation in BULL
        sideways_equity_pct: float = 0.60,
        volatile_equity_pct: float = 0.30,
        bear_equity_pct: float = 0.10,
    ):
```

**Inline regime classification (inside `next()`):**

```python
def _classify_regime(self) -> str:
    """Classify current market regime from rolling returns."""
    prices = np.array(self.datas[0].close.get(size=self.lookback + 1))
    if len(prices) < self.lookback + 1:
        return "sideways"  # insufficient history → default
    daily_returns = np.diff(prices) / prices[:-1]
    ann_return = float(np.mean(daily_returns) * 252)
    ann_vol = float(np.std(daily_returns) * (252 ** 0.5))
    if ann_vol > self.vol_threshold:
        return "volatile"
    if ann_return > self.bull_threshold:
        return "bull"
    if ann_return < self.bear_threshold:
        return "bear"
    return "sideways"
```

**Rebalance logic (`next()`):**

```python
def next(self):
    if len(self.datas[0]) < self.lookback + 1:
        return
    self.periods_elapsed += 1
    if self.periods_elapsed < self.rebal_interval:
        return
    self.periods_elapsed = 0

    regime = self._classify_regime()
    equity_pct = {
        "bull": self.bull_equity_pct,
        "bear": self.bear_equity_pct,
        "volatile": self.volatile_equity_pct,
        "sideways": self.sideways_equity_pct,
    }[regime]
    bond_pct = 1.0 - equity_pct

    total_value = self.broker.get_value()
    # Sell first to free cash, then buy
    self._set_target_pct(self.datas[0], equity_pct, total_value)
    self._set_target_pct(self.datas[1], bond_pct, total_value)
```

**Registration in `BacktraderAdapter`:**
Add `"regime_adaptive": RegimeAdaptive` to the strategy registry dict (following the
same pattern as `dual_momentum`, `risk_parity`, etc.).

### 5.2 Completing `segment_by_regime()` in `regime.py`

The current implementation returns `metrics={}` for each regime. The enhancement
accepts an optional `equity_curve` parameter:

```python
def segment_by_regime(
    result: BacktestRunResult,
    market_data: pd.DataFrame,
    detector: SimpleRegimeDetector | None = None,
    config: RegimeConfig | None = None,
    *,
    equity_curve: pd.Series | None = None,  # NEW: DatetimeIndex → portfolio value
) -> dict[MarketRegime, RegimeMetrics]:
```

If `equity_curve` is provided (a `pd.Series` with `DatetimeIndex`):
1. For each `RegimePeriod` from `detector.detect()`, slice `equity_curve` to that
   period's date range
2. Compute daily returns from the sliced equity curve
3. Calculate: annualised return (CAGR), annualised volatility, Sharpe ratio (risk-free=0)
4. Accumulate per-regime: combine all same-regime slices and compute aggregate metrics
5. Populate `RegimeMetrics.metrics` with keys:
   `{"cagr", "volatility", "sharpe", "total_return", "days"}`

If `equity_curve` is `None`, falls back to existing metadata-only behaviour.

The existing tests are unaffected (they don't pass `equity_curve`).

### 5.3 Tests: `tests/unit/test_regime_adaptive.py`

Helper: `_make_synthetic_data(n_bars, trend)` — builds a two-feed OHLCV price
history with configurable trend/volatility, suitable for Backtrader.

| Test | What it asserts |
|------|-----------------|
| `test_strategy_can_be_imported` | Import succeeds |
| `test_strategy_has_required_params` | `lookback`, `rebal_interval`, allocation params |
| `test_classify_regime_bull` | Returns "bull" for strongly trending data |
| `test_classify_regime_bear` | Returns "bear" for declining data |
| `test_classify_regime_volatile` | Returns "volatile" for high-vol data |
| `test_classify_regime_sideways` | Returns "sideways" for flat data |
| `test_classify_regime_insufficient_data` | Returns "sideways" (safe default) |
| `test_strategy_runs_full_backtest` | `BacktestRunner.run_backtest()` returns positive final value |
| `test_strategy_respects_rebal_interval` | Orders only placed at rebal intervals |
| `test_bull_allocation_higher_equity` | In pure bull market, equity allocation > 0.80 of portfolio |
| `test_bear_allocation_lower_equity` | In pure bear market, equity allocation < 0.30 of portfolio |
| `test_default_params_preserved` | Default thresholds match documented values |
| `test_segment_by_regime_with_equity_curve` | Returns non-empty metrics dict per regime |
| `test_segment_by_regime_metrics_keys` | Each regime has cagr/volatility/sharpe/days keys |

### 5.4 Validation

- `uv run pytest tests/unit/test_regime_adaptive.py -v` → all 14 tests pass
- `uv run pytest tests/unit/test_regime.py -v` → all existing 10 tests still pass
- `uv run pytest tests/integration/test_backtest_parity_ab.py -v` → parity maintained
- Strategy registered and reachable via `BacktraderAdapter`:
  `BacktraderAdapter().run(BacktestRunRequest(strategy_name="regime_adaptive", ...))`

---

## 6. Phase 4 — Deferred Unit Tests (P7.23)

**Goal:** Add unit tests for three long-deferred modules: `backtest_batch`,
`rebalance_optimizer`, and `bond_ladder_simulator`. These were deferred in P1 due
to API/FRED dependencies; this phase uses synthetic data to test without external calls.

**Estimated duration:** 3–4 days
**Deliverables:**
- `tests/unit/test_backtest_batch.py` (12+ tests)
- `tests/unit/test_rebalance_optimizer_unit.py` (8+ tests)
- `tests/unit/test_bond_ladder_unit.py` (12+ tests)
- Net coverage increase: expected +1.5–2.5%

### 6.1 `tests/unit/test_backtest_batch.py`

`backtest_batch()` is a parallel runner that takes `**kwargs` with tuple-wrapped
values and fans out to `run_backtest` via `process_map`. Tests must avoid starting
heavy multiprocessing in the CI single-core environment.

**Approach:** Use `pytest-mock` or `unittest.mock.patch` to patch `process_map`
with a sequential equivalent; test the argument-processing, date-alignment, and
result-aggregation logic directly.

| Test | What it asserts |
|------|-----------------|
| `test_batch_single_run_returns_dataframe` | Output is `pd.DataFrame` with expected columns |
| `test_batch_coerces_non_tuple_args` | Scalar kwargs are coerced to 1-tuples |
| `test_batch_empty_price_histories_raises` | `ValueError` for empty price histories |
| `test_batch_empty_dataframe_in_histories_raises` | `ValueError` for empty DataFrame entry |
| `test_batch_date_alignment` | latest_start_date/earliest_end_date correctly computed |
| `test_batch_truncates_histories` | Each price history is truncated to overlap period |
| `test_batch_multiple_strategies_returns_all_rows` | N strategies → N rows in output |
| `test_batch_duration_step_validation` | `ValueError` for multiple durations or steps |
| `test_get_starts_from_steps_basic` | Correct list of start dates |
| `test_get_starts_from_steps_empty_range` | Returns [] when range too small |
| `test_batch_sort_by_cagr` | Results sorted descending by CAGR |
| `test_batch_result_has_strategy_name_column` | "strategy" column present in output |

### 6.2 `tests/unit/test_rebalance_optimizer_unit.py`

`rebalance_optimizer()` runs a gradient-descent-like loop, calling `run_backtest`
via `process_map` at each iteration. Tests patch `process_map` and inject
deterministic returns.

| Test | What it asserts |
|------|-----------------|
| `test_optimizer_returns_best_ratios` | Returns dict or array with n_stocks ratios |
| `test_optimizer_ratios_sum_to_one` | Optimized ratios sum to 1.0 within tolerance |
| `test_optimizer_single_asset` | Works with n_stocks=1 (100% allocation) |
| `test_optimizer_two_assets` | Works with n_stocks=2 |
| `test_optimizer_respects_iterations_limit` | Runs at most 1000 iterations |
| `test_optimizer_uses_cagr_for_ranking` | Sorts by CAGR to find best |
| `test_optimizer_date_alignment` | Truncates histories to overlap |
| `test_optimizer_invalid_price_histories` | `ValueError` for missing data |

### 6.3 `tests/unit/test_bond_ladder_unit.py`

The bond ladder module (`finbot/services/simulation/bond_ladder/`) has 6 files.
Tests use a flat yield curve (constant rates) to avoid FRED lookups.

Key modules to test:
- `bond.py`: `Bond` class — coupon payments, maturity, present value
- `ladder.py`: `Ladder` class — holds collection of `Bond` objects, total value
- `bond_ladder_simulator.py`: `simulate_bond_ladder()` — main entry point
- `build_yield_curve.py`: `build_flat_yield_curve()` helper (if available; else mock)

| Test | What it asserts |
|------|-----------------|
| `test_bond_creation` | `Bond` initialises with face_value, coupon_rate, maturity |
| `test_bond_present_value` | PV matches numpy_financial.pv calculation |
| `test_bond_annual_coupon` | Annual coupon = face_value * coupon_rate |
| `test_ladder_empty` | Empty ladder has total_value=0 |
| `test_ladder_add_bond` | After adding bond, total_value > 0 |
| `test_ladder_maturity_handling` | Matured bonds are removed on update |
| `test_ladder_reinvestment` | Matured proceeds reinvested into new bond |
| `test_simulate_bond_ladder_returns_dataframe` | Output is DataFrame with date index |
| `test_simulate_bond_ladder_columns` | Expected columns present (total_value, income, etc.) |
| `test_simulate_bond_ladder_flat_yield` | With flat yield, total value grows predictably |
| `test_simulate_bond_ladder_positive_values` | No negative total values |
| `test_simulate_bond_ladder_duration` | Output length matches input date range |

### 6.4 Validation

- `uv run pytest tests/unit/test_backtest_batch.py tests/unit/test_rebalance_optimizer_unit.py tests/unit/test_bond_ladder_unit.py -v`
- `uv run pytest --cov=finbot tests/ --cov-report=term-missing` → coverage ≥ 62% (expected +1.5–2.5%)
- No regressions in existing tests

---

## 7. Phase 5 — Mypy Phase 1 Annotation Audit (P7.1)

**Goal:** Produce an authoritative audit report of un-annotated functions and
type errors under stricter mypy settings, creating an actionable roadmap for
future tightening without changing any production code in this phase.

**Estimated duration:** 1–2 days
**Deliverables:**
- `docs/planning/mypy-phase1-audit-report.md` — full audit report
- No code changes

### 7.1 Audit methodology

Run mypy in three progressive modes and capture output:

**Mode A — Strict unannotated functions (primary audit):**
```bash
uv run mypy finbot/ \
  --disallow-untyped-defs \
  --disallow-incomplete-defs \
  --no-error-summary \
  2>&1 | grep "error:" | sort > /tmp/mypy_mode_a.txt
wc -l /tmp/mypy_mode_a.txt
```

**Mode B — Missing return types only:**
```bash
uv run mypy finbot/ \
  --disallow-untyped-defs \
  --disallow-any-generics \
  --warn-return-any \
  2>&1 | grep "error:" | sort > /tmp/mypy_mode_b.txt
```

**Mode C — Full strict (informational only):**
```bash
uv run mypy finbot/ --strict 2>&1 | grep "error:" | sort > /tmp/mypy_mode_c.txt
```

### 7.2 Report structure: `docs/planning/mypy-phase1-audit-report.md`

```markdown
# Mypy Phase 1 Annotation Audit Report

## Summary
- Mode A errors: N (unannotated functions)
- Mode B errors: M (missing return types)
- Mode C errors: P (full strict)
- Current production errors: 0 (under existing config)

## Error Distribution by Module (Mode A)
| Module | Unannotated functions | Priority |
|--------|-----------------------|----------|
| finbot/services/backtesting/ | X | High |
| finbot/utils/ | Y | Medium |
| finbot/services/simulation/ | Z | Low |
...

## Top 10 High-Impact Modules (most errors, most frequently imported)

## Recommended Phases 3–7 (future tightening roadmap)
- Phase 3: Enable disallow_untyped_defs for finbot/core/contracts/ (likely 0 new errors)
- Phase 4: Enable for finbot/services/backtesting/strategies/
- Phase 5: Enable for finbot/services/execution/
- Phase 6: Enable for finbot/services/backtesting/
- Phase 7: Enable for finbot/utils/ (largest surface area)

## Blockers
- [Any modules that would require external annotation stubs]

## Effort Estimate
- Total unannotated functions: N
- Estimated annotation effort: X–Y days
```

### 7.3 Validation

- Report file exists and is well-formed Markdown
- Mode A error count is documented and will serve as baseline for Phase 3+ work
- No pyproject.toml changes in this phase (audit only)

---

## 8. Dependencies and Sequencing

```
Phase 1 (Walk-forward viz)     ──> No dependencies; can start immediately
Phase 2 (Hypothesis testing)   ──> No dependencies; can start immediately
Phase 3 (Regime-adaptive)      ──> No dependencies; can start immediately
Phase 4 (Deferred unit tests)  ──> No dependencies; can start immediately
Phase 5 (Mypy audit)           ──> No dependencies; run last (smallest)

Phases 1–4 are fully independent and can be executed in any order.
Recommended order: 1 → 2 → 3 → 4 → 5 (dependency-free, complexity-ascending order).
```

**Parallelisation opportunity:** Phases 1 and 2 are completely isolated (different
files, different domains) and could be developed simultaneously if bandwidth allows.

### Inter-phase data flow

- P7.15 (viz) consumes `WalkForwardResult` — the same type that hypothesis testing (P7.22)
  consumes — so the two modules can be used together in the dashboard to provide a
  complete "run walk-forward → visualize → test significance" workflow
- P7.16 (regime strategy) registers in the same adapter that all parity tests use —
  the parity gate must remain green throughout

---

## 9. Timeline and Milestones

### High-Level Timeline (2–3 weeks)

```
Days 1–4:   Phase 1 — Walk-forward visualization
             → walkforward_viz.py + dashboard page + 13 tests

Days 5–8:   Phase 2 — Hypothesis testing
             → hypothesis_testing.py + 18 tests

Days 9–13:  Phase 3 — Regime-adaptive strategy
             → regime_adaptive.py + segment_by_regime() upgrade + 14 tests

Days 14–17: Phase 4 — Deferred unit tests
             → 32 new tests across 3 modules

Days 18–19: Phase 5 — Mypy audit
             → mypy-phase1-audit-report.md
```

### Milestones

**M1 (End of Phase 1):**
- 5 visualization functions implemented and tested
- Dashboard page 8 live
- `test_walkforward_viz.py` all passing

**M2 (End of Phase 2):**
- Hypothesis testing module complete
- Can compare any two lists of `BacktestRunResult` with p-values
- `test_hypothesis_testing.py` all passing

**M3 (End of Phase 3):**
- `RegimeAdaptive` strategy registered and testable via adapter
- `segment_by_regime()` returns real per-regime metrics when equity curve provided
- All parity tests still green

**M4 (End of Phase 4):**
- 32+ new tests across 3 deferred modules
- Coverage at or above 62% (from current 61.63%)
- Full test suite (990+ tests) all green

**M5 (End of Phase 5):**
- Mypy audit report published
- Phased annotation roadmap defined
- Batch 2 complete — P7 at 22/27 items (81%)

---

## 10. Rollout and Rollback Strategy

### Rollout approach

- Each phase is delivered as a standalone feature branch: `feature/p7-15-walkforward-viz`,
  `feature/p7-22-hypothesis-testing`, `feature/p7-16-regime-adaptive`,
  `feature/p7-23-deferred-tests`, `feature/p7-1-mypy-audit`
- Each branch merged to `main` only after: all new tests pass, CI is green, ruff/mypy clean
- Commit messages follow conventional commit format: `feat(backtesting): add walk-forward visualization module`
- Dashboard page merged last (after `walkforward_viz.py` is in main)

### Quality gate (per phase)

Before marking a phase complete:
```bash
uv run pytest tests/ -v                    # All tests pass
uv run ruff check . --fix                  # No lint errors
uv run ruff format .                       # Formatted
uv run mypy finbot/                        # 0 errors (existing config)
uv run pytest tests/integration/test_backtest_parity_ab.py  # Parity maintained
```

### Rollback strategy

**Per-phase rollback:** Each phase is an additive change (new files + updated imports).
Rolling back is straightforward: `git revert` the merge commit or delete the new files.

**Phase 3 rollback note:** `segment_by_regime()` upgrade is backward-compatible (new
parameter is `equity_curve=None` with existing behaviour preserved); the strategy
registration is additive. No breaking changes.

**Coverage regression:** If any phase causes coverage to drop below 60%, add targeted
tests before merging (not after).

---

## 11. P7 Roadmap Progress After This Batch

| Item | Title | Status After Batch 2 |
|------|-------|----------------------|
| P7.1  | Mypy Phase 1 audit | ✅ Complete |
| P7.2  | Coverage 60%+ | ✅ Complete (prior) |
| P7.3  | Scheduled CI | ✅ Complete (prior) |
| P7.4  | Conventional commits | ⬜ Deferred (force-push) |
| P7.5  | "Why I Built Finbot" blog | ✅ Complete (prior) |
| P7.6  | "Backtesting Engines Compared" | ✅ Complete (prior) |
| P7.7  | "Health Economics with Python" series | ✅ Complete (prior) |
| P7.8  | Overview video | ⬜ Requires human recording |
| P7.9  | Research poster | ⬜ Requires design tool |
| P7.10 | CanMEDS reflection essay | ✅ Complete (prior) |
| P7.11 | Portfolio 1-pager | ✅ Complete (prior) |
| P7.12 | Lessons learned | ✅ Complete (prior) |
| P7.13 | Impact statement | ✅ Complete (prior) |
| P7.14 | Nautilus migration guide | ✅ Complete (prior) |
| P7.15 | Walk-forward visualization | ✅ **This batch** |
| P7.16 | Regime-adaptive strategy | ✅ **This batch** |
| P7.17 | Multi-objective optimization | ⬜ Deferred to P8 |
| P7.18 | Options overlay | ⬜ Blocked (data) |
| P7.19 | Real-time data feeds | ⬜ Blocked (cost) |
| P7.20 | Video tutorials | ⬜ Requires recording |
| P7.21 | HE clinical scenarios | ⬜ Deferred |
| P7.22 | Hypothesis testing | ✅ **This batch** |
| P7.23 | Deferred unit tests | ✅ **This batch** |
| P7.24 | Roadmap updates | ✅ Complete (ongoing) |
| P7.25 | Getting Started video | ⬜ Requires recording |
| P7.26 | FAQ document | ✅ Complete (prior) |
| P7.27 | Contributing guide video | ⬜ Requires recording |

**After Batch 2: 22/27 items complete (81%) — P7 substantially done.**

Remaining open items after Batch 2:
- P7.4: Force-push conventional commits (user decision required)
- P7.8/9/20/25/27: All require recording/design tools (user action)
- P7.17: Multi-objective optimization (deferred to P8)
- P7.18/19: Blocked on external data/costs
- P7.21: Health economics scenarios (separate content effort)

---

## 12. Acceptance Criteria (Full Batch)

- [x] `finbot/services/backtesting/walkforward_viz.py` — 5 functions, all return `go.Figure`
- [x] `finbot/dashboard/pages/8_walkforward.py` — Streamlit page with 5 chart tabs
- [x] `tests/unit/test_walkforward_viz.py` — 23 tests, all passing
- [x] `finbot/services/backtesting/hypothesis_testing.py` — 6 functions, 2 dataclasses
- [x] `tests/unit/test_hypothesis_testing.py` — 24 tests, all passing
- [x] `finbot/services/backtesting/strategies/regime_adaptive.py` — `RegimeAdaptive` strategy
- [x] `segment_by_regime()` upgraded — returns real metrics when `equity_curve` provided
- [x] `RegimeAdaptive` registered in `BacktraderAdapter`
- [x] `tests/unit/test_regime_adaptive.py` — 19 tests, all passing
- [x] `tests/unit/test_backtest_batch.py` — 11 tests, all passing
- [x] `tests/unit/test_rebalance_optimizer_unit.py` — 5 tests, all passing
- [x] `tests/unit/test_bond_ladder_unit.py` — 23 tests, all passing
- [x] `docs/planning/mypy-phase1-audit-report.md` — published audit report
- [x] Full test suite: 1063 tests, all passing (11 skipped OK)
- [ ] Coverage: ≥ 62% (up from 61.63%)
- [ ] CI: all 7 jobs green
- [ ] Parity gate: all 3 golden strategies still match
- [x] mypy: 0 errors under existing config
- [x] ruff: 0 lint errors

---

## 13. Resource Requirements

**Libraries:** All required (`scipy`, `statsmodels`, `plotly`, `numpy`, `pandas`,
`backtrader`) are already in `pyproject.toml`. No new dependencies.

**Human time:** Solo developer + Claude Code assistance. Estimated 14–19 hours of
active development work.

**Risk-free items:** Phases 1, 2, and 5 are purely additive (new files only).
Phase 3 modifies one function signature (backward-compatible). Phase 4 adds test
files only.

---

## 14. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-17 | Initial draft — 5 phases, 14–19 day estimate |
| 1.1 | 2026-02-17 | Phases 1–4 complete; 107 new tests (1063 total); Phase 5 in progress |
| 1.2 | 2026-02-17 | All 5 phases complete; mypy audit report published; P7 at 22/27 (81%) |

---

**END OF DOCUMENT**
