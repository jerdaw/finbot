"""Apply custom validation and transformation functions to DataFrame columns.

Provides a framework for applying column-specific validation functions that
transform/clean data according to custom business logic. Useful for enforcing
data quality rules, standardizing formats, or applying domain-specific
transformations.

Typical usage:
    ```python
    # Define validation functions for specific columns
    validations = {
        "email": lambda s: s.str.lower().str.strip(),
        "age": lambda s: s.clip(0, 120),  # Cap age at reasonable range
        "zipcode": lambda s: s.astype(str).str.zfill(5),  # Pad with zeros
        "phone": lambda s: s.str.replace(r"[^0-9]", "", regex=True),  # Remove non-digits
    }

    # Apply all validations
    df_validated = apply_custom_validations(df, validation_functions=validations)
    ```

Validation function signature:
    - Input: pd.Series (column to validate)
    - Output: pd.Series (validated/transformed column)
    - Function modifies column in-place in result DataFrame

Features:
    - Column-specific validation logic
    - Applies transformations to specified columns only
    - Returns modified DataFrame
    - Simple dict-based configuration

Use cases:
    - Email normalization (lowercase, trimming)
    - Phone number standardization (remove formatting)
    - ZIP code formatting (leading zeros)
    - Data type enforcement with coercion
    - Range validation and capping
    - Text cleaning and standardization
    - Categorical value mapping

Example validation functions:
    ```python
    # Email cleaning
    'email': lambda s: s.str.lower().str.strip().replace('', pd.NA)

    # Currency formatting (remove symbols, convert to float)
    'price': lambda s: s.str.replace('$', '').str.replace(',', '').astype(float)

    # Date standardization
    'date': lambda s: pd.to_datetime(s, errors='coerce')

    # Categorical mapping
    'status': lambda s: s.map({'active': 'A', 'inactive': 'I', 'pending': 'P'})

    # Text normalization
    'name': lambda s: s.str.title().str.strip()
    ```

Best practices:
    - Test validation functions on sample data first
    - Handle errors appropriately (use errors='coerce' for type conversions)
    - Document validation logic for each column
    - Consider impact on data types
    - Chain simple operations for clarity

Error handling:
    - Validation functions should handle edge cases
    - Use pd.NA or np.nan for invalid values
    - Consider using .pipe() for complex multi-step validations
    - Log validation failures if needed

Limitations:
    - Operates column-by-column (no cross-column validation)
    - No built-in error handling (functions must handle their own errors)
    - Modifies DataFrame directly (no validation reports)

For more structured validation:
    - Consider using libraries like pandera or great_expectations
    - For cross-column validation, use irrelevant_data_handler with custom functions
    - For type consistency, see type_and_format_consistency module

Related modules: type_and_format_consistency (standardize types/formats),
irrelevant_data_handler (row-level validation), identify_corrupted_data
(corruption detection).
"""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd


def apply_custom_validations(
    data: pd.DataFrame,
    validation_functions: dict[str, Callable[[pd.Series], pd.Series]],
) -> pd.DataFrame:
    """
    Apply custom validation functions to specified columns.
    """
    for column, func in validation_functions.items():
        data[column] = func(data[column])
    return data
