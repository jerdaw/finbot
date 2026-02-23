from __future__ import annotations

# ruff: noqa: N803 - Using sklearn naming convention (X for data parameter)
import pandas as pd

from finbot.utils.data_science_utils.data_transformation.scalers_normalizers._base_scaler import BaseScaler


class SimpleScaler(BaseScaler):
    """
    A simple scaler for normalizing data using various scaling methods.

    Parameters:
        scale_method (str): The scaling method to use. Must be one of the following: 'min', 'max', 'first', 'last', 'mean', 'median', 'mode'.
        abs_fit (bool): Whether to use the absolute value of the data during fitting. Default is False.

    Attributes:
        scale_method (str): The scaling method used.
        scale_value (pd.Series): The computed scale value.
    """

    def __init__(self, scale_method: str, abs_fit: bool = False) -> None:
        if scale_method not in ["max", "min", "first", "last", "mean", "median", "mode"]:
            raise ValueError(
                "scale_method must be one of the following: 'min', 'max', 'first', 'last', 'mean', 'median', 'mode'.",
            )
        self.scale_method = scale_method
        self.scale_value: float | int | None = None
        self.abs_fit = abs_fit

    def fit(self, X: pd.Series[int | float]) -> SimpleScaler:
        """
        Computes the scale value based on the specified method.

        Parameters:
            X (pd.Series): Data to compute the scale value.

        Returns:
            SimpleScaler: The fitted scaler instance.
        """
        if not isinstance(X, pd.Series) or X.empty:
            raise ValueError("X must be a non-empty pandas Series.")

        fit_series = X.abs() if self.abs_fit else X
        if self.scale_method == "min":
            self.scale_value = fit_series.min()
        elif self.scale_method == "max":
            self.scale_value = fit_series.max()
        elif self.scale_method == "first":
            self.scale_value = fit_series.iloc[0]
        elif self.scale_method == "last":
            self.scale_value = fit_series.iloc[-1]
        elif self.scale_method == "mean":
            self.scale_value = fit_series.mean()
        elif self.scale_method == "median":
            self.scale_value = fit_series.median()
        elif self.scale_method == "mode":
            self.scale_value = fit_series.mode().iloc[0]

        return self

    def transform(self, X: pd.Series[int | float]) -> pd.Series:
        """
        Scales features of X.

        Parameters:
            X (pd.Series): Data to scale.

        Returns:
            pd.Series: Scaled data.
        """
        if self.scale_value is None:
            raise RuntimeError("The fit method must be called before transform.")

        if not isinstance(X, pd.Series) or X.empty:
            raise ValueError("X must be a non-empty pandas Series.")

        return X / self.scale_value

    def fit_transform(self, X: pd.Series[int | float]) -> pd.Series:
        """
        Fit to data, then transform it.

        Parameters:
            X (pd.Series): Data to compute the scale value and to scale.

        Returns:
            pd.Series: Scaled data.
        """
        return self.fit(X).transform(X)

    def reset(self) -> None:
        """
        Reset the scaler to its initial state.
        """
        self.scale_value = None

    def inverse_transform(self, X: pd.Series[int | float]) -> pd.Series:
        """
        Apply inverse transformation to the data.

        Parameters:
            X (pd.Series): The scaled data.

        Returns:
            pd.Series: Data after applying the inverse of the scaling.
        """
        if self.scale_value is None:
            raise RuntimeError("The scaler must be fitted before calling inverse_transform.")

        return X * self.scale_value


if __name__ == "__main__":
    from finbot.constants.data_constants import DEMO_DATA
    from finbot.utils.plotting_utils.interactive.interactive_plotter import InteractivePlotter

    close_series = DEMO_DATA["Close"]

    examples = {
        f"Method: {m}": SimpleScaler(scale_method=m).fit_transform(close_series)
        for m in ("max", "min", "first", "last", "mean", "median", "mode")
    }

    plotter = InteractivePlotter()
    concatted = pd.concat(examples.values(), axis=1)
    concatted.columns = pd.Index(examples.keys())
    plotter.plot_time_series(concatted)
