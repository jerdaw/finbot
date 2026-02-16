"""Latency simulation configuration for order execution.

This module provides contracts for simulating realistic order processing delays
in paper trading and backtesting environments.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True, slots=True)
class LatencyConfig:
    """Latency simulation configuration.

    Attributes:
        submission_latency: Delay from submit_order() to SUBMITTED status
        fill_latency_min: Minimum delay from price update to order fill
        fill_latency_max: Maximum delay from price update to order fill
        cancel_latency: Delay from cancel_order() to CANCELLED status

    Example:
        >>> config = LatencyConfig(
        ...     submission_latency=timedelta(milliseconds=50),
        ...     fill_latency_min=timedelta(milliseconds=100),
        ...     fill_latency_max=timedelta(milliseconds=200),
        ...     cancel_latency=timedelta(milliseconds=50),
        ... )
    """

    submission_latency: timedelta
    fill_latency_min: timedelta
    fill_latency_max: timedelta
    cancel_latency: timedelta


# Pre-configured latency profiles

LATENCY_INSTANT = LatencyConfig(
    submission_latency=timedelta(0),
    fill_latency_min=timedelta(0),
    fill_latency_max=timedelta(0),
    cancel_latency=timedelta(0),
)
"""Instant execution with no latency (default for backtesting)."""

LATENCY_FAST = LatencyConfig(
    submission_latency=timedelta(milliseconds=10),
    fill_latency_min=timedelta(milliseconds=50),
    fill_latency_max=timedelta(milliseconds=100),
    cancel_latency=timedelta(milliseconds=20),
)
"""Fast execution profile (co-located/direct market access)."""

LATENCY_NORMAL = LatencyConfig(
    submission_latency=timedelta(milliseconds=50),
    fill_latency_min=timedelta(milliseconds=100),
    fill_latency_max=timedelta(milliseconds=200),
    cancel_latency=timedelta(milliseconds=50),
)
"""Normal execution profile (typical retail broker)."""

LATENCY_SLOW = LatencyConfig(
    submission_latency=timedelta(milliseconds=100),
    fill_latency_min=timedelta(milliseconds=500),
    fill_latency_max=timedelta(milliseconds=1000),
    cancel_latency=timedelta(milliseconds=100),
)
"""Slow execution profile (high-latency network or congested broker)."""
