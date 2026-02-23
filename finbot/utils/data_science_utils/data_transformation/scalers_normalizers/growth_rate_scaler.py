"""Growth rate scaling for removing compounding growth trends from time series.

Removes the constant growth rate trend from time series data by computing the
average growth rate from first to last value, then dividing out the cumulative
effect. Useful for detrending exponentially growing series to analyze
deviations from the long-term growth rate.

Typical usage:
    ```python
    # Remove growth trend from stock prices
    scaler = GrowthRateScaler()
    detrended = scaler.fit_transform(stock_prices)
    # Result shows deviations from constant growth path

    # Reverse the transformation
    original = scaler.inverse_transform(detrended)
    ```

How growth rate scaling works:
    1. Calculate annualized growth rate: `g = (last / first)^(1/(n-1)) - 1`
    2. Compute expected growth path: `(1 + g)^t` for each time step t
    3. Divide actual values by expected growth path
    4. Result shows ratio of actual to trend (1.0 = on trend)

Growth rate formula:
    ```
    growth_rate = (X[-1] / X[0]) ^ (1 / (len(X) - 1)) - 1
    cumulative_growth = (1 + growth_rate) ^ range(len(X))
    scaled = X / cumulative_growth
    ```

Features:
    - Automatically computes growth rate from data
    - Full inverse_transform support
    - Removes exponential growth trend
    - Preserves pandas index
    - sklearn-compatible API via BaseScaler

Use cases:
    - Detrending exponentially growing stock prices
    - Analyzing GDP/population growth deviations
    - Removing user/revenue growth trends
    - Identifying growth anomalies
    - Preparing exponential data for linear models

Example interpretation:
    ```python
    scaler = GrowthRateScaler()
    detrended = scaler.fit_transform(prices)

    # If scaler.growth_rate_ = 0.10 (10% annual growth):
    # detrended > 1.0: Growing faster than 10% trend
    # detrended < 1.0: Growing slower than 10% trend
    # detrended == 1.0: Exactly on 10% growth trend

    # Identify periods of above/below trend growth
    above_trend = detrended[detrended > 1.05]  # 5% above trend
    below_trend = detrended[detrended < 0.95]  # 5% below trend
    ```

Advantages:
    - Simple one-parameter model
    - Full invertibility
    - Interpretable (ratio to trend line)
    - Automatic growth rate estimation

Limitations:
    - **Assumes constant growth rate** (may not fit all data)
    - **First value must be non-zero** (raises ValueError)
    - Sensitive to first and last values (outliers affect growth rate)
    - Not suitable for data with changing growth regimes

Error handling:
    - ValueError if first value is zero (division by zero)
    - TypeError if data is non-numeric
    - RuntimeError if transform called before fit

Best practices:
    - Verify constant growth assumption is reasonable
    - Check for outliers in first/last values
    - Visualize fitted growth rate against data
    - Consider trimming data before fitting if endpoints are anomalous

Comparison to other scalers:
    - **vs MAScaler**: GrowthRate removes global trend, MA removes local trend
    - **vs LogarithmicScaler**: GrowthRate assumes exponential, Log compresses all scales
    - **vs SimpleScaler**: GrowthRate handles compounding, Simple uses static reference

Related modules: MAScaler (local trend removal), LogarithmicScaler (log
transform), SimpleScaler (statistical scaling), rebase_cumu_pct_change
(cumulative returns).
"""

from __future__ import annotations

# ruff: noqa: N803 - Using sklearn naming convention (X for data parameter)
import pandas as pd

from finbot.utils.data_science_utils.data_transformation.scalers_normalizers._base_scaler import BaseScaler


class GrowthRateScaler(BaseScaler):
    """
    A scaler that applies growth rate scaling to a pandas Series.
    The growth rate is calculated based on the first and last elements of the Series.
    """

    def __init__(self) -> None:
        """
        Initializes the GrowthRateScaler.
        """
        self.growth_rate_: None | float = None

    def fit(self, X: pd.Series[int | float]) -> GrowthRateScaler:
        """
        Computes the growth rate based on the provided Series.

        Parameters:
            X (pd.Series): The data series used to compute the growth rate.

        Returns:
            GrowthRateScaler: The instance itself, with the growth rate computed.

        Raises:
            ValueError: If X is not a non-empty pandas Series or if the initial value of X is zero.
        """
        if not isinstance(X, pd.Series) or X.empty:
            raise ValueError("X must be a non-empty pandas Series.")
        if X.iloc[0] == 0:
            raise ValueError("Initial value of series must be non-zero for growth rate calculation.")
        if not (isinstance(X.iloc[0], int | float) and isinstance(X.iloc[-1], int | float)):
            raise TypeError("X must contain numerical data for growth rate calculation.")

        self.growth_rate_ = (X.iloc[-1] / X.iloc[0]) ** (1 / (len(X) - 1)) - 1
        return self

    def transform(self, X: pd.Series[int | float]) -> pd.Series:
        """
        Applies the growth rate scaling to the Series.

        Parameters:
            X (pd.Series): The data series to which the scaling is applied.

        Returns:
            pd.Series: The scaled series.

        Raises:
            ValueError: If X is not a non-empty pandas Series.
            RuntimeError: If the scaler is not fitted before transformation.
        """
        if not isinstance(X, pd.Series) or X.empty:
            raise ValueError("X must be a non-empty pandas Series.")
        if self.growth_rate_ is None:
            raise RuntimeError("GrowthRateScaler must be fit before transform.")

        _growth_mult = 1 + self.growth_rate_
        _cumu_prod_growth = _growth_mult ** pd.Series(range(len(X)), index=X.index)

        return X / _cumu_prod_growth

    def fit_transform(self, X: pd.Series[int | float]) -> pd.Series:
        """
        Fits the scaler to the Series and then transforms it.

        Parameters:
            X (pd.Series): The data series to fit and transform.

        Returns:
            pd.Series: The scaled series.
        """
        return self.fit(X).transform(X)

    def reset(self) -> None:
        """
        Reset the scaler to its initial state.
        """
        self.growth_rate_ = None

    def inverse_transform(self, X: pd.Series[int | float]) -> pd.Series:
        """
        Reverses the growth rate scaling applied to the Series.

        Parameters:
            X (pd.Series): The scaled data series to reverse the scaling.

        Returns:
            pd.Series: The series with the scaling reversed.

        Raises:
            RuntimeError: If the scaler is not fitted before calling this method.
        """
        if self.growth_rate_ is None:
            raise RuntimeError("GrowthRateScaler must be fit before inverse transform.")

        _inverse_growth_mult = 1 / (1 + self.growth_rate_)
        _cumu_prod_inverse_growth = _inverse_growth_mult ** pd.Series(range(len(X)), index=X.index)

        return X * _cumu_prod_inverse_growth


if __name__ == "__main__":
    from finbot.constants.data_constants import DEMO_DATA
    from finbot.utils.plotting_utils.interactive.interactive_plotter import InteractivePlotter

    close_series = DEMO_DATA["Close"]

    examples = {"Default": GrowthRateScaler().fit_transform(close_series)}

    plotter = InteractivePlotter()
    plotter.plot_time_series(pd.DataFrame(examples), title="GrowthRateScaler")
