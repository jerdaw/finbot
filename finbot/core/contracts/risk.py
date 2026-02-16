"""Risk control contracts for execution safety.

This module defines contracts for risk management including position limits,
exposure limits, drawdown protection, and kill-switch functionality.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class RiskRuleType(StrEnum):
    """Type of risk rule."""

    POSITION_LIMIT = "position_limit"
    EXPOSURE_LIMIT = "exposure_limit"
    DRAWDOWN_LIMIT = "drawdown_limit"
    KILL_SWITCH = "kill_switch"


@dataclass(frozen=True, slots=True)
class RiskViolation:
    """Risk rule violation details.

    Attributes:
        rule_type: Type of rule violated
        message: Human-readable violation message
        current_value: Current value that triggered violation
        limit_value: Limit that was exceeded
    """

    rule_type: RiskRuleType
    message: str
    current_value: Decimal
    limit_value: Decimal


@dataclass(frozen=True, slots=True)
class PositionLimitRule:
    """Limit position size per symbol.

    Attributes:
        max_shares: Maximum shares per symbol (None = unlimited)
        max_value: Maximum position value per symbol (None = unlimited)

    Example:
        >>> rule = PositionLimitRule(
        ...     max_shares=Decimal("1000"),
        ...     max_value=Decimal("50000"),
        ... )
    """

    max_shares: Decimal | None = None
    max_value: Decimal | None = None


@dataclass(frozen=True, slots=True)
class ExposureLimitRule:
    """Limit total portfolio exposure.

    Attributes:
        max_gross_exposure_pct: Maximum gross exposure as % of capital (default: 100%)
        max_net_exposure_pct: Maximum net exposure as % of capital (default: 100%)

    Example:
        >>> rule = ExposureLimitRule(
        ...     max_gross_exposure_pct=Decimal("150"),  # 150% allows 1.5x leverage
        ...     max_net_exposure_pct=Decimal("100"),  # Net long must be <= 100%
        ... )
    """

    max_gross_exposure_pct: Decimal = Decimal("100")
    max_net_exposure_pct: Decimal = Decimal("100")


@dataclass(frozen=True, slots=True)
class DrawdownLimitRule:
    """Limit portfolio drawdown from peak.

    Attributes:
        max_daily_drawdown_pct: Maximum daily loss % (None = unlimited)
        max_total_drawdown_pct: Maximum total loss % from peak (None = unlimited)

    Example:
        >>> rule = DrawdownLimitRule(
        ...     max_daily_drawdown_pct=Decimal("5"),  # Stop if down 5% today
        ...     max_total_drawdown_pct=Decimal("20"),  # Stop if down 20% from peak
        ... )
    """

    max_daily_drawdown_pct: Decimal | None = None
    max_total_drawdown_pct: Decimal | None = None


@dataclass
class RiskConfig:
    """Risk control configuration.

    Attributes:
        position_limit: Position size limits per symbol
        exposure_limit: Total portfolio exposure limits
        drawdown_limit: Drawdown protection limits
        trading_enabled: Kill-switch state (False = all trading disabled)

    Example:
        >>> config = RiskConfig(
        ...     position_limit=PositionLimitRule(max_shares=Decimal("1000")),
        ...     exposure_limit=ExposureLimitRule(max_gross_exposure_pct=Decimal("100")),
        ...     drawdown_limit=DrawdownLimitRule(max_daily_drawdown_pct=Decimal("5")),
        ...     trading_enabled=True,
        ... )
    """

    position_limit: PositionLimitRule | None = None
    exposure_limit: ExposureLimitRule | None = None
    drawdown_limit: DrawdownLimitRule | None = None
    trading_enabled: bool = True
