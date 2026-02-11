"""Multiple normalization methods for transforming data toward normal distributions.

Provides three normalization techniques (standardization, Box-Cox, mean-range)
through a unified Normalizers class. Each method targets different aspects of
data transformation, from simple scaling to sophisticated variance stabilization.

Typical usage:
    ```python
    # Z-score normalization (standardization)
    normalizer = Normalizers(method="standardization")
    normalized = normalizer.fit_transform(data)
    # Result: mean=0, std=1

    # Box-Cox transformation (variance stabilization)
    normalizer_bc = Normalizers(method="boxcox")
    normalized_bc = normalizer_bc.fit_transform(positive_data)
    # Result: more normal distribution, optimal λ chosen automatically

    # Mean-range normalization
    normalizer_mr = Normalizers(method="mean_range")
    normalized_mr = normalizer_mr.fit_transform(data)
    # Result: centered at 0, scaled by range
    ```

Normalization methods:

1. **Standardization (Z-score normalization)**:
   - Formula: `(X - mean) / std`
   - Maps to approximately normal distribution with mean=0, std=1
   - Uses sklearn.preprocessing.StandardScaler
   - Most common normalization for machine learning

2. **Box-Cox Transformation**:
   - Formula: `(X^λ - 1) / λ` if λ ≠ 0, else `log(X)`
   - Finds optimal λ to maximize normality
   - **Requires all positive values** (X > 0)
   - Stabilizes variance across range
   - Good for heteroscedastic data

3. **Mean-Range Normalization**:
   - Formula: `(X - mean) / range`
   - Centers at 0, scales by data range
   - Alternative to standardization
   - Less affected by outliers than std

Features:
    - Full inverse_transform support for all methods
    - Automatic parameter fitting (mean, std, λ, range)
    - sklearn-compatible API via BaseScaler
    - Works with pandas Series (preserves index)
    - Clear error messages for invalid usage

Use cases:

**Standardization**:
    - Preprocessing for machine learning (especially neural networks)
    - Making features comparable across different scales
    - Statistical analysis requiring z-scores
    - Outlier detection (values > 3 standard deviations)

**Box-Cox**:
    - Stabilizing variance in heteroscedastic data
    - Transforming skewed distributions toward normality
    - Preprocessing for linear regression assumptions
    - Financial returns, physical measurements

**Mean-Range**:
    - Alternative normalization less sensitive to outliers
    - Quick scaling for visualization
    - When standard deviation is not meaningful

Parameters:
    - method: Normalization technique ('standardization', 'boxcox', 'mean_range')
    - **kwargs: Additional parameters (currently unused)

Inverse transformation:
    All methods support full inverse transformation:
    ```python
    normalizer = Normalizers(method="boxcox")
    normalized = normalizer.fit_transform(data)
    recovered = normalizer.inverse_transform(normalized)
    # recovered == data (within numerical precision)
    ```

Box-Cox λ interpretation:
    - λ = 1: No transformation (linear)
    - λ = 0.5: Square root transformation
    - λ = 0: Log transformation
    - λ = -1: Reciprocal transformation
    - Fitted λ shows optimal transformation power

Advantages:
    - **Standardization**: Simple, interpretable, widely used
    - **Box-Cox**: Powerful variance stabilization, automatic λ selection
    - **Mean-Range**: Robust to outliers, simple

Limitations:
    - **Standardization**: Assumes meaningful mean/std (fails for heavy-tailed distributions)
    - **Box-Cox**: Requires strictly positive data, computationally expensive
    - **Mean-Range**: Range sensitive to outliers, less statistical basis

Error handling:
    - ValueError for invalid method choice
    - ValueError if Box-Cox receives non-positive data
    - TypeError if input is not pandas Series
    - RuntimeError if transform called before fit

Best practices:
    - Use standardization for most machine learning tasks
    - Use Box-Cox when normality assumption is critical
    - Check data positivity before Box-Cox
    - Visualize distributions before/after normalization
    - Store fitted normalizer for consistent test set transformation

Example workflow:
    ```python
    # Fit on training data
    normalizer = Normalizers(method="standardization")
    train_norm = normalizer.fit_transform(train_data)

    # Transform test data using same parameters
    test_norm = normalizer.transform(test_data)

    # Make predictions, then inverse transform
    predictions_norm = model.predict(test_norm)
    predictions_original = normalizer.inverse_transform(predictions_norm)
    ```

Dependencies: scikit-learn (StandardScaler), scipy (boxcox, inv_boxcox)

Related modules: LogarithmicScaler (log transformation), SimpleScaler
(statistical scaling), GrowthRateScaler (growth rate removal).
"""

from __future__ import annotations

# ruff: noqa: N803 - Using sklearn naming convention (X for data parameter)
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
    from finbot.constants.data_constants import DEMO_DATA
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
