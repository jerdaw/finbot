"""Tests for order lifecycle and execution."""

from __future__ import annotations

import tempfile
import uuid
from datetime import datetime
from decimal import Decimal

import pytest

from finbot.core.contracts.models import OrderSide, OrderType
from finbot.core.contracts.orders import Order, OrderExecution, OrderStatus, RejectionReason
from finbot.services.execution.execution_simulator import ExecutionSimulator
from finbot.services.execution.order_registry import OrderRegistry
from finbot.services.execution.order_validator import OrderValidator


class TestOrderLifecycle:
    """Test order state transitions and tracking."""

    def test_order_creation(self):
        """Test creating a new order."""
        order = Order(
            order_id="order-001",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("100"),
            created_at=datetime.now(),
        )

        assert order.status == OrderStatus.NEW
        assert order.filled_quantity == Decimal("0")
        assert order.remaining_quantity() == Decimal("100")
        assert not order.is_complete()

    def test_order_add_execution(self):
        """Test adding executions to order."""
        order = Order(
            order_id="order-001",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("100"),
            created_at=datetime.now(),
            status=OrderStatus.SUBMITTED,
        )

        execution = OrderExecution(
            execution_id="exec-001",
            order_id="order-001",
            timestamp=datetime.now(),
            quantity=Decimal("50"),
            price=Decimal("450.00"),
            commission=Decimal("1.00"),
            is_partial=True,
        )

        order.add_execution(execution)

        assert order.filled_quantity == Decimal("50")
        assert order.remaining_quantity() == Decimal("50")
        assert order.status == OrderStatus.PARTIALLY_FILLED
        assert order.avg_fill_price == Decimal("450.00")
        assert order.total_commission == Decimal("1.00")

    def test_order_full_fill(self):
        """Test order becoming fully filled."""
        order = Order(
            order_id="order-001",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("100"),
            created_at=datetime.now(),
            status=OrderStatus.SUBMITTED,
        )

        # Add two executions
        exec1 = OrderExecution(
            execution_id="exec-001",
            order_id="order-001",
            timestamp=datetime.now(),
            quantity=Decimal("60"),
            price=Decimal("450.00"),
            commission=Decimal("1.00"),
            is_partial=True,
        )
        exec2 = OrderExecution(
            execution_id="exec-002",
            order_id="order-001",
            timestamp=datetime.now(),
            quantity=Decimal("40"),
            price=Decimal("451.00"),
            commission=Decimal("1.00"),
            is_partial=False,
        )

        order.add_execution(exec1)
        order.add_execution(exec2)

        assert order.filled_quantity == Decimal("100")
        assert order.remaining_quantity() == Decimal("0")
        assert order.status == OrderStatus.FILLED
        assert order.is_complete()

        # Average price calculation: (60*450 + 40*451) / 100 = 450.4
        assert order.avg_fill_price == Decimal("450.4")
        assert order.total_commission == Decimal("2.00")


class TestOrderValidator:
    """Test order validation logic."""

    def test_validate_positive_quantity(self):
        """Test quantity must be positive."""
        validator = OrderValidator()

        order = Order(
            order_id="order-001",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("-10"),
            created_at=datetime.now(),
        )

        result = validator.validate(order, Decimal("10000"), {})

        assert not result.is_valid
        assert result.rejection_reason == RejectionReason.INVALID_QUANTITY

    def test_validate_min_quantity(self):
        """Test minimum quantity requirement."""
        validator = OrderValidator(min_order_quantity=Decimal("1"))

        order = Order(
            order_id="order-001",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.5"),
            created_at=datetime.now(),
        )

        result = validator.validate(order, Decimal("10000"), {})

        assert not result.is_valid
        assert result.rejection_reason == RejectionReason.INVALID_QUANTITY

    def test_validate_max_quantity(self):
        """Test maximum quantity limit."""
        validator = OrderValidator(max_order_quantity=Decimal("100"))

        order = Order(
            order_id="order-001",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("200"),
            created_at=datetime.now(),
        )

        result = validator.validate(order, Decimal("10000"), {})

        assert not result.is_valid
        assert result.rejection_reason == RejectionReason.INVALID_QUANTITY

    def test_validate_insufficient_funds_limit_order(self):
        """Test insufficient funds rejection for limit order."""
        validator = OrderValidator()

        order = Order(
            order_id="order-001",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("450.00"),
            created_at=datetime.now(),
        )

        # Need 45,000 but only have 10,000
        result = validator.validate(order, Decimal("10000"), {})

        assert not result.is_valid
        assert result.rejection_reason == RejectionReason.INSUFFICIENT_FUNDS

    def test_validate_insufficient_position_for_sell(self):
        """Test selling more than owned."""
        validator = OrderValidator()

        order = Order(
            order_id="order-001",
            symbol="SPY",
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=Decimal("100"),
            created_at=datetime.now(),
        )

        # Only have 50 shares
        positions = {"SPY": Decimal("50")}
        result = validator.validate(order, Decimal("10000"), positions)

        assert not result.is_valid
        assert result.rejection_reason == RejectionReason.INVALID_QUANTITY

    def test_validate_valid_order(self):
        """Test valid order passes validation."""
        validator = OrderValidator()

        order = Order(
            order_id="order-001",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("10"),
            created_at=datetime.now(),
        )

        current_prices = {"SPY": Decimal("450.00")}
        result = validator.validate(order, Decimal("10000"), {}, current_prices)

        assert result.is_valid
        assert result.rejection_reason is None


