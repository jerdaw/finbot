"""Multiple Imputation by Chained Equations (MICE) for missing values.

Performs sophisticated multivariate imputation using iterative modeling where
each feature with missing values is modeled as a function of other features in
a round-robin fashion. Also known as "fully conditional specification" or
"sequential regression multiple imputation".

Typical usage:
    ```python
    # MICE imputation with default 10 iterations
    df_filled = mice_imputation(df, max_iter=10)

    # More iterations for better convergence
    df_filled = mice_imputation(df, max_iter=20)

    # In-place imputation
    mice_imputation(df, max_iter=15, inplace=True)
    ```

How MICE works:
    1. Start with simple imputation (e.g., mean)
    2. For each feature with missing values:
       - Use other features as predictors in regression model
       - Predict missing values for that feature
       - Update imputed values
    3. Repeat until convergence or max_iter reached
    4. Each iteration refines imputation using updated values

Algorithm characteristics:
    - Iterative refinement produces more accurate imputations
    - Models complex dependencies between features
    - Handles arbitrary missing patterns (MAR assumption)
    - Can use different models for different features

Parameters:
    - max_iter: Maximum imputation iterations (default: 10, range: 1-100)
    - Warning issued if max_iter > 10 (can be very slow)

Features:
    - Preserves multivariate relationships
    - Works with arbitrary missing patterns
    - In-place or copy modification
    - Convergence monitoring via iteration count

Use cases:
    - Complex multivariate missing patterns
    - When features are highly correlated
    - When simple methods produce biased estimates
    - Research/statistical analysis requiring rigorous imputation

Trade-offs:
    - Most computationally expensive imputation method
    - Can take very long time for large datasets or high max_iter
    - Requires multiple complete cases to initialize
    - May not converge for all datasets

Dependencies: scikit-learn (sklearn.impute.IterativeImputer)

Related modules: iterative_imputation (same algorithm, different wrapper),
knn_imputation (simpler but faster), simple_imputation (fastest baseline).
"""

from __future__ import annotations

import pandas as pd
from sklearn.impute import IterativeImputer

from finbot.utils.data_science_utils.data_cleaning.missing_data_handlers._missing_data_utils import (
    _check_numeric,
    _validate_df_or_series,
)


def mice_imputation(data: pd.DataFrame, max_iter: int = 10, inplace: bool = False) -> pd.DataFrame:
    """
    Perform Multiple Imputation by Chained Equations (MICE) on the given data.

    Args:
        data (pd.DataFrame): The input data with missing values.
        max_iter (int): Maximum number of imputation iterations. Default is 10.
        inplace (bool): Whether to perform the imputation in-place. Default is False.

    Returns:
        pd.DataFrame: The imputed data with missing values replaced by MICE.

    Raises:
        TypeError: If the data is not a DataFrame.
    """
    if not inplace:
        data = data.copy()
    _validate_df_or_series(data)
    _check_numeric(data)

    if not 1 <= max_iter <= 100:
        raise ValueError(
            "Maximum number of iterations must be between 1 and 100.",
        )
    elif max_iter > 10:
        print("WARNING: Maximum number of iterations greater than 10 may take a (very) long time to run.")

    imputer = IterativeImputer(max_iter=max_iter)
    imputed_data = imputer.fit_transform(data)
    data.loc[:, :] = imputed_data

    return data
