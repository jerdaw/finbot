"""Risk Analytics — VaR/CVaR, stress testing, and Kelly criterion dashboard."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from finbot.dashboard.disclaimer import show_sidebar_accessibility, show_sidebar_disclaimer

st.set_page_config(page_title="Risk Analytics — Finbot", layout="wide")

show_sidebar_disclaimer()
show_sidebar_accessibility()

st.title("Risk Analytics")
st.markdown(
    "Standalone risk analysis: Value at Risk / Expected Shortfall, parametric stress testing, "
    "and Kelly criterion position sizing."
)

tab1, tab2, tab3 = st.tabs(["📊 VaR / CVaR", "💥 Stress Testing", "🎯 Kelly Criterion"])

# ── Shared helper ─────────────────────────────────────────────────────────────


def _load_returns_from_ticker(ticker: str, start: str, end: str) -> np.ndarray | None:
    """Attempt to load daily returns from local parquet; return None on failure."""
    try:
        from finbot.constants.path_constants import PRICE_HISTORIES_DATA_DIR
        from finbot.utils.pandas_utils.load_dataframe import load_dataframe

        candidates = list(PRICE_HISTORIES_DATA_DIR.glob(f"{ticker.upper()}*.parquet"))
        if not candidates:
            return None
        df = load_dataframe(candidates[0])
        if "Close" not in df.columns and "close" not in df.columns:
            col = df.columns[0]
        else:
            col = "Close" if "Close" in df.columns else "close"
        prices = df[col].dropna()
        prices = prices.loc[pd.Timestamp(start) : pd.Timestamp(end)]
        return np.asarray(prices.pct_change().dropna(), dtype=float)
    except Exception:
        return None


# ── Tab 1: VaR / CVaR ─────────────────────────────────────────────────────────
with tab1:
    with st.sidebar:
        st.header("VaR / CVaR")
        ticker_var = st.text_input("Ticker (or upload returns below)", value="SPY", key="var_ticker")
        uploaded_var = st.file_uploader("Upload returns CSV (single column)", type="csv", key="var_upload")
        confidence = st.slider("Confidence Level", min_value=0.90, max_value=0.99, value=0.95, step=0.01)
        method_choice = st.selectbox("Method", ["historical", "parametric", "montecarlo"])
        horizon = st.selectbox("Horizon (days)", [1, 5, 10, 21], index=0)
        portfolio_value = st.number_input("Portfolio Value ($, optional)", min_value=0.0, value=0.0, step=1000.0)
        start_var = st.date_input("Start Date", value=pd.Timestamp("2015-01-01"), key="var_start")
        end_var = st.date_input("End Date", value=pd.Timestamp("2023-12-31"), key="var_end")
        run_var = st.button("Run VaR Analysis", type="primary", key="run_var")

    if run_var:
        from finbot.services.risk_analytics.var import compute_cvar, compute_var, var_backtest
        from finbot.services.risk_analytics.viz import plot_var_comparison, plot_var_distribution

        # Load returns
        returns_var: np.ndarray | None = None
        if uploaded_var is not None:
            df_uploaded = pd.read_csv(uploaded_var, header=None)
            returns_var = np.asarray(df_uploaded.iloc[:, 0].dropna(), dtype=float)
        else:
            returns_var = _load_returns_from_ticker(ticker_var, str(start_var), str(end_var))

        if returns_var is None or len(returns_var) < 30:
            st.error("Could not load enough return data. Run the daily update pipeline first or upload a CSV.")
            st.stop()

        pv = portfolio_value if portfolio_value > 0 else None

        with st.spinner("Computing VaR…"):
            var_hist = compute_var(
                returns_var, confidence=confidence, method="historical", horizon_days=horizon, portfolio_value=pv
            )
            var_param = compute_var(
                returns_var, confidence=confidence, method="parametric", horizon_days=horizon, portfolio_value=pv
            )
            var_mc = compute_var(
                returns_var, confidence=confidence, method="montecarlo", horizon_days=horizon, portfolio_value=pv
            )
            cvar_result = compute_cvar(returns_var, confidence=confidence, method=method_choice)

        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(f"Historical VaR ({confidence:.0%})", f"{var_hist.var:.2%}")
        col2.metric(f"Parametric VaR ({confidence:.0%})", f"{var_param.var:.2%}")
        col3.metric(f"MC VaR ({confidence:.0%})", f"{var_mc.var:.2%}")
        col4.metric(f"CVaR / ES ({confidence:.0%})", f"{cvar_result.cvar:.2%}")

        if pv:
            st.info(
                f"Dollar VaR — Historical: ${var_hist.var_dollars:,.0f} | "
                f"Parametric: ${var_param.var_dollars:,.0f} | MC: ${var_mc.var_dollars:,.0f}"
            )

        st.plotly_chart(
            plot_var_distribution(returns_var, [var_hist, var_param, var_mc], [cvar_result]),
            use_container_width=True,
        )
        st.plotly_chart(
            plot_var_comparison([var_hist, var_param, var_mc]),
            use_container_width=True,
        )

        # Backtest section
        if len(returns_var) > 252:
            with st.spinner("Running VaR backtest…"):
                bt_result = var_backtest(returns_var, confidence=confidence, method=method_choice)
            st.subheader("VaR Backtest")
            bcol1, bcol2, bcol3 = st.columns(3)
            bcol1.metric("Violation Rate", f"{bt_result.violation_rate:.2%}")
            bcol2.metric("Expected Rate", f"{bt_result.expected_violation_rate:.2%}")
            bcol3.metric("Calibrated", "✅ Yes" if bt_result.is_calibrated else "❌ No")
    else:
        st.info("Configure VaR settings in the sidebar and click **Run VaR Analysis**.")

# ── Tab 2: Stress Testing ──────────────────────────────────────────────────────
with tab2:
    with st.sidebar:
        st.header("Stress Testing")
        ticker_stress = st.text_input("Ticker", value="SPY", key="stress_ticker")
        uploaded_stress = st.file_uploader("Upload returns CSV", type="csv", key="stress_upload")
        scenario_options = [
            "2008_financial_crisis",
            "covid_crash_2020",
            "dot_com_bubble",
            "black_monday_1987",
        ]
        selected_scenarios = st.multiselect(
            "Scenarios",
            scenario_options,
            default=scenario_options,
        )
        initial_value_stress = st.number_input("Portfolio Value ($)", min_value=1.0, value=100_000.0, step=1000.0)
        start_stress = st.date_input("Start Date", value=pd.Timestamp("2015-01-01"), key="stress_start")
        end_stress = st.date_input("End Date", value=pd.Timestamp("2023-12-31"), key="stress_end")
        run_stress = st.button("Run Stress Test", type="primary", key="run_stress")

    if run_stress:
        from finbot.services.risk_analytics.stress import run_stress_test
        from finbot.services.risk_analytics.viz import plot_stress_comparison, plot_stress_path

        if not selected_scenarios:
            st.error("Select at least one scenario.")
            st.stop()

        returns_stress: np.ndarray | None = None
        if uploaded_stress is not None:
            df_up = pd.read_csv(uploaded_stress, header=None)
            returns_stress = np.asarray(df_up.iloc[:, 0].dropna(), dtype=float)
        else:
            returns_stress = _load_returns_from_ticker(ticker_stress, str(start_stress), str(end_stress))

        if returns_stress is None:
            returns_stress = np.zeros(1)  # stress test doesn't use returns values

        results_stress = {}
        for key in selected_scenarios:
            results_stress[key] = run_stress_test(returns_stress, key, initial_value=initial_value_stress)

        st.subheader("Scenario Summary")
        summary_rows = [
            {
                "Scenario": r.scenario_name,
                "Trough ($)": f"${r.trough_value:,.0f}",
                "Max Drawdown": f"{r.max_drawdown_pct:.1f}%",
                "Shock Days": r.shock_duration_days,
                "Recovery Days": r.recovery_days,
            }
            for r in results_stress.values()
        ]
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)

        st.plotly_chart(plot_stress_comparison(results_stress), use_container_width=True)

        for result in results_stress.values():
            with st.expander(f"Path: {result.scenario_name}"):
                st.plotly_chart(plot_stress_path(result), use_container_width=True)
    else:
        st.info("Configure stress parameters in the sidebar and click **Run Stress Test**.")

# ── Tab 3: Kelly Criterion ─────────────────────────────────────────────────────
with tab3:
    with st.sidebar:
        st.header("Kelly Criterion")
        kelly_mode = st.radio("Mode", ["Single Asset", "Multi-Asset"], key="kelly_mode")
        if kelly_mode == "Single Asset":
            ticker_kelly = st.text_input("Ticker", value="SPY", key="kelly_ticker")
            uploaded_kelly = st.file_uploader("Upload returns CSV", type="csv", key="kelly_upload")
        else:
            tickers_kelly = st.text_input("Tickers (comma-separated)", value="SPY,TLT", key="kelly_tickers")
            uploaded_kelly_multi = st.file_uploader(
                "Upload multi-asset returns CSV (one column per asset, header row)",
                type="csv",
                key="kelly_multi_upload",
            )
        start_kelly = st.date_input("Start Date", value=pd.Timestamp("2015-01-01"), key="kelly_start")
        end_kelly = st.date_input("End Date", value=pd.Timestamp("2023-12-31"), key="kelly_end")
        run_kelly = st.button("Compute Kelly", type="primary", key="run_kelly")

    if run_kelly:
        from finbot.services.risk_analytics.kelly import compute_kelly_from_returns, compute_multi_asset_kelly
        from finbot.services.risk_analytics.viz import plot_kelly_correlation_heatmap, plot_kelly_fractions

        if kelly_mode == "Single Asset":
            returns_kelly: np.ndarray | None = None
            if uploaded_kelly is not None:
                df_k = pd.read_csv(uploaded_kelly, header=None)
                returns_kelly = np.asarray(df_k.iloc[:, 0].dropna(), dtype=float)
            else:
                returns_kelly = _load_returns_from_ticker(ticker_kelly, str(start_kelly), str(end_kelly))

            if returns_kelly is None or len(returns_kelly) < 10:
                st.error("Not enough return data. Upload a CSV or run the daily pipeline first.")
                st.stop()

            result_k = compute_kelly_from_returns(returns_kelly)

            kcol1, kcol2, kcol3, kcol4 = st.columns(4)
            kcol1.metric("Full Kelly", f"{result_k.full_kelly:.1%}")
            kcol2.metric("Half Kelly", f"{result_k.half_kelly:.1%}")
            kcol3.metric("Quarter Kelly", f"{result_k.quarter_kelly:.1%}")
            kcol4.metric("Win Rate", f"{result_k.win_rate:.1%}")

            st.plotly_chart(plot_kelly_fractions(result_k), use_container_width=True)

        else:  # Multi-Asset
            if "uploaded_kelly_multi" in dir() and uploaded_kelly_multi is not None:
                returns_df = pd.read_csv(uploaded_kelly_multi)
                returns_df = returns_df.select_dtypes(include=[float, int]).dropna()
            else:
                assets = [t.strip().upper() for t in tickers_kelly.split(",") if t.strip()]
                frames = {}
                for asset in assets:
                    arr = _load_returns_from_ticker(asset, str(start_kelly), str(end_kelly))
                    if arr is not None:
                        frames[asset] = arr
                if len(frames) < 2:
                    st.error("Need at least 2 assets with available data.")
                    st.stop()
                min_len = min(len(v) for v in frames.values())
                returns_df = pd.DataFrame({k: v[:min_len] for k, v in frames.items()})

            result_multi = compute_multi_asset_kelly(returns_df)

            st.subheader("Optimal Weights")
            weight_data = [
                {
                    "Asset": asset,
                    "Practical Weight": f"{w:.1%}",
                    "Full Kelly": f"{result_multi.full_kelly_weights[asset]:.1%}",
                    "Half Kelly": f"{result_multi.half_kelly_weights[asset]:.1%}",
                }
                for asset, w in result_multi.weights.items()
            ]
            st.dataframe(pd.DataFrame(weight_data), use_container_width=True)

            st.plotly_chart(
                plot_kelly_fractions(result_multi.asset_kelly_results),
                use_container_width=True,
            )
            st.plotly_chart(
                plot_kelly_correlation_heatmap(result_multi),
                use_container_width=True,
            )
    else:
        st.info("Configure Kelly settings in the sidebar and click **Compute Kelly**.")
