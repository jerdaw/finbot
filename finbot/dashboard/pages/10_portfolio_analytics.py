"""Portfolio Analytics — rolling metrics, benchmark comparison, drawdown, and diversification."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from finbot.core.contracts.portfolio_analytics import (
    BenchmarkComparisonResult,
    DiversificationResult,
    DrawdownAnalysisResult,
    RollingMetricsResult,
)
from finbot.dashboard.disclaimer import show_sidebar_accessibility, show_sidebar_disclaimer

st.set_page_config(page_title="Portfolio Analytics — Finbot", layout="wide")

show_sidebar_disclaimer()
show_sidebar_accessibility()

st.title("Portfolio Analytics")
st.markdown(
    "Standalone portfolio analysis: rolling risk/return metrics, benchmark comparison, "
    "drawdown period decomposition, and correlation / diversification metrics."
)

tab1, tab2, tab3, tab4 = st.tabs(["📈 Rolling Metrics", "🎯 Benchmark", "📉 Drawdown", "🔗 Correlation"])

# ── Shared helper ──────────────────────────────────────────────────────────────


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


# ── Tab 1: Rolling Metrics ─────────────────────────────────────────────────────
with tab1:
    with st.sidebar:
        st.header("Rolling Metrics")
        ticker_roll = st.text_input("Ticker", value="SPY", key="roll_ticker")
        bench_roll = st.text_input("Benchmark ticker (optional)", value="", key="roll_bench", placeholder="e.g. SPY")
        window_roll = st.slider("Window (bars)", min_value=21, max_value=252, value=63, step=1)
        rf_roll = (
            st.number_input("Risk-free rate (annual %)", min_value=0.0, max_value=20.0, value=4.0, step=0.1) / 100.0
        )
        start_roll = st.date_input("Start Date", value=pd.Timestamp("2015-01-01"), key="roll_start")
        end_roll = st.date_input("End Date", value=pd.Timestamp("2023-12-31"), key="roll_end")
        run_roll = st.button("Compute Rolling Metrics", type="primary", key="run_roll")

    roll_result: RollingMetricsResult | None = st.session_state.get("roll_result")

    if run_roll:
        from finbot.services.portfolio_analytics.rolling import compute_rolling_metrics

        returns_roll = _load_returns(ticker_roll, str(start_roll), str(end_roll))
        if returns_roll is None or len(returns_roll) < 30:
            st.error("Could not load enough return data. Run the daily update pipeline first.")
            st.stop()

        bench_arr: np.ndarray | None = None
        if bench_roll.strip():
            bench_arr = _load_returns(bench_roll.strip(), str(start_roll), str(end_roll))
            if bench_arr is not None:
                min_len = min(len(returns_roll), len(bench_arr))
                returns_roll = returns_roll[:min_len]
                bench_arr = bench_arr[:min_len]

        with st.spinner("Computing rolling metrics…"):
            roll_result = compute_rolling_metrics(
                returns_roll,
                window=window_roll,
                benchmark_returns=bench_arr,
                risk_free_rate=rf_roll,
            )

        st.session_state["roll_result"] = roll_result

    if roll_result is None:
        st.info("Configure settings in the sidebar and click **Compute Rolling Metrics**.")
        st.stop()

    valid_sharpe = [x for x in roll_result.sharpe if x == x]  # filter NaN
    valid_vol = [x for x in roll_result.volatility if x == x]
    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Mean Rolling Sharpe",
        f"{(sum(valid_sharpe) / len(valid_sharpe)):.2f}" if valid_sharpe else "N/A",
    )
    col2.metric(
        "Mean Rolling Vol",
        f"{(sum(valid_vol) / len(valid_vol)):.1%}" if valid_vol else "N/A",
    )
    if roll_result.beta is not None:
        valid_beta = [x for x in roll_result.beta if x == x]
        col3.metric(
            "Mean Rolling Beta",
            f"{(sum(valid_beta) / len(valid_beta)):.2f}" if valid_beta else "N/A",
        )

    from finbot.services.portfolio_analytics.viz import plot_rolling_metrics as _plot_roll

    st.plotly_chart(_plot_roll(roll_result), use_container_width=True)

# ── Tab 2: Benchmark Comparison ────────────────────────────────────────────────
with tab2:
    with st.sidebar:
        st.header("Benchmark Comparison")
        ticker_port = st.text_input("Portfolio ticker", value="QQQ", key="bench_port")
        ticker_bench = st.text_input("Benchmark ticker", value="SPY", key="bench_bench")
        rf_bench = (
            st.number_input(
                "Risk-free rate (annual %)",
                min_value=0.0,
                max_value=20.0,
                value=4.0,
                step=0.1,
                key="rf_bench",
            )
            / 100.0
        )
        start_bench = st.date_input("Start Date", value=pd.Timestamp("2015-01-01"), key="bench_start")
        end_bench = st.date_input("End Date", value=pd.Timestamp("2023-12-31"), key="bench_end")
        run_bench = st.button("Run Benchmark Comparison", type="primary", key="run_bench")

    bench_result: BenchmarkComparisonResult | None = st.session_state.get("bench_result")
    bench_p_rets: np.ndarray | None = st.session_state.get("bench_p_rets")
    bench_b_rets: np.ndarray | None = st.session_state.get("bench_b_rets")

    if run_bench:
        from finbot.services.portfolio_analytics.benchmark import compute_benchmark_comparison

        p_rets = _load_returns(ticker_port, str(start_bench), str(end_bench))
        b_rets = _load_returns(ticker_bench, str(start_bench), str(end_bench))

        if p_rets is None or len(p_rets) < 30:
            st.error(f"Could not load enough data for {ticker_port}.")
            st.stop()
        if b_rets is None or len(b_rets) < 30:
            st.error(f"Could not load enough data for {ticker_bench}.")
            st.stop()

        min_len = min(len(p_rets), len(b_rets))
        p_rets, b_rets = p_rets[:min_len], b_rets[:min_len]

        with st.spinner("Computing benchmark statistics…"):
            bench_result = compute_benchmark_comparison(
                p_rets, b_rets, risk_free_rate=rf_bench, benchmark_name=ticker_bench.upper()
            )

        bench_p_rets, bench_b_rets = p_rets, b_rets
        st.session_state["bench_result"] = bench_result
        st.session_state["bench_p_rets"] = bench_p_rets
        st.session_state["bench_b_rets"] = bench_b_rets

    if bench_result is None:
        st.info("Configure settings in the sidebar and click **Run Benchmark Comparison**.")
        st.stop()

    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    col1.metric("Alpha (ann.)", f"{bench_result.alpha:.2%}")
    col2.metric("Beta", f"{bench_result.beta:.2f}")
    col3.metric("R²", f"{bench_result.r_squared:.2f}")
    col4.metric("Tracking Error", f"{bench_result.tracking_error:.2%}")
    ir_val = bench_result.information_ratio
    ir_display = f"{ir_val:.2f}" if abs(ir_val) < 1e9 else ("∞" if ir_val > 0 else "-∞")
    col5.metric("Information Ratio", ir_display)
    col6.metric(
        "Up/Down Capture",
        f"{bench_result.up_capture:.2f} / {bench_result.down_capture:.2f}",
    )

    if bench_p_rets is not None and bench_b_rets is not None:
        from finbot.services.portfolio_analytics.viz import plot_benchmark_scatter as _plot_bench

        st.plotly_chart(
            _plot_bench(bench_p_rets, bench_b_rets, bench_result),
            use_container_width=True,
        )

# ── Tab 3: Drawdown Analysis ───────────────────────────────────────────────────
with tab3:
    with st.sidebar:
        st.header("Drawdown Analysis")
        ticker_dd = st.text_input("Ticker", value="SPY", key="dd_ticker")
        top_n_dd = st.slider("Top-N periods", min_value=1, max_value=10, value=5)
        start_dd = st.date_input("Start Date", value=pd.Timestamp("2010-01-01"), key="dd_start")
        end_dd = st.date_input("End Date", value=pd.Timestamp("2023-12-31"), key="dd_end")
        run_dd = st.button("Run Drawdown Analysis", type="primary", key="run_dd")

    dd_result: DrawdownAnalysisResult | None = st.session_state.get("dd_result")

    if run_dd:
        from finbot.services.portfolio_analytics.drawdown import compute_drawdown_analysis

        returns_dd = _load_returns(ticker_dd, str(start_dd), str(end_dd))
        if returns_dd is None or len(returns_dd) < 2:
            st.error("Could not load enough return data.")
            st.stop()

        with st.spinner("Analysing drawdowns…"):
            dd_result = compute_drawdown_analysis(returns_dd, top_n=top_n_dd)

        st.session_state["dd_result"] = dd_result

    if dd_result is None:
        st.info("Configure settings in the sidebar and click **Run Drawdown Analysis**.")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Max Drawdown", f"{dd_result.max_depth:.1%}")
    col2.metric("Avg Drawdown", f"{dd_result.avg_depth:.1%}")
    col3.metric("Drawdown Periods", str(dd_result.n_periods))
    col4.metric("Current Drawdown", f"{dd_result.current_drawdown:.1%}")

    from finbot.services.portfolio_analytics.viz import plot_drawdown_periods as _plot_dd
    from finbot.services.portfolio_analytics.viz import plot_underwater_curve as _plot_uw

    st.plotly_chart(_plot_uw(dd_result), use_container_width=True)
    st.plotly_chart(_plot_dd(dd_result, top_n=top_n_dd), use_container_width=True)

    if dd_result.periods:
        st.subheader("Drawdown Period Details")
        rows = [
            {
                "Rank": i + 1,
                "Start Bar": p.start_idx,
                "Trough Bar": p.trough_idx,
                "End Bar": p.end_idx if p.end_idx is not None else "ongoing",
                "Depth": f"{p.depth:.1%}",
                "Duration (bars)": p.duration_bars,
                "Recovery (bars)": p.recovery_bars if p.recovery_bars is not None else "-",
            }
            for i, p in enumerate(dd_result.periods)
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

# ── Tab 4: Correlation & Diversification ──────────────────────────────────────
with tab4:
    with st.sidebar:
        st.header("Correlation & Diversification")
        tickers_corr = st.text_input("Tickers (comma-separated, ≥ 2)", value="SPY,TLT,GLD", key="corr_tickers")
        weights_input = st.text_input(
            "Weights (comma-separated, optional)",
            value="",
            key="corr_weights",
            placeholder="e.g. 0.6,0.3,0.1",
        )
        start_corr = st.date_input("Start Date", value=pd.Timestamp("2015-01-01"), key="corr_start")
        end_corr = st.date_input("End Date", value=pd.Timestamp("2023-12-31"), key="corr_end")
        run_corr = st.button("Run Correlation Analysis", type="primary", key="run_corr")

    corr_result: DiversificationResult | None = st.session_state.get("corr_result")

    if run_corr:
        from finbot.services.portfolio_analytics.correlation import compute_diversification_metrics

        assets_list = [t.strip().upper() for t in tickers_corr.split(",") if t.strip()]
        if len(assets_list) < 2:
            st.error("Please enter at least 2 tickers.")
            st.stop()

        frames: dict[str, np.ndarray] = {}
        for asset in assets_list:
            arr = _load_returns(asset, str(start_corr), str(end_corr))
            if arr is not None and len(arr) >= 30:
                frames[asset] = arr
            else:
                st.warning(f"No data for {asset} — skipping.")

        if len(frames) < 2:
            st.error("Need at least 2 assets with available data.")
            st.stop()

        min_len = min(len(v) for v in frames.values())
        returns_df = pd.DataFrame({k: v[:min_len] for k, v in frames.items()})

        weights_dict: dict[str, float] | None = None
        if weights_input.strip():
            try:
                raw_w = [float(x.strip()) for x in weights_input.split(",") if x.strip()]
                if len(raw_w) != len(frames):
                    st.error(f"Expected {len(frames)} weights, got {len(raw_w)}.")
                    st.stop()
                total_w = sum(raw_w)
                weights_dict = {a: w / total_w for a, w in zip(frames.keys(), raw_w, strict=False)}
            except ValueError:
                st.error("Weights must be numeric values.")
                st.stop()

        with st.spinner("Computing diversification metrics…"):
            corr_result = compute_diversification_metrics(returns_df, weights=weights_dict)

        st.session_state["corr_result"] = corr_result

    if corr_result is None:
        st.info("Configure settings in the sidebar and click **Run Correlation Analysis**.")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("HHI (Concentration)", f"{corr_result.herfindahl_index:.3f}")
    col2.metric("Effective N", f"{corr_result.effective_n:.1f}")
    col3.metric("Diversification Ratio", f"{corr_result.diversification_ratio:.2f}")
    col4.metric("Avg Pairwise Corr", f"{corr_result.avg_pairwise_correlation:.2f}")

    from finbot.services.portfolio_analytics.viz import plot_correlation_heatmap as _plot_corr
    from finbot.services.portfolio_analytics.viz import plot_diversification_weights as _plot_wts

    st.plotly_chart(_plot_corr(corr_result), use_container_width=True)
    st.plotly_chart(_plot_wts(corr_result), use_container_width=True)

    st.subheader("Per-Asset Volatility")
    vol_rows = [{"Asset": a, "Annualized Vol": f"{v:.1%}"} for a, v in corr_result.individual_vols.items()]
    vol_rows.append({"Asset": "Portfolio", "Annualized Vol": f"{corr_result.portfolio_vol:.1%}"})
    st.dataframe(pd.DataFrame(vol_rows), use_container_width=True)
