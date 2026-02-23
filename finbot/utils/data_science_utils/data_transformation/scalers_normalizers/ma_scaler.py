"""Moving Average (MA) scaler for detrending time series data.

Scales time series by dividing by its moving average, effectively detrending
the data and highlighting deviations from the local trend. Useful for removing
trend effects while preserving cyclical patterns and anomalies.

Typical usage:
    ```python
    # Scale by 20-period moving average
    scaler = MAScaler(window_size=20)
    scaled_series = scaler.fit_transform(prices)
    # Result shows ratio of price to 20-period MA

    # Longer window = smoother trend, more stable scaling
    scaler_long = MAScaler(window_size=200)
    scaled_long = scaler_long.fit_transform(prices)
    ```

How MA scaling works:
    1. Compute moving average with specified window_size
    2. Divide original series by moving average
    3. Result shows deviations from local trend
    4. Values > 1: above moving average
    5. Values < 1: below moving average

Parameters:
    - window_size: Number of periods for moving average (default: 5)
      - Smaller window: more responsive, captures short-term deviations
      - Larger window: smoother, captures longer-term trends

Features:
    - Detrending without removing data points
    - Preserves cyclical patterns and anomalies
    - No fitting required (transform is stateless)
    - Works with pandas Series (preserves index)
    - sklearn-compatible API via BaseScaler

Use cases:
    - Technical analysis (price relative to moving average)
    - Detecting overbought/oversold conditions
    - Removing trend before machine learning
    - Cyclical pattern analysis
    - Mean reversion trading signals

Example interpretation:
    ```python
    scaler = MAScaler(window_size=50)
    scaled = scaler.fit_transform(stock_prices)

    # scaled > 1.0: Price above 50-day MA (bullish signal)
    # scaled < 1.0: Price below 50-day MA (bearish signal)
    # scaled == 1.0: Price exactly at 50-day MA

    # Extreme values indicate strong deviations
    overbought = scaled[scaled > 1.10]  # 10% above MA
    oversold = scaled[scaled < 0.90]  # 10% below MA
    ```

Window size selection guidelines:
    - 5-10: Very short-term (daily noise)
    - 20-50: Short-term trend (weeks/months)
    - 100-200: Medium-term trend (months/year)
    - 250+: Long-term trend (years)

Advantages:
    - Simple and interpretable
    - Automatic trend removal
    - Highlights local deviations
    - No parameter fitting needed

Limitations:
    - **Inverse transform not implemented** (division by MA is not easily reversible)
    - First window_size values will have NaN (MA not yet computable)
    - Sensitive to window_size choice
    - Not suitable for non-stationary data with regime changes

Best practices:
    - Choose window_size based on frequency of data and analysis goals
    - Visualize scaled data to verify appropriate detrending
    - Be aware of leading NaN values from MA calculation
    - Consider combining with other transformations

Related modules: SimpleScaler (statistical scaling), LogarithmicScaler (log
transformation), GrowthRateScaler (growth rate removal), data_smoothing
(moving average methods).
"""

from __future__ import annotations

# ruff: noqa: N803 - Using sklearn naming convention (X for data parameter)
import pandas as pd

from finbot.utils.data_science_utils.data_transformation.data_smoothing import DataSmoother
from finbot.utils.data_science_utils.data_transformation.scalers_normalizers._base_scaler import BaseScaler


class MAScaler(BaseScaler):
    """
    MAScaler scales features based on a moving average applied to a pandas Series.

    Attributes:
        window_size (int): The size of the moving average window.
    """

    def __init__(self, window_size: int = 5):
        super().__init__()
        if not isinstance(window_size, int) or window_size <= 0:
            raise ValueError("window_size must be a positive integer.")
        self.window_size = window_size

    def fit(self, *args: object, **kwargs: object) -> MAScaler:
        """
        This operation has no effect for this scaler but is present for API consistency.
        """
        return self

    def transform(self, X: pd.Series) -> pd.Series:
        """
        Scales features of X based on a moving average.

        Parameters:
            X (pd.Series): Data to scale.

        Returns:
            pd.Series: Scaled data.
        """
        if not isinstance(X, pd.Series) or X.empty:
            raise ValueError("X must be a non-empty pandas Series.")

        smoother = DataSmoother(X)
        smoothed_ma = smoother.moving_average(window_size=self.window_size)
        return X / smoothed_ma

    def fit_transform(self, X: pd.Series) -> pd.Series:
        """
        Fit to data, then transform it.

        Parameters:
            X (pd.Series): Data to scale.

        Returns:
            pd.Series: Scaled data.
        """
        return self.fit().transform(X)

    def inverse_transform(self, X: pd.Series) -> pd.Series:
        """
        Reverses the scaling applied to the Series.

        Parameters:
            X (pd.Series): The scaled data series to reverse the scaling.

        Returns:
            pd.Series: The series with the scaling reversed.

        Raises:
            NotImplementedError: Inverse transformation for moving average scaling is not straightforward and may not be meaningful.
        """
        raise NotImplementedError("Inverse transformation is not implemented for moving average scaling.")

    def reset(self) -> None:
        """
        Reset the normalizer to its initial state.
        """
        self.scaler = None
        self.lambda_ = None
        self.mean_ = None
        self.range_ = None


if __name__ == "__main__":
    from finbot.constants.data_constants import DEMO_DATA
    from finbot.utils.plotting_utils.interactive.interactive_plotter import InteractivePlotter

    close_series = DEMO_DATA["Close"]

    examples = {
        f"Window: {w}": MAScaler(window_size=w).fit_transform(close_series) for w in (1, 5, 20, 50, 250, 1250, 2500)
    }

    plotter = InteractivePlotter()
    concatted = pd.concat(examples.values(), axis=1)
    concatted.columns = pd.Index(examples.keys())
    plotter.plot_time_series(concatted)
