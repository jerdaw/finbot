# E4-T4: Dashboard Experiment Comparison Implementation Plan

**Created:** 2026-02-16
**Epic:** E4 - Reproducibility and Observability
**Task:** E4-T4
**Estimated Effort:** S (1-2 days)

## Overview

Create a Streamlit dashboard page for comparing experiment cohorts side-by-side, enabling analysis of assumptions and results across multiple backtest runs.

## Current State

**Already Implemented:**
- ✅ ExperimentRegistry with query capabilities
- ✅ Streamlit dashboard with 6 existing pages
- ✅ Dashboard components (charts, sidebar)
- ✅ BacktestRunResult with metadata and metrics

**What's Missing:**
- Experiment comparison page
- Side-by-side metric comparison
- Assumption difference visualization
- Filtering and selection UI

## Goals

1. **Multi-experiment selection** - Select 2+ experiments to compare
2. **Assumption comparison** - Show differences in configuration
3. **Metric comparison** - Side-by-side performance metrics
4. **Visual comparison** - Charts showing metric differences
5. **Export capability** - Download comparison as CSV/JSON

## Design Decisions

**Page Structure:**
```
Experiments Comparison
├── Filters (sidebar)
│   ├── Strategy filter
│   ├── Date range filter
│   └── Limit
├── Experiment Selection
│   └── Multi-select from available experiments
├── Assumptions Comparison
│   └── Table showing configuration differences
├── Metrics Comparison
│   ├── Summary metrics table
│   └── Bar chart comparison
└── Export
    └── Download comparison data
```

**Comparison Features:**
- Show only differences in assumptions (highlight what changed)
- Color-code metrics (green = better, red = worse)
- Support 2-10 experiments simultaneously
- Sort by any metric column

## Implementation

### Step 1: Experiment Comparison Page (2-3 hours)

**File:** `finbot/dashboard/pages/7_experiments.py`

```python
import streamlit as st
import pandas as pd
from finbot.services.backtesting.experiment_registry import ExperimentRegistry
from finbot.constants.path_constants import BACKTESTS_DIR

st.set_page_config(page_title="Experiments — Finbot", layout="wide")
st.title("Experiment Comparison")

# Initialize registry
registry = ExperimentRegistry(BACKTESTS_DIR / "experiments")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    strategy_filter = st.selectbox("Strategy", ["All", ...])
    date_range = st.date_input("Date Range", ...)
    limit = st.number_input("Max Results", value=50)

# Load experiments
experiments = registry.list_runs(...)

# Multi-select experiments
selected = st.multiselect("Select experiments to compare", ...)

# Comparison table
if len(selected) >= 2:
    # Assumptions comparison
    st.subheader("Assumptions")
    assumptions_df = build_assumptions_comparison(selected)
    st.dataframe(assumptions_df)

    # Metrics comparison
    st.subheader("Metrics")
    metrics_df = build_metrics_comparison(selected)
    st.dataframe(metrics_df)

    # Charts
    st.subheader("Visual Comparison")
    plot_metrics_comparison(metrics_df)

    # Export
    st.download_button("Download Comparison", ...)
```

### Step 2: Comparison Helper Functions (1-2 hours)

**File:** `finbot/dashboard/utils/experiment_comparison.py`

```python
def build_assumptions_comparison(
    experiments: list[BacktestRunResult],
) -> pd.DataFrame:
    """Build assumptions comparison table."""
    # Extract assumptions from each experiment
    # Show only fields that differ
    # Return DataFrame with experiments as columns

def build_metrics_comparison(
    experiments: list[BacktestRunResult],
) -> pd.DataFrame:
    """Build metrics comparison table."""
    # Extract metrics from each experiment
    # Return DataFrame with metrics as rows, experiments as columns

def highlight_best_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Apply styling to highlight best/worst values."""
    # For each metric row, highlight max (green) and min (red)

def plot_metrics_comparison(df: pd.DataFrame):
    """Plot metrics comparison charts."""
    # Bar charts for each metric
    # Use plotly for interactivity
```

### Step 3: Integration (1 hour)

