"""Data Status — Data freshness monitoring dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Data Status — Finbot", layout="wide")
st.title("Data Status")
st.markdown("Monitor data source freshness, file counts, and storage usage.")


@st.cache_data(ttl=300)
def _load_freshness() -> list[dict]:
    from finbot.services.data_quality.check_data_freshness import check_all_freshness

    statuses = check_all_freshness()
    return [
        {
            "Source": s.source.name,
            "Files": s.file_count,
            "Last Updated": s.age_str,
            "Size": s.size_str,
            "Size (bytes)": s.total_size_bytes,
            "Max Age (days)": s.source.max_age_days,
            "Status": "Fresh" if not s.is_stale else "Stale",
        }
        for s in statuses
    ]


try:
    rows = _load_freshness()
    df = pd.DataFrame(rows)

    # Summary metrics
    total_files = df["Files"].sum()
    total_size = df["Size (bytes)"].sum()
    fresh_count = (df["Status"] == "Fresh").sum()
    stale_count = (df["Status"] == "Stale").sum()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Sources", len(df))
    m2.metric("Total Files", int(total_files))
    m3.metric("Fresh", int(fresh_count))
    m4.metric("Stale", int(stale_count))

    # Status table with highlighting
    st.markdown("### Source Details")

    def _highlight_status(val: object) -> str:
        if val == "Stale":
            return "background-color: #ffcccc"
        return "background-color: #ccffcc"

    display_df = df[["Source", "Files", "Last Updated", "Size", "Status"]]
    st.dataframe(
        display_df.style.map(_highlight_status, subset=["Status"]),
        use_container_width=True,
        hide_index=True,
    )

    # Charts side by side
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Files by Source")
        fig_bar = go.Figure(
            data=go.Bar(
                x=df["Source"],
                y=df["Files"],
                marker_color=["green" if s == "Fresh" else "red" for s in df["Status"]],
            )
        )
        fig_bar.update_layout(
            xaxis_title="Source",
            yaxis_title="File Count",
            template="plotly_white",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.markdown("### Storage by Source")
        fig_pie = go.Figure(
            data=go.Pie(
                labels=df["Source"],
                values=df["Size (bytes)"],
                textinfo="label+percent",
            )
        )
        fig_pie.update_layout(template="plotly_white")
        st.plotly_chart(fig_pie, use_container_width=True)

except Exception as e:
    st.error(f"Failed to load data freshness: {e}")
