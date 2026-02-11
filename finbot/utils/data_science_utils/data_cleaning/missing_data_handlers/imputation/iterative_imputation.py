"""Iterative imputation using sklearn's IterativeImputer (MICE algorithm).

Performs multivariate imputation using iterative modeling. This is a general
wrapper around sklearn's IterativeImputer, which implements the MICE (Multiple
Imputation by Chained Equations) algorithm. See mice_imputation.py for a more
specific MICE implementation with additional safeguards.

Typical usage:
    ```python
    # Basic iterative imputation
    df_filled = iterative_impute(df)

    # Customize imputation parameters
    df_filled = iterative_impute(df, max_iter=20, random_state=42, initial_strategy="median")

    # In-place modification
    iterative_impute(df, inplace=True)
    ```

How iterative imputation works:
    1. Initialize missing values using simple strategy (default: mean)
    2. For each feature with missing values:
       - Treat it as dependent variable
       - Use other features as independent variables
       - Fit regression model and predict missing values
    3. Iterate until convergence or max_iter reached

Key parameters (via **kwargs):
    - max_iter: Maximum iterations (default: 10)
    - initial_strategy: Initial imputation ('mean', 'median', 'most_frequent')
    - random_state: Seed for reproducibility
    - estimator: Regression estimator (default: BayesianRidge)
    - imputation_order: Order to impute features ('ascending', 'descending', etc.)

Features:
    - Flexible configuration via sklearn kwargs
    - Preserves multivariate relationships
    - Handles arbitrary missing patterns
    - In-place or copy modification
    - Works with both DataFrames and Series

Use cases:
    - Complex multivariate missing patterns
    - When default MICE parameters need customization
    - Research requiring specific estimator choice
    - Comparing different iterative strategies

Trade-offs:
    - Computationally expensive for large datasets
    - Requires tuning for optimal performance
    - May not converge for all datasets
    - Less user-friendly than mice_imputation.py (no max_iter validation)

Dependencies: scikit-learn (sklearn.impute.IterativeImputer)

Related modules: mice_imputation (same algorithm with safeguards),
knn_imputation (simpler alternative), simple_imputation (fastest baseline).
"""

from __future__ import annotations

import pandas as pd
from sklearn.impute import IterativeImputer

from finbot.utils.data_science_utils.data_cleaning.missing_data_handlers._missing_data_utils import (
    _check_numeric,
    _validate_df_or_series,
)


def iterative_impute(data, inplace: bool = False, **kwargs):
    """
    Perform imputation on the given data using sklearn's IterativeImputer.

    Args:
        data (pd.DataFrame or pd.Series): The input data with missing values to be imputed.
        inplace (bool): Whether to perform the imputation in-place. Default is False.
        **kwargs: Additional keyword arguments to pass to sklearn's IterativeImputer.

    Returns:
        pd.DataFrame or pd.Series: The imputed data with missing values replaced.
    """
    _validate_df_or_series(data)
    _check_numeric(data)

    was_series = False
    if isinstance(data, pd.Series):
        data = data.to_frame()
        was_series = True

    imputer = IterativeImputer(**kwargs)
    imputed_data = imputer.fit_transform(data)

    if inplace:
        data.loc[:, :] = imputed_data
        return data.squeeze() if was_series else data
    else:
        imputed_result = pd.DataFrame(
            imputed_data,
            columns=data.columns,
            index=data.index,
        )
        return imputed_result.squeeze() if was_series else imputed_result
