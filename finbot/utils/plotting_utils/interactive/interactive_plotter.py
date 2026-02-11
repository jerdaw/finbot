"""Interactive plotly-based visualizations for financial time series data.

Provides a simple, consistent interface for creating interactive plots of
time series data using plotly. Designed for financial data visualization
with sensible defaults and flexible customization.

Typical usage:
    ```python
    import pandas as pd
    from finbot.utils.plotting_utils.interactive.interactive_plotter import InteractivePlotter

    # Prepare data
    df = pd.DataFrame(
        {
            "Date": pd.date_range("2020-01-01", periods=100),
            "SPY": [100 + i * 0.5 for i in range(100)],
            "QQQ": [200 + i * 0.8 for i in range(100)],
        }
    ).set_index("Date")

    # Create plotter
    plotter = InteractivePlotter()

    # Plot single time series
    plotter.plot_time_series(df["SPY"], title="SPY Price History")

    # Plot multiple time series
    plotter.plot_time_series(df, title="SPY vs QQQ")

    # Plot with custom columns
    plotter.plot_time_series(df, value_cols=["SPY"], title="SPY Only")

    # Scatter plot
    plotter.plot_scatter(df, x_col="SPY", y_col="QQQ", title="SPY vs QQQ Correlation")

    # Histogram
    plotter.plot_histogram(df["SPY"], title="SPY Returns Distribution")
    ```

Plot types:

1. **plot_time_series()**: Line plots for time series
   - Single or multiple series
   - Uses index as x-axis by default
   - Interactive zoom, pan, hover

2. **plot_multiple_series()**: Multiple overlaid line plots
   - Alternative to plot_time_series with go.Figure
   - More control over individual series
   - Custom legends and colors

3. **plot_scatter()**: Scatter plots
   - X-Y relationships
   - Correlation visualization
   - Interactive point inspection

4. **plot_histogram()**: Distribution visualization
   - Value frequency/distribution
   - Configurable bins
   - Useful for returns analysis

Features:
    - Interactive plots (zoom, pan, hover, export)
    - Automatic index handling (uses df.index if time_col=None)
    - Works with both DataFrame and Series
    - Sensible default titles and labels
    - Browser-based rendering (opens in browser)
    - Export to PNG/SVG (via plotly toolbar)

Interactive features (plotly):
    - Zoom: Click and drag to zoom
    - Pan: Drag while holding shift
    - Reset: Double-click to reset view
    - Hover: Detailed information on data points
    - Legend: Click to show/hide series
    - Export: Download as PNG/SVG
    - Range selector: Drag to select time range

Use cases:
    - Exploratory data analysis
    - Visualizing backt test results
    - Comparing multiple strategies/assets
    - Analyzing price histories
    - Portfolio performance visualization
    - Correlation analysis
    - Distribution analysis (returns, drawdowns)

Example workflows:
    ```python
    # Visualize backtest results
    plotter = InteractivePlotter()
    results = run_backtest(strategy, data)
    plotter.plot_time_series(results["portfolio_value"], title="Portfolio Value Over Time")

    # Compare multiple strategies
    all_results = pd.DataFrame(
        {"Strategy A": strategy_a_results, "Strategy B": strategy_b_results, "Benchmark": benchmark_results}
    )
    plotter.plot_time_series(all_results, title="Strategy Comparison")

    # Analyze returns distribution
    returns = calculate_returns(prices)
    plotter.plot_histogram(returns, bins=50, title="Returns Distribution")

    # Correlation analysis
    plotter.plot_scatter(df, x_col="SPY", y_col="TLT", title="SPY vs TLT Correlation")
    ```

Default behavior:
    - time_col=None: Uses DataFrame/Series index
    - value_cols=None: Plots all columns
    - series_cols=None: Plots all columns
    - Automatic column name extraction from Series
    - Opens plot in default browser

Advantages over matplotlib:
    - Interactive (zoom, pan, hover)
    - No need for plt.show()
    - Better for exploratory analysis
    - Easier multiple series handling
    - Built-in export functionality
    - Modern, polished appearance

Limitations:
    - Requires browser for display
    - Not suitable for static reports (use matplotlib)
    - Performance degrades with >100K points
    - No 3D plots (use plotly.graph_objects directly)

Performance:
    - Fast for typical financial data (<10K points)
    - Responsive interactivity
    - Browser rendering (GPU accelerated)

Why plotly:
    - Industry standard for interactive visualization
    - Rich ecosystem and documentation
    - Works well with pandas
    - No explicit show() call needed
    - Professional appearance

Dependencies: pandas, plotly (plotly.express, plotly.graph_objects)

Related modules: backtesting (generates data to plot), simulation (generates
price histories), monte_carlo (visualization of trials).
"""

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class InteractivePlotter:
    def __init__(self):
        # Initialization, if needed
        pass

    def plot_time_series(
        self,
        df: pd.DataFrame | pd.Series,
        time_col: None | str = None,
        value_cols: None | list[str | None] = None,
        title: str = "Time Series Plot",
    ) -> None:
        """
        Creates an interactive time series plot.

        :param df: pandas DataFrame or Series containing the data.
        :param time_col: String, the name of the column with time data. If None, df.index is used.
        :param value_cols: List of strings, names of columns to plot. If None, all columns are used.
        :param title: String, the title of the plot.
        """
        x_values = df.index if time_col is None else df[time_col]
        if value_cols is None:
            value_cols = (
                [str(df.name) if df.name is not None else None]
                if isinstance(df, pd.Series)
                else [str(c) for c in df.columns]
            )

        fig = px.line(df, x=x_values, y=value_cols)
        fig.update_layout(title=title, xaxis_title="Time", yaxis_title="Values")
        fig.show()

    def plot_multiple_series(
        self,
        df: pd.DataFrame | pd.Series,
        time_col: None | str = None,
        series_cols: None | list[str] = None,
        title: str = "Multiple Time Series Plot",
    ) -> None:
        """
        Plots multiple time series in one graph.

        :param df: pandas DataFrame or Series.
        :param time_col: String, the time column. If None, df.index is used.
        :param series_cols: List of strings, the columns representing different series. If None, all columns are used.
        :param title: String, the title of the plot.
        """
        x_values = df.index if time_col is None else df[time_col]
        if series_cols is None:
            series_cols = [str(df.name)] if isinstance(df, pd.Series) else [str(c) for c in df.columns]

        fig = go.Figure()
        for col in series_cols:
            fig.add_trace(go.Scatter(x=x_values, y=df[col], mode="lines", name=col))
        fig.update_layout(title=title, xaxis_title="Time", yaxis_title="Value")
        fig.show()

    def plot_scatter(
        self,
        df: pd.DataFrame | pd.Series,
        x_col: None | str = None,
        y_col: None | str = None,
        title: str = "Scatter Plot",
    ) -> None:
        """
        Creates an interactive scatter plot for time series data.

        :param df: pandas DataFrame or Series.
        :param x_col: String, the x-axis column (time).
        :param y_col: String, the y-axis column (value).
        :param title: String, the title of the plot.
        """
        x_values = df.index if x_col is None else df[x_col]
        y_col_names = (
            [str(df.name)] if isinstance(df, pd.Series) else [str(c) for c in df.columns] if y_col is None else [y_col]
        )
        fig = px.scatter(df, x=x_values, y=y_col_names)
        fig.update_layout(title=title, xaxis_title=x_col, yaxis_title=y_col)
        fig.show()

    def plot_histogram(
        self,
        df: pd.DataFrame | pd.Series,
        column: None | str = None,
        bins: None | int = None,
        title: str = "Histogram",
    ) -> None:
        """
        Visualizes the distribution of values over time.

        :param df: pandas DataFrame or Series.
        :param column: String, the column to plot.
        :param bins: Integer, number of bins (optional).
        :param title: String, the title of the plot.
        """
        if column is None:
            column = str(df.name) if isinstance(df, pd.Series) else str(df.columns[0])

        fig = px.histogram(df, x=column, nbins=bins)
        fig.update_layout(title=title, xaxis_title=column, yaxis_title="Frequency")
        fig.show()

    def plot_heatmap(self, df: pd.DataFrame, title: str = "Correlation Heatmap Plot") -> None:
        """
        Shows correlation between different time series.

        :param df: pandas DataFrame.
        :param title: String, the title of the plot.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("plot_heatmap requires a pandas DataFrame as input.")

        correlation_matrix = df.corr()
        fig = go.Figure(data=go.Heatmap(z=correlation_matrix, x=df.columns, y=df.columns))
        fig.update_layout(title=title)
        fig.show()

    def plot_candlestick(
        self,
        df: pd.DataFrame,
        time_col: None | str = None,
        open_col: str = "Open",
        high_col: str = "High",
        low_col: str = "Low",
        close_col: str = "Close",
        title: str = "Candlestick Plot",
    ) -> None:
        """
        Creates a candlestick plot, commonly used for financial data.

        :param df: pandas DataFrame.
        :param time_col: String, the time column. If None, df.index is used.
        :param open_col: String, the open value column.
        :param high_col: String, the high value column.
        :param low_col: String, the low value column.
        :param close_col: String, the close value column.
        :param title: String, the title of the plot.
        """
        x_values = df.index if time_col is None else df[time_col]

        fig = go.Figure(
            data=[
                go.Candlestick(x=x_values, open=df[open_col], high=df[high_col], low=df[low_col], close=df[close_col]),
            ],
        )
        fig.update_layout(title=title, xaxis_title="Time", yaxis_title="Price")
        fig.show()

    def plot_bar_chart(self, df: pd.DataFrame, x_col: str, y_col: str, title: str = "Bar Chart") -> None:
        """
        Creates an interactive bar chart to visualize numeric score data using a pandas DataFrame.

        :param df: pandas DataFrame containing the data.
        :param x_col: String, the column name for the x-axis (identifiers).
        :param y_col: String, the column name for the y-axis (scores).
        :param title: String, the title of the plot.
        """
        # Validating DataFrame
        if x_col not in df.columns or y_col not in df.columns:
            raise ValueError("Specified columns do not exist in the DataFrame")

        # Creating a bar chart
        fig = px.bar(df, x=x_col, y=y_col)

        # Customizing the chart
        fig.update_layout(title=title, xaxis_title=x_col, yaxis_title=y_col, showlegend=False)

        fig.show()

    @staticmethod
    def mark_plot(fig: go.Figure, data: pd.DataFrame | pd.Series, marker_specs: dict[Any, dict[str, Any]]) -> None:
        """
        Adds markers to a plot based on specified conditions.

        :param fig: Plotly figure object to which markers will be added.
        :param data: pandas DataFrame or Series with the data.
        :param marker_specs: A dictionary where keys are conditions (expressed as boolean masks or callable functions)
                             and values are dictionaries with marker styles.
        :raises TypeError: If provided data types are incorrect.
        """
        if not isinstance(fig, go.Figure):
            raise TypeError("fig must be a Plotly graph_objects.Figure")
        if not isinstance(data, pd.DataFrame | pd.Series):
            raise TypeError("data must be a pandas DataFrame or Series")

        for condition, style in marker_specs.items():
            # Check if condition is a function and apply it, else use it directly
            marker_data = data[condition(data)] if callable(condition) else data[condition]

            # Add markers to the figure
            fig.add_trace(go.Scatter(x=marker_data.index, y=marker_data.values, mode="markers", **style))

    @staticmethod
    def export_plot(fig: go.Figure, filename: str, file_format: str = "png") -> None:
        """
        Exports the plot to a file.

        :param fig: Plotly figure object.
        :param filename: String, the name of the file to save.
        :param file_format: String, file format (e.g., 'png', 'jpeg', 'svg', 'html').
        """
        if file_format == "html":
            fig.write_html(f"{filename}.html")
        else:
            fig.write_image(f"{filename}.{file_format}")


if __name__ == "__main__":
    # Example usage
    from collections import Counter

    from finbot.constants.data_constants import DEMO_DATA

    OHLC = DEMO_DATA[["Open", "High", "Low", "Close"]]
    CLOSE = DEMO_DATA["Close"]
    _CHANGE = CLOSE.pct_change().dropna()
    _CHANGE.name = "% Change"
    CHANGE = pd.DataFrame(_CHANGE)
    OUTLIERS = pd.DataFrame(dict(Counter(round(c[0], 3) for c in CHANGE.values)), index=["Frequency"]).T
    OUTLIERS.index.name = "Change"
    OUTLIERS.reset_index(inplace=True)
    OUTLIERS = OUTLIERS[OUTLIERS["Frequency"] <= 1].dropna()

    plotter = InteractivePlotter()

    plotter.plot_time_series(CLOSE)
    plotter.plot_multiple_series(OHLC)
    plotter.plot_candlestick(OHLC)
    plotter.plot_scatter(CLOSE)
    plotter.plot_histogram(CHANGE)
    plotter.plot_heatmap(OHLC)
    plotter.plot_bar_chart(OUTLIERS, x_col="Change", y_col="Frequency")
