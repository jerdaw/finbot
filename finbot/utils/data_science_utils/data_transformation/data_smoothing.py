"""Comprehensive time series smoothing methods using statistical and signal processing techniques.

Provides a unified interface (DataSmoother class) for applying 10+ smoothing
techniques to pandas Series. Includes moving averages, exponential smoothing,
Kalman filtering, wavelet transforms, and more. Essential for noise reduction,
trend identification, and time series preprocessing.

Typical usage:
    ```python
    smoother = DataSmoother(data_series)

    # Simple moving average
    smoothed = smoother.moving_average(window_size=20)

    # Exponential smoothing
    smoothed = smoother.exponential_smoothing(alpha=0.3)

    # Hodrick-Prescott filter (separate trend from cycle)
    trend = smoother.hp_smoothing(lamb=1600)  # λ=1600 for quarterly data

    # Savitzky-Golay filter (preserves peaks)
    smoothed = smoother.savitzky_golay_smoothing(window_size=21, polynomial_order=3)
    ```

Available smoothing methods:

1. **Moving Average**:
   - Simple rolling window average
   - Parameters: window_size
   - Fast, easy to interpret

2. **Exponential Smoothing** (Simple):
   - Weighted average favoring recent observations
   - Parameters: alpha (0-1)
   - Good for data without trend/seasonality

3. **Double Exponential Smoothing** (Holt):
   - Handles level + trend
   - Parameters: alpha (level), beta (trend), damped
   - Use when data has trend

4. **Triple Exponential Smoothing** (Holt-Winters):
   - Handles level + trend + seasonality
   - Parameters: alpha, beta, gamma, period, damped
   - Best for seasonal data

5. **Savitzky-Golay Filter**:
   - Polynomial fitting in sliding window
   - Parameters: window_size (odd), polynomial_order
   - Preserves peaks and features better than simple averaging

6. **Hodrick-Prescott Filter**:
   - Decomposes into trend + cyclical components
   - Parameters: lamb (smoothing parameter, higher = smoother)
   - Common in economics/finance for trend extraction

7. **Kalman Filter**:
   - Optimal recursive estimator for linear systems
   - Parameters: initial_state, covariances, transition matrix
   - Powerful for noisy sensor data, state estimation

8. **Wavelet Transform**:
   - Multi-resolution decomposition
   - Parameters: wavelet_name, mode, level
   - Good for non-stationary signals, denoising

9. **Breakpoint Analysis**:
   - Identifies structural breaks (regime changes)
   - Parameters: penalty, efficient_mode
   - Detects abrupt shifts in mean/variance

10. **LOESS (Local Regression)**:
    - Non-parametric local polynomial regression
    - Parameters: fraction, it (iterations), downsample
    - Flexible for non-linear relationships

Features:
    - Unified DataSmoother interface for all methods
    - Parameter validation with helpful error messages
    - Performance warnings for large datasets
    - Preserves pandas index
    - Extensive __main__ examples with visualizations

Use cases:
    - Noise reduction in financial time series
    - Trend identification for forecasting
    - Preprocessing for machine learning
    - Signal processing (sensor data)
    - Economic cycle analysis (HP filter)

Parameter selection guidelines:
    - Moving average: window_size = 5-20 for daily data
    - Exponential: alpha = 0.1-0.3 (lower = smoother)
    - HP filter: lamb = 100 (annual), 1600 (quarterly), 14400 (monthly)
    - Savitzky-Golay: window_size = 2-3 cycles, polynomial_order = 2-3

Performance considerations:
    - Warnings issued for large datasets (>10K points)
    - Efficient mode available for breakpoint analysis
    - Downsampling option for LOESS
    - Chunking option for Kalman filter

Dependencies:
    - scipy (savgol_filter)
    - statsmodels (ExponentialSmoothing, hpfilter, lowess)
    - pywt (wavelet transforms)
    - ruptures (breakpoint detection)
    - filterpy (Kalman filtering)

Related modules: scalers_normalizers (normalization methods),
seasonal_imputation (seasonal decomposition for missing data).
"""

import numpy as np
import pandas as pd
import pywt
import ruptures as rpt
from filterpy.kalman import KalmanFilter
from scipy.signal import savgol_filter
from statsmodels.nonparametric.smoothers_lowess import lowess
from statsmodels.tsa.filters.hp_filter import hpfilter
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from finbot.config import logger
from finbot.utils.validation_utils.validation_helpers import validate_num_in_range, validate_types


