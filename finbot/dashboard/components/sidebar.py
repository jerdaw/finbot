"""Common sidebar widgets for the dashboard."""

from __future__ import annotations

from datetime import date

import streamlit as st

from finbot.services.simulation.sim_specific_funds import FUND_CONFIGS

_COMMON_ASSETS = ["SPY", "QQQ", "UPRO", "TQQQ", "TLT", "IEF"]


def fund_selector(default: list[str] | None = None) -> list[str]:
    """Multi-select widget for fund tickers from FUND_CONFIGS."""
    tickers = sorted(FUND_CONFIGS.keys())
    return st.sidebar.multiselect(
        "Select Funds",
        options=tickers,
        default=default or ["SPY"],
    )


def asset_selector(label: str = "Asset Ticker") -> str:
    """Single asset selector with common presets and custom input."""
    preset = st.sidebar.selectbox(label, options=[*_COMMON_ASSETS, "Custom..."])
    if preset == "Custom...":
        return st.sidebar.text_input("Enter ticker", value="SPY").upper()
    return str(preset)


def date_range_selector(
    default_start: date = date(2000, 1, 1),
) -> tuple[date, date]:
    """Date range picker for start/end dates."""
    col1, col2 = st.sidebar.columns(2)
    start = col1.date_input("Start", value=default_start)
    end = col2.date_input("End", value=date.today())
    return start, end  # type: ignore[return-value,unused-ignore]
