from __future__ import annotations

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

    def fit(self, *args, **kwargs) -> MAScaler:
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

    def reset(self):
        """
        Reset the normalizer to its initial state.
        """
        self.scaler = None
        self.lambda_ = None
        self.mean_ = None
        self.range_ = None


if __name__ == "__main__":
    from constants.data_constants import DEMO_DATA
    from finbot.utils.plotting_utils.interactive.interactive_plotter import InteractivePlotter

    close_series = DEMO_DATA["Close"]

    examples = {
        f"Window: {w}": MAScaler(window_size=w).fit_transform(close_series) for w in (1, 5, 20, 50, 250, 1250, 2500)
    }

    plotter = InteractivePlotter()
    concatted = pd.concat(examples.values(), axis=1)
    concatted.columns = pd.Index(examples.keys())
    plotter.plot_time_series(concatted)