class TestExecutionSimulator:
    """Test execution simulation."""

    def test_submit_valid_order(self):
        """Test submitting a valid order."""
        simulator = ExecutionSimulator(initial_cash=Decimal("100000"))

        order = Order(
            order_id="order-001",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("10"),
            created_at=datetime.now(),
        )

        result = simulator.submit_order(order)

        assert result.status == OrderStatus.SUBMITTED
        assert result.submitted_at is not None
        assert order.order_id in simulator.pending_orders

    def test_submit_invalid_order(self):
        """Test submitting an invalid order (negative quantity)."""
        simulator = ExecutionSimulator(initial_cash=Decimal("100000"))

        order = Order(
            order_id="order-001",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("-10"),
            created_at=datetime.now(),
        )

        result = simulator.submit_order(order)

        assert result.status == OrderStatus.REJECTED
        assert result.rejection_reason == RejectionReason.INVALID_QUANTITY
        assert order.order_id in simulator.completed_orders

    def test_execute_market_buy_order(self):
        """Test executing a market buy order."""
        simulator = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            slippage_bps=Decimal("5"),
            commission_per_share=Decimal("0.01"),
        )

        order = Order(
            order_id=f"order-{uuid.uuid4().hex[:8]}",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("10"),
            created_at=datetime.now(),
        )

        simulator.submit_order(order)

        # Process market data
        executions = simulator.process_market_data("SPY", Decimal("450.00"))

        assert len(executions) == 1
        assert executions[0].quantity == Decimal("10")
        # Price with 5 bps slippage: 450 * 1.0005 = 450.225
        assert executions[0].price == Decimal("450") * Decimal("1.0005")
        assert executions[0].commission == Decimal("0.1")

        # Check order status
        assert order.status == OrderStatus.FILLED
        assert order.filled_quantity == Decimal("10")

        # Check positions and cash
        assert simulator.positions["SPY"] == Decimal("10")
        # Cash: 100000 - (10 * 450.225) - 0.1 = 95497.65
        expected_cash = Decimal("100000") - (Decimal("10") * Decimal("450.225")) - Decimal("0.1")
        assert simulator.cash == expected_cash

    def test_execute_market_sell_order(self):
        """Test executing a market sell order."""
        simulator = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            slippage_bps=Decimal("5"),
            commission_per_share=Decimal("0.01"),
        )

        # Set up position
        simulator.positions["SPY"] = Decimal("100")

        order = Order(
            order_id=f"order-{uuid.uuid4().hex[:8]}",
            symbol="SPY",
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=Decimal("50"),
            created_at=datetime.now(),
        )

        simulator.submit_order(order)

        # Process market data
        executions = simulator.process_market_data("SPY", Decimal("450.00"))

        assert len(executions) == 1
        assert executions[0].quantity == Decimal("50")
        # Price with 5 bps slippage: 450 * 0.9995 = 449.775
        assert executions[0].price == Decimal("450") * Decimal("0.9995")

        # Check positions and cash
        assert simulator.positions["SPY"] == Decimal("50")
        # Cash: 100000 + (50 * 449.775) - 0.5 = 122488.25
        expected_cash = Decimal("100000") + (Decimal("50") * Decimal("449.775")) - Decimal("0.5")
        assert simulator.cash == expected_cash

    def test_execute_limit_buy_order(self):
        """Test limit buy order execution."""
        simulator = ExecutionSimulator(initial_cash=Decimal("100000"))

        order = Order(
            order_id=f"order-{uuid.uuid4().hex[:8]}",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("10"),
            limit_price=Decimal("450.00"),
            created_at=datetime.now(),
        )

        simulator.submit_order(order)

        # Price above limit - should not fill
        executions = simulator.process_market_data("SPY", Decimal("451.00"))
        assert len(executions) == 0
        assert order.status == OrderStatus.SUBMITTED

        # Price at limit - should fill
        executions = simulator.process_market_data("SPY", Decimal("450.00"))
        assert len(executions) == 1
        assert order.status == OrderStatus.FILLED

    def test_cancel_order(self):
        """Test cancelling an order."""
        simulator = ExecutionSimulator(initial_cash=Decimal("100000"))

        order = Order(
            order_id="order-001",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("10"),
            limit_price=Decimal("450.00"),
            created_at=datetime.now(),
        )

        simulator.submit_order(order)
        assert order.order_id in simulator.pending_orders

        cancelled = simulator.cancel_order("order-001")

        assert cancelled is not None
        assert cancelled.status == OrderStatus.CANCELLED
        assert cancelled.cancelled_at is not None
        assert order.order_id not in simulator.pending_orders
        assert order.order_id in simulator.completed_orders


