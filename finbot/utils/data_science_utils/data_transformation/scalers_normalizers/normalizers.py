from __future__ import annotations

import pandas as pd
from scipy.special import inv_boxcox
from scipy.stats import boxcox
from sklearn.preprocessing import StandardScaler

from finbot.utils.data_science_utils.data_transformation.scalers_normalizers._base_scaler import BaseScaler


class Normalizers(BaseScaler):
    """
    A module providing various normalization techniques specifically for `pandas.Series` objects to transform data
    distributions towards normality.

    This module includes methods for:
    - Standardization (Z-score normalization)
    - Box-Cox Transformation
    - Mean Range Normalization
    """

    def __init__(self, method: str, **kwargs):
        """
        Initializes the Normalizers class with a specific normalization method for `pandas.Series`.

        Parameters:
            method (str): Normalization method. Options: 'standardization', 'boxcox', 'mean_range'.
            **kwargs: Additional parameters for specific normalization methods.
        """
        valid_methods = ["standardization", "boxcox", "mean_range"]
        if method not in valid_methods:
            raise ValueError(f"Method must be one of {valid_methods}")

        self.method = method
        self.kwargs = kwargs
        self.scaler = None
        self.lambda_: None | float = None
        self.mean_: None | float = None
        self.range_: None | float = None

    def fit(self, X: pd.Series[int | float], y=None) -> Normalizers:
        """
        Fit the normalizer to the data.

        Parameters:
            X (pd.Series): The data to be normalized.
            y: Ignored, present for compatibility with sklearn's TransformerMixin.

        Returns:
            Normalizers: The instance itself.
        """
        if not isinstance(X, pd.Series):
            raise TypeError("Input must be a pandas.Series object.")

        if self.method == "standardization":
            self.scaler = StandardScaler().fit(X.to_numpy().reshape(-1, 1))
        elif self.method == "boxcox":
            if (X <= 0).any():
                raise ValueError("Box-Cox transformation requires all data to be positive.")
            _, self.lambda_ = boxcox(X)
        elif self.method == "mean_range":
            self.mean_ = X.mean()
            self.range_ = X.max() - X.min()

        return self

    def transform(self, X: pd.Series[int | float]) -> pd.Series:
        """
        Apply the normalization transformation to the data.

        Parameters:
            X (pd.Series): The data to apply the normalization to.

        Returns:
            pd.Series: Normalized data.
        """
        if not isinstance(X, pd.Series):
            raise TypeError("Input must be a pandas.Series object.")

        if self.method == "standardization":
            if self.scaler is None:
                raise RuntimeError("The scaler must be fitted before calling transform.")
            return pd.Series(self.scaler.transform(X.values.reshape(-1, 1)).squeeze(), index=X.index)
        elif self.method == "boxcox":
            if self.lambda_ is None:
                raise RuntimeError("Box-Cox lambda value is not set.")
            transformed_data = boxcox(X, self.lambda_)
            return pd.Series(transformed_data, index=X.index)
        elif self.method == "mean_range":
            if self.mean_ is None or self.range_ is None:
                raise RuntimeError("Mean and range values must be set.")
            return (X - self.mean_) / self.range_
        else:
            raise ValueError(f"Unknown normalization method: {self.method}")

    def inverse_transform(self, X: pd.Series[int | float]) -> pd.Series:
        """
        Apply inverse transformation to the data.

        Parameters:
            X (pd.Series): The normalized data.

        Returns:
            pd.Series: Data after applying the inverse of the normalization.
        """
        if not isinstance(X, pd.Series):
            raise TypeError("Input must be a pandas.Series object.")

        if self.method == "standardization":
            if self.scaler is None:
                raise RuntimeError("The scaler must be fitted before calling inverse_transform.")
            return pd.Series(self.scaler.inverse_transform(X.values.reshape(-1, 1)).squeeze(), index=X.index)
        elif self.method == "boxcox":
            if self.lambda_ is None:
                raise RuntimeError("Box-Cox lambda value is not set.")
            inverse_transformed_data = inv_boxcox(X, self.lambda_)
            return pd.Series(inverse_transformed_data, index=X.index)
        elif self.method == "mean_range":
            if self.mean_ is None or self.range_ is None:
                raise RuntimeError("Mean and range values must be set.")
            return X * self.range_ + self.mean_
        else:
            raise ValueError(f"Unknown normalization method: {self.method}")

    def fit_transform(self, X: pd.Series[int | float], y=None) -> pd.Series:
        """
        Fit to data, then transform it.

        Parameters:
            X (pd.Series): Data to fit and transform.
            y: Ignored, present for compatibility with sklearn's TransformerMixin.

        Returns:
            pd.Series: Normalized data.
        """
        return self.fit(X, y).transform(X)


# Example usage
if __name__ == "__main__":
    from constants.data_constants import DEMO_DATA
    from finbot.utils.plotting_utils.interactive.interactive_plotter import InteractivePlotter

    close_series = pd.Series(DEMO_DATA["Close"])
    methods = ["standardization", "boxcox", "mean_range"]

    _data = {}

    for method in methods:
        normalizer = Normalizers(method=method)
        normalized_data = normalizer.fit_transform(close_series)
        inverse_normalized_data = normalizer.inverse_transform(normalized_data)
        _data[f"{method} - Normalized"] = normalized_data
        _data[f"{method} - Inversed"] = inverse_normalized_data

    plotter = InteractivePlotter()
    plotter.plot_time_series(pd.DataFrame(_data), title="Normalized Data")
