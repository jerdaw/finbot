"""Walk-Forward Analysis — interactive walk-forward testing and visualization."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from finbot.dashboard.disclaimer import show_sidebar_accessibility, show_sidebar_disclaimer
from finbot.services.backtesting.walkforward_viz import (
    build_summary_dataframe,
    plot_metric_heatmap,
    plot_rolling_metric,
    plot_summary_boxplot,
    plot_train_test_scatter,
    plot_window_timeline,
)

st.set_page_config(page_title="Walk-Forward — Finbot", layout="wide")

show_sidebar_disclaimer()
show_sidebar_accessibility()

st.title("Walk-Forward Analysis")
st.markdown(
    "Walk-forward testing validates a strategy's out-of-sample robustness by running it "
    "on successive non-overlapping test windows, each trained on prior data only."
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Configuration")

    strategy_name = st.selectbox(
        "Strategy",
        ["NoRebalance", "Rebalance", "DualMomentum", "RiskParity", "RegimeAdaptive"],
        index=0,
    )

    symbols_input = st.text_input("Symbols (comma-separated)", value="SPY,TLT")
    symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]

    st.markdown("**Window Settings**")
    train_window = st.slider("Train Window (days)", 126, 504, 252, step=21)
    test_window = st.slider("Test Window (days)", 21, 252, 63, step=21)
    step_size = st.slider("Step Size (days)", 21, 126, 63, step=21)
    anchored = st.checkbox("Anchored (expanding train window)", value=False)
    include_train = st.checkbox("Include train-period results", value=False)

    st.markdown("**Date Range**")
    start_date = st.date_input("Start", value=pd.Timestamp("2015-01-01"))
    end_date = st.date_input("End", value=pd.Timestamp("2023-12-31"))

    run_btn = st.button("Run Walk-Forward", type="primary")

# ── Main content ──────────────────────────────────────────────────────────────
if run_btn:
    from finbot.core.contracts import BacktestRunRequest
    from finbot.core.contracts.walkforward import WalkForwardConfig
    from finbot.services.backtesting.walkforward import run_walk_forward

    # Attempt to load price histories from local parquet files
    try:
        from finbot.constants.path_constants import PRICE_HISTORIES_DATA_DIR
        from finbot.utils.pandas_utils.load_dataframe import load_dataframe

        price_histories: dict[str, pd.DataFrame] = {}
        missing_symbols = []

        for sym in symbols:
            candidates = list(PRICE_HISTORIES_DATA_DIR.glob(f"{sym}*.parquet"))
            if candidates:
                df = load_dataframe(candidates[0])
                price_histories[sym] = df
            else:
                missing_symbols.append(sym)

        if missing_symbols:
            st.warning(
                f"Could not find local price data for: {', '.join(missing_symbols)}. "
                "Run the daily update pipeline first (`uv run python scripts/update_daily.py`)."
            )

        if not price_histories:
            st.error("No price data available. Cannot run walk-forward analysis.")
            st.stop()

    except Exception as exc:
        st.error(f"Error loading price data: {exc}")
        st.stop()

    # Build adapter and request
    try:
        from finbot.services.backtesting.adapters.backtrader_adapter import BacktraderAdapter

        adapter = BacktraderAdapter(price_histories=price_histories)

        request = BacktestRunRequest(
            strategy_name=strategy_name.lower(),
            symbols=tuple(price_histories.keys()),
            start=pd.Timestamp(start_date),
            end=pd.Timestamp(end_date),
            initial_cash=100_000.0,
        )

        config = WalkForwardConfig(
            train_window=train_window,
            test_window=test_window,
            step_size=step_size,
            anchored=anchored,
        )

        with st.spinner("Running walk-forward analysis…"):
            wf_result = run_walk_forward(adapter, request, config, include_train=include_train)

        st.success(f"Completed {len(wf_result.windows)} windows.")
        st.session_state["wf_result"] = wf_result

    except Exception as exc:
        st.error(f"Walk-forward failed: {exc}")
        st.stop()

# ── Visualisation (renders cached or freshly-run result) ─────────────────────
wf_result = st.session_state.get("wf_result")  # type: ignore[assignment]

if wf_result is None:
    st.info("Configure the walk-forward parameters in the sidebar and click **Run Walk-Forward**.")  # type: ignore[unreachable]
    st.stop()

# ── Summary table ─────────────────────────────────────────────────────────────
st.subheader("Summary Statistics")
summary_df = build_summary_dataframe(wf_result)
if not summary_df.empty:
    st.dataframe(summary_df.style.format("{:.4f}", subset=["mean", "min", "max", "std"]), use_container_width=True)

# ── Chart tabs ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Rolling Metrics", "Heatmap", "Train vs Test", "Timeline", "Distribution"])

with tab1:
    st.markdown("Out-of-sample metric value for each test window.")
    metric_opt = st.selectbox(
        "Metric", ["cagr", "sharpe", "sortino", "max_drawdown", "volatility"], key="rolling_metric"
    )
    fig = plot_rolling_metric(wf_result, metric=metric_opt, include_train=include_train)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("Relative metric performance across all windows (green = relatively better).")
    fig = plot_metric_heatmap(wf_result)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    if wf_result.train_results:
        st.markdown("Each point is one window. Points **below** the diagonal indicate in-sample over-fitting.")
        metric_scatter = st.selectbox("Metric", ["cagr", "sharpe", "sortino"], key="scatter_metric")
        fig = plot_train_test_scatter(wf_result, metric=metric_scatter)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Enable **Include train-period results** in the sidebar to see this chart.")

with tab4:
    st.markdown("Gantt-style view of train (light) and test (dark) date ranges.")
    fig = plot_window_timeline(wf_result)
    st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.markdown("Distribution of per-window out-of-sample metric values.")
    fig = plot_summary_boxplot(wf_result)
    st.plotly_chart(fig, use_container_width=True)
