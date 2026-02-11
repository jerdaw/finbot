"""Intraday time range with iteration and membership testing.

Provides a class for working with time ranges within a single day, supporting
iteration at various granularities (hours, minutes, seconds, microseconds) and
membership testing with configurable inclusivity.

Useful for:
    - Market hours filtering (e.g., 9:30 AM to 4:00 PM)
    - Intraday data validation
    - Time-based scheduling within a day
    - Filtering tick data by time of day

The DailyTimeRange class supports:
    - Iteration with __iter__ (e.g., for t in time_range)
    - Membership testing with __contains__ (e.g., time(10, 30) in time_range)
    - Configurable inclusivity ('both', 'left', 'right', 'neither')
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date, datetime, time, timedelta

from finbot.config import logger


class DailyTimeRange:
    """
    A class to represent a range of times within a day, with a specified granularity.

    Attributes:
        start (time): The start time of the range.
        end (time): The end time of the range.
        granularity (str): The level of granularity for time iteration (e.g., 'hours', 'minutes').
        inclusive (str): Inclusivity of start and end times ('both', 'left', 'right', 'neither').
        step (timedelta): The step size for iteration, derived from granularity.

    Methods:
        __iter__() -> Iterator[time]: An iterator over the time range.
        __contains__(time_check: time) -> bool: Checks if a time is within the range.
    """

    def _get_step_size(self, granularity: str) -> timedelta:
        """
        Determines the step size for iteration based on the specified granularity.

        Args:
            granularity (str): The granularity level ('hours', 'minutes', etc.).

        Returns:
            timedelta: The step size for time iteration.
        """
        granularities = {
            "hours": timedelta(hours=1),
            "minutes": timedelta(minutes=1),
            "seconds": timedelta(seconds=1),
            "milliseconds": timedelta(milliseconds=1),
            "microseconds": timedelta(microseconds=1),
        }
        step = granularities.get(granularity, timedelta(hours=1))
        logger.debug(f"Step size for granularity '{granularity}' is {step}")
        return step

    def __init__(
        self,
        start: time,
        end: time,
        granularity: str = "hours",
        inclusive: str = "both",
    ):
        """
        Constructs all the necessary attributes for the DailyTimeRange object.

        Args:
            start (time): The start time of the range.
            end (time): The end time of the range.
            granularity (str): The level of granularity for time iteration.
            inclusive (str): Inclusivity of start and end times.
        """
        self.start = start
        self.end = end
        self.granularity = granularity
        self.inclusive = inclusive
        self.step = self._get_step_size(granularity)
        logger.info(
            f"Initialized DailyTimeRange with start={start}, end={end}, granularity={granularity}, inclusive={inclusive}",
        )

    def __iter__(self) -> Iterator[time]:
        """
        Iterates over the time range based on the specified granularity.

        Yields:
            time: The next time in the range.
        """
        current_time = datetime.combine(date.min, self.start)
        end_datetime = datetime.combine(date.min, self.end)

        while current_time <= end_datetime:
            yield current_time.time()
            current_time += self.step

    def __contains__(self, time_check: time) -> bool:
        """
        Checks if a specific time is within the range.

        Args:
            time_check (time): The time to check.

        Returns:
            bool: True if the time is within the range, False otherwise.
        """
        start_dt = datetime.combine(date.min, self.start)
        end_dt = datetime.combine(date.min, self.end)
        check_dt = datetime.combine(date.min, time_check)

        if self.inclusive in ["both", "left"]:
            if check_dt < start_dt:
                return False
        else:
            if check_dt <= start_dt:
                return False

        if self.inclusive in ["both", "right"]:
            if check_dt > end_dt:
                return False
        else:
            if check_dt >= end_dt:
                return False

        return True


if __name__ == "__main__":
    time_range = DailyTimeRange(time(8, 0), time(17, 0))
    for t in time_range:
        print(t)
    print(time(8, 0) in time_range)
    print(time(7, 59) in time_range)
    print(time(8, 1) in time_range)
