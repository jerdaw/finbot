"""Focused tests for implemented data-cleaning utility behavior."""

from __future__ import annotations

import numpy as np
import pandas as pd

from finbot.utils.data_science_utils.data_cleaning.data_integrity_handlers.custom_validations import (
    apply_custom_validations,
)
from finbot.utils.data_science_utils.data_cleaning.data_integrity_handlers.duplicates_handlers import (
    remove_duplicates,
)
from finbot.utils.data_science_utils.data_cleaning.data_integrity_handlers.identify_corrupted_data import (
    identify_corrupted_data,
)
from finbot.utils.data_science_utils.data_cleaning.data_integrity_handlers.type_and_format_consistency import (
    standardize_column_names,
    standardize_string_formats,
    standardize_types,
    validate_data_ranges,
)
from finbot.utils.data_science_utils.data_cleaning.outlier_handlers.get_outliers_quantile import (
    get_outliers_quantile,
)


def test_quantile_outlier_detection_flags_extreme_values() -> None:
    data = pd.Series([10, 11, 12, 13, 100], name="returns")

    mask = get_outliers_quantile(data)

    assert mask.tolist() == [False, False, False, False, True]


def test_quantile_outlier_detection_can_remove_outliers() -> None:
    data = pd.Series([10, 11, 12, 13, 100], name="returns")

    cleaned = get_outliers_quantile(data, remove=True)

    pd.testing.assert_series_equal(cleaned, pd.Series([10, 11, 12, 13], name="returns"))


def test_quantile_outlier_detection_handles_numeric_dataframes_columnwise() -> None:
    data = pd.DataFrame(
        {
            "a": [10, 11, 12, 13, 100],
            "b": [1, 1, 1, 1, 20],
        }
    )

    mask = get_outliers_quantile(data)

    assert mask.to_dict("list") == {
        "a": [False, False, False, False, True],
        "b": [False, False, False, False, True],
    }


def test_data_integrity_helpers_standardize_and_filter_values() -> None:
    raw = pd.DataFrame(
        {
            "User ID": ["1", "bad", "3"],
            "Status": [" Active ", "INACTIVE ", " pending"],
            "score": [0.8, 1.2, -0.1],
        }
    )

    typed = standardize_types(raw, {"User ID": int})
    assert typed["User ID"].tolist()[0] == 1
    assert np.isnan(typed["User ID"].tolist()[1])

    formatted = standardize_string_formats(raw.copy(), ["Status"], case="lower")
    assert formatted["Status"].tolist() == ["active", "inactive", "pending"]

    in_range = validate_data_ranges(raw.copy(), {"score": (0, 1)})
    assert in_range["score"].tolist() == [0.8]

    renamed = standardize_column_names(raw.copy())
    assert renamed.columns.tolist() == ["user_id", "status", "score"]


def test_duplicate_and_custom_validation_helpers_transform_current_dataframe_behavior() -> None:
    raw = pd.DataFrame(
        {
            "email": [" A@EXAMPLE.COM ", " A@EXAMPLE.COM ", "b@example.com"],
            "quantity": [1, 1, 3],
        }
    )

    deduped = remove_duplicates(raw)
    assert len(deduped) == 2

    validated = apply_custom_validations(
        deduped.copy(),
        {
            "email": lambda series: series.str.lower().str.strip(),
            "quantity": lambda series: series.clip(lower=2),
        },
    )

    assert validated["email"].tolist() == ["a@example.com", "b@example.com"]
    assert validated["quantity"].tolist() == [2, 3]


def test_identify_corrupted_data_returns_column_specific_mask() -> None:
    data = pd.DataFrame(
        {
            "price": [10.0, -1.0, 12.0],
            "symbol": ["SPY", "", "QQQ"],
        }
    )

    mask = identify_corrupted_data(
        data,
        {
            "price": lambda value: value < 0,
            "symbol": lambda value: not value,
        },
    )

    assert mask.to_dict("list") == {
        "price": [False, True, False],
        "symbol": [False, True, False],
    }
