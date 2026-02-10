from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from finbot.utils.data_science_utils.data_transformation.scalers_normalizers._base_scaler import BaseScaler


class LogarithmicScaler(BaseScaler):
    """
    LogarithmicScaler scales features using logarithmic transformation.
    Typically, logarithmic scaling is used to normalize data without distorting their distribution.
    This is useful in situations where the features in a dataset have significantly different scales.

    Default (non-normalized) formula:
        y = log(x + epsilon) / log(base)

    Range normalization formula:
        y = (log(x + epsilon) - log(min(x) + epsilon)) / (log(max(x) + epsilon) - log(min(x) + epsilon))

    First-last normalization formula:
        y = (log(x + epsilon) - log(first(x) + epsilon)) / (log(last(x) + epsilon) - log(first(x) + epsilon))

    Note:
        Normalizing a certain number (n) to y = 1.0 is achieved by setting the base to n.

    Attributes:
        base (float or str): The logarithmic base to use, default is Euler's number (e). If a string specifying a statistical function (e.g., 'max', 'mean'), the base will be dynamically determined.
        epsilon (float): Small constant added to data to manage zero values (e.g., epsilon=1e-9). Defaults to 0.
        normalize (str): Normalize the data to a certain range. Options: None (no normalization), 'range', 'first_last'.
    """

    TARGET_FUNCS: dict[str, Callable[[Any], float]] = {
        "min": np.min,
        "max": np.max,
        "first": lambda x: x.iloc[0],
        "last": lambda x: x.iloc[-1],
        "mean": np.mean,
        "median": np.median,
        "mode": lambda x: (lambda m: (m.mode[0] if isinstance(m.mode, np.ndarray) else m.mode) if m.count else np.nan)(
            stats.mode(x, nan_policy="omit"),
        ),  # TODO: Make this more readable
    }
    DEFAULT_BASE = np.e
    DEFAULT_EPSILON = 1e-9

    def __init__(
        self,
        base: float | int | str = DEFAULT_BASE,
        epsilon: float | int = DEFAULT_EPSILON,
        normalize: None | str = None,
    ):
        """
        Initialize LogarithmicScaler with transformation parameter.

        Parameters:
            base (float or str): The logarithmic base to use. Can be a number or a string specifying a statistical function (e.g., 'max', 'mean').
            epsilon (float): Small constant added to data to manage zero values.
            normalize (str): Normalize the data to a certain range. Options: None (no normalization), 'range', 'first_last'.
        """
        if not (isinstance(base, float | int) or base in self.TARGET_FUNCS):
            raise ValueError(
                f"Invalid base: {base}. Must be a float, int, or one of: " + ", ".join(self.TARGET_FUNCS.keys()),
            )

        if not isinstance(epsilon, float) or epsilon <= 0:
            raise ValueError("epsilon must be a positive float.")

        if normalize not in [None, "range", "first_last"]:
            raise ValueError("Invalid normalize value. Must be None, 'range', or 'first_last'.")

        self.base = base
        self.epsilon = epsilon
        self.normalize = normalize

    def fit(self, X: pd.Series[int | float]) -> LogarithmicScaler:
        """
        Fit the scaler to the data by computing the bases if they are specified as statistical functions.

        Parameters:
            X (pd.Series): Data to compute the bases.
        """
        if not isinstance(X, pd.Series):
            raise ValueError("X must be a pandas Series.")

        if X.empty:
            raise ValueError("X must be a non-empty pandas Series.")

        self.base_: float | int | str  # to appease lord MyPy
        if isinstance(self.base, int | float):
            self.base_ = self.base
        elif isinstance(self.base, str) and self.base in self.TARGET_FUNCS:
            # To normalize a certian (vaild) number (n) to have a (y) value of 1.0 in the transformed data,
            # we can just use the number (n) as the base (b) for the logarithmic transformation.
            # 1.0 = log_b(n) = log(n) / log(b)
            # log(b) = log(n) / 1.0
            # b = e^(log(n) / 1.0)
            # b = e^log(n)
            # b = n
            self.base_ = self.TARGET_FUNCS[self.base](X + self.epsilon)
        else:
            raise ValueError(
                f"Invalid base: {self.base}. Must be a float, int, or one of: {', '.join(self.TARGET_FUNCS.keys())}",
            )

        return self

    def transform(self, X: pd.Series[int | float]) -> pd.Series:
        """
        Scales features of X using the previously computed bases.

        Parameters:
            X (pd.Series): Data to scale.

        Returns:
            pd.Series: Scaled data.
        """
        if not hasattr(self, "base_"):
            raise RuntimeError(
                "The scaler is not fitted yet. Call 'fit' with appropriate data before using this method.",
            )

        if not isinstance(X, pd.Series) or X.empty:
            raise ValueError("X must be a non-empty pandas Series.")

        if self.normalize == "range":
            X_scaled = (np.log(X + self.epsilon) - np.log(X.min() + self.epsilon)) / (
                np.log(X.max() + self.epsilon) - np.log(X.min() + self.epsilon)
            )
        elif self.normalize == "first_last":
            X_scaled = (np.log(X + self.epsilon) - np.log(X.iloc[0] + self.epsilon)) / (
                np.log(X.iloc[-1] + self.epsilon) - np.log(X.iloc[0] + self.epsilon)
            )
        else:
            X_scaled = np.log(X + self.epsilon) / np.log(self.base_)

        return pd.Series(X_scaled, index=X.index)

    def fit_transform(self, X: pd.Series[int | float]) -> pd.Series:
        """
        Fit to data, then transform it.

        Parameters:
            X (pd.Series): Data to fit scaler and scale.

        Returns:
            pd.Series: Scaled data.
        """
        return self.fit(X).transform(X)

    def reset(self):
        """
        Reset the scaler to its initial state, setting base_ to the initial base value.
        """
        self.base_ = self.base

    def inverse_transform(self, X: pd.Series) -> pd.Series:
        """
        Reverses the logarithmic scaling applied to the Series.

        Parameters:
            X (pd.Series): The scaled data series to reverse the scaling.

        Returns:
            pd.Series: The series with the scaling reversed, if possible.

        Raises:
            RuntimeError: If the scaler is not fitted before calling this method.
            NotImplementedError: If inverse transformation is not feasible.
        """
        if not hasattr(self, "base_"):
            raise RuntimeError("LogarithmicScaler must be fit before inverse transform.")

        if self.normalize is not None:
            raise NotImplementedError("Inverse transform is not implemented for normalized data.")

        return pd.Series(np.exp(X * np.log(self.base_)) - self.epsilon, index=X.index)


if __name__ == "__main__":
    from constants.data_constants import DEMO_DATA
    from finbot.utils.plotting_utils.interactive.interactive_plotter import InteractivePlotter

    close_series = DEMO_DATA["Close"]

    examples = {"Default": LogarithmicScaler().fit_transform(close_series)}

    bases: list[str | float] = [
        "min",
        "max",
        "first",
        "last",
        "mean",
        "median",
        "mode",
        10,
    ]
    examples.update({f"Base {base}": LogarithmicScaler(base=base).fit_transform(close_series) for base in bases})

    examples.update(
        {f"Normalize {n}": LogarithmicScaler(normalize=n).fit_transform(close_series) for n in ["range", "first_last"]},
    )

    plotter = InteractivePlotter()
    concatted = pd.concat(examples.values(), axis=1)
    concatted.columns = pd.Index(examples.keys())
    plotter.plot_time_series(concatted)
