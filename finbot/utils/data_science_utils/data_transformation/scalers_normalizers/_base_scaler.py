"""Base class for all pandas Series scalers following sklearn API conventions.

Provides abstract base class for custom scalers that work with pandas Series
objects. Inherits from sklearn's BaseEstimator and TransformerMixin to ensure
compatibility with sklearn pipelines while maintaining pandas-specific
functionality.

Typical usage:
    Subclass BaseScaler to create custom scaling transformations:

    ```python
    class MyCustomScaler(BaseScaler):
        def __init__(self, param=1.0):
            self.param = param
            self.scale_value_ = None

        def fit(self, X):
            self.scale_value_ = X.max() * self.param
            return self

        def transform(self, X):
            return X / self.scale_value_

        def inverse_transform(self, X):
            return X * self.scale_value_

        def reset(self):
            self.scale_value_ = None
    ```

sklearn API methods (must override in subclasses):
    - fit(X): Compute scaling parameters from data, return self
    - transform(X): Apply scaling transformation, return scaled Series
    - inverse_transform(X): Reverse scaling transformation, return original scale
    - reset(): Reset scaler to initial state (clear fitted parameters)

Additional inherited methods (automatic):
    - fit_transform(X): Calls fit(X).transform(X) automatically

sklearn compatibility:
    - Inherits from BaseEstimator and TransformerMixin
    - Can be used in sklearn.pipeline.Pipeline
    - Supports get_params/set_params for hyperparameter tuning
    - Compatible with sklearn model selection tools

Features:
    - Enforces consistent API across all scaler implementations
    - Works specifically with pandas.Series (preserves index)
    - Provides fit_transform automatically via TransformerMixin
    - Minimal base implementation (fit is no-op)

Subclass requirements:
    - Override transform() with actual scaling logic
    - Override inverse_transform() if reversible
    - Override fit() if parameters need to be computed from data
    - Override reset() to clear fitted parameters

Use cases:
    - Creating domain-specific scalers
    - Implementing custom normalization methods
    - Extending finbot with new transformation techniques
    - Building sklearn-compatible pandas transformers

Existing subclass implementations:
    - SimpleScaler: Scale by statistical measure (min, max, mean, etc.)
    - MAScaler: Scale by moving average
    - LogarithmicScaler: Logarithmic transformation
    - GrowthRateScaler: Remove growth trend
    - Normalizers: Various normalization methods (z-score, Box-Cox, range)

Design pattern: Template Method pattern with abstract methods for subclasses.

Dependencies: scikit-learn (BaseEstimator, TransformerMixin)

Related modules: All modules in scalers_normalizers/ directory,
data_smoothing.DataSmoother (different interface for smoothing).
"""

from __future__ import annotations

# ruff: noqa: N803 - Using sklearn naming convention (X for data parameter)
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
