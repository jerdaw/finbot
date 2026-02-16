"""Missing data policy definitions for backtesting."""

from __future__ import annotations

from enum import StrEnum


class MissingDataPolicy(StrEnum):
    """Policy for handling missing data in backtests.

    Defines how to handle gaps or missing values in price history data.
    """

    FORWARD_FILL = "forward_fill"
    """Forward fill missing values with the last known price.

    This is the default behavior and most common approach. Missing values
    are replaced with the previous valid value, assuming prices remain
    constant until new information arrives.

    Use case: Normal market data with occasional gaps.
    Risk: May hide data quality issues.
    """

    DROP = "drop"
    """Drop rows with any missing values.

    Removes any rows (dates) that contain missing values in any column.
    This reduces the dataset size but ensures all data is complete.

    Use case: When you want to ensure data quality.
    Risk: May lose significant data if gaps are frequent.
    """

    ERROR = "error"
    """Raise an error if missing values are detected.

    Fails fast if any missing values are found, forcing the user to
    address data quality issues before proceeding.

    Use case: When data quality is critical and gaps are unexpected.
    Risk: Backtest will fail on any gap.
    """

    INTERPOLATE = "interpolate"
    """Linearly interpolate missing values.

    Fills gaps by linear interpolation between known values. More
    sophisticated than forward fill, but assumes linear price movement.

    Use case: When you want smooth transitions over gaps.
    Risk: May create unrealistic price movements.
    """

    BACKFILL = "backfill"
    """Backward fill missing values with the next known price.

    Opposite of forward fill - uses future values to fill gaps. This
    creates look-ahead bias and should only be used for specific scenarios.

    Use case: Rare, mostly for data preparation outside backtesting.
    Risk: Introduces look-ahead bias in backtests.
    """


# Default policy for all backtests
DEFAULT_MISSING_DATA_POLICY = MissingDataPolicy.FORWARD_FILL
