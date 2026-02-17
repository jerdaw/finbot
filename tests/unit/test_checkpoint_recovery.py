"""Tests for checkpoint and recovery functionality."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from finbot.core.contracts.checkpoint import CHECKPOINT_VERSION, ExecutionCheckpoint
from finbot.core.contracts.latency import LATENCY_FAST, LATENCY_INSTANT, LATENCY_NORMAL, LATENCY_SLOW
from finbot.core.contracts.models import OrderSide, OrderType
from finbot.core.contracts.orders import Order, OrderStatus
from finbot.core.contracts.risk import DrawdownLimitRule, ExposureLimitRule, PositionLimitRule, RiskConfig
from finbot.services.execution.checkpoint_manager import CheckpointManager
from finbot.services.execution.checkpoint_serialization import deserialize_checkpoint, serialize_checkpoint
from finbot.services.execution.execution_simulator import ExecutionSimulator


class TestCheckpointCreation:
    """Test checkpoint creation."""

    def test_create_checkpoint_basic(self, tmp_path: Path):
        """Create checkpoint from basic simulator."""
        manager = CheckpointManager(tmp_path)
        simulator = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            simulator_id="test-sim",
        )

        checkpoint = manager.create_checkpoint(simulator)

        assert checkpoint.version == CHECKPOINT_VERSION
        assert checkpoint.simulator_id == "test-sim"
        assert checkpoint.cash == Decimal("100000")
        assert checkpoint.initial_cash == Decimal("100000")
        assert checkpoint.positions == {}
        assert checkpoint.pending_orders == []
        assert checkpoint.completed_orders == []

    def test_checkpoint_includes_all_state(self, tmp_path: Path):
        """Checkpoint contains all required state."""
        manager = CheckpointManager(tmp_path)
        simulator = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            slippage_bps=Decimal("10"),
            commission_per_share=Decimal("0.01"),
            latency_config=LATENCY_FAST,
            simulator_id="test-sim-2",
        )

        # Add some state
        simulator.cash = Decimal("95000")
        simulator.positions = {"AAPL": Decimal("100"), "SPY": Decimal("50")}

        # Create and submit an order
        order = Order(
            order_id="ord-001",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("10"),
            created_at=datetime.now(),
            status=OrderStatus.NEW,
        )
        simulator.pending_orders[order.order_id] = order

        checkpoint = manager.create_checkpoint(simulator)

        assert checkpoint.cash == Decimal("95000")
        assert checkpoint.positions == {"AAPL": Decimal("100"), "SPY": Decimal("50")}
        assert len(checkpoint.pending_orders) == 1
        assert checkpoint.pending_orders[0].order_id == "ord-001"
        assert checkpoint.slippage_bps == Decimal("10")
        assert checkpoint.commission_per_share == Decimal("0.01")
        assert checkpoint.latency_config_name == "FAST"

    def test_checkpoint_with_risk_state(self, tmp_path: Path):
        """Checkpoint includes risk state."""
        manager = CheckpointManager(tmp_path)
        risk_config = RiskConfig(
            position_limit=PositionLimitRule(max_shares=Decimal("1000")),
            drawdown_limit=DrawdownLimitRule(max_daily_drawdown_pct=Decimal("5")),
        )
        simulator = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            risk_config=risk_config,
            simulator_id="test-sim-3",
        )

        # Update risk state
        assert simulator.risk_checker is not None
        simulator.risk_checker.peak_value = Decimal("110000")
        simulator.risk_checker.daily_start_value = Decimal("105000")
        simulator.risk_checker.trading_enabled = False

        checkpoint = manager.create_checkpoint(simulator)

        assert checkpoint.peak_value == Decimal("110000")
        assert checkpoint.daily_start_value == Decimal("105000")
        assert checkpoint.trading_enabled is False
        assert checkpoint.risk_config_data is not None


class TestCheckpointSerialization:
    """Test checkpoint serialization."""

    def test_serialize_deserialize_roundtrip(self):
        """Checkpoint survives serialize/deserialize."""
        original = ExecutionCheckpoint(
            version=CHECKPOINT_VERSION,
            simulator_id="test-123",
            checkpoint_timestamp=datetime(2024, 1, 15, 10, 30, 0),
            cash=Decimal("95000.50"),
            initial_cash=Decimal("100000"),
            positions={"AAPL": Decimal("100"), "SPY": Decimal("50.5")},
            pending_orders=[],
            completed_orders=[],
            slippage_bps=Decimal("5.5"),
            commission_per_share=Decimal("0.01"),
            latency_config_name="NORMAL",
        )

        # Serialize and deserialize
        data = serialize_checkpoint(original)
        restored = deserialize_checkpoint(data)

        assert restored.version == original.version
        assert restored.simulator_id == original.simulator_id
        assert restored.checkpoint_timestamp == original.checkpoint_timestamp
        assert restored.cash == original.cash
        assert restored.initial_cash == original.initial_cash
        assert restored.positions == original.positions
        assert restored.slippage_bps == original.slippage_bps
        assert restored.commission_per_share == original.commission_per_share
        assert restored.latency_config_name == original.latency_config_name

    def test_decimal_precision_preserved(self):
        """Decimal values maintain precision."""
        checkpoint = ExecutionCheckpoint(
            version=CHECKPOINT_VERSION,
            simulator_id="test-123",
            checkpoint_timestamp=datetime.now(),
            cash=Decimal("123456.789012"),
            initial_cash=Decimal("100000.000001"),
            positions={"AAPL": Decimal("100.123456")},
            pending_orders=[],
            completed_orders=[],
        )

        data = serialize_checkpoint(checkpoint)
        restored = deserialize_checkpoint(data)

        assert restored.cash == Decimal("123456.789012")
        assert restored.initial_cash == Decimal("100000.000001")
        assert restored.positions["AAPL"] == Decimal("100.123456")

    def test_datetime_preserved(self):
        """Datetime values preserved correctly."""
        timestamp = datetime(2024, 1, 15, 10, 30, 45, 123456)
        checkpoint = ExecutionCheckpoint(
            version=CHECKPOINT_VERSION,
            simulator_id="test-123",
            checkpoint_timestamp=timestamp,
            cash=Decimal("100000"),
            initial_cash=Decimal("100000"),
            positions={},
            pending_orders=[],
            completed_orders=[],
        )

        data = serialize_checkpoint(checkpoint)
        restored = deserialize_checkpoint(data)

        assert restored.checkpoint_timestamp == timestamp


class TestCheckpointPersistence:
    """Test checkpoint save/load."""

    def test_save_and_load_checkpoint(self, tmp_path: Path):
        """Save and load checkpoint from disk."""
        manager = CheckpointManager(tmp_path)
        simulator = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            simulator_id="test-save",
        )

        # Create and save checkpoint
        checkpoint = manager.create_checkpoint(simulator)
        saved_path = manager.save_checkpoint(checkpoint)

        # Verify file was created
        assert saved_path.exists()
        assert saved_path.name.endswith(".json")

        # Verify latest.json was created
        latest_path = tmp_path / "test-save" / "latest.json"
        assert latest_path.exists()

        # Load checkpoint
        loaded = manager.load_checkpoint("test-save")

        assert loaded.simulator_id == checkpoint.simulator_id
        assert loaded.cash == checkpoint.cash
        assert loaded.initial_cash == checkpoint.initial_cash

    def test_list_checkpoints(self, tmp_path: Path):
        """List available checkpoints."""
        manager = CheckpointManager(tmp_path)
        simulator = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            simulator_id="test-list",
        )

        # Create multiple checkpoints
        for _ in range(3):
            checkpoint = manager.create_checkpoint(simulator)
            manager.save_checkpoint(checkpoint)

        # List checkpoints
        checkpoints = manager.list_checkpoints("test-list")

        assert len(checkpoints) == 3
        # Should be sorted newest first
        assert checkpoints[0][0] > checkpoints[1][0]
        assert checkpoints[1][0] > checkpoints[2][0]

    def test_load_nonexistent_checkpoint(self, tmp_path: Path):
        """Loading nonexistent checkpoint raises error."""
        manager = CheckpointManager(tmp_path)

        with pytest.raises(FileNotFoundError):
            manager.load_checkpoint("nonexistent")


class TestStateRestoration:
    """Test state restoration."""

    def test_restore_cash_and_positions(self, tmp_path: Path):
        """Cash and positions restored correctly."""
        manager = CheckpointManager(tmp_path)

        # Create simulator with state
        original = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            simulator_id="test-restore-1",
        )
        original.cash = Decimal("85000")
        original.positions = {"AAPL": Decimal("100"), "SPY": Decimal("200")}

        # Save checkpoint
        checkpoint = manager.create_checkpoint(original)
        manager.save_checkpoint(checkpoint)

        # Restore simulator
        restored = manager.restore_simulator(checkpoint)

        assert restored.cash == Decimal("85000")
        assert restored.positions == {"AAPL": Decimal("100"), "SPY": Decimal("200")}
        assert restored.initial_cash == Decimal("100000")

    def test_restore_pending_orders(self, tmp_path: Path):
        """Pending orders restored correctly."""
        manager = CheckpointManager(tmp_path)

        # Create simulator with pending order
        original = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            simulator_id="test-restore-2",
        )
        order = Order(
            order_id="ord-001",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("50"),
            limit_price=Decimal("150"),
            created_at=datetime.now(),
            status=OrderStatus.SUBMITTED,
        )
        original.pending_orders[order.order_id] = order

        # Save and restore
        checkpoint = manager.create_checkpoint(original)
        restored = manager.restore_simulator(checkpoint)

        assert len(restored.pending_orders) == 1
        assert "ord-001" in restored.pending_orders
        restored_order = restored.pending_orders["ord-001"]
        assert restored_order.symbol == "AAPL"
        assert restored_order.quantity == Decimal("50")
        assert restored_order.limit_price == Decimal("150")

    def test_restore_completed_orders(self, tmp_path: Path):
        """Completed orders history preserved."""
        manager = CheckpointManager(tmp_path)

        # Create simulator with completed order
        original = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            simulator_id="test-restore-3",
        )
        order = Order(
            order_id="ord-001",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("100"),
            created_at=datetime.now(),
            status=OrderStatus.FILLED,
        )
        original.completed_orders[order.order_id] = order

        # Save and restore
        checkpoint = manager.create_checkpoint(original)
        restored = manager.restore_simulator(checkpoint)

        assert len(restored.completed_orders) == 1
        assert "ord-001" in restored.completed_orders
        assert restored.completed_orders["ord-001"].status == OrderStatus.FILLED

    def test_restore_risk_state(self, tmp_path: Path):
        """Risk state restored correctly."""
        manager = CheckpointManager(tmp_path)

        # Create simulator with risk controls
        risk_config = RiskConfig(
            drawdown_limit=DrawdownLimitRule(max_daily_drawdown_pct=Decimal("5")),
        )
        original = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            risk_config=risk_config,
            simulator_id="test-restore-4",
        )

        # Update risk state
        assert original.risk_checker is not None
        original.risk_checker.peak_value = Decimal("110000")
        original.risk_checker.daily_start_value = Decimal("105000")

        # Save and restore
        checkpoint = manager.create_checkpoint(original)
        restored = manager.restore_simulator(checkpoint)

        assert restored.risk_checker is not None
        assert restored.risk_checker.peak_value == Decimal("110000")
        assert restored.risk_checker.daily_start_value == Decimal("105000")

    def test_restore_configuration(self, tmp_path: Path):
        """Configuration restored correctly."""
        manager = CheckpointManager(tmp_path)

        # Create simulator with custom config
        original = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            slippage_bps=Decimal("15"),
            commission_per_share=Decimal("0.02"),
            latency_config=LATENCY_SLOW,
            simulator_id="test-restore-5",
        )

        # Save and restore
        checkpoint = manager.create_checkpoint(original)
        restored = manager.restore_simulator(checkpoint)

        assert restored.slippage_bps == Decimal("15")
        assert restored.commission_per_share == Decimal("0.02")
        assert restored.latency_config == LATENCY_SLOW

    def test_restore_all_latency_configs(self, tmp_path: Path):
        """All latency configs restore correctly."""
        manager = CheckpointManager(tmp_path)

        configs = [
            ("INSTANT", LATENCY_INSTANT),
            ("FAST", LATENCY_FAST),
            ("NORMAL", LATENCY_NORMAL),
            ("SLOW", LATENCY_SLOW),
        ]

        for i, (name, config) in enumerate(configs):
            simulator = ExecutionSimulator(
                initial_cash=Decimal("100000"),
                latency_config=config,
                simulator_id=f"test-latency-{i}",
            )

            checkpoint = manager.create_checkpoint(simulator)
            assert checkpoint.latency_config_name == name

            restored = manager.restore_simulator(checkpoint)
            assert restored.latency_config == config


class TestCheckpointVersioning:
    """Test checkpoint version handling."""

    def test_version_mismatch_detected(self, tmp_path: Path):
        """Incompatible versions detected."""
        manager = CheckpointManager(tmp_path)

        # Create checkpoint with wrong version
        checkpoint = ExecutionCheckpoint(
            version="0.9.0",  # Wrong version
            simulator_id="test-version",
            checkpoint_timestamp=datetime.now(),
            cash=Decimal("100000"),
            initial_cash=Decimal("100000"),
            positions={},
            pending_orders=[],
            completed_orders=[],
        )

        # Should raise error on restore
        with pytest.raises(ValueError, match="incompatible"):
            manager.restore_simulator(checkpoint)

    def test_checkpoint_version_in_file(self, tmp_path: Path):
        """Version number saved in checkpoint file."""
        manager = CheckpointManager(tmp_path)
        simulator = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            simulator_id="test-version-2",
        )

        checkpoint = manager.create_checkpoint(simulator)
        saved_path = manager.save_checkpoint(checkpoint)

        # Load raw JSON
        with saved_path.open() as f:
            data = json.load(f)

        assert data["version"] == CHECKPOINT_VERSION


class TestCheckpointIntegration:
    """Integration tests for checkpoint/restore cycles."""

    def test_full_checkpoint_restore_cycle(self, tmp_path: Path):
        """Complete checkpoint and restore cycle."""
        manager = CheckpointManager(tmp_path)

        # Create simulator with complex state
        risk_config = RiskConfig(
            position_limit=PositionLimitRule(max_shares=Decimal("1000")),
            exposure_limit=ExposureLimitRule(
                max_gross_exposure_pct=Decimal("150"),
                max_net_exposure_pct=Decimal("100"),
            ),
        )
        original = ExecutionSimulator(
            initial_cash=Decimal("100000"),
            slippage_bps=Decimal("10"),
            commission_per_share=Decimal("0.01"),
            latency_config=LATENCY_NORMAL,
            risk_config=risk_config,
            simulator_id="test-full-cycle",
        )

        # Add complex state
        original.cash = Decimal("85000")
        original.positions = {"AAPL": Decimal("100"), "SPY": Decimal("200"), "QQQ": Decimal("150")}

        # Pending order
        pending = Order(
            order_id="pend-001",
            symbol="MSFT",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("50"),
            limit_price=Decimal("300"),
            created_at=datetime.now(),
            status=OrderStatus.SUBMITTED,
        )
        original.pending_orders[pending.order_id] = pending

        # Completed order
        completed = Order(
            order_id="comp-001",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("100"),
            created_at=datetime.now(),
            status=OrderStatus.FILLED,
        )
        original.completed_orders[completed.order_id] = completed

        # Save checkpoint
        checkpoint = manager.create_checkpoint(original)
        manager.save_checkpoint(checkpoint)

        # Restore simulator
        restored = manager.restore_simulator(checkpoint)

        # Verify all state
        assert restored.simulator_id == "test-full-cycle"
        assert restored.cash == Decimal("85000")
        assert restored.initial_cash == Decimal("100000")
        assert restored.positions == {"AAPL": Decimal("100"), "SPY": Decimal("200"), "QQQ": Decimal("150")}
        assert len(restored.pending_orders) == 1
        assert len(restored.completed_orders) == 1
        assert restored.slippage_bps == Decimal("10")
        assert restored.commission_per_share == Decimal("0.01")
        assert restored.latency_config == LATENCY_NORMAL
        assert restored.risk_checker is not None
