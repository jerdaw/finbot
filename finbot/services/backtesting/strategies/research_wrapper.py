"""Strategy wrapper utilities for portfolio-research backtests.

Adds recurring and one-time portfolio cashflows plus allocation-history
capture around existing Backtrader strategies so the flagship backtesting
workflow can expose retirement-planning and drift diagnostics without
rewriting each individual strategy.

Typical usage:
    wrapped_strategy = build_research_strategy(NoRebalance)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

import backtrader as bt


@dataclass(slots=True)
class _RecurringCashflowRule:
    amount: float
    frequency: str
    start_date: date | None
    end_date: date | None
    label: str
    last_period_key: tuple[int, ...] | None = None


@dataclass(slots=True)
class _OneTimeCashflowRule:
    amount: float
    date: date
    label: str
    applied: bool = False


def _parse_date(value: str | date | datetime | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.fromisoformat(value).date()


def _parse_required_date(value: str | date | datetime | None) -> date:
    parsed_date = _parse_date(value)
    if parsed_date is None:
        raise ValueError("One-time cashflow rules require a date")
    return parsed_date


def _period_key(current_date: date, frequency: str) -> tuple[int, ...]:
    if frequency == "monthly":
        return (current_date.year, current_date.month)
    if frequency == "quarterly":
        return (current_date.year, (current_date.month - 1) // 3 + 1)
    if frequency == "yearly":
        return (current_date.year,)
    raise ValueError(f"Unsupported recurring cashflow frequency: {frequency}")


def _build_recurring_cashflows(rules: list[dict[str, Any]] | None) -> list[_RecurringCashflowRule]:
    return [
        _RecurringCashflowRule(
            amount=float(rule["amount"]),
            frequency=str(rule["frequency"]),
            start_date=_parse_date(rule.get("start_date")),
            end_date=_parse_date(rule.get("end_date")),
            label=str(rule.get("label") or "Recurring cashflow"),
        )
        for rule in (rules or [])
    ]


def _build_one_time_cashflows(rules: list[dict[str, Any]] | None) -> list[_OneTimeCashflowRule]:
    return [
        _OneTimeCashflowRule(
            amount=float(rule["amount"]),
            date=_parse_required_date(rule["date"]),
            label=str(rule.get("label") or "One-time cashflow"),
        )
        for rule in (rules or [])
    ]


class _ResearchWorkflowMixin:
    def __init__(
        self,
        recurring_cashflows: list[dict[str, Any]] | None = None,
        one_time_cashflows: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> None:
        self._recurring_cashflows = _build_recurring_cashflows(recurring_cashflows)
        self._one_time_cashflows = _build_one_time_cashflows(one_time_cashflows)
        self._cashflow_events: list[dict[str, Any]] = []
        self._allocation_history: list[dict[str, Any]] = []
        self._one_time_cashflows.sort(key=lambda rule: rule.date)
        super().__init__(**kwargs)

    def _current_date(self: Any) -> date:
        return bt.num2date(self.datetime[0]).date()

    def _record_cashflow_event(
        self: Any,
        *,
        amount: float,
        scheduled_date: date,
        applied_date: date,
        label: str,
        source: str,
    ) -> None:
        self._cashflow_events.append(
            {
                "scheduled_date": scheduled_date.isoformat(),
                "applied_date": applied_date.isoformat(),
                "label": label,
                "source": source,
                "direction": "contribution" if amount >= 0 else "withdrawal",
                "amount": amount,
                "cash_after": float(self.broker.get_cash()),
                "portfolio_value_after": float(self.broker.get_value()),
            }
        )

    def _apply_cashflows(self: Any) -> None:
        current_date = self._current_date()

        for rule in self._recurring_cashflows:
            if rule.start_date is not None and current_date < rule.start_date:
                continue
            if rule.end_date is not None and current_date > rule.end_date:
                continue

            current_period = _period_key(current_date, rule.frequency)
            if current_period == rule.last_period_key:
                continue

            self.broker.add_cash(rule.amount)
            rule.last_period_key = current_period
            self._record_cashflow_event(
                amount=rule.amount,
                scheduled_date=current_date,
                applied_date=current_date,
                label=rule.label,
                source="recurring",
            )

        for one_time_rule in self._one_time_cashflows:
            if one_time_rule.applied or current_date < one_time_rule.date:
                continue
            self.broker.add_cash(one_time_rule.amount)
            one_time_rule.applied = True
            self._record_cashflow_event(
                amount=one_time_rule.amount,
                scheduled_date=one_time_rule.date,
                applied_date=current_date,
                label=one_time_rule.label,
                source="one_time",
            )

    def _record_allocation_snapshot(self: Any) -> None:
        total_value = float(self.broker.get_value())
        current_date = self._current_date().isoformat()
        snapshot: dict[str, Any] = {"date": current_date}

        cash = float(self.broker.get_cash())
        snapshot["Cash"] = (cash / total_value) if total_value else None

        for data in self.datas:
            symbol = data._name if hasattr(data, "_name") else str(data)
            position_value = float(self.getposition(data).size * data.close[0])
            snapshot[symbol] = (position_value / total_value) if total_value else None

        self._allocation_history.append(snapshot)

    def next(self: Any) -> None:
        self._apply_cashflows()
        self._record_allocation_snapshot()
        parent_next = getattr(super(), "next", None)
        if parent_next is not None:
            parent_next()

    def get_cashflow_events(self) -> list[dict[str, Any]]:
        return list(self._cashflow_events)

    def get_allocation_history(self) -> list[dict[str, Any]]:
        return list(self._allocation_history)


def build_research_strategy(base_strategy: Any) -> Any:
    """Wrap a Backtrader strategy with research-workflow instrumentation."""

    return type(
        f"ResearchWrapped{base_strategy.__name__}",
        (_ResearchWorkflowMixin, base_strategy),
        {},
    )
