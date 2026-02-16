"""Experiments — Experiment comparison and analysis dashboard."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from finbot.dashboard.utils.experiment_comparison import (
    build_assumptions_comparison,
    build_metrics_comparison,
    export_comparison_csv,
    highlight_best_worst,
    plot_metrics_comparison,
)

st.set_page_config(page_title="Experiments — Finbot", layout="wide")
st.title("Experiment Comparison")
st.markdown("Compare backtest experiments side-by-side to analyze assumptions and results.")


@st.cache_resource
def _get_registry():
    """Get experiment registry (cached)."""
    from finbot.constants.path_constants import BACKTESTS_DATA_DIR
    from finbot.services.backtesting.experiment_registry import ExperimentRegistry

    return ExperimentRegistry(BACKTESTS_DATA_DIR / "experiments")


@st.cache_data(ttl=60)
def _load_experiments(strategy: str | None, limit: int) -> list[dict]:
    """Load experiments from registry."""
    registry = _get_registry()

    # Apply filters
    metadata_list = registry.list_runs(
        strategy=strategy if strategy != "All" else None,
        limit=limit,
    )

    if not metadata_list:
        return []

    # Convert to display format
    return [
        {
            "run_id": meta.run_id,
            "strategy": meta.strategy_name,
            "created_at": meta.created_at,
            "display": f"{meta.run_id[:12]}... ({meta.strategy_name}, {meta.created_at.strftime('%Y-%m-%d')})",
        }
        for meta in metadata_list
    ]


# Sidebar filters
with st.sidebar:
    st.header("Filters")

    # Strategy filter
    all_strategies = ["All", "Rebalance", "NoRebalance", "DualMomentum", "RiskParity", "SMACrossover", "MACDSingle"]
    strategy_filter = st.selectbox("Strategy", all_strategies, index=0)

    # Limit
    limit = st.number_input("Max Results", min_value=10, max_value=200, value=50, step=10)

    st.markdown("---")
    st.markdown("**Tips:**")
    st.markdown("- Select 2+ experiments to compare")
    st.markdown("- Green = best, Red = worst")
    st.markdown("- Only differing assumptions shown")

# Load available experiments
experiments = _load_experiments(strategy_filter, limit)

if not experiments:
    st.warning("No experiments found. Run some backtests first!")
    st.stop()

# Experiment selection
st.subheader("Select Experiments to Compare")

# Create options for multiselect
options = {exp["display"]: exp["run_id"] for exp in experiments}

selected_displays = st.multiselect(
    "Choose experiments (2-10 recommended)",
    options=options.keys(),
    default=list(options.keys())[:3] if len(options) >= 3 else list(options.keys()),
    max_selections=10,
)

selected_run_ids = [options[disp] for disp in selected_displays]

if len(selected_run_ids) < 2:
    st.info("👆 Please select at least 2 experiments to compare.")
    st.stop()

# Load full experiment data
registry = _get_registry()
selected_experiments = []

for run_id in selected_run_ids:
    try:
        result = registry.load(run_id)
        selected_experiments.append(result)
    except Exception as e:
        st.error(f"Error loading {run_id}: {e}")

if len(selected_experiments) < 2:
    st.error("Could not load experiments. Please try again.")
    st.stop()

# Build comparison tables
assumptions_df = build_assumptions_comparison(selected_experiments)
metrics_df = build_metrics_comparison(selected_experiments)

# Assumptions Comparison
st.subheader("📋 Assumptions Comparison")

if not assumptions_df.empty:
    st.markdown("*Showing only assumptions that differ across experiments*")

    # Style the dataframe
    styled_assumptions = assumptions_df.style.set_properties(
        **{"background-color": "#fffacd"}, subset=pd.IndexSlice[:, :]
    )

    st.dataframe(styled_assumptions, use_container_width=True)
else:
    st.info("All assumptions are identical across selected experiments.")

# Metrics Comparison
st.subheader("📊 Metrics Comparison")

if not metrics_df.empty:
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("*Green = Best, Red = Worst*")

    with col2:
        sort_by = st.selectbox(
            "Sort by",
            ["None", *metrics_df.index.tolist()],
            index=0,
        )

    # Sort if requested
    if sort_by != "None":
        metrics_df = metrics_df.loc[[sort_by] + [m for m in metrics_df.index if m != sort_by]]

    # Apply highlighting
    styled_metrics = highlight_best_worst(metrics_df)

    # Format numbers
    styled_metrics = styled_metrics.format("{:.4f}")

    st.dataframe(styled_metrics, use_container_width=True)

    # Visual Comparison
    st.subheader("📈 Visual Comparison")

    # Select metrics to plot
    default_metrics = ["cagr", "sharpe", "max_drawdown", "sortino"]
    available_metrics = [m for m in default_metrics if m in metrics_df.index]

    if not available_metrics:
        available_metrics = metrics_df.index.tolist()[:4]

    selected_metrics = st.multiselect(
        "Select metrics to visualize",
        metrics_df.index.tolist(),
        default=available_metrics,
    )

    if selected_metrics:
        figures = plot_metrics_comparison(metrics_df, selected_metrics)

        # Display charts in a grid
        cols_per_row = 2
        for i in range(0, len(figures), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, fig in enumerate(figures[i : i + cols_per_row]):
                with cols[j]:
                    st.plotly_chart(fig, use_container_width=True)

    # Summary Statistics
    st.subheader("📉 Summary Statistics")

    summary_data = []

    for col in metrics_df.columns:
        exp_metrics = metrics_df[col].dropna()

        summary_data.append(
            {
                "Experiment": col,
                "Metrics Count": len(exp_metrics),
                "Mean": exp_metrics.mean(),
                "Std": exp_metrics.std(),
            }
        )

    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)

else:
    st.warning("No metrics found in selected experiments.")

# Export Section
st.subheader("💾 Export Comparison")

csv_data = export_comparison_csv(assumptions_df, metrics_df)

st.download_button(
    label="Download Comparison (CSV)",
    data=csv_data,
    file_name=f"experiment_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv",
)

# Metadata Table
with st.expander("🔍 Experiment Metadata"):
    metadata_rows = [
        {
            "Run ID": exp.metadata.run_id,
            "Strategy": exp.metadata.strategy_name,
            "Engine": f"{exp.metadata.engine_name} {exp.metadata.engine_version}",
            "Created": exp.metadata.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "Config Hash": exp.metadata.config_hash[:16] + "...",
            "Snapshot ID": exp.metadata.data_snapshot_id[:16] + "..." if exp.metadata.data_snapshot_id else "N/A",
        }
        for exp in selected_experiments
    ]

    metadata_df = pd.DataFrame(metadata_rows)
    st.dataframe(metadata_df, use_container_width=True)
