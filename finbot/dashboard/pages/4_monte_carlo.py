"""Monte Carlo — Stochastic simulation with fan charts and statistics."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from finbot.dashboard.components.charts import create_fan_chart
from finbot.dashboard.components.sidebar import asset_selector
from finbot.dashboard.disclaimer import show_sidebar_accessibility, show_sidebar_disclaimer

st.set_page_config(page_title="Monte Carlo — Finbot", layout="wide")

# Show disclaimer and accessibility info
show_sidebar_disclaimer()
show_sidebar_accessibility()

st.title("Monte Carlo Simulator")
st.markdown("Run Monte Carlo simulations to model possible future price paths.")

# Sidebar controls
st.sidebar.header("Configuration")
ticker = asset_selector("Asset")
sim_periods = st.sidebar.number_input("Simulation Periods", value=252, min_value=10, max_value=2520, step=21)
n_sims = st.sidebar.number_input("Number of Simulations", value=1000, min_value=100, max_value=50000, step=500)
start_price_input = st.sidebar.number_input("Start Price (0 = auto)", value=0.0, min_value=0.0, step=10.0)


@st.cache_data(ttl=3600)
def _load_prices(symbol: str) -> pd.DataFrame:
    from finbot.utils.data_collection_utils.yfinance.get_history import get_history

    return get_history(symbol)


run = st.sidebar.button("Run Simulation", type="primary")

if run:
    with st.spinner(f"Running {n_sims} Monte Carlo simulations..."):
        try:
            from finbot.services.simulation.monte_carlo.monte_carlo_simulator import monte_carlo_simulator

            equity_data = _load_prices(ticker)
            kwargs: dict = {
                "equity_data": equity_data,
                "sim_periods": int(sim_periods),
                "n_sims": int(n_sims),
            }
            if start_price_input > 0:
                kwargs["start_price"] = float(start_price_input)

            trials_df = monte_carlo_simulator(**kwargs)

            st.session_state["mc_trials"] = trials_df
            st.session_state["mc_ticker"] = ticker
            st.session_state["mc_periods"] = sim_periods
        except Exception as e:
            st.error(f"Monte Carlo simulation failed: {e}")

# Display results
if "mc_trials" in st.session_state:
    trials_df = st.session_state["mc_trials"]
    mc_ticker = st.session_state["mc_ticker"]
    mc_periods = st.session_state["mc_periods"]

    st.markdown(f"### Results: {mc_ticker} — {len(trials_df)} simulations, {mc_periods} periods")

    # Fan chart
    st.plotly_chart(
        create_fan_chart(trials_df, f"Monte Carlo Simulation — {mc_ticker}"),
        use_container_width=True,
    )

    # Summary statistics
    final_values = trials_df.iloc[:, -1]
    start_val = trials_df.iloc[:, 0].median()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Median Final", f"${final_values.median():,.2f}")
    c2.metric("Mean Final", f"${final_values.mean():,.2f}")
    c3.metric("5th Pctl (VaR)", f"${final_values.quantile(0.05):,.2f}")
    p_loss = (final_values < start_val).mean() * 100
    c4.metric("P(Loss)", f"{p_loss:.1f}%")

    # Final value histogram
    st.markdown("### Final Value Distribution")
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(x=final_values.values, nbinsx=60, name="Final Value"))
    fig_hist.add_vline(x=start_val, line_dash="dash", line_color="red", annotation_text="Start Price")
    fig_hist.add_vline(x=final_values.median(), line_dash="dash", line_color="blue", annotation_text="Median")
    fig_hist.update_layout(
        xaxis_title="Final Price",
        yaxis_title="Count",
        template="plotly_white",
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # Detailed statistics table
    st.markdown("### Detailed Statistics")
    stats_data = {
        "Metric": [
            "Start Price",
            "Mean Final",
            "Median Final",
            "Std Dev",
            "Min",
            "Max",
            "5th Percentile",
            "25th Percentile",
            "75th Percentile",
            "95th Percentile",
            "P(Loss)",
            "P(>2x)",
        ],
        "Value": [
            f"${start_val:,.2f}",
            f"${final_values.mean():,.2f}",
            f"${final_values.median():,.2f}",
            f"${final_values.std():,.2f}",
            f"${final_values.min():,.2f}",
            f"${final_values.max():,.2f}",
            f"${final_values.quantile(0.05):,.2f}",
            f"${final_values.quantile(0.25):,.2f}",
            f"${final_values.quantile(0.75):,.2f}",
            f"${final_values.quantile(0.95):,.2f}",
            f"{p_loss:.1f}%",
            f"{(final_values > 2 * start_val).mean() * 100:.1f}%",
        ],
    }
    st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)
else:
    st.info("Configure parameters and click **Run Simulation** to see results.")
