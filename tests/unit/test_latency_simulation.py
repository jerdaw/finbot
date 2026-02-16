"""Tests for order execution latency simulation."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from finbot.core.contracts.latency import LATENCY_FAST, LATENCY_INSTANT, LATENCY_NORMAL, LATENCY_SLOW, LatencyConfig
from finbot.core.contracts.models import OrderSide, OrderType
from finbot.core.contracts.orders import Order, OrderStatus
from finbot.services.execution.execution_simulator import ExecutionSimulator
from finbot.services.execution.pending_actions import ActionType, PendingAction, PendingActionQueue


class TestLatencyProfiles:
    """Test pre-configured latency profiles."""

    def test_instant_profile(self):
        """INSTANT profile has zero latency."""
        assert LATENCY_INSTANT.submission_latency == timedelta(0)
        assert LATENCY_INSTANT.fill_latency_min == timedelta(0)
        assert LATENCY_INSTANT.fill_latency_max == timedelta(0)
        assert LATENCY_INSTANT.cancel_latency == timedelta(0)

    def test_fast_profile(self):
        """FAST profile has 10/50-100/20ms latencies."""
        assert LATENCY_FAST.submission_latency == timedelta(milliseconds=10)
        assert LATENCY_FAST.fill_latency_min == timedelta(milliseconds=50)
        assert LATENCY_FAST.fill_latency_max == timedelta(milliseconds=100)
        assert LATENCY_FAST.cancel_latency == timedelta(milliseconds=20)

    def test_normal_profile(self):
        """NORMAL profile has 50/100-200/50ms latencies."""
        assert LATENCY_NORMAL.submission_latency == timedelta(milliseconds=50)
        assert LATENCY_NORMAL.fill_latency_min == timedelta(milliseconds=100)
        assert LATENCY_NORMAL.fill_latency_max == timedelta(milliseconds=200)
        assert LATENCY_NORMAL.cancel_latency == timedelta(milliseconds=50)

    def test_slow_profile(self):
        """SLOW profile has 100/500-1000/100ms latencies."""
        assert LATENCY_SLOW.submission_latency == timedelta(milliseconds=100)
        assert LATENCY_SLOW.fill_latency_min == timedelta(milliseconds=500)
        assert LATENCY_SLOW.fill_latency_max == timedelta(milliseconds=1000)
        assert LATENCY_SLOW.cancel_latency == timedelta(milliseconds=100)


class TestPendingActionQueue:
    """Test pending action queue."""

    def test_add_action_maintains_sorted_order(self):
        """Actions are kept in sorted order by scheduled_time."""
        queue = PendingActionQueue()

        base_time = datetime(2024, 1, 15, 10, 0, 0)

        # Add actions out of order
        queue.add_action(
            PendingAction(
                action_type=ActionType.FILL,
                order_id="order-003",
                scheduled_time=base_time + timedelta(seconds=30),
                data={},
            )
        )
        queue.add_action(
            PendingAction(
                action_type=ActionType.SUBMIT,
                order_id="order-001",
                scheduled_time=base_time + timedelta(seconds=10),
                data={},
            )
        )
        queue.add_action(
            PendingAction(
                action_type=ActionType.CANCEL,
                order_id="order-002",
                scheduled_time=base_time + timedelta(seconds=20),
                data={},
            )
        )

        # Verify sorted order
        assert queue.actions[0].order_id == "order-001"
        assert queue.actions[1].order_id == "order-002"
        assert queue.actions[2].order_id == "order-003"

    def test_get_due_actions(self):
        """Get and remove actions due by current time."""
        queue = PendingActionQueue()

        base_time = datetime(2024, 1, 15, 10, 0, 0)

        # Add 3 actions
        for i in range(3):
            queue.add_action(
                PendingAction(
                    action_type=ActionType.SUBMIT,
                    order_id=f"order-{i:03d}",
                    scheduled_time=base_time + timedelta(seconds=i * 10),
                    data={},
                )
            )

        # Get actions due at t+15 (should get first 2)
        due_actions = queue.get_due_actions(base_time + timedelta(seconds=15))

        assert len(due_actions) == 2
        assert due_actions[0].order_id == "order-000"
        assert due_actions[1].order_id == "order-001"

        # Queue should have 1 remaining
        assert queue.get_pending_count() == 1

    def test_cancel_order_actions(self):
        """Remove all pending actions for an order."""
        queue = PendingActionQueue()

        base_time = datetime(2024, 1, 15, 10, 0, 0)

        # Add actions for different orders
        queue.add_action(
            PendingAction(
                action_type=ActionType.SUBMIT,
                order_id="order-001",
                scheduled_time=base_time,
                data={},
            )
        )
        queue.add_action(
            PendingAction(
                action_type=ActionType.FILL,
                order_id="order-001",
                scheduled_time=base_time + timedelta(seconds=10),
                data={},
            )
        )
        queue.add_action(
            PendingAction(
                action_type=ActionType.SUBMIT,
                order_id="order-002",
                scheduled_time=base_time + timedelta(seconds=5),
                data={},
            )
        )

        # Cancel order-001 actions
        cancelled = queue.cancel_order_actions("order-001")

        assert cancelled == 2
        assert queue.get_pending_count() == 1
        assert queue.actions[0].order_id == "order-002"


class TestSubmissionLatency:
    """Test order submission latency."""

    def test_order_submitted_immediately_with_instant_latency(self):
        """Order is SUBMITTED immediately with LATENCY_INSTANT."""
        simulator = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            latency_config=LATENCY_INSTANT,
        )

        order = Order(
            order_id=f"order-{uuid.uuid4().hex[:8]}",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("10"),
            created_at=datetime.now(),
        )

        result = simulator.submit_order(order)

        assert result.status == OrderStatus.SUBMITTED
        assert result.submitted_at is not None

    def test_order_not_submitted_immediately_with_latency(self):
        """Order status is NEW immediately after submit with latency."""
        simulator = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            latency_config=LATENCY_NORMAL,
        )

        base_time = datetime(2024, 1, 15, 10, 0, 0)

        order = Order(
            order_id=f"order-{uuid.uuid4().hex[:8]}",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("10"),
            created_at=base_time,
        )

        result = simulator.submit_order(order, timestamp=base_time)

        assert result.status == OrderStatus.NEW
        assert result.submitted_at is None

    def test_order_submitted_after_latency(self):
        """Order becomes SUBMITTED after latency period."""
        simulator = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            latency_config=LATENCY_NORMAL,  # 50ms submission latency
        )

        base_time = datetime(2024, 1, 15, 10, 0, 0)

        order = Order(
            order_id=f"order-{uuid.uuid4().hex[:8]}",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("10"),
            created_at=base_time,
        )

        simulator.submit_order(order, timestamp=base_time)

        # Process market data after latency period
        simulator.process_market_data(
            "SPY",
            Decimal("450.00"),
            timestamp=base_time + timedelta(milliseconds=60),
        )

        # Order should now be submitted
        assert order.status == OrderStatus.SUBMITTED
        assert order.submitted_at == base_time + timedelta(milliseconds=50)


class TestFillLatency:
    """Test order fill latency."""

    def test_order_filled_immediately_with_instant_latency(self):
        """Order fills immediately when price matches with LATENCY_INSTANT."""
        simulator = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            latency_config=LATENCY_INSTANT,
        )

        base_time = datetime(2024, 1, 15, 10, 0, 0)

        order = Order(
            order_id=f"order-{uuid.uuid4().hex[:8]}",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("10"),
            created_at=base_time,
        )

        simulator.submit_order(order, timestamp=base_time)

        # Process market data - should fill immediately
        executions = simulator.process_market_data(
            "SPY",
            Decimal("450.00"),
            timestamp=base_time + timedelta(milliseconds=1),
        )

        assert len(executions) == 1
        assert order.status == OrderStatus.FILLED

    def test_order_not_filled_immediately_with_latency(self):
        """Order doesn't fill immediately when price matches with latency."""
        simulator = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            latency_config=LATENCY_NORMAL,  # 100-200ms fill latency
        )

        base_time = datetime(2024, 1, 15, 10, 0, 0)

        order = Order(
            order_id=f"order-{uuid.uuid4().hex[:8]}",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("10"),
            created_at=base_time,
        )

        # Submit with instant submission for this test
        simulator.latency_config = LatencyConfig(
            submission_latency=timedelta(0),
            fill_latency_min=timedelta(milliseconds=100),
            fill_latency_max=timedelta(milliseconds=200),
            cancel_latency=timedelta(0),
        )

        simulator.submit_order(order, timestamp=base_time)

        # Process market data immediately - should not fill yet
        executions = simulator.process_market_data(
            "SPY",
            Decimal("450.00"),
            timestamp=base_time + timedelta(milliseconds=1),
        )

        assert len(executions) == 0
        assert order.status == OrderStatus.SUBMITTED

    def test_order_filled_after_latency(self):
        """Order fills after latency period."""
        simulator = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            latency_config=LatencyConfig(
                submission_latency=timedelta(0),
                fill_latency_min=timedelta(milliseconds=100),
                fill_latency_max=timedelta(milliseconds=100),  # Fixed latency for determinism
                cancel_latency=timedelta(0),
            ),
        )

        base_time = datetime(2024, 1, 15, 10, 0, 0)

        order = Order(
            order_id=f"order-{uuid.uuid4().hex[:8]}",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("10"),
            created_at=base_time,
        )

        simulator.submit_order(order, timestamp=base_time)

        # Trigger fill at t=0
        simulator.process_market_data("SPY", Decimal("450.00"), timestamp=base_time)

        # No fill yet
        assert order.status == OrderStatus.SUBMITTED

        # Process market data after latency period
        simulator.process_market_data(
            "SPY",
            Decimal("451.00"),  # Different price, but shouldn't matter
            timestamp=base_time + timedelta(milliseconds=110),
        )

        # Order should now be filled (at original price)
        assert order.status == OrderStatus.FILLED
        assert len(order.executions) == 1


