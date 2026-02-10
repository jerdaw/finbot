from __future__ import annotations

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class BaseScaler(BaseEstimator, TransformerMixin):
    """
    BaseScaler is a base class for scalers designed to work with pandas.Series objects.

    This class serves as a foundation for implementing various scaling techniques on Series data.
    """

    def __init__(self):
        """
        Initialize BaseScaler.
        """
        pass  # No columns attribute needed

    def fit(self, X: pd.Series[float | int]) -> BaseScaler:
        """
        This operation has no effect for this scaler but is present for API consistency.

        Parameters:
            X (pd.Series): Not used.

        Returns:
            BaseScaler: The fitted scaler instance.
        """
        return self

    def transform(self, X: pd.Series[float | int]) -> pd.Series:
        """
        Scales features of X. This method should be overridden by child class.

        Parameters:
            X (pd.Series): Data to scale.

        Returns:
            pd.Series: Scaled data.
        """
        raise NotImplementedError(
            "This method should be overridden by child class",
        )

    def inverse_transform(self, X: pd.Series[float | int]) -> pd.Series:
        """
        Inverse scales features of X. This method should be overridden by child class.

        Parameters:
            X (pd.Series): Data to inverse scale.

        Returns:
            pd.Series: Inverse scaled data.
        """
        raise NotImplementedError(
            "This method should be overridden by child class",
        )

    def reset(self):
        """
        Reset the scaler.
        """
        raise NotImplementedError(
            "This method should be overridden by child class",
        )

    def fit_transform(self, X: pd.Series[float | int]) -> pd.Series:
        """
        Fit to data, then transform it.

        Parameters:
            X (pd.Series): Data to fit scaler and scale.

        Returns:
            pd.Series: Scaled data.
        """
        return self.fit(X).transform(X)
