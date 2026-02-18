"""CLI parameter validators for input validation.

Provides Click callbacks and custom types for validating CLI inputs
with helpful error messages.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

import click


class DateParamType(click.ParamType):
    """Custom Click type for date parameters (YYYY-MM-DD format)."""

    name = "date"

    def convert(
        self,
        value: Any,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> str | None:
        """Convert and validate date string.

        Args:
            value: Input value
            param: Click parameter
            ctx: Click context

        Returns:
            Validated date string in YYYY-MM-DD format

        Raises:
            click.BadParameter: If date format is invalid
        """
        if value is None:
            return value

        # If already a string, validate format
        if isinstance(value, str):
            # Check format with regex
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
                self.fail(
                    f"'{value}' is not a valid date. Expected format: YYYY-MM-DD (e.g., 2024-01-15)",
                    param,
                    ctx,
                )

            # Validate that it's a real date
            try:
                datetime.strptime(value, "%Y-%m-%d")
                return value
            except ValueError as e:
                self.fail(
                    f"'{value}' is not a valid date: {e}. Expected format: YYYY-MM-DD",
                    param,
                    ctx,
                )

        self.fail(f"Expected string, got {type(value).__name__}", param, ctx)


class TickerParamType(click.ParamType):
    """Custom Click type for stock/fund ticker symbols."""

    name = "ticker"

    def convert(
        self,
        value: Any,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> str | None:
        """Convert and validate ticker symbol.

        Args:
            value: Input value
            param: Click parameter
            ctx: Click context

        Returns:
            Validated uppercase ticker symbol

        Raises:
            click.BadParameter: If ticker format is invalid
        """
        if value is None:
            return value

        if isinstance(value, str):
            # Convert to uppercase
            ticker = value.upper().strip()

            # Validate format: 1-5 letters, optional numbers
            if not re.match(r"^[A-Z]{1,5}[0-9]?$", ticker):
                self.fail(
                    f"'{value}' is not a valid ticker symbol. Expected 1-5 letters (e.g., SPY, TQQQ, BND)",
                    param,
                    ctx,
                )

            return ticker

        self.fail(f"Expected string, got {type(value).__name__}", param, ctx)


class PositiveFloatParamType(click.ParamType):
    """Custom Click type for positive float values."""

    name = "positive_float"

    def __init__(self, min_value: float = 0.0):
        """Initialize with minimum allowed value.

        Args:
            min_value: Minimum allowed value (exclusive)
        """
        self.min_value = min_value

    def convert(
        self,
        value: Any,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> float | None:
        """Convert and validate positive float.

        Args:
            value: Input value
            param: Click parameter
            ctx: Click context

        Returns:
            Validated positive float

        Raises:
            click.BadParameter: If value is not positive
        """
        if value is None:
            return value

        try:
            float_value = float(value)
        except (ValueError, TypeError):
            self.fail(f"'{value}' is not a valid number", param, ctx)
            return None  # type: ignore  # fail() raises

        if float_value <= self.min_value:
            self.fail(
                f"Value must be greater than {self.min_value}, got {float_value}",
                param,
                ctx,
            )

        return float_value


class PositiveIntParamType(click.ParamType):
    """Custom Click type for positive integer values."""

    name = "positive_int"

    def __init__(self, min_value: int = 0):
        """Initialize with minimum allowed value.

        Args:
            min_value: Minimum allowed value (exclusive)
        """
        self.min_value = min_value

    def convert(
        self,
        value: Any,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> int | None:
        """Convert and validate positive integer.

        Args:
            value: Input value
            param: Click parameter
            ctx: Click context

        Returns:
            Validated positive integer

        Raises:
            click.BadParameter: If value is not a positive integer
        """
        if value is None:
            return value

        try:
            int_value = int(value)
        except (ValueError, TypeError):
            self.fail(f"'{value}' is not a valid integer", param, ctx)
            return None  # type: ignore  # fail() raises

        if int_value <= self.min_value:
            self.fail(
                f"Value must be greater than {self.min_value}, got {int_value}",
                param,
                ctx,
            )

        return int_value


# Reusable validator instances
DATE = DateParamType()
TICKER = TickerParamType()
POSITIVE_FLOAT = PositiveFloatParamType(min_value=0.0)
POSITIVE_INT = PositiveIntParamType(min_value=0)


def validate_date_range(
    ctx: click.Context,
    param: click.Parameter,
    value: tuple[str | None, str | None] | None,
) -> tuple[str | None, str | None] | None:
    """Validate that start date is before end date.

    This is a callback for Click commands with both --start and --end options.

    Args:
        ctx: Click context
        param: Click parameter
        value: Tuple of (start_date, end_date)

    Returns:
        Validated date range tuple

    Raises:
        click.BadParameter: If start date is after end date
    """
    if value is None:
        return value

    start_date, end_date = value

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")

            if start >= end:
                raise click.BadParameter(
                    f"Start date ({start_date}) must be before end date ({end_date})",
                    ctx=ctx,
                    param=param,
                )
        except ValueError as e:
            raise click.BadParameter(f"Invalid date format: {e}", ctx=ctx, param=param) from e

    return value


def validate_allocation_ratio(
    ctx: click.Context,
    param: click.Parameter,
    value: float | None,
) -> float | None:
    """Validate allocation ratio is between 0 and 1.

    Args:
        ctx: Click context
        param: Click parameter
        value: Allocation ratio value

    Returns:
        Validated ratio

    Raises:
        click.BadParameter: If ratio is not between 0 and 1
    """
    if value is None:
        return value

    if not 0.0 <= value <= 1.0:
        raise click.BadParameter(
            f"Allocation ratio must be between 0 and 1, got {value}",
            ctx=ctx,
            param=param,
        )

    return value


def validate_commission_rate(
    ctx: click.Context,
    param: click.Parameter,
    value: float | None,
) -> float | None:
    """Validate commission rate is between 0 and 1.

    Args:
        ctx: Click context
        param: Click parameter
        value: Commission rate value

    Returns:
        Validated commission rate

    Raises:
        click.BadParameter: If rate is not between 0 and 1
    """
    if value is None:
        return value

    if not 0.0 <= value <= 1.0:
        raise click.BadParameter(
            f"Commission rate must be between 0 and 1 (0% to 100%), got {value}",
            ctx=ctx,
            param=param,
        )

    return value


def validate_leverage_ratio(
    ctx: click.Context,
    param: click.Parameter,
    value: float | None,
) -> float | None:
    """Validate leverage ratio is reasonable (-10 to 10).

    Args:
        ctx: Click context
        param: Click parameter
        value: Leverage ratio value

    Returns:
        Validated leverage ratio

    Raises:
        click.BadParameter: If ratio is unreasonable
    """
    if value is None:
        return value

    if not -10.0 <= value <= 10.0:
        raise click.BadParameter(
            f"Leverage ratio must be between -10 and 10, got {value}",
            ctx=ctx,
            param=param,
        )

    return value