class TestCancellationLatency:
    """Test order cancellation latency."""

    def test_order_cancelled_immediately_with_instant_latency(self):
        """Order is CANCELLED immediately with LATENCY_INSTANT."""
        simulator = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            latency_config=LATENCY_INSTANT,
        )

        base_time = datetime(2024, 1, 15, 10, 0, 0)

        order = Order(
            order_id="order-001",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("10"),
            limit_price=Decimal("450.00"),
            created_at=base_time,
        )

        simulator.submit_order(order, timestamp=base_time)
        cancelled = simulator.cancel_order("order-001", timestamp=base_time)

        assert cancelled.status == OrderStatus.CANCELLED
        assert cancelled.cancelled_at == base_time

    def test_order_not_cancelled_immediately_with_latency(self):
        """Order remains active immediately after cancel request with latency."""
        simulator = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            latency_config=LATENCY_NORMAL,  # 50ms cancel latency
        )

        base_time = datetime(2024, 1, 15, 10, 0, 0)

        order = Order(
            order_id="order-001",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("10"),
            limit_price=Decimal("450.00"),
            created_at=base_time,
        )

        simulator.submit_order(order, timestamp=base_time)

        # Advance time past submission latency
        simulator.process_market_data("SPY", Decimal("451.00"), timestamp=base_time + timedelta(milliseconds=60))

        # Cancel at t=60
        cancelled = simulator.cancel_order("order-001", timestamp=base_time + timedelta(milliseconds=60))

        # Order should still be in pending_orders, not yet cancelled
        assert cancelled.order_id == "order-001"
        assert order.status == OrderStatus.SUBMITTED  # Still active

    def test_order_cancelled_after_latency(self):
        """Order becomes CANCELLED after latency period."""
        simulator = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            latency_config=LatencyConfig(
                submission_latency=timedelta(0),
                fill_latency_min=timedelta(0),
                fill_latency_max=timedelta(0),
                cancel_latency=timedelta(milliseconds=50),
            ),
        )

        base_time = datetime(2024, 1, 15, 10, 0, 0)

        order = Order(
            order_id="order-001",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("10"),
            limit_price=Decimal("450.00"),
            created_at=base_time,
        )

        simulator.submit_order(order, timestamp=base_time)
        simulator.cancel_order("order-001", timestamp=base_time)

        # Process market data after latency period
        simulator.process_market_data(
            "SPY",
            Decimal("449.00"),  # Price would fill limit order, but it's being cancelled
            timestamp=base_time + timedelta(milliseconds=60),
        )

        # Order should now be cancelled
        assert order.status == OrderStatus.CANCELLED
        assert order.cancelled_at == base_time + timedelta(milliseconds=50)

    def test_pending_fills_cancelled_when_order_cancelled(self):
        """Pending fill actions are cancelled when order is cancelled."""
        simulator = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            latency_config=LatencyConfig(
                submission_latency=timedelta(0),
                fill_latency_min=timedelta(milliseconds=100),
                fill_latency_max=timedelta(milliseconds=100),
                cancel_latency=timedelta(milliseconds=50),
            ),
        )

        base_time = datetime(2024, 1, 15, 10, 0, 0)

        order = Order(
            order_id="order-001",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("10"),
            created_at=base_time,
        )

        # Submit order
        simulator.submit_order(order, timestamp=base_time)

        # Trigger fill (will be delayed by 100ms)
        simulator.process_market_data("SPY", Decimal("450.00"), timestamp=base_time)

        # Verify fill action is pending
        assert simulator.action_queue.get_pending_count() > 0

        # Cancel order before fill processes
        simulator.cancel_order("order-001", timestamp=base_time + timedelta(milliseconds=10))

        # Process past both fill and cancel times
        simulator.process_market_data(
            "SPY",
            Decimal("451.00"),
            timestamp=base_time + timedelta(milliseconds=200),
        )

        # Order should be cancelled, not filled
        assert order.status == OrderStatus.CANCELLED
        assert len(order.executions) == 0
