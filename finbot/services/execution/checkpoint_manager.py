"""Checkpoint manager for ExecutionSimulator state persistence."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from finbot.core.contracts.checkpoint import CHECKPOINT_VERSION, ExecutionCheckpoint
from finbot.core.contracts.latency import LATENCY_FAST, LATENCY_INSTANT, LATENCY_NORMAL, LATENCY_SLOW
from finbot.services.execution.checkpoint_serialization import deserialize_checkpoint, serialize_checkpoint
from finbot.services.execution.execution_simulator import ExecutionSimulator


class CheckpointManager:
    """Manages ExecutionSimulator state checkpoints.

    Features:
    - Create checkpoints from simulator state
    - Save checkpoints to disk (JSON format)
    - Load checkpoints from disk
    - Restore ExecutionSimulator from checkpoint
    - List available checkpoints

    Example:
        >>> manager = CheckpointManager(Path("checkpoints"))
        >>> checkpoint = manager.create_checkpoint(simulator, "sim-001")
        >>> manager.save_checkpoint(checkpoint)
        >>> restored_sim = manager.restore_simulator(checkpoint)
    """

    def __init__(self, checkpoint_dir: Path | str):
        """Initialize checkpoint manager.

        Args:
            checkpoint_dir: Directory for storing checkpoints
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def create_checkpoint(
        self,
        simulator: ExecutionSimulator,
        simulator_id: str | None = None,
    ) -> ExecutionCheckpoint:
        """Create checkpoint from simulator state.

        Args:
            simulator: ExecutionSimulator to checkpoint
            simulator_id: Simulator ID (uses simulator.simulator_id if not provided)

        Returns:
            ExecutionCheckpoint containing current state
        """
        if simulator_id is None:
            simulator_id = getattr(simulator, "simulator_id", "default")

        # Determine latency config name
        latency_config_name = "INSTANT"
        if simulator.latency_config == LATENCY_FAST:
            latency_config_name = "FAST"
        elif simulator.latency_config == LATENCY_NORMAL:
            latency_config_name = "NORMAL"
        elif simulator.latency_config == LATENCY_SLOW:
            latency_config_name = "SLOW"

        # Extract risk state if risk checker exists
        peak_value = None
        daily_start_value = None
        trading_enabled = True
        risk_config_data = None

        if simulator.risk_checker:
            peak_value = simulator.risk_checker.peak_value
            daily_start_value = simulator.risk_checker.daily_start_value
            trading_enabled = simulator.risk_checker.trading_enabled

            # Serialize risk config
            if simulator.risk_checker.risk_config:
                risk_config_data = self._serialize_risk_config(simulator.risk_checker.risk_config)

        return ExecutionCheckpoint(
            version=CHECKPOINT_VERSION,
            simulator_id=simulator_id,
            checkpoint_timestamp=datetime.now(),
            cash=simulator.cash,
            initial_cash=simulator.initial_cash,
            positions=simulator.positions.copy(),
            pending_orders=list(simulator.pending_orders.values()),
            completed_orders=list(simulator.completed_orders.values()),
            peak_value=peak_value,
            daily_start_value=daily_start_value,
            trading_enabled=trading_enabled,
            slippage_bps=simulator.slippage_bps,
            commission_per_share=simulator.commission_per_share,
            latency_config_name=latency_config_name,
            risk_config_data=risk_config_data,
        )

    def save_checkpoint(
        self,
        checkpoint: ExecutionCheckpoint,
    ) -> Path:
        """Save checkpoint to disk.

        Args:
            checkpoint: Checkpoint to save

        Returns:
            Path to saved checkpoint file
        """
        # Create directory for this simulator
        sim_dir = self.checkpoint_dir / checkpoint.simulator_id
        sim_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped filename
        timestamp_str = checkpoint.checkpoint_timestamp.strftime("%Y%m%d_%H%M%S_%f")
        checkpoint_path = sim_dir / f"{timestamp_str}.json"

        # Serialize and save
        checkpoint_data = serialize_checkpoint(checkpoint)
        with checkpoint_path.open("w") as f:
            json.dump(checkpoint_data, f, indent=2)

        # Update latest.json
        latest_path = sim_dir / "latest.json"
        with latest_path.open("w") as f:
            json.dump(checkpoint_data, f, indent=2)

        return checkpoint_path

    def load_checkpoint(
        self,
        simulator_id: str,
        timestamp: datetime | None = None,
    ) -> ExecutionCheckpoint:
        """Load checkpoint from disk.

        Args:
            simulator_id: Simulator ID
            timestamp: Specific checkpoint timestamp (loads latest if None)

        Returns:
            Loaded checkpoint

        Raises:
            FileNotFoundError: If checkpoint not found
        """
        sim_dir = self.checkpoint_dir / simulator_id

        if not sim_dir.exists():
            msg = f"No checkpoints found for simulator {simulator_id}"
            raise FileNotFoundError(msg)

        # Load specific timestamp or latest
        if timestamp is None:
            checkpoint_path = sim_dir / "latest.json"
        else:
            timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S_%f")
            checkpoint_path = sim_dir / f"{timestamp_str}.json"

        if not checkpoint_path.exists():
            msg = f"Checkpoint not found: {checkpoint_path}"
            raise FileNotFoundError(msg)

        # Load and deserialize
        with checkpoint_path.open() as f:
            checkpoint_data = json.load(f)

        return deserialize_checkpoint(checkpoint_data)

    def restore_simulator(
        self,
        checkpoint: ExecutionCheckpoint,
    ) -> ExecutionSimulator:
        """Restore ExecutionSimulator from checkpoint.

        Args:
            checkpoint: Checkpoint to restore from

        Returns:
            Restored ExecutionSimulator

        Raises:
            ValueError: If checkpoint version incompatible
        """
        # Validate version
        if checkpoint.version != CHECKPOINT_VERSION:
            msg = f"Checkpoint version {checkpoint.version} incompatible with current version {CHECKPOINT_VERSION}"
            raise ValueError(msg)

        # Map latency config name to config
        latency_config = LATENCY_INSTANT
        if checkpoint.latency_config_name == "FAST":
            latency_config = LATENCY_FAST
        elif checkpoint.latency_config_name == "NORMAL":
            latency_config = LATENCY_NORMAL
        elif checkpoint.latency_config_name == "SLOW":
            latency_config = LATENCY_SLOW

        # Deserialize risk config
        risk_config = None
        if checkpoint.risk_config_data:
            risk_config = self._deserialize_risk_config(checkpoint.risk_config_data)

        # Create simulator with config
        simulator = ExecutionSimulator(
            initial_cash=checkpoint.initial_cash,
            slippage_bps=checkpoint.slippage_bps,
            commission_per_share=checkpoint.commission_per_share,
            latency_config=latency_config,
            risk_config=risk_config,
        )

        # Restore state
        simulator.cash = checkpoint.cash
        simulator.positions = checkpoint.positions.copy()
        simulator.pending_orders = {order.order_id: order for order in checkpoint.pending_orders}
        simulator.completed_orders = {order.order_id: order for order in checkpoint.completed_orders}

        # Restore risk state
        if simulator.risk_checker and checkpoint.peak_value is not None:
            simulator.risk_checker.peak_value = checkpoint.peak_value
            simulator.risk_checker.daily_start_value = checkpoint.daily_start_value or checkpoint.cash
            simulator.risk_checker.trading_enabled = checkpoint.trading_enabled

        # Store simulator_id
        simulator.simulator_id = checkpoint.simulator_id

        return simulator

    def list_checkpoints(
        self,
        simulator_id: str,
    ) -> list[tuple[datetime, Path]]:
        """List available checkpoints for simulator.

        Args:
            simulator_id: Simulator ID

        Returns:
            List of (timestamp, path) tuples, sorted by timestamp (newest first)
        """
        sim_dir = self.checkpoint_dir / simulator_id

        if not sim_dir.exists():
            return []

        checkpoints: list[tuple[datetime, Path]] = []

        for checkpoint_file in sim_dir.glob("*.json"):
            if checkpoint_file.name == "latest.json":
                continue

            # Parse timestamp from filename
            timestamp_str = checkpoint_file.stem  # Remove .json
            try:
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S_%f")
                checkpoints.append((timestamp, checkpoint_file))
            except ValueError:
                # Skip files that don't match expected format
                continue

        # Sort by timestamp, newest first
        checkpoints.sort(key=lambda x: x[0], reverse=True)

        return checkpoints

    def _serialize_risk_config(self, risk_config) -> dict:
        """Serialize risk config to dict.

        Args:
            risk_config: RiskConfig to serialize

        Returns:
            Serialized risk config
        """

        data: dict = {
            "trading_enabled": risk_config.trading_enabled,
        }

        if risk_config.position_limit:
            data["position_limit"] = {
                "max_shares": str(risk_config.position_limit.max_shares)
                if risk_config.position_limit.max_shares is not None
                else None,
                "max_value": str(risk_config.position_limit.max_value)
                if risk_config.position_limit.max_value is not None
                else None,
            }

        if risk_config.exposure_limit:
            data["exposure_limit"] = {
                "max_gross_exposure_pct": str(risk_config.exposure_limit.max_gross_exposure_pct),
                "max_net_exposure_pct": str(risk_config.exposure_limit.max_net_exposure_pct),
            }

        if risk_config.drawdown_limit:
            data["drawdown_limit"] = {
                "max_daily_drawdown_pct": str(risk_config.drawdown_limit.max_daily_drawdown_pct)
                if risk_config.drawdown_limit.max_daily_drawdown_pct is not None
                else None,
                "max_total_drawdown_pct": str(risk_config.drawdown_limit.max_total_drawdown_pct)
                if risk_config.drawdown_limit.max_total_drawdown_pct is not None
                else None,
            }

        return data

    def _deserialize_risk_config(self, data: dict):
        """Deserialize risk config from dict.

        Args:
            data: Serialized risk config

        Returns:
            RiskConfig instance
        """
        from decimal import Decimal

        from finbot.core.contracts.risk import DrawdownLimitRule, ExposureLimitRule, PositionLimitRule, RiskConfig

        position_limit = None
        if "position_limit" in data:
            position_limit = PositionLimitRule(
                max_shares=Decimal(data["position_limit"]["max_shares"])
                if data["position_limit"]["max_shares"] is not None
                else None,
                max_value=Decimal(data["position_limit"]["max_value"])
                if data["position_limit"]["max_value"] is not None
                else None,
            )

        exposure_limit = None
        if "exposure_limit" in data:
            exposure_limit = ExposureLimitRule(
                max_gross_exposure_pct=Decimal(data["exposure_limit"]["max_gross_exposure_pct"]),
                max_net_exposure_pct=Decimal(data["exposure_limit"]["max_net_exposure_pct"]),
            )

        drawdown_limit = None
        if "drawdown_limit" in data:
            drawdown_limit = DrawdownLimitRule(
                max_daily_drawdown_pct=Decimal(data["drawdown_limit"]["max_daily_drawdown_pct"])
                if data["drawdown_limit"]["max_daily_drawdown_pct"] is not None
                else None,
                max_total_drawdown_pct=Decimal(data["drawdown_limit"]["max_total_drawdown_pct"])
                if data["drawdown_limit"]["max_total_drawdown_pct"] is not None
                else None,
            )

        return RiskConfig(
            position_limit=position_limit,
            exposure_limit=exposure_limit,
            drawdown_limit=drawdown_limit,
            trading_enabled=data.get("trading_enabled", True),
        )
