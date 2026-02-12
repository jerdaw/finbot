"""DCA Optimizer — Dollar cost averaging grid search optimizer."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from finbot.dashboard.components.charts import create_bar_chart, create_heatmap
from finbot.dashboard.components.sidebar import asset_selector

st.set_page_config(page_title="DCA Optimizer — Finbot", layout="wide")
st.title("DCA Optimizer")
st.markdown(
    "Optimize dollar cost averaging parameters across ratios, durations, and purchase intervals. "
    "This runs a grid search and may take a few minutes."
)

# Sidebar controls
st.sidebar.header("Configuration")
ticker = asset_selector("Asset")
starting_cash = st.sidebar.number_input("Starting Cash ($)", value=1000, min_value=100, step=100)

st.sidebar.markdown("### Ratio Range")
ratio_options = [1.0, 1.5, 2.0, 3.0, 5.0, 10.0]
selected_ratios = st.sidebar.multiselect("DCA Ratios", options=ratio_options, default=[1.0, 2.0, 5.0])

st.sidebar.markdown("### Trial Durations")
duration_options = {"3 years": 252 * 3, "5 years": 252 * 5}
selected_durations = st.sidebar.multiselect(
    "Trial Durations", options=list(duration_options.keys()), default=["3 years"]
)


@st.cache_data(ttl=3600)
def _load_prices(symbol: str) -> pd.Series:
    from finbot.utils.data_collection_utils.yfinance.get_history import get_history

    df = get_history(symbol)
    col = "Adj Close" if "Adj Close" in df.columns else "Close"
    return df[col]


run = st.sidebar.button("Run Optimizer", type="primary")

if run:
    if not selected_ratios:
        st.warning("Select at least one DCA ratio.")
        st.stop()
    if not selected_durations:
        st.warning("Select at least one trial duration.")
        st.stop()

    with st.spinner("Running DCA optimization (this may take a few minutes)..."):
        try:
            from finbot.services.optimization.dca_optimizer import analyze_results_helper, dca_optimizer

            price_hist = _load_prices(ticker)
            trial_durs = tuple(int(duration_options[d]) for d in selected_durations)
            raw_df = dca_optimizer(
                price_history=price_hist,
                ticker=ticker,
                ratio_range=tuple(selected_ratios),
                trial_durations=trial_durs,
                starting_cash=float(starting_cash),
                save_df=False,
                analyze_results=False,
            )
            assert isinstance(raw_df, pd.DataFrame)
            ratio_df, duration_df = analyze_results_helper(raw_df, plot=False)

            st.session_state["dca_raw"] = raw_df
            st.session_state["dca_ratio"] = ratio_df
            st.session_state["dca_duration"] = duration_df
            st.session_state["dca_ticker"] = ticker
        except Exception as e:
            st.error(f"DCA optimization failed: {e}")

# Display results
if "dca_ratio" in st.session_state:
    st.markdown(f"### Results for {st.session_state['dca_ticker']}")

    ratio_df = st.session_state["dca_ratio"]
    duration_df = st.session_state["dca_duration"]
    raw_df = st.session_state["dca_raw"]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### By Ratio")
        ratio_display = ratio_df.reset_index()
        st.plotly_chart(
            create_bar_chart(
                ratio_display,
                "Ratio",
                ["Ratio Sharpe Avg", "Ratio CAGR Avg"],
                "Average Metrics by DCA Ratio",
            ),
            use_container_width=True,
        )
        st.dataframe(ratio_df, use_container_width=True)

    with col2:
        st.markdown("#### By Duration")
        dur_display = duration_df.reset_index()
        st.plotly_chart(
            create_bar_chart(
                dur_display,
                "Duration",
                ["Duration Sharpe Avg", "Duration CAGR Avg"],
                "Average Metrics by DCA Duration",
            ),
            use_container_width=True,
        )
        st.dataframe(duration_df, use_container_width=True)

    # Sharpe heatmap: ratio vs duration
    st.markdown("#### Sharpe Ratio Heatmap (Ratio x Duration)")
    if "DCA Ratio" in raw_df.columns and "DCA Duration" in raw_df.columns:
        pivot = raw_df.pivot_table(values="Sharpe", index="DCA Ratio", columns="DCA Duration", aggfunc="mean")
        if not pivot.empty:
            st.plotly_chart(create_heatmap(pivot, "Average Sharpe by Ratio x Duration"), use_container_width=True)

    # Raw results
    with st.expander("Raw Results Table"):
        st.dataframe(raw_df, use_container_width=True)
else:
    st.info("Configure parameters and click **Run Optimizer** to see results.")
