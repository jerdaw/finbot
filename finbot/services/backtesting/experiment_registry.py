"""Experiment registry for persisting and querying backtest runs."""

from __future__ import annotations

import json
from pathlib import Path

from finbot.core.contracts import BacktestRunResult, backtest_result_from_payload, backtest_result_to_payload
from finbot.core.contracts.models import BacktestRunMetadata


class ExperimentRegistry:
    """File-based registry for backtest experiment results.

    Stores each run as a JSON file organized by year/month for efficient access.

    Storage structure:
        experiments/
        ├── 2026/
        │   ├── 02/
        │   │   ├── bt-uuid1.json
        │   │   ├── bt-uuid2.json
        │   │   └── ...
        │   └── 03/
        └── ...

    Attributes:
        storage_dir: Root directory for experiment storage
    """

    def __init__(self, storage_dir: Path | str):
        """Initialize experiment registry.

        Args:
            storage_dir: Directory to store experiment results
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, result: BacktestRunResult) -> Path:
        """Save backtest result to registry.

        Args:
            result: Backtest result to save

        Returns:
            Path to saved file

        Raises:
            ValueError: If result already exists (based on run_id)
        """
        # Organize by year/month
        year = result.metadata.created_at.year
        month = f"{result.metadata.created_at.month:02d}"

        # Create directory structure
        year_dir = self.storage_dir / str(year)
        month_dir = year_dir / month
        month_dir.mkdir(parents=True, exist_ok=True)

        # Create filename from run_id
        filename = f"{result.metadata.run_id}.json"
        filepath = month_dir / filename

        # Check if already exists
        if filepath.exists():
            raise ValueError(f"Experiment {result.metadata.run_id} already exists at {filepath}")

        # Serialize and save
        payload = backtest_result_to_payload(result)

        with filepath.open("w") as f:
            json.dump(payload, f, indent=2)

        return filepath

    def load(self, run_id: str) -> BacktestRunResult:
        """Load experiment by run ID.

        Args:
            run_id: Unique run identifier

        Returns:
            Loaded backtest result

        Raises:
            FileNotFoundError: If run_id not found
        """
        # Search for file (we don't know the year/month a priori)
        filepath = self._find_run_file(run_id)

        if filepath is None:
            raise FileNotFoundError(f"Experiment {run_id} not found in registry")

        # Load and deserialize
        with filepath.open("r") as f:
            payload = json.load(f)

        return backtest_result_from_payload(payload)

    def list_runs(
        self,
        strategy: str | None = None,
        since: str | None = None,
        until: str | None = None,
        limit: int | None = None,
    ) -> list[BacktestRunMetadata]:
        """List experiments matching criteria.

        Args:
            strategy: Filter by strategy name (case-insensitive)
            since: ISO date string (e.g., "2026-01-01") - include runs on or after
            until: ISO date string (e.g., "2026-12-31") - include runs on or before
            limit: Maximum number of results to return

        Returns:
            List of matching experiment metadata, sorted by created_at descending
        """
        import datetime
        from datetime import UTC

        # Parse date filters if provided
        since_dt = datetime.datetime.fromisoformat(since).replace(tzinfo=UTC) if since else None
        until_dt = datetime.datetime.fromisoformat(until).replace(tzinfo=UTC) if until else None

        # Collect all run files
        run_files = sorted(self.storage_dir.glob("*/*/*.json"), reverse=True)  # Newest first

        metadata_list: list[BacktestRunMetadata] = []

        for filepath in run_files:
            # Load just metadata (lightweight)
            try:
                with filepath.open("r") as f:
                    payload = json.load(f)

                # Extract metadata
                metadata_dict = payload.get("metadata", {})
                created_at_str = metadata_dict.get("created_at")
                strategy_name = metadata_dict.get("strategy_name")

                # Parse created_at
                created_at = datetime.datetime.fromisoformat(created_at_str)

                # Apply filters
                if since_dt and created_at < since_dt:
                    continue
                if until_dt and created_at > until_dt:
                    continue
                if strategy and strategy.lower() != strategy_name.lower():
                    continue

                # Create metadata object
                metadata = BacktestRunMetadata(
                    run_id=metadata_dict["run_id"],
                    engine_name=metadata_dict["engine_name"],
                    engine_version=metadata_dict["engine_version"],
                    strategy_name=metadata_dict["strategy_name"],
                    created_at=created_at,
                    config_hash=metadata_dict["config_hash"],
                    data_snapshot_id=metadata_dict["data_snapshot_id"],
                    random_seed=metadata_dict.get("random_seed"),
                )

                metadata_list.append(metadata)

                # Check limit
                if limit and len(metadata_list) >= limit:
                    break

            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip malformed files
                continue

        return metadata_list

    def find_by_hash(self, config_hash: str) -> list[BacktestRunResult]:
        """Find all runs with matching config hash.

        Useful for finding all runs with identical configuration.

        Args:
            config_hash: Configuration hash to match

        Returns:
            List of matching backtest results
        """
        # Get all runs
        all_metadata = self.list_runs()

        # Filter by hash
        matching = [m for m in all_metadata if m.config_hash == config_hash]

        # Load full results
        results: list[BacktestRunResult] = []
        for metadata in matching:
            try:
                result = self.load(metadata.run_id)
                results.append(result)
            except FileNotFoundError:
                continue

        return results

    def count(self) -> int:
        """Count total number of experiments in registry.

        Returns:
            Total number of stored experiments
        """
        return len(list(self.storage_dir.glob("*/*/*.json")))

    def _find_run_file(self, run_id: str) -> Path | None:
        """Find file path for given run_id.

        Args:
            run_id: Run identifier

        Returns:
            Path to file if found, None otherwise
        """
        # Search pattern: */*/{run_id}.json
        matches = list(self.storage_dir.glob(f"*/*/{run_id}.json"))

        if not matches:
            return None

        # Should only be one match (run_id is unique)
        return matches[0]

    def delete(self, run_id: str) -> None:
        """Delete experiment from registry.

        Args:
            run_id: Run identifier

        Raises:
            FileNotFoundError: If run_id not found
        """
        filepath = self._find_run_file(run_id)

        if filepath is None:
            raise FileNotFoundError(f"Experiment {run_id} not found in registry")

        filepath.unlink()
