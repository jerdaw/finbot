"""Finbot Dashboard — Main entry point and home page."""

from __future__ import annotations

import streamlit as st

from finbot.dashboard.disclaimer import (
    show_full_disclaimer_section,
    show_sidebar_accessibility,
    show_sidebar_disclaimer,
)

st.set_page_config(
    page_title="Finbot Dashboard",
    page_icon="📊",
    layout="wide",
)

# Display disclaimer and accessibility info in sidebar (shown on all pages)
show_sidebar_disclaimer()
show_sidebar_accessibility()

st.title("Finbot Dashboard")
st.markdown("Financial simulation, backtesting, and optimization platform. Use the sidebar to navigate between pages.")
st.warning("Research/education use only. This dashboard does not provide financial or medical advice.")

# Add full disclaimer section on home page
show_full_disclaimer_section()

# Quick links
st.markdown("### Pages")
col1, col2, col3, col4, col5 = st.columns(5)
col1.page_link("pages/1_simulations.py", label="Simulations", icon="📈")
col2.page_link("pages/2_backtesting.py", label="Backtesting", icon="🔬")
col3.page_link("pages/3_optimizer.py", label="DCA Optimizer", icon="⚙️")
col4.page_link("pages/4_monte_carlo.py", label="Monte Carlo", icon="🎲")
col5.page_link("pages/5_data_status.py", label="Data Status", icon="🗄️")

row2 = st.columns(7)
row2[0].page_link("pages/6_health_economics.py", label="Health Econ", icon="🏥")
row2[1].page_link("pages/7_experiments.py", label="Experiments", icon="🧪")
row2[2].page_link("pages/8_walkforward.py", label="Walk-Forward", icon="🔁")
row2[3].page_link("pages/9_risk_analytics.py", label="Risk Analytics", icon="⚠️")
row2[4].page_link("pages/10_portfolio_analytics.py", label="Portfolio", icon="📊")
row2[5].page_link("pages/11_realtime_quotes.py", label="Realtime Quotes", icon="📡")
row2[6].page_link("pages/12_factor_analytics.py", label="Factor Analytics", icon="🔢")

# Data freshness summary
st.markdown("---")
st.markdown("### Data Status Summary")

try:
    from finbot.services.data_quality.check_data_freshness import check_all_freshness

    statuses = check_all_freshness()
    fresh = sum(1 for s in statuses if not s.is_stale)
    stale = sum(1 for s in statuses if s.is_stale)

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Sources", len(statuses))
    m2.metric("Fresh", fresh)
    m3.metric("Stale", stale)

    for s in statuses:
        icon = "✅" if not s.is_stale else "⚠️"
        st.text(f"  {icon} {s.source.name}: {s.file_count} files, {s.age_str}, {s.size_str}")
except Exception as e:
    st.warning(f"Could not load data status: {e}")
