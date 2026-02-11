"""Generate set of all months between two dates.

Returns a set of (year, month) tuples representing every month in the date range.
Useful for iterating over months or identifying missing monthly data.

Supports both integer tuples (2022, 1) and string tuples ('2022', '01') for
compatibility with different data storage formats.

Typical usage:
    - Identify missing months in time series data
    - Generate monthly data collection schedules
    - Iterate over months for batch processing
    - Validate data completeness
"""

from __future__ import annotations

from datetime import date

from dateutil.relativedelta import relativedelta

from config import logger


def get_months_between_dates(
    start_date: date,
    end_date: date,
    return_type: str = "int",
) -> set[tuple[int, int]] | set[tuple[str, str]]:
    """
    Get a set of all months between two dates in specified format.

    Args:
        start_date (date): The start date.
        end_date (date): The end date.
        return_type (str): The return type of the months ('int' for integers, 'str' for strings).

    Returns:
        set[tuple[int, int]] | set[tuple[str, str]]: A set of months in specified format.
    """
    try:
        current = start_date
        months_as_int: set[tuple[int, int]] = set()
        months_as_str: set[tuple[str, str]] = set()

        while current <= end_date:
            year, month = current.year, current.month
            if return_type == "str":
                months_as_str.add((f"{year:04d}", f"{month:02d}"))
            else:  # default to int
                months_as_int.add((year, month))
            current = current.replace(day=1) + relativedelta(months=1)

        return months_as_str if return_type.lower() == "str" else months_as_int
    except Exception as e:
        logger.error(
            f"Error in getting months between {start_date} and {end_date}: {e}",
        )
        raise


if __name__ == "__main__":
    start_date = date(2022, 1, 1)
    end_date = date(2022, 12, 31)
    months = get_months_between_dates(start_date, end_date)
    print(months)
