"""Real-Time Quotes — live prices from Alpaca, Twelve Data, and yfinance."""

from __future__ import annotations

import streamlit as st

from finbot.core.contracts.realtime_data import ProviderStatus, Quote
from finbot.dashboard.disclaimer import show_sidebar_accessibility, show_sidebar_disclaimer

st.set_page_config(page_title="Real-Time Quotes — Finbot", layout="wide")

show_sidebar_disclaimer()
show_sidebar_accessibility()

st.title("Real-Time Quotes")
st.markdown(
    "Live stock and ETF prices from Alpaca (US, IEX feed), Twelve Data (US + Canada/TSX), "
    "and yfinance (fallback). Quotes are cached for 15 seconds."
)

tab1, tab2, tab3 = st.tabs(["📊 Live Quotes", "📋 Watchlist", "🔧 Provider Status"])

# ── Tab 1: Live Quotes ──────────────────────────────────────────────────────
with tab1:
    with st.sidebar:
        st.header("Quick Quote")
        symbols_input = st.text_input(
            "Symbols (comma-separated)",
            value="SPY, QQQ, TLT",
            key="live_symbols",
            placeholder="SPY, QQQ, RY.TO",
        )
        run_btn = st.button("Fetch Quotes", key="fetch_live")

    live_quotes: list[Quote] | None = st.session_state.get("live_quotes")

    if run_btn:
        symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]
        if not symbols:
            st.warning("Enter at least one symbol.")
            st.stop()

        with st.spinner("Fetching quotes..."):
            from finbot.services.realtime_data import CompositeQuoteProvider
            from finbot.services.realtime_data.viz import plot_quote_table

            provider = CompositeQuoteProvider()
            batch = provider.get_quotes(symbols)

        live_quotes = list(batch.quotes.values())
        st.session_state["live_quotes"] = live_quotes

        if live_quotes:
            fig = plot_quote_table(live_quotes, title="Live Quotes")
            st.plotly_chart(fig, use_container_width=True)

            # Show individual quote details
            cols = st.columns(min(len(live_quotes), 4))
            for i, q in enumerate(live_quotes):
                col = cols[i % len(cols)]
                with col:
                    delta = f"{q.change:+.2f} ({q.change_percent:+.2f}%)" if q.change is not None else "N/A"
                    st.metric(label=q.symbol, value=f"${q.price:.2f}", delta=delta)

        if batch.errors:
            st.warning(f"Failed to fetch: {', '.join(batch.errors.keys())}")

    elif live_quotes:
        from finbot.services.realtime_data.viz import plot_quote_table

        fig = plot_quote_table(live_quotes, title="Live Quotes (cached)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Enter symbols and click **Fetch Quotes** to view live prices.")

# ── Tab 2: Watchlist ─────────────────────────────────────────────────────────
with tab2:
    with st.sidebar:
        st.header("Watchlist")
        watchlist_input = st.text_area(
            "Watchlist symbols (one per line)",
            value="SPY\nQQQ\nTLT\nIWM\nGLD",
            key="watchlist_symbols",
            height=150,
        )
        refresh_btn = st.button("Refresh Watchlist", key="refresh_watchlist")

    watchlist_quotes: list[Quote] | None = st.session_state.get("watchlist_quotes")

    if refresh_btn:
        symbols = [s.strip().upper() for s in watchlist_input.strip().splitlines() if s.strip()]
        if not symbols:
            st.warning("Add at least one symbol to the watchlist.")
            st.stop()

        with st.spinner(f"Fetching {len(symbols)} symbols..."):
            from finbot.services.realtime_data import CompositeQuoteProvider
            from finbot.services.realtime_data.viz import plot_quote_table

            provider = CompositeQuoteProvider()
            batch = provider.get_quotes(symbols)

        watchlist_quotes = list(batch.quotes.values())
        st.session_state["watchlist_quotes"] = watchlist_quotes

        if watchlist_quotes:
            fig = plot_quote_table(watchlist_quotes, title="Watchlist")
            st.plotly_chart(fig, use_container_width=True)

        if batch.errors:
            st.warning(f"Failed: {', '.join(batch.errors.keys())}")

    elif watchlist_quotes:
        from finbot.services.realtime_data.viz import plot_quote_table

        fig = plot_quote_table(watchlist_quotes, title="Watchlist (cached)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Configure your watchlist in the sidebar and click **Refresh Watchlist**.")

# ── Tab 3: Provider Status ───────────────────────────────────────────────────
with tab3:
    check_btn = st.button("Check Provider Status", key="check_status")

    provider_statuses: list[ProviderStatus] | None = st.session_state.get("provider_statuses")

    if check_btn:
        from finbot.services.realtime_data import CompositeQuoteProvider
        from finbot.services.realtime_data.viz import plot_provider_status

        provider = CompositeQuoteProvider()
        provider_statuses = provider.get_provider_status()
        st.session_state["provider_statuses"] = provider_statuses

        fig = plot_provider_status(provider_statuses, title="Provider Health")
        st.plotly_chart(fig, use_container_width=True)

        for ps in provider_statuses:
            status_icon = "✅" if ps.is_available else "❌"
            with st.expander(f"{status_icon} {ps.provider.value.title()}"):
                st.write(f"**Available:** {ps.is_available}")
                st.write(f"**Total Requests:** {ps.total_requests}")
                st.write(f"**Total Errors:** {ps.total_errors}")
                if ps.last_success:
                    st.write(f"**Last Success:** {ps.last_success.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                if ps.last_error:
                    st.write(f"**Last Error:** {ps.last_error}")

    elif provider_statuses:
        from finbot.services.realtime_data.viz import plot_provider_status

        fig = plot_provider_status(provider_statuses, title="Provider Health (cached)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Click **Check Provider Status** to see provider availability and health.")