class TestOrderRegistry:
    """Test order persistence."""

    def test_save_and_load_order(self):
        """Test saving and loading an order."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = OrderRegistry(tmpdir)

            order = Order(
                order_id="order-001",
                symbol="SPY",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=Decimal("100"),
                created_at=datetime(2024, 1, 15, 10, 30),
                status=OrderStatus.FILLED,
                filled_quantity=Decimal("100"),
                avg_fill_price=Decimal("450.00"),
                total_commission=Decimal("1.00"),
            )

            # Add execution
            execution = OrderExecution(
                execution_id="exec-001",
                order_id="order-001",
                timestamp=datetime(2024, 1, 15, 10, 31),
                quantity=Decimal("100"),
                price=Decimal("450.00"),
                commission=Decimal("1.00"),
                is_partial=False,
            )
            order.executions.append(execution)

            # Save
            registry.save_order(order)

            # Load
            loaded = registry.load_order("order-001")

            assert loaded.order_id == order.order_id
            assert loaded.symbol == order.symbol
            assert loaded.quantity == order.quantity
            assert loaded.status == order.status
            assert len(loaded.executions) == 1
            assert loaded.executions[0].execution_id == "exec-001"

    def test_list_orders_filter_by_symbol(self):
        """Test listing orders filtered by symbol."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = OrderRegistry(tmpdir)

            # Save multiple orders
            for i, symbol in enumerate(["SPY", "QQQ", "SPY"]):
                order = Order(
                    order_id=f"order-{i:03d}",
                    symbol=symbol,
                    side=OrderSide.BUY,
                    order_type=OrderType.MARKET,
                    quantity=Decimal("100"),
                    created_at=datetime(2024, 1, 15 + i, 10, 30),
                )
                registry.save_order(order)

            # List SPY orders only
            spy_orders = registry.list_orders(symbol="SPY")

            assert len(spy_orders) == 2
            assert all(o.symbol == "SPY" for o in spy_orders)

    def test_list_orders_filter_by_status(self):
        """Test listing orders filtered by status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = OrderRegistry(tmpdir)

            # Save orders with different statuses
            for i, status in enumerate([OrderStatus.NEW, OrderStatus.FILLED, OrderStatus.REJECTED]):
                order = Order(
                    order_id=f"order-{i:03d}",
                    symbol="SPY",
                    side=OrderSide.BUY,
                    order_type=OrderType.MARKET,
                    quantity=Decimal("100"),
                    created_at=datetime(2024, 1, 15, 10, 30 + i),
                    status=status,
                )
                registry.save_order(order)

            # List filled orders only
            filled_orders = registry.list_orders(status=OrderStatus.FILLED)

            assert len(filled_orders) == 1
            assert filled_orders[0].status == OrderStatus.FILLED

    def test_list_orders_with_limit(self):
        """Test listing orders with limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = OrderRegistry(tmpdir)

            # Save 10 orders
            for i in range(10):
                order = Order(
                    order_id=f"order-{i:03d}",
                    symbol="SPY",
                    side=OrderSide.BUY,
                    order_type=OrderType.MARKET,
                    quantity=Decimal("100"),
                    created_at=datetime(2024, 1, 15, 10, 30 + i),
                )
                registry.save_order(order)

            # List with limit
            orders = registry.list_orders(limit=5)

            assert len(orders) == 5

    def test_delete_order(self):
        """Test deleting an order."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = OrderRegistry(tmpdir)

            order = Order(
                order_id="order-001",
                symbol="SPY",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=Decimal("100"),
                created_at=datetime(2024, 1, 15, 10, 30),
            )

            registry.save_order(order)

            # Delete
            deleted = registry.delete_order("order-001")
            assert deleted is True

            # Verify deletion
            with pytest.raises(FileNotFoundError):
                registry.load_order("order-001")

    def test_get_executions(self):
        """Test retrieving executions for an order."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = OrderRegistry(tmpdir)

            order = Order(
                order_id="order-001",
                symbol="SPY",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=Decimal("100"),
                created_at=datetime(2024, 1, 15, 10, 30),
            )

            # Add executions
            for i in range(3):
                execution = OrderExecution(
                    execution_id=f"exec-{i:03d}",
                    order_id="order-001",
                    timestamp=datetime(2024, 1, 15, 10, 31 + i),
                    quantity=Decimal("33.33"),
                    price=Decimal("450.00"),
                    commission=Decimal("0.33"),
                    is_partial=True,
                )
                order.executions.append(execution)

            registry.save_order(order)

            # Get executions
            executions = registry.get_executions("order-001")

            assert len(executions) == 3
            assert all(e.order_id == "order-001" for e in executions)