- Add to dashboard navigation (if not automatic)
- Add example in docstring
- Test with real experiment data

### Step 4: Tests (1-2 hours)

**File:** `tests/unit/test_experiment_comparison_utils.py`

- Test assumption comparison with different configs
- Test metrics comparison
- Test styling/highlighting
- Test edge cases (1 experiment, no experiments)

## Features

**Filters (Sidebar):**
- Strategy dropdown (All, Rebalance, DualMomentum, etc.)
- Date range selector
- Limit number of results

**Experiment Selection:**
- Multi-select dropdown showing run_id + strategy + date
- Display 2-10 experiments
- Clear selection button

**Assumptions Comparison:**
- Table with assumptions as rows
- Each experiment as a column
- Highlight differences in yellow
- Hide fields that are identical across all

**Metrics Comparison:**
- Table with metrics as rows (CAGR, Sharpe, Max Drawdown, etc.)
- Each experiment as a column
- Color-code best (green) and worst (red)
- Sort by any column

**Visual Comparison:**
- Bar chart for each key metric
- Side-by-side bars per experiment
- Interactive (hover for values)

**Export:**
- Download button for CSV export
- Includes both assumptions and metrics

## Acceptance Criteria

- [ ] Dashboard page at pages/7_experiments.py
- [ ] Experiment selection with filters
- [ ] Assumptions comparison table
- [ ] Metrics comparison table with highlighting
- [ ] Visual comparison charts
- [ ] Export to CSV
- [ ] Tests for comparison utilities
- [ ] Works with experiment registry

## Out of Scope (Future Work)

- Statistical significance testing
- Time-series comparison (equity curves)
- Advanced filtering (by metric ranges)
- Saved comparison templates
- Diff view for code/strategy changes

## Timeline

- Step 1: Dashboard page (2-3 hours)
- Step 2: Comparison utilities (1-2 hours)
- Step 3: Integration (1 hour)
- Step 4: Tests (1-2 hours)
- Total: 5-8 hours (~1 day)

## Implementation Status

### Completed (2026-02-16)

- [x] Step 1: Experiment comparison page ✅
  - Created `finbot/dashboard/pages/7_experiments.py`
  - Sidebar filters (strategy, limit)
  - Multi-select experiment selection (2-10 experiments)
  - Assumptions comparison table with difference highlighting
  - Metrics comparison table with best/worst highlighting
  - Visual comparison with bar charts
  - Export to CSV functionality
  - Metadata table in expander

- [x] Step 2: Comparison helper functions ✅
  - Created `finbot/dashboard/utils/experiment_comparison.py`
  - `build_assumptions_comparison()` - Shows only differing assumptions
  - `build_metrics_comparison()` - All metrics side-by-side
  - `format_metric_value()` - Smart percentage/decimal formatting
  - `highlight_best_worst()` - Color-code best (green) and worst (red)
  - `plot_metrics_comparison()` - Interactive plotly bar charts
  - `export_comparison_csv()` - Export both tables to CSV

- [x] Step 3: Integration ✅
  - Added to dashboard as page 7
  - Uses existing ExperimentRegistry
  - Follows dashboard page pattern
  - Works with cached data loading

- [x] Step 4: Tests ✅
  - Created `tests/unit/test_experiment_comparison_utils.py`
  - 14 comprehensive tests covering:
    - Assumptions comparison (with differences, empty, few differences)
    - Metrics comparison (normal, empty)
    - Value formatting (percentage, decimal, non-numeric)
    - Highlighting best/worst values
    - Plotting metrics (selected, empty)
    - CSV export (normal, empty)
  - All 14 tests passing
  - 583 tests total (up from 569)

## Acceptance Criteria

- [x] Dashboard page at pages/7_experiments.py ✅
- [x] Experiment selection with filters ✅
- [x] Assumptions comparison table ✅
- [x] Metrics comparison table with highlighting ✅
- [x] Visual comparison charts ✅
- [x] Export to CSV ✅
- [x] Tests for comparison utilities ✅
- [x] Works with experiment registry ✅

**All acceptance criteria met!** The experiment comparison dashboard is fully functional
and ready for use.
