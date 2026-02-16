"""Unit tests for experiment registry."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from finbot.core.contracts import BacktestRunMetadata, BacktestRunResult
from finbot.services.backtesting.experiment_registry import ExperimentRegistry


@pytest.fixture
def temp_registry(tmp_path):
    """Create temporary experiment registry."""
    return ExperimentRegistry(tmp_path / "experiments")


@pytest.fixture
def sample_result():
    """Create sample backtest result."""
    metadata = BacktestRunMetadata(
        run_id="bt-test-001",
        engine_name="backtrader",
        engine_version="1.9.0",
        strategy_name="TestStrategy",
        created_at=datetime(2026, 2, 15, 12, 0, 0, tzinfo=UTC),
        config_hash="abc123",
        data_snapshot_id="test-snapshot",
        random_seed=42,
    )

    return BacktestRunResult(
        metadata=metadata,
        metrics={"cagr": 0.15, "sharpe": 1.5, "max_drawdown": -0.10},
        assumptions={"symbols": ["SPY"], "start": "2020-01-01", "end": "2023-12-31"},
    )


def test_registry_initialization(tmp_path):
    """Test registry initializes and creates directory."""
    registry_path = tmp_path / "experiments"
    assert not registry_path.exists()

    registry = ExperimentRegistry(registry_path)

    assert registry.storage_dir == registry_path
    assert registry_path.exists()
    assert registry_path.is_dir()


def test_save_experiment(temp_registry, sample_result):
    """Test saving experiment creates correct file structure."""
    filepath = temp_registry.save(sample_result)

    # Check file exists
    assert filepath.exists()
    assert filepath.is_file()

    # Check structure: experiments/2026/02/bt-test-001.json
    assert filepath.parent.name == "02"  # Month
    assert filepath.parent.parent.name == "2026"  # Year
    assert filepath.name == "bt-test-001.json"


def test_save_duplicate_raises_error(temp_registry, sample_result):
    """Test saving duplicate run_id raises error."""
    # First save succeeds
    temp_registry.save(sample_result)

    # Second save should fail
    with pytest.raises(ValueError, match="already exists"):
        temp_registry.save(sample_result)


def test_load_experiment(temp_registry, sample_result):
    """Test loading experiment returns correct data."""
    # Save first
    temp_registry.save(sample_result)

    # Load
    loaded = temp_registry.load("bt-test-001")

    # Verify
    assert loaded.metadata.run_id == sample_result.metadata.run_id
    assert loaded.metadata.strategy_name == sample_result.metadata.strategy_name
    assert loaded.metadata.config_hash == sample_result.metadata.config_hash
    assert loaded.metrics == sample_result.metrics


def test_load_nonexistent_raises_error(temp_registry):
    """Test loading nonexistent run raises error."""
    with pytest.raises(FileNotFoundError, match="not found in registry"):
        temp_registry.load("nonexistent-id")


def test_list_runs_empty(temp_registry):
    """Test listing runs when registry is empty."""
    runs = temp_registry.list_runs()
    assert runs == []


def test_list_runs_returns_all(temp_registry):
    """Test listing runs returns all experiments."""
    # Create multiple results
    results = []
    for i in range(3):
        metadata = BacktestRunMetadata(
            run_id=f"bt-test-{i:03d}",
            engine_name="backtrader",
            engine_version="1.9.0",
            strategy_name="TestStrategy",
            created_at=datetime(2026, 2, 15 + i, 12, 0, 0, tzinfo=UTC),
            config_hash=f"hash{i}",
            data_snapshot_id="test-snapshot",
        )
        result = BacktestRunResult(
            metadata=metadata,
            metrics={"cagr": 0.10 + i * 0.05},
        )
        results.append(result)
        temp_registry.save(result)

    # List all
    runs = temp_registry.list_runs()

    assert len(runs) == 3
    # Should be sorted newest first
    assert runs[0].run_id == "bt-test-002"
    assert runs[1].run_id == "bt-test-001"
    assert runs[2].run_id == "bt-test-000"


def test_list_runs_filter_by_strategy(temp_registry):
    """Test filtering runs by strategy name."""
    # Create runs with different strategies
    for i, strategy in enumerate(["Rebalance", "NoRebalance", "Rebalance"]):
        metadata = BacktestRunMetadata(
            run_id=f"bt-{strategy}-{i:03d}",
            engine_name="backtrader",
            engine_version="1.9.0",
            strategy_name=strategy,
            created_at=datetime(2026, 2, 15, 12, 0, 0, tzinfo=UTC),
            config_hash="hash1",
            data_snapshot_id="test-snapshot",
        )
        result = BacktestRunResult(metadata=metadata, metrics={})
        temp_registry.save(result)

    # Filter by strategy
    rebalance_runs = temp_registry.list_runs(strategy="Rebalance")

    assert len(rebalance_runs) == 2
    assert all(r.strategy_name == "Rebalance" for r in rebalance_runs)


def test_list_runs_filter_by_date_range(temp_registry):
    """Test filtering runs by date range."""
    # Create runs on different dates
    dates = [
        datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC),
        datetime(2026, 2, 15, 12, 0, 0, tzinfo=UTC),
        datetime(2026, 3, 15, 12, 0, 0, tzinfo=UTC),
    ]

    for i, date in enumerate(dates):
        metadata = BacktestRunMetadata(
            run_id=f"bt-test-{i:03d}",
            engine_name="backtrader",
            engine_version="1.9.0",
            strategy_name="TestStrategy",
            created_at=date,
            config_hash="hash1",
            data_snapshot_id="test-snapshot",
        )
        result = BacktestRunResult(metadata=metadata, metrics={})
        temp_registry.save(result)

    # Filter by date range (February only)
    feb_runs = temp_registry.list_runs(since="2026-02-01", until="2026-02-28")

    assert len(feb_runs) == 1
    assert feb_runs[0].created_at.month == 2


def test_list_runs_with_limit(temp_registry):
    """Test limiting number of results."""
    # Create 5 runs
    for i in range(5):
        metadata = BacktestRunMetadata(
            run_id=f"bt-test-{i:03d}",
            engine_name="backtrader",
            engine_version="1.9.0",
            strategy_name="TestStrategy",
            created_at=datetime(2026, 2, 15, 12, 0, 0, tzinfo=UTC),
            config_hash="hash1",
            data_snapshot_id="test-snapshot",
        )
        result = BacktestRunResult(metadata=metadata, metrics={})
        temp_registry.save(result)

    # Limit to 3
    runs = temp_registry.list_runs(limit=3)

    assert len(runs) == 3


def test_find_by_hash(temp_registry):
    """Test finding runs by config hash."""
    # Create runs with same and different hashes
    hashes = ["hash-A", "hash-B", "hash-A", "hash-C"]

    for i, config_hash in enumerate(hashes):
        metadata = BacktestRunMetadata(
            run_id=f"bt-test-{i:03d}",
            engine_name="backtrader",
            engine_version="1.9.0",
            strategy_name="TestStrategy",
            created_at=datetime(2026, 2, 15, 12, 0, 0, tzinfo=UTC),
            config_hash=config_hash,
            data_snapshot_id="test-snapshot",
        )
        result = BacktestRunResult(metadata=metadata, metrics={"cagr": i * 0.05})
        temp_registry.save(result)

    # Find runs with hash-A
    hash_a_runs = temp_registry.find_by_hash("hash-A")

    assert len(hash_a_runs) == 2
    assert all(r.metadata.config_hash == "hash-A" for r in hash_a_runs)


def test_count(temp_registry):
    """Test counting experiments."""
    assert temp_registry.count() == 0

    # Add some experiments
    for i in range(3):
        metadata = BacktestRunMetadata(
            run_id=f"bt-test-{i:03d}",
            engine_name="backtrader",
            engine_version="1.9.0",
            strategy_name="TestStrategy",
            created_at=datetime(2026, 2, 15, 12, 0, 0, tzinfo=UTC),
            config_hash="hash1",
            data_snapshot_id="test-snapshot",
        )
        result = BacktestRunResult(metadata=metadata, metrics={})
        temp_registry.save(result)

    assert temp_registry.count() == 3


def test_delete(temp_registry, sample_result):
    """Test deleting experiment."""
    # Save
    temp_registry.save(sample_result)
    assert temp_registry.count() == 1

    # Delete
    temp_registry.delete("bt-test-001")
    assert temp_registry.count() == 0

    # Should not be loadable
    with pytest.raises(FileNotFoundError):
        temp_registry.load("bt-test-001")


def test_delete_nonexistent_raises_error(temp_registry):
    """Test deleting nonexistent run raises error."""
    with pytest.raises(FileNotFoundError, match="not found in registry"):
        temp_registry.delete("nonexistent-id")