class DataSmoother:
    """
    A class for applying various smoothing techniques to pandas.Series objects representing time series data.
    This class provides a suite of methods to apply different smoothing algorithms, making it a versatile tool for
    time series analysis, particularly useful in preprocessing steps for noise reduction and trend identification.
    """

    def __init__(self, data: pd.Series):
        """
        Initializes the DataSmoother class with time series data.

        Parameters:
            data (pd.Series): Time series data. It must be a pandas Series object.

        Raises:
            ValueError: If the input data is not a pandas Series.
        """
        if not isinstance(data, pd.Series):
            raise ValueError("Data must be a pandas Series")
        self._data = data

    def moving_average(self, window_size: int) -> pd.Series:
        """
        Applies simple moving average smoothing by averaging over a specified window.
        This method is useful for reducing random noise and identifying underlying trends in the data.

        Parameters:
            window_size (int): The size of the moving window.
            **kwargs: Optional keyword arguments for additional configuration.

        Returns:
            pd.Series: Smoothed data using the moving average method.
        """
        validate_num_in_range(value=window_size, parameter_name="window_size", min_value=1, max_value=len(self._data))

        if window_size > len(self._data) // 2:  # Example condition for optimization
            logger.warning("Large window sizes can be computationally intensive. Consider using a smaller window size.")

        return self._data.rolling(window=window_size).mean()

    def exponential_smoothing(self, alpha: float) -> pd.Series:
        """
        Applies simple exponential smoothing, giving more weight to recent observations.
        It's particularly useful when data has no clear trend or seasonal pattern.

        Parameters:
            alpha (float): Smoothing factor between 0 and 1, where closer to 1 puts more
                           weight on recent observations.

        Returns:
            pd.Series: Smoothed data using exponential smoothing.

        Raises:
            ValueError: If alpha is not between 0 and 1.
        """
        validate_num_in_range(value=alpha, parameter_name="alpha", min_value=0, max_value=1)
        return self._data.ewm(alpha=alpha, adjust=False).mean()

    def double_exponential_smoothing(self, alpha: float, beta: float, **kwargs) -> pd.Series:
        """
        Applies Double Exponential Smoothing with additional configurable parameters.

        Parameters:
            alpha (float): Smoothing factor for the level.
            beta (float): Smoothing factor for the trend.
            **kwargs: Optional keyword arguments for additional configuration.

        Returns:
            pd.Series: Smoothed data using double exponential smoothing.
        """
        validate_num_in_range(value=alpha, parameter_name="alpha", min_value=0, max_value=1)
        validate_num_in_range(value=beta, parameter_name="beta", min_value=0, max_value=1)

        # Extracting optional parameters
        damped = kwargs.get("damped", False)

        model = ExponentialSmoothing(self._data, trend="add", damped_trend=damped, seasonal=None)
        fitted_model = model.fit(smoothing_level=alpha, smoothing_trend=beta, **kwargs)
        return fitted_model.fittedvalues

    def triple_exponential_smoothing(
        self,
        alpha: float,
        beta: float,
        gamma: float,
        period: int,
        damped: bool = False,
    ) -> pd.Series:
        """
        Applies Holt-Winters Exponential Smoothing, suitable for data with both trends and seasonality.
        It models the level, trend, and seasonality of the series.

        Parameters:
            alpha (float): Smoothing factor for the level.
            beta (float): Smoothing factor for the trend.
            gamma (float): Smoothing factor for the seasonality.
            period (int): Number of time steps in a full seasonal cycle.
            damped (bool): If True, applies damping to the trend.

        Returns:
            pd.Series: Smoothed data using triple exponential smoothing.

        Raises:
            ValueError: If alpha, beta, or gamma is not between 0 and 1, or if period is not a positive integer.
        """
        validate_num_in_range(value=alpha, parameter_name="alpha", min_value=0, max_value=1)
        validate_num_in_range(value=beta, parameter_name="beta", min_value=0, max_value=1)
        validate_num_in_range(value=gamma, parameter_name="gamma", min_value=0, max_value=1)
        validate_num_in_range(value=period, parameter_name="period", min_value=0)
        validate_types(period, "period", [int])

        model = ExponentialSmoothing(
            self._data,
            trend="add",
            seasonal="add",
            seasonal_periods=period,
            damped_trend=damped,
        )
        fitted_model = model.fit(smoothing_level=alpha, smoothing_trend=beta, smoothing_seasonal=gamma)
        return fitted_model.fittedvalues

    def savitzky_golay_smoothing(self, window_size: int, polynomial_order: int) -> pd.Series:
        """
        Applies Savitzky-Golay smoothing, fitting successive sub-sets of adjacent data points with a low-degree polynomial.
        This method is effective for smoothing out noise while preserving the shape and features of the signal.

        Parameters:
            window_size (int): The size of the filter window, determining the number of coefficients.
            polynomial_order (int): The order of the polynomial used to fit the samples.

        Returns:
            pd.Series: Smoothed data using the Savitzky-Golay filter.

        Raises:
            ValueError: If window_size is not a positive odd integer, or if polynomial_order is not less than window_size.
        """
        validate_num_in_range(value=window_size, parameter_name="window_size", min_value=0)
        validate_types(window_size, "window_size", [int])
        if window_size % 2 == 0:
            raise ValueError("window_size must be an odd integer")
        if not 0 <= polynomial_order < window_size:
            raise ValueError("polynomial_order must be non-negative and less than window_size")

        return pd.Series(savgol_filter(self._data, window_size, polynomial_order), index=self._data.index)

    def hp_smoothing(self, lamb: float) -> pd.Series:
        """
        Applies Hodrick-Prescott smoothing to separate the time series into a trend and a cyclical component.
        This method is particularly useful for economic time series analysis, where it's essential to examine
        fluctuations around a long-term trend.

        Parameters:
            lamb (float): The smoothing parameter lambda. A higher value of lambda yields a smoother trend component.

        Returns:
            pd.Series: The trend component of the time series.

        Raises:
            ValueError: If lambda is not a positive float.
        """
        validate_num_in_range(value=lamb, parameter_name="lamb", min_value=0)

        _cycle, trend = hpfilter(self._data, lamb=lamb)
        return trend

    def kalman_smoothing(
        self,
        initial_state,
        observation_covariance,
        transition_covariance,
        transition_matrix,
        chunk_size=None,
    ) -> pd.Series:
        """
        Applies Kalman Filter smoothing, a powerful algorithm used in a wide range of applications
        including tracking and navigation, economics, and engineering. It is ideal for systems
        continuously changing over time and under uncertainty.

        Parameters:
            initial_state: Initial state estimation for the Kalman Filter.
            observation_covariance: Covariance of the observation noise.
            transition_covariance: Covariance of the state transition noise.
            transition_matrix: State transition matrix.
            chunk_size (int, optional): Size of chunks to process the data in for large datasets.
                                        If None, the data is processed as a whole.

        Returns:
            pd.Series: Smoothed data using the Kalman Filter.
        """
        kf = KalmanFilter(dim_x=1, dim_z=1)
        kf.x = np.array([initial_state])  # initial state
        kf.R = np.array([[observation_covariance]])  # observation noise
        kf.Q = np.array([[transition_covariance]])  # transition noise
        kf.F = np.array([[transition_matrix]])  # state transition matrix
        kf.H = np.array([[1]])  # Measurement function

        data_array = np.asarray(self._data)  # Explicit conversion to NumPy array
        predictions = []
        for chunk in np.array_split(data_array, len(data_array) // chunk_size if chunk_size else 1):
            for z in chunk:
                kf.predict()
                kf.update(z)
                predictions.append(kf.x[0])

        return pd.Series(predictions, index=self._data.index)

    def wavelet_smoothing(self, wavelet_name: str, mode: str = "symmetric", level: int | None = None) -> pd.Series:
        """
        Applies Wavelet Transform smoothing, an effective method for denoising and feature extraction in signals.
        Wavelet smoothing is advantageous in handling non-stationary signals where frequency characteristics
        change over time.


        Parameters:
            wavelet_name (str): The name of the wavelet to use.
            mode (str): The signal extension mode.
            level (int, optional): The level of decomposition to perform.

        Returns:
            pd.Series: Smoothed data using Wavelet Transform.
        """
        validate_types(wavelet_name, "wavelet_name", [str])
        validate_types(level, "level", [int, type(None)])

        if len(self._data) > 10000:  # Example threshold
            logger.warning("Wavelet Transform on large datasets can be resource-intensive.")

        coeffs = pywt.wavedec(self._data, wavelet_name, mode=mode, level=level)
        coeffs[1:] = [np.zeros_like(c) for c in coeffs[1:]]
        reconstructed_signal = pywt.waverec(coeffs, wavelet_name, mode=mode)
        return pd.Series(reconstructed_signal, index=self._data.index)[: len(self._data)]

    def breakpoint_analysis(self, penalty: float, efficient_mode: bool | None = False) -> pd.Series:
        """
        Applies Breakpoint Analysis to identify structural changes in the time series, such as abrupt shifts
        in the mean or variance. This method is useful for detecting and dating structural breaks in time series data.

        Parameters:
            penalty (float): The penalty value used to decide the number of breakpoints.
            efficient_mode (Optional[bool]): If True, uses a more efficient method for large datasets.

        Returns:
            pd.Series: A series with the same index as the original data, where the value is the mean of the segment.
        """
        validate_num_in_range(value=penalty, parameter_name="penalty", min_value=0)

        if len(self._data) > 10000 and not efficient_mode:
            logger.warning(
                "Breakpoint analysis on large datasets can be very slow. Consider setting efficient_mode=True.",
            )

        algo_class = rpt.Pelt if not efficient_mode else rpt.Binseg
        algo = algo_class(model="l2").fit(self._data.values)
        breakpoints = algo.predict(pen=penalty)
        last_bp = 0
        output = pd.Series(index=self._data.index)
        for bp in breakpoints:
            output.iloc[last_bp:bp] = self._data.iloc[last_bp:bp].mean()
            last_bp = bp
        return output

    def loess_smoothing(self, fraction: float, it: int = 3, downsample: bool = False) -> pd.Series:
        """
        Applies Loess (Local Regression) smoothing, a non-parametric technique that combines multiple
        regression models in a k-nearest-neighbor-based meta-model. It's particularly effective for
        smoothing data with non-linear relationships.

        Parameters:
            fraction (float): The fraction of the data used when estimating each y-value.
            it (int): The number of residual-based reweightings to perform.
            downsample (bool): If True, downsamples large datasets for faster computation.

        Returns:
            pd.Series: Smoothed data using Loess smoothing.
        """
        validate_num_in_range(value=fraction, parameter_name="fraction", min_value=0, max_value=1)
        validate_num_in_range(value=it, parameter_name="it", min_value=0)
        validate_types(it, "it", [int])

        if len(self._data) > 10000 and not downsample:  # Example threshold, adjust based on performance tests
            logger.warning("Loess smoothing on large datasets can be very slow. Consider setting downsample=True.")

        data_to_use = self._data if not downsample else self._data.iloc[::2]  # Example downsampling strategy
        return pd.Series(
            lowess(data_to_use, np.arange(len(data_to_use)), frac=fraction, it=it)[:, 1],
            index=self._data.index,
        )


if __name__ == "__main__":
    # Example usage:
    from finbot.constants.data_constants import DEMO_DATA
    from finbot.utils.plotting_utils.interactive.interactive_plotter import InteractivePlotter

    data = pd.Series(DEMO_DATA["Close"], name="SP500 Closing Price")
    data = data.asfreq("B", method="ffill")
    smoother = DataSmoother(data)

    smoothed_data = {"Original": data}
    # Applying different smoothing techniques
    smoothing_methods = [
        (smoother.moving_average(window_size=5), "Moving Average (5 days)"),
        (smoother.moving_average(window_size=30), "Moving Average (30 days)"),
        (smoother.exponential_smoothing(alpha=0.35), "Exponential Smoothing (α=0.35)"),  # noqa: RUF001
        (smoother.exponential_smoothing(alpha=0.10), "Exponential Smoothing (α=0.10)"),  # noqa: RUF001
        (smoother.double_exponential_smoothing(alpha=0.25, beta=0.1), "Double Exponential (α=0.25, β=0.1)"),  # noqa: RUF001
        (smoother.double_exponential_smoothing(alpha=0.05, beta=0.125), "Double Exponential (α=0.05, β=0.125)"),  # noqa: RUF001
        (
            smoother.triple_exponential_smoothing(alpha=0.25, beta=0.1, gamma=0.3, period=252),
            "Holt-Winters (α=0.25, β=0.1, γ=0.3, period=252)",  # noqa: RUF001
        ),
        (smoother.savitzky_golay_smoothing(window_size=21, polynomial_order=3), "Savitzky-Golay (20 days, 3rd order)"),
        (smoother.savitzky_golay_smoothing(window_size=41, polynomial_order=3), "Savitzky-Golay (41 days, 3rd order)"),
        (smoother.hp_smoothing(lamb=20), "Hodrick-Prescott Filter (λ=20)"),
        (smoother.hp_smoothing(lamb=10000), "Hodrick-Prescott Filter (λ=10000)"),
        (
            smoother.kalman_smoothing(
                initial_state=0,
                observation_covariance=1,
                transition_covariance=0.1,
                transition_matrix=1,
            ),
            "Kalman Filter 0,1,0.1,1",
        ),
        (
            smoother.kalman_smoothing(
                initial_state=0,
                observation_covariance=10,
                transition_covariance=0.1,
                transition_matrix=1,
            ),
            "Kalman Filter 0.10,0.1,1",
        ),
        (smoother.wavelet_smoothing(wavelet_name="coif5", level=3), "Wavelet Transform (coif5, level 3)"),
        (smoother.wavelet_smoothing(wavelet_name="coif16", level=3), "Wavelet Transform (coif16, level 3)"),
        (smoother.wavelet_smoothing(wavelet_name="bior1.1", level=3), "Wavelet Transform (bior1.1, level 3)"),
        (smoother.wavelet_smoothing(wavelet_name="bior4.4", level=3), "Wavelet Transform (bior4.4, level 3)"),
        (smoother.wavelet_smoothing(wavelet_name="db1", level=3), "Wavelet Transform (db1, level 3)"),
        (smoother.wavelet_smoothing(wavelet_name="db3", level=3), "Wavelet Transform (db3, level 3)"),
        (smoother.wavelet_smoothing(wavelet_name="db6", level=3), "Wavelet Transform (db6, level 3)"),
        (smoother.wavelet_smoothing(wavelet_name="db7", level=3), "Wavelet Transform (db7, level 3)"),
        (smoother.wavelet_smoothing(wavelet_name="db22", level=3), "Wavelet Transform (db22, level 3)"),
        (smoother.wavelet_smoothing(wavelet_name="db28", level=3), "Wavelet Transform (db28, level 3)"),
        (smoother.wavelet_smoothing(wavelet_name="db36", level=3), "Wavelet Transform (db36, level 3)"),
        (smoother.wavelet_smoothing(wavelet_name="dmey", level=3), "Wavelet Transform (dmey, level 3)"),
        (smoother.wavelet_smoothing(wavelet_name="haar", level=3), "Wavelet Transform (haar, level 3)"),
        (smoother.wavelet_smoothing(wavelet_name="rbio5.5", level=3), "Wavelet Transform (rbio5.5, level 3)"),
        (smoother.wavelet_smoothing(wavelet_name="rbio1.5", level=3), "Wavelet Transform (rbio1.5, level 3)"),
        (smoother.wavelet_smoothing(wavelet_name="sym20", level=3), "Wavelet Transform (sym20, level 3)"),
        (smoother.wavelet_smoothing(wavelet_name="db4", level=5), "Wavelet Transform (db4, level 5)"),
        (smoother.breakpoint_analysis(penalty=5), "Breakpoint Analysis (penalty=5)"),
        (smoother.loess_smoothing(fraction=90 / len(data)), f"Loess ({round(90 / len(data), 4) * 100}% fraction)"),
        (smoother.loess_smoothing(fraction=60 / len(data)), f"Loess ({round(60 / len(data), 4) * 100}% fraction)"),
    ]

    # Warning: This will add a lot of plots to the plotter
    # smoothing_methods += [
    #     (smoother.wavelet_smoothing(str(wave), level=3), f"Wavelet Transform ({str(wave)}, level 3)")
    #     for wave in pywt.wavelist(kind="discrete")
    # ]

    smoothed_data.update({d[1]: d[0] for d in smoothing_methods})

    # Plotting all smoothed datasets for comparison
    plotter = InteractivePlotter()
    plotter.plot_time_series(pd.DataFrame(smoothed_data), title="Comparison of Smoothing Techniques")
