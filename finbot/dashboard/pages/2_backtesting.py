"""Backtesting — Strategy backtester with interactive configuration."""

from __future__ import annotations

from typing import Any

import backtrader as bt
import pandas as pd
import streamlit as st

from finbot.dashboard.components.charts import create_drawdown_chart, create_time_series_chart
from finbot.dashboard.components.sidebar import asset_selector, date_range_selector
from finbot.services.backtesting.backtest_runner import BacktestRunner
from finbot.services.backtesting.brokers.commission_schemes import CommInfo_NoCommission
from finbot.services.backtesting.strategies.dip_buy_sma import DipBuySMA
from finbot.services.backtesting.strategies.dip_buy_stdev import DipBuyStdev
from finbot.services.backtesting.strategies.dual_momentum import DualMomentum
from finbot.services.backtesting.strategies.macd_dual import MACDDual
from finbot.services.backtesting.strategies.macd_single import MACDSingle
from finbot.services.backtesting.strategies.no_rebalance import NoRebalance
from finbot.services.backtesting.strategies.rebalance import Rebalance
from finbot.services.backtesting.strategies.risk_parity import RiskParity
from finbot.services.backtesting.strategies.sma_crossover import SMACrossover
from finbot.services.backtesting.strategies.sma_crossover_double import SMACrossoverDouble
from finbot.services.backtesting.strategies.sma_crossover_triple import SMACrossoverTriple
from finbot.services.backtesting.strategies.sma_rebal_mix import SmaRebalMix

st.set_page_config(page_title="Backtesting — Finbot", layout="wide")
st.title("Strategy Backtester")
st.markdown("Run backtests with different strategies and parameters.")

STRATEGIES: dict[str, Any] = {
    "NoRebalance": NoRebalance,
    "Rebalance": Rebalance,
    "SMACrossover": SMACrossover,
    "SMACrossoverDouble": SMACrossoverDouble,
    "SMACrossoverTriple": SMACrossoverTriple,
    "MACDSingle": MACDSingle,
    "MACDDual": MACDDual,
    "DipBuySMA": DipBuySMA,
    "DipBuyStdev": DipBuyStdev,
    "SmaRebalMix": SmaRebalMix,
    "DualMomentum": DualMomentum,
    "RiskParity": RiskParity,
}

# Sidebar controls
st.sidebar.header("Configuration")
ticker = asset_selector("Asset")
strategy_name = st.sidebar.selectbox("Strategy", list(STRATEGIES.keys()))
start_date, end_date = date_range_selector()
init_cash = st.sidebar.number_input("Initial Cash ($)", value=10000, min_value=100, step=1000)

# Strategy-specific parameters
st.sidebar.markdown("### Strategy Parameters")
strat_kwargs: dict[str, Any] = {}

if strategy_name == "NoRebalance":
    strat_kwargs["equity_proportions"] = (1.0,)

elif strategy_name == "Rebalance":
    strat_kwargs["rebal_proportions"] = (1.0,)
    strat_kwargs["rebal_interval"] = st.sidebar.number_input("Rebalance Interval (days)", value=63, min_value=1)

elif strategy_name in ("SMACrossover", "SMACrossoverDouble"):
    strat_kwargs["fast_ma"] = st.sidebar.number_input("Fast MA Period", value=50, min_value=2)
    strat_kwargs["slow_ma"] = st.sidebar.number_input("Slow MA Period", value=200, min_value=2)

elif strategy_name in ("SMACrossoverTriple", "DipBuySMA", "SmaRebalMix"):
    strat_kwargs["fast_ma"] = st.sidebar.number_input("Fast MA Period", value=20, min_value=2)
    strat_kwargs["med_ma"] = st.sidebar.number_input("Medium MA Period", value=50, min_value=2)
    strat_kwargs["slow_ma"] = st.sidebar.number_input("Slow MA Period", value=200, min_value=2)

elif strategy_name in ("MACDSingle", "MACDDual"):
    strat_kwargs["fast_ma"] = st.sidebar.number_input("Fast MA Period", value=12, min_value=2)
    strat_kwargs["slow_ma"] = st.sidebar.number_input("Slow MA Period", value=26, min_value=2)
    strat_kwargs["signal_period"] = st.sidebar.number_input("Signal Period", value=9, min_value=1)

elif strategy_name == "DipBuyStdev":
    strat_kwargs["buy_quantile"] = st.sidebar.slider("Buy Quantile", 0.0, 1.0, 0.1)
    strat_kwargs["sell_quantile"] = st.sidebar.slider("Sell Quantile", 0.0, 1.0, 1.0)

