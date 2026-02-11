"""Calculate correlation matrices for multiple pandas DataFrames or Series.

Computes correlation between multiple datasets using Pearson, Spearman, or
Kendall methods. Useful for analyzing relationships between different time
series, features, or asset returns.

Typical usage:
    ```python
    # Calculate Pearson correlation between multiple assets
    correlation_matrix = get_correlation(datas=[stock_a, stock_b, bond], method="pearson")

    # Spearman rank correlation (robust to outliers)
    correlation_matrix = get_correlation(datas=[price_series_1, price_series_2, price_series_3], method="spearman")

    # Kendall tau correlation (ordinal relationships)
    correlation_matrix = get_correlation(datas=[data1, data2, data3], method="kendall")
    ```

Correlation methods:

1. **Pearson** (default):
   - Measures linear correlation
   - Range: -1 to +1
   - Assumes normal distribution
   - Sensitive to outliers
   - Most common method

2. **Spearman**:
   - Measures monotonic correlation (rank-based)
   - Range: -1 to +1
   - Non-parametric (no distribution assumption)
   - Robust to outliers
   - Good for non-linear monotonic relationships

3. **Kendall**:
   - Measures ordinal association (rank concordance)
   - Range: -1 to +1
   - Non-parametric
   - More robust than Spearman for small samples
   - Computational cost higher than Pearson/Spearman

Correlation interpretation:
    - +1.0: Perfect positive correlation
    - +0.7 to +1.0: Strong positive correlation
    - +0.3 to +0.7: Moderate positive correlation
    - -0.3 to +0.3: Weak or no correlation
    - -0.7 to -0.3: Moderate negative correlation
    - -1.0 to -0.7: Strong negative correlation
    - -1.0: Perfect negative correlation

Features:
    - Supports multiple DataFrames/Series simultaneously
    - Three correlation methods (Pearson, Spearman, Kendall)
    - Automatic index alignment via pd.concat
    - Input validation with helpful error messages
    - Warning for single dataset (trivial 1x1 correlation)

Use cases:
    - Portfolio diversification analysis
    - Feature selection (remove highly correlated features)
    - Asset correlation matrices for risk analysis
    - Time series similarity analysis
    - Multi-collinearity detection

Requirements:
    - All datasets must have identical index
    - All datasets must have same number of columns
    - List must contain at least 1 dataset

Error handling:
    - ValueError for empty list
    - ValueError for non-DataFrame/Series items
    - ValueError for invalid correlation method
    - ValueError for index mismatch
    - ValueError for column count mismatch
    - Warning (logged) if only single dataset provided

Example workflows:
    ```python
    # Portfolio correlation analysis
    stocks = [get_history(ticker)["Close"] for ticker in ["AAPL", "MSFT", "GOOGL"]]
    corr_matrix = get_correlation(stocks, method="pearson")
    print(corr_matrix)  # Shows inter-stock correlations

    # Feature correlation for ML preprocessing
    features = [df["feature1"], df["feature2"], df["feature3"]]
    corr = get_correlation(features, method="spearman")
    # Identify highly correlated features (> 0.9) for removal

    # Asset class diversification
    assets = [stocks_returns, bonds_returns, commodities_returns, real_estate_returns]
    corr = get_correlation(assets, method="pearson")
    # Low correlations indicate good diversification
    ```

Best practices:
    - Use Pearson for normally distributed continuous data
    - Use Spearman for non-linear monotonic relationships or outliers
    - Use Kendall for small samples or ordinal data
    - Check for index alignment before calling
    - Visualize correlation matrix with heatmap
    - Consider significance testing for small samples

Limitations:
    - Correlation does not imply causation
    - Only measures specific relationship types (linear, monotonic, ordinal)
    - Sensitive to time period selection
    - Spurious correlations possible in non-stationary data

Related modules: data_smoothing (preprocessing), rebase_cumu_pct_change
(normalize before correlation), pandas_utils (data alignment).
"""

from typing import Literal

import pandas as pd

from config import logger


def _validate_params(datas: list[pd.DataFrame | pd.Series], method: Literal["pearson", "kendall", "spearman"]) -> None:
    if not isinstance(datas, list):
        raise ValueError("Input data must be a list of pandas DataFrame or Series.")

    if not datas:
        raise ValueError("Value Error: Input data list cannot be empty.")

    for item in datas:
        if not isinstance(item, pd.DataFrame | pd.Series):
            raise ValueError("All items in the list must be pandas DataFrame or Series objects.")

    valid_methods = {"pearson", "spearman", "kendall"}
    if method not in valid_methods:
        raise ValueError(f"Invalid correlation method: {method}. Valid methods are: {valid_methods}")

    if not all(datas[0].index.equals(item.index) for item in datas):
        raise ValueError("Value Error: All DataFrames/Series must have the same index for correlation calculation.")

    if len({len(data.columns) for data in datas if isinstance(data, pd.DataFrame)}) > 1:
        raise ValueError("All DataFrames/Series in the list must have the same number of columns.")

    if len(datas) == 1:
        logger.warning("Only one dataset provided. Correlation matrix will be a 1x1 DataFrame with correlation 1.0.")


def get_correlation(
    datas: list[pd.DataFrame | pd.Series],
    method: Literal["pearson", "kendall", "spearman"] = "pearson",
) -> pd.DataFrame:
    """
    Calculate the correlation between multiple datasets.

    Parameters:
    datas (List[pd.DataFrame | pd.Series]): A list of pandas DataFrames or Series containing the datasets.
    method (str, optional): The correlation method to use. Default is "pearson".
        Valid methods are:
        - "pearson": Standard correlation coefficient
        - "spearman": Spearman rank correlation
        - "kendall": Kendall Tau correlation coefficient

    Returns:
    pd.DataFrame: A DataFrame containing the correlation matrix.

    Raises:
    ValueError: If the input list is empty, contains invalid types, or an invalid correlation method is provided.
    """

    _validate_params(datas=datas, method=method)
    combined_data = pd.concat(datas, axis=1)
    return combined_data.corr(method=method)


if __name__ == "__main__":
    # Example usage:
    import numpy as np

    from constants.data_constants import DEMO_DATA

    CLOSE_DATA = DEMO_DATA["Close"].rename("Original")
    INV_DATA = (CLOSE_DATA * -1).rename("Inverse")
    RAND_DATA = pd.DataFrame(np.random.rand(len(DEMO_DATA)), index=DEMO_DATA.index).squeeze().rename("Random")

    print(CLOSE_DATA)
    print(INV_DATA)
    print(RAND_DATA)

    data = [CLOSE_DATA, RAND_DATA, INV_DATA]
    correlation_matrix = get_correlation(datas=data, method="spearman")
    print(correlation_matrix)
