from __future__ import annotations

# ruff: noqa: N803 - Using sklearn naming convention (X for data parameter)
import pandas as pd

from finbot.utils.data_science_utils.data_transformation.scalers_normalizers._base_scaler import BaseScaler


class GrowthRateScaler(BaseScaler):
    """
    A scaler that applies growth rate scaling to a pandas Series.
    The growth rate is calculated based on the first and last elements of the Series.
    """

    def __init__(self):
        """
        Initializes the GrowthRateScaler.
        """
        self.growth_rate_: None | float = None

    def fit(self, X: pd.Series) -> GrowthRateScaler:
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

    def transform(self, X: pd.Series) -> pd.Series:
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

    def fit_transform(self, X: pd.Series) -> pd.Series:
        """
        Fits the scaler to the Series and then transforms it.

        Parameters:
            X (pd.Series): The data series to fit and transform.

        Returns:
            pd.Series: The scaled series.
        """
        return self.fit(X).transform(X)

    def reset(self):
        """
        Reset the scaler to its initial state.
        """
        self.growth_rate_ = None

    def inverse_transform(self, X: pd.Series) -> pd.Series:
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
    from constants.data_constants import DEMO_DATA
    from finbot.utils.plotting_utils.interactive.interactive_plotter import InteractivePlotter

    close_series = DEMO_DATA["Close"]

    examples = {"Default": GrowthRateScaler().fit_transform(close_series)}

    plotter = InteractivePlotter()
    plotter.plot_time_series(pd.DataFrame(examples), title="GrowthRateScaler")
