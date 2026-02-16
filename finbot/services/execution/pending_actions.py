"""Pending action queue for time-based order processing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any


class ActionType(StrEnum):
    """Type of pending action."""

    SUBMIT = "submit"
    FILL = "fill"
    CANCEL = "cancel"


@dataclass
class PendingAction:
    """Action waiting to be processed at future time.

    Attributes:
        action_type: Type of action (submit/fill/cancel)
        order_id: Order ID this action applies to
        scheduled_time: Time when action should be processed
        data: Action-specific data (e.g., fill price, execution details)
    """

    action_type: ActionType
    order_id: str
    scheduled_time: datetime
    data: dict[str, Any]


class PendingActionQueue:
    """Queue for time-based action processing.

    Maintains actions in sorted order by scheduled_time for efficient
    processing of due actions.
    """

    def __init__(self):
        """Initialize empty action queue."""
        self.actions: list[PendingAction] = []

    def add_action(self, action: PendingAction) -> None:
        """Add action to queue, maintaining sorted order.

        Args:
            action: Pending action to add
        """
        # Insert in sorted order by scheduled_time
        # Binary search for insertion point
        left, right = 0, len(self.actions)
        while left < right:
            mid = (left + right) // 2
            if self.actions[mid].scheduled_time <= action.scheduled_time:
                left = mid + 1
            else:
                right = mid

        self.actions.insert(left, action)

    def get_due_actions(self, current_time: datetime) -> list[PendingAction]:
        """Get and remove all actions due by current time.

        Args:
            current_time: Current simulation time

        Returns:
            List of actions with scheduled_time <= current_time
        """
        due_actions: list[PendingAction] = []

        # Actions are sorted, so we can stop at first future action
        while self.actions and self.actions[0].scheduled_time <= current_time:
            due_actions.append(self.actions.pop(0))

        return due_actions

    def cancel_order_actions(self, order_id: str) -> int:
        """Remove all pending actions for an order.

        Args:
            order_id: Order ID to cancel actions for

        Returns:
            Number of actions cancelled
        """
        original_count = len(self.actions)
        self.actions = [action for action in self.actions if action.order_id != order_id]
        return original_count - len(self.actions)

    def get_pending_count(self) -> int:
        """Get number of pending actions.

        Returns:
            Number of actions in queue
        """
        return len(self.actions)

    def get_pending_for_order(self, order_id: str) -> list[PendingAction]:
        """Get all pending actions for an order without removing them.

        Args:
            order_id: Order ID to query

        Returns:
            List of pending actions for this order
        """
        return [action for action in self.actions if action.order_id == order_id]

    def clear(self) -> None:
        """Remove all pending actions."""
        self.actions.clear()
