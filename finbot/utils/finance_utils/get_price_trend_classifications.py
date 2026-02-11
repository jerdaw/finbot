"""Classify price trends into Growth, Decline, or Stagnation.

Uses wavelet smoothing (or HP filter) to denoise price data, then classifies
each period as Growth, Decline, or Stagnation based on smoothed percentage changes
relative to a threshold (default: mean of smoothed changes).

Provides a higher-level trend classification than simple moving averages,
with configurable smoothing parameters for different time scales.

Smoothing methods available:
    - Wavelet smoothing (default: Daubechies 7, level 4)
    - Hodrick-Prescott filter (alternative: lambda=625 for daily data)

Typical usage:
    - Identify market regimes for backtesting
    - Visualize long-term trends vs short-term noise
    - Filter trading signals based on trend direction
    - Economic cycle overlay for price data
"""

import numpy as np
import pandas as pd

from finbot.utils.data_science_utils.data_transformation.data_smoothing import DataSmoother
from finbot.utils.plotting_utils.interactive.interactive_plotter import InteractivePlotter


def classify_trends(relative_change: pd.Series, threshold: float | None = None):
    if threshold is None:
        threshold = relative_change.mean()  # Standard deviation as a threshold

    trend = pd.Series(index=relative_change.index, data=np.nan, dtype="object")

    trend[relative_change > threshold] = "Growth"  # type: ignore[call-overload]
    trend[relative_change < -threshold] = "Decline"  # type: ignore[call-overload]
    trend[abs(relative_change) <= threshold] = "Stagnation"  # type: ignore[call-overload]

    return trend


def _smooth_data(data: pd.Series, smoothing_wavelet: str = "db7", smoothing_level: int = 4):
    """
    Smooth the data using the specified wavelet and level.
    The default wavelet is Daubechies 7 and the default level is 4.
    This is chosen because it is relatively easy to set a custom wavely and level.
    However, smoother.hp_smoothing(lamb=625) arguably gives better results for daily price data.
    """
    smoother = DataSmoother(data)
    # Other options:
    # smoothed_data = smoother.hp_smoothing(lamb=625)
    # smoothed_data = smoother.wavelet_smoothing(wavelet_name="db36", level=4)
    smoothed_data = smoother.wavelet_smoothing(wavelet_name=smoothing_wavelet, level=smoothing_level)
    return smoothed_data


def get_price_trends_classifications(price_data: pd.Series, smoothing_wavelet: str = "db7", smoothing_level: int = 4):
    if not isinstance(price_data, pd.Series):
        raise ValueError("Data must be a pandas Series")

    pct_change = price_data.pct_change().fillna(0)

    smoothed_data = _smooth_data(data=pct_change, smoothing_wavelet=smoothing_wavelet, smoothing_level=smoothing_level)

    trend = classify_trends(relative_change=smoothed_data)

    return trend


def plot_trends(trend_data: pd.DataFrame, original_data: pd.Series | None = None) -> None:
    """
    Plot the original time series with classified trends using Plotly for interactivity.

    :param trend_data: pandas DataFrame containing the trend classification.
    :param original_data: pandas Series containing the original time series data.
    :raises ValueError: If data validations fail.
    """
    if original_data is not None:
        if not isinstance(original_data, pd.Series):
            raise ValueError("original_data must be a pandas Series")
        if not original_data.index.equals(trend_data.index):
            raise ValueError("Index of original_data must match index of trend_data")

    fig = go.Figure()

    # Add the time series data
    if original_data is not None:
        fig.add_trace(go.Scatter(x=trend_data.index, y=original_data.values, mode="lines", name="Time Series"))

    # Define marker specifications
    marker_specs = {
        lambda x: trend_data == "Decline": {"marker_color": "red", "name": "Decline"},
        lambda x: trend_data == "Stagnation": {"marker_color": "blue", "name": "Stagnation"},
        lambda x: trend_data == "Growth": {"marker_color": "green", "name": "Growth"},
    }

    # Add markers using the mark_plot method

    plotter = InteractivePlotter()
    plotter.mark_plot(fig, original_data if original_data is not None else trend_data, marker_specs)

    fig.update_layout(
        title="Time Series with Trend Classification",
        xaxis_title="Time",
        yaxis_title="Value",
        legend_title="Trend",
    )
    fig.show()


if __name__ == "__main__":
    import plotly.graph_objects as go

    from finbot.constants.data_constants import DEMO_DATA

    close_serie = DEMO_DATA["Close"]
    for i in ("db7", "db36"):
        for j in (4, 5):
            print(f"Smoothing wavelet: {i}, Smoothing level: {j}")
            trend_data = get_price_trends_classifications(close_serie, smoothing_wavelet=i, smoothing_level=j)
            print(trend_data)
            plot_trends(trend_data, close_serie)
            # plot_trends(trend_data)

    smoother = DataSmoother(close_serie.pct_change().fillna(0))
    smoothed_data = smoother.hp_smoothing(lamb=625)
    trend_data = classify_trends(smoothed_data)
    plot_trends(trend_data, close_serie)
