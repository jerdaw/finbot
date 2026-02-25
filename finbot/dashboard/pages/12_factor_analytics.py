"""Factor Analytics — multi-factor regression, return attribution, and risk decomposition."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from finbot.core.contracts.factor_analytics import (
    FactorAttributionResult,
    FactorModelType,
    FactorRegressionResult,
    FactorRiskResult,
)
from finbot.dashboard.disclaimer import show_sidebar_accessibility, show_sidebar_disclaimer

st.set_page_config(page_title="Factor Analytics — Finbot", layout="wide")

show_sidebar_disclaimer()
show_sidebar_accessibility()

st.title("Factor Analytics")
st.markdown(
    "Fama-French-style multi-factor model analysis: OLS factor regression, "
    "return attribution, and variance decomposition."
)

tab1, tab2, tab3 = st.tabs(["Factor Regression", "Return Attribution", "Risk Decomposition"])

# ── Shared helpers ─────────────────────────────────────────────────────────────


def _load_returns(ticker: str, start: str, end: str) -> np.ndarray | None:
    """Load daily returns from local parquet; return None on failure."""
    try:
        from finbot.constants.path_constants import PRICE_HISTORIES_DATA_DIR
        from finbot.utils.pandas_utils.load_dataframe import load_dataframe

        candidates = list(PRICE_HISTORIES_DATA_DIR.glob(f"{ticker.upper()}*.parquet"))
        if not candidates:
            return None
        df = load_dataframe(candidates[0])
        col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else df.columns[0])
        prices = df[col].dropna()
        prices = prices.loc[pd.Timestamp(start) : pd.Timestamp(end)]
        arr = np.asarray(prices.pct_change().dropna(), dtype=float)
        return arr if len(arr) >= 2 else None
    except Exception:
        return None


def _load_factor_data(uploaded_file: object) -> pd.DataFrame | None:
    """Parse uploaded CSV into a factor returns DataFrame."""
    try:
        df = pd.read_csv(uploaded_file)  # type: ignore[arg-type]
        # Drop date column if present
        for col_name in ("Date", "date", "DATE"):
            if col_name in df.columns:
                df = df.drop(columns=[col_name])
        # Convert to float (Fama-French data often uses percentage points)
        df = df.apply(pd.to_numeric, errors="coerce")
        df = df.dropna()
        return df if len(df) >= 30 and df.shape[1] >= 1 else None
    except Exception:
        return None


# ── Tab 1: Factor Regression ──────────────────────────────────────────────────
with tab1:
    with st.sidebar:
        st.header("Factor Regression")
        ticker_reg = st.text_input("Portfolio ticker", value="QQQ", key="fa_ticker")
        model_choice = st.selectbox(
            "Model type",
            options=["Auto-detect", "CAPM", "FF3", "FF5", "CUSTOM"],
            key="fa_model",
        )
        factor_file = st.file_uploader(
            "Upload factor returns CSV",
            type=["csv"],
            key="fa_factor_file",
            help="CSV with columns like Mkt-RF, SMB, HML, RMW, CMA. "
            "One row per trading day. Values can be in decimal or percentage form.",
        )
        start_reg = st.date_input("Start Date", value=pd.Timestamp("2015-01-01"), key="fa_start")
        end_reg = st.date_input("End Date", value=pd.Timestamp("2023-12-31"), key="fa_end")
        run_reg = st.button("Run Factor Regression", type="primary", key="fa_run_reg")

    reg_result: FactorRegressionResult | None = st.session_state.get("fa_reg_result")

    if run_reg:
        if factor_file is None:
            st.error("Please upload a factor returns CSV file.")
            st.stop()

        from finbot.services.factor_analytics.factor_regression import compute_factor_regression

        port_returns = _load_returns(ticker_reg, str(start_reg), str(end_reg))
        if port_returns is None or len(port_returns) < 30:
            st.error(f"Could not load enough return data for {ticker_reg}.")
            st.stop()

        factor_df = _load_factor_data(factor_file)
        if factor_df is None:
            st.error("Could not parse factor CSV. Ensure numeric columns with >= 30 rows.")
            st.stop()

        # Align lengths
        min_len = min(len(port_returns), len(factor_df))
        port_returns = port_returns[:min_len]
        factor_df = factor_df.iloc[:min_len].reset_index(drop=True)

        model_type_map: dict[str, FactorModelType | None] = {
            "Auto-detect": None,
            "CAPM": FactorModelType.CAPM,
            "FF3": FactorModelType.FF3,
            "FF5": FactorModelType.FF5,
            "CUSTOM": FactorModelType.CUSTOM,
        }
        selected_model = model_type_map.get(model_choice)

        with st.spinner("Running factor regression..."):
            reg_result = compute_factor_regression(
                port_returns,
                factor_df,
                model_type=selected_model,
            )

        st.session_state["fa_reg_result"] = reg_result

    if reg_result is None:
        st.info("Upload a factor CSV, configure settings, and click **Run Factor Regression**.")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Alpha (ann.)", f"{reg_result.alpha:.2%}")
    col2.metric("R-squared", f"{reg_result.r_squared:.3f}")
    col3.metric("Adj. R-squared", f"{reg_result.adj_r_squared:.3f}")
    col4.metric("Model", reg_result.model_type.value)

    st.subheader("Factor Loadings")
    loading_rows = [
        {
            "Factor": name,
            "Loading": f"{reg_result.loadings[name]:.4f}",
            "t-stat": f"{reg_result.t_stats[name]:.2f}",
            "p-value": f"{reg_result.p_values[name]:.4f}",
        }
        for name in reg_result.factor_names
    ]
    loading_rows.append(
        {
            "Factor": "Alpha",
            "Loading": f"{reg_result.alpha:.4f}",
            "t-stat": f"{reg_result.t_stats['alpha']:.2f}",
            "p-value": f"{reg_result.p_values['alpha']:.4f}",
        }
    )
    st.dataframe(pd.DataFrame(loading_rows), use_container_width=True)

    from finbot.services.factor_analytics.viz import plot_factor_loadings as _plot_loadings

    st.plotly_chart(_plot_loadings(reg_result), use_container_width=True)

# ── Tab 2: Return Attribution ─────────────────────────────────────────────────
with tab2:
    attr_result: FactorAttributionResult | None = st.session_state.get("fa_attr_result")

    with st.sidebar:
        st.header("Return Attribution")
        run_attr = st.button("Run Attribution", type="primary", key="fa_run_attr")

    if run_attr:
        if reg_result is None:
            st.error("Run a factor regression first (Tab 1).")
            st.stop()

        if factor_file is None:
            st.error("Please upload a factor returns CSV file in Tab 1.")
            st.stop()

        from finbot.services.factor_analytics.factor_attribution import compute_factor_attribution

        port_returns = _load_returns(ticker_reg, str(start_reg), str(end_reg))
        if port_returns is None:
            st.error("Could not load portfolio returns.")
            st.stop()

        factor_df = _load_factor_data(factor_file)
        if factor_df is None:
            st.error("Could not parse factor CSV.")
            st.stop()

        min_len = min(len(port_returns), len(factor_df))
        port_returns = port_returns[:min_len]
        factor_df = factor_df.iloc[:min_len].reset_index(drop=True)

        with st.spinner("Computing return attribution..."):
            attr_result = compute_factor_attribution(port_returns, factor_df, regression_result=reg_result)

        st.session_state["fa_attr_result"] = attr_result

    if attr_result is None:
        st.info("Run a factor regression first (Tab 1), then click **Run Attribution**.")
        st.stop()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Return", f"{attr_result.total_return:.2%}")
    col2.metric("Explained Return", f"{attr_result.explained_return:.2%}")
    col3.metric("Residual Return", f"{attr_result.residual_return:.2%}")

    from finbot.services.factor_analytics.viz import plot_factor_attribution as _plot_attr

    st.plotly_chart(_plot_attr(attr_result), use_container_width=True)

    st.subheader("Contribution Breakdown")
    attr_rows = [
        {"Component": name, "Contribution": f"{attr_result.factor_contributions[name]:.4f}"}
        for name in attr_result.factor_names
    ]
    attr_rows.append({"Component": "Alpha", "Contribution": f"{attr_result.alpha_contribution:.4f}"})
    attr_rows.append({"Component": "Residual", "Contribution": f"{attr_result.residual_return:.4f}"})
    st.dataframe(pd.DataFrame(attr_rows), use_container_width=True)

# ── Tab 3: Risk Decomposition ─────────────────────────────────────────────────
with tab3:
    risk_result: FactorRiskResult | None = st.session_state.get("fa_risk_result")

    with st.sidebar:
        st.header("Risk Decomposition")
        run_risk = st.button("Run Risk Decomposition", type="primary", key="fa_run_risk")

    if run_risk:
        if reg_result is None:
            st.error("Run a factor regression first (Tab 1).")
            st.stop()

        if factor_file is None:
            st.error("Please upload a factor returns CSV file in Tab 1.")
            st.stop()

        from finbot.services.factor_analytics.factor_risk import compute_factor_risk

        port_returns = _load_returns(ticker_reg, str(start_reg), str(end_reg))
        if port_returns is None:
            st.error("Could not load portfolio returns.")
            st.stop()

        factor_df = _load_factor_data(factor_file)
        if factor_df is None:
            st.error("Could not parse factor CSV.")
            st.stop()

        min_len = min(len(port_returns), len(factor_df))
        port_returns = port_returns[:min_len]
        factor_df = factor_df.iloc[:min_len].reset_index(drop=True)

        with st.spinner("Computing risk decomposition..."):
            risk_result = compute_factor_risk(port_returns, factor_df, regression_result=reg_result)

        st.session_state["fa_risk_result"] = risk_result

    if risk_result is None:
        st.info("Run a factor regression first (Tab 1), then click **Run Risk Decomposition**.")
        st.stop()

    col1, col2, col3 = st.columns(3)
    col1.metric("Systematic Var", f"{risk_result.systematic_variance:.6f}")
    col2.metric("Idiosyncratic Var", f"{risk_result.idiosyncratic_variance:.6f}")
    col3.metric("% Systematic", f"{risk_result.pct_systematic:.1%}")

    from finbot.services.factor_analytics.viz import plot_factor_risk_decomposition as _plot_risk

    st.plotly_chart(_plot_risk(risk_result), use_container_width=True)

    st.subheader("Marginal Contributions")
    mc_rows = [
        {"Factor": name, "Marginal Contribution": f"{risk_result.marginal_contributions[name]:.6f}"}
        for name in risk_result.factor_names
    ]
    st.dataframe(pd.DataFrame(mc_rows), use_container_width=True)
