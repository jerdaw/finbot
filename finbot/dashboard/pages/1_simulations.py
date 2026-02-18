"""Simulations — Fund simulation explorer."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from finbot.dashboard.components.charts import create_histogram_chart, create_time_series_chart
from finbot.dashboard.components.sidebar import date_range_selector, fund_selector
from finbot.dashboard.disclaimer import show_sidebar_accessibility, show_sidebar_disclaimer
from finbot.services.simulation.sim_specific_funds import FUND_CONFIGS

st.set_page_config(page_title="Simulations — Finbot", layout="wide")

# Show disclaimer and accessibility info
show_sidebar_disclaimer()
show_sidebar_accessibility()

st.title("Fund Simulation Explorer")
st.markdown("Explore simulated leveraged and unleveraged fund price histories.")

# Sidebar controls
st.sidebar.header("Settings")
tickers = fund_selector(default=["SPY", "UPRO"])
start_date, end_date = date_range_selector()
normalize = st.sidebar.checkbox("Normalize to $1 start", value=True)


@st.cache_data(ttl=3600)
def _load_sim(ticker: str) -> pd.DataFrame:
    from finbot.services.simulation.sim_specific_funds import simulate_fund

    return simulate_fund(ticker, save_sim=False)


if not tickers:
    st.info("Select at least one fund from the sidebar.")
    st.stop()

# Load simulations
sim_data: dict[str, pd.Series] = {}
for t in tickers:
    try:
        df = _load_sim(t)
        closes = df["Close"].loc[str(start_date) : str(end_date)]  # type: ignore[misc]
        if not closes.empty:
            sim_data[t] = closes
    except Exception as e:
        st.warning(f"Could not load {t}: {e}")

if not sim_data:
    st.warning("No simulation data available for the selected funds and date range.")
    st.stop()

# Price chart
st.plotly_chart(
    create_time_series_chart(sim_data, "Fund Prices", normalize=normalize),
    use_container_width=True,
)

# Summary metrics table
st.markdown("### Summary Metrics")
metrics_rows = []
for name, series in sim_data.items():
    total_ret = (series.iloc[-1] / series.iloc[0] - 1) * 100
    n_years = (series.index[-1] - series.index[0]).days / 365.25
    cagr = ((series.iloc[-1] / series.iloc[0]) ** (1 / n_years) - 1) * 100 if n_years > 0 else 0.0
    daily_ret = series.pct_change().dropna()
    vol = daily_ret.std() * np.sqrt(252) * 100
    cummax = series.cummax()
    max_dd = ((series - cummax) / cummax).min() * 100
    config = FUND_CONFIGS.get(name)
    metrics_rows.append(
        {
            "Ticker": name,
            "Leverage": f"{config.leverage_mult:.0f}x" if config else "N/A",
            "Total Return": f"{total_ret:.1f}%",
            "CAGR": f"{cagr:.2f}%",
            "Volatility (ann.)": f"{vol:.2f}%",
            "Max Drawdown": f"{max_dd:.1f}%",
        }
    )

st.dataframe(pd.DataFrame(metrics_rows), use_container_width=True, hide_index=True)

# Daily returns histogram
st.markdown("### Daily Returns Distribution")
returns_data = {name: series.pct_change().dropna() for name, series in sim_data.items()}
st.plotly_chart(
    create_histogram_chart(returns_data, "Daily Returns", bins=80),
    use_container_width=True,
)