elif strategy_name == "DualMomentum":
    strat_kwargs["lookback"] = st.sidebar.number_input("Lookback Period", value=252, min_value=21)
    strat_kwargs["rebal_interval"] = st.sidebar.number_input("Rebalance Interval (days)", value=21, min_value=1)
    st.sidebar.info("Requires 2 assets. Add a safe asset (e.g., TLT) as the second ticker below.")
    alt_ticker = st.sidebar.text_input("Safe/Alternative Asset", value="TLT").upper()

elif strategy_name == "RiskParity":
    strat_kwargs["vol_window"] = st.sidebar.number_input("Volatility Window", value=63, min_value=10)
    strat_kwargs["rebal_interval"] = st.sidebar.number_input("Rebalance Interval (days)", value=21, min_value=1)
    st.sidebar.info("Requires 2+ assets. Add a second ticker below.")
    alt_ticker = st.sidebar.text_input("Second Asset", value="TLT").upper()


@st.cache_data(ttl=3600)
def _load_prices(symbol: str) -> pd.DataFrame:
    from finbot.utils.data_collection_utils.yfinance.get_history import get_history

    return get_history(symbol)


# Run button
run = st.sidebar.button("Run Backtest", type="primary")

if run:
    with st.spinner("Running backtest..."):
        try:
            price_df = _load_prices(ticker)
            start_ts = pd.Timestamp(start_date)
            end_ts = pd.Timestamp(end_date)

            # Build price histories dict (multi-asset for DualMomentum/RiskParity)
            price_histories = {ticker: price_df}
            if strategy_name in ("DualMomentum", "RiskParity") and alt_ticker:
                price_histories[alt_ticker] = _load_prices(alt_ticker)

            runner = BacktestRunner(
                price_histories=price_histories,
                start=start_ts,
                end=end_ts,
                duration=None,
                start_step=None,
                init_cash=float(init_cash),
                strat=STRATEGIES[strategy_name],
                strat_kwargs=strat_kwargs,
                broker=bt.brokers.BackBroker,
                broker_kwargs={},
                broker_commission=CommInfo_NoCommission,
                sizer=bt.sizers.AllInSizer,
                sizer_kwargs={},
                plot=False,
            )
            stats_df = runner.run_backtest()
            value_hist = runner.get_value_history()

            st.session_state["bt_stats"] = stats_df
            st.session_state["bt_value_hist"] = value_hist
            st.session_state["bt_ticker"] = ticker
            st.session_state["bt_strategy"] = strategy_name
        except Exception as e:
            st.error(f"Backtest failed: {e}")

# Display results if available
if "bt_stats" in st.session_state:
    stats_df = st.session_state["bt_stats"]
    value_hist = st.session_state["bt_value_hist"]

    st.markdown(f"### Results: {st.session_state['bt_strategy']} on {st.session_state['bt_ticker']}")

    # Key metric cards
    def _safe_get(col: str) -> Any:
        return stats_df[col].iloc[0] if col in stats_df.columns else "N/A"

    c1, c2, c3, c4 = st.columns(4)
    cagr = _safe_get("CAGR")
    sharpe = _safe_get("Sharpe")
    max_dd = _safe_get("Max Drawdown")
    roi = _safe_get("ROI")

    c1.metric("CAGR", f"{cagr:.2%}" if isinstance(cagr, float) else str(cagr))
    c2.metric("Sharpe", f"{sharpe:.3f}" if isinstance(sharpe, float) else str(sharpe))
    c3.metric("Max Drawdown", f"{max_dd:.2%}" if isinstance(max_dd, float) else str(max_dd))
    c4.metric("ROI", f"{roi:.2%}" if isinstance(roi, float) else str(roi))

    # Portfolio value chart
    st.plotly_chart(
        create_time_series_chart(
            {"Portfolio Value": value_hist["Value"]},
            "Portfolio Value Over Time",
            y_label="Value ($)",
        ),
        use_container_width=True,
    )

    # Drawdown chart
    st.plotly_chart(
        create_drawdown_chart(value_hist["Value"], "Portfolio Drawdown"),
        use_container_width=True,
    )

    # Full stats table
    st.markdown("### Full Statistics")
    st.dataframe(stats_df.T.rename(columns={0: "Value"}), use_container_width=True)
else:
    st.info("Configure parameters and click **Run Backtest** to see results.")
