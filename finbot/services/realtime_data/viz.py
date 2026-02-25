"""Real-time data visualisation functions.

All functions return ``plotly.graph_objects.Figure`` objects.  They are
designed to be used stand-alone or embedded in the Streamlit dashboard.
Never call ``.show()``; the caller handles display.

Colours follow the Wong (2011) colour-blind-safe palette.
"""

from __future__ import annotations

import plotly.graph_objects as go

from finbot.core.contracts.realtime_data import ProviderStatus, Quote

_BLUE = "#0072B2"
_ORANGE = "#D55E00"
_GREEN = "#009E73"
_RED = "#D55E00"
_LIGHT_BLUE = "#56B4E9"


def plot_quote_table(quotes: list[Quote], *, title: str | None = None) -> go.Figure:
    """Table figure displaying live quote data for multiple symbols.

    Args:
        quotes: List of ``Quote`` objects to display.
        title: Optional figure title.

    Returns:
        Plotly ``Figure`` with a styled table.
    """
    if not quotes:
        fig = go.Figure()
        fig.update_layout(title=title or "No Quotes Available")
        return fig

    symbols = [q.symbol for q in quotes]
    prices = [f"{q.price:.2f}" for q in quotes]
    changes = [f"{q.change:+.2f}" if q.change is not None else "N/A" for q in quotes]
    change_pcts = [f"{q.change_percent:+.2f}%" if q.change_percent is not None else "N/A" for q in quotes]
    volumes = [f"{q.volume:,}" if q.volume is not None else "N/A" for q in quotes]
    providers = [q.provider.value for q in quotes]
    times = [q.timestamp.strftime("%H:%M:%S") for q in quotes]

    # Color change cells
    change_colors = []
    for q in quotes:
        if q.change is not None and q.change > 0:
            change_colors.append("#c6efce")  # green tint
        elif q.change is not None and q.change < 0:
            change_colors.append("#ffc7ce")  # red tint
        else:
            change_colors.append("white")

    fig = go.Figure(
        go.Table(
            header={
                "values": ["Symbol", "Price", "Change", "Change %", "Volume", "Provider", "Time"],
                "fill_color": _BLUE,
                "font": {"color": "white", "size": 12},
                "align": "center",
            },
            cells={
                "values": [symbols, prices, changes, change_pcts, volumes, providers, times],
                "fill_color": [
                    ["white"] * len(quotes),
                    ["white"] * len(quotes),
                    change_colors,
                    change_colors,
                    ["white"] * len(quotes),
                    ["white"] * len(quotes),
                    ["white"] * len(quotes),
                ],
                "align": "center",
                "font": {"size": 11},
            },
        )
    )
    fig.update_layout(title=title or "Live Quotes", height=max(200, 50 + 30 * len(quotes)))
    return fig


def plot_sparkline(
    prices: list[float],
    *,
    symbol: str = "",
    title: str | None = None,
) -> go.Figure:
    """Minimal sparkline chart for a price series.

    Args:
        prices: Sequential price values.
        symbol: Ticker symbol for labelling.
        title: Optional figure title.

    Returns:
        Plotly ``Figure`` with a compact line chart.
    """
    if not prices:
        fig = go.Figure()
        fig.update_layout(title=title or f"No data for {symbol}")
        return fig

    color = _GREEN if len(prices) >= 2 and prices[-1] >= prices[0] else _RED
    fig = go.Figure(
        go.Scatter(
            y=prices,
            mode="lines",
            line={"color": color, "width": 2},
            showlegend=False,
        )
    )
    fig.update_layout(
        title=title or f"{symbol} Intraday",
        height=200,
        margin={"l": 30, "r": 10, "t": 40, "b": 20},
        xaxis={"visible": False},
        yaxis={"visible": True, "tickformat": ".2f"},
    )
    return fig


def plot_provider_status(statuses: list[ProviderStatus], *, title: str | None = None) -> go.Figure:
    """Bar chart summarising provider health metrics.

    Displays total requests and errors for each provider, with a
    visual indicator of availability.

    Args:
        statuses: List of ``ProviderStatus`` objects.
        title: Optional figure title.

    Returns:
        Plotly ``Figure`` with grouped bars.
    """
    if not statuses:
        fig = go.Figure()
        fig.update_layout(title=title or "No Provider Data")
        return fig

    names = [s.provider.value for s in statuses]
    requests = [s.total_requests for s in statuses]
    errors = [s.total_errors for s in statuses]
    avail_text = ["Available" if s.is_available else "Unavailable" for s in statuses]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(name="Requests", x=names, y=requests, marker_color=_BLUE, text=avail_text, textposition="outside")
    )
    fig.add_trace(go.Bar(name="Errors", x=names, y=errors, marker_color=_ORANGE))
    fig.update_layout(
        barmode="group",
        title=title or "Provider Status",
        xaxis_title="Provider",
        yaxis_title="Count",
    )
    return fig
