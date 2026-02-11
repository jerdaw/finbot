"""Cap (winsorize) outliers by limiting values to specified bounds.

Treats outliers by capping extreme values at specified lower and upper limits
rather than removing them. Also known as "winsorization". Preserves sample
size while reducing influence of extreme values.

**STATUS: NOT IMPLEMENTED** - This module raises NotImplementedError and has
not been confirmed to work as intended.

Typical usage (when implemented):
    ```python
    # Cap outliers at 5th and 95th percentiles
    df_capped = cap_outliers(df, limit=(df.quantile(0.05), df.quantile(0.95)))

    # Cap at specific values
    df_capped = cap_outliers(df, limit=(-100, 100))

    # Cap using IQR bounds
    q1, q3 = df.quantile(0.25), df.quantile(0.75)
    iqr = q3 - q1
    df_capped = cap_outliers(df, limit=(q1 - 1.5 * iqr, q3 + 1.5 * iqr))
    ```

Capping/Winsorization:
    - Replace values below lower limit with lower limit
    - Replace values above upper limit with upper limit
    - Preserves sample size (unlike removal)
    - Reduces impact of outliers without deletion

Parameters (when implemented):
    - data: DataFrame to treat
    - limit: Tuple of (lower_bound, upper_bound) for capping
    - mask: Optional boolean mask identifying outliers

Advantages over removal:
    - Preserves sample size (important for small datasets)
    - Maintains row-to-row correspondence
    - Reduces outlier influence while keeping information
    - Useful when outliers are errors but sample size is critical

Disadvantages:
    - Introduces bias at distribution tails
    - May distort true data patterns
    - Arbitrary choice of limits
    - Can create artificial "spikes" at cap values

Use cases (when implemented):
    - Small datasets where removal loses too much data
    - Time series where gaps are problematic
    - Machine learning when sample size is limited
    - Regulatory/compliance contexts requiring data retention

Capping methods:
    - Percentile-based: Cap at Xth and (100-X)th percentiles
    - IQR-based: Cap at Q1 - k*IQR and Q3 + k*IQR
    - Domain-based: Cap at known physical/business limits
    - Sigma-based: Cap at mu +/- k*sigma (for normal data)

Best practices (when implemented):
    - Document capping limits and rationale
    - Visualize before/after distributions
    - Consider if capping is appropriate for your analysis
    - Report number of capped values

Alternative approaches:
    - **treat_outliers_remove**: Remove outliers entirely (lose data)
    - **treat_outliers_transform**: Transform data (log, sqrt) to reduce skew
    - **Imputation**: Replace outliers with imputed values

Note: Until this module is implemented, use pandas.DataFrame.clip() directly
for capping functionality.

Related modules: treat_outliers_remove (removal instead of capping),
treat_outliers_transform (transformation), get_outliers_quantile (detection).
"""

import pandas as pd

from finbot.utils.data_science_utils.data_cleaning.outlier_handlers._outliers_utils import _apply_treatment_to_pandas


def _cap_outliers_logic(**kwargs) -> pd.Series:
    """Cap outliers in the Series within the specified limits."""
    raise NotImplementedError("This function hasn't yet been confirmed to work as intended.")
    data = kwargs.get("data")  # type: ignore[unreachable]
    limit = kwargs.get("limit")
    return data.where(~kwargs.get("mask"), data.clip(limit[0], limit[1]))


def cap_outliers(data: pd.DataFrame, limit: tuple[float, float]) -> pd.DataFrame:
    raise NotImplementedError("This function hasn't yet been confirmed to work as intended.")
    return _apply_treatment_to_pandas(  # type: ignore[unreachable]
        data=data,
        method=_cap_outliers_logic,
        limit=limit,
    )
