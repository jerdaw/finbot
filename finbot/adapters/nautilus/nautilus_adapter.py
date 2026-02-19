"""NautilusTrader pilot adapter implementing the BacktestEngine contract."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from importlib.util import find_spec
from uuid import uuid4

import pandas as pd

from finbot.core.contracts.interfaces import BacktestEngine
from finbot.core.contracts.models import BacktestRunMetadata, BacktestRunRequest, BacktestRunResult
from finbot.services.backtesting.adapters.backtrader_adapter import BacktraderAdapter
from finbot.services.backtesting.strategies.rebalance import Rebalance
from finbot.utils.dict_utils.hash_dictionary import hash_dictionary


class NautilusAdapter(BacktestEngine):
    """Pilot adapter for evaluating a Nautilus execution path.

    Notes:
        - This adapter is intentionally scoped to E6 pilot work.
        - It currently supports only the `Rebalance` strategy shape.
        - When native Nautilus execution is unavailable, it falls back to the
          Backtrader contract path and tags outputs accordingly.
    """

    def __init__(
        self,
        price_histories: dict[str, pd.DataFrame],
        *,
        data_snapshot_id: str = "nautilus-pilot-local",
        random_seed: int | None = None,
        enable_backtrader_fallback: bool = True,
    ) -> None:
        self.name = "nautilus-pilot"
        self.version = self._get_nautilus_version()
        self._price_histories = price_histories
        self._data_snapshot_id = data_snapshot_id
        self._random_seed = random_seed
        self._enable_backtrader_fallback = enable_backtrader_fallback

    def run(self, request: BacktestRunRequest) -> BacktestRunResult:
        """Run pilot backtest through the contract interface."""
        self._validate_request(request)

        native_available = self._supports_native_nautilus()
        warnings: list[str] = []

        if native_available:
            warnings.append(
                "Native Nautilus execution path is not enabled yet; using backtrader fallback for E6 pilot."
            )
        else:
            warnings.append("NautilusTrader package is unavailable; using backtrader fallback for E6 pilot.")

        if not self._enable_backtrader_fallback:
            raise RuntimeError("Nautilus fallback is disabled and native execution path is not implemented.")

        fallback_result = self._run_via_backtrader(request)

        metadata = BacktestRunMetadata(
            run_id=f"nt-{uuid4()}",
            engine_name=self.name,
            engine_version=self.version,
            strategy_name=request.strategy_name,
            created_at=datetime.now(UTC),
            config_hash=self._build_config_hash(request),
            data_snapshot_id=fallback_result.metadata.data_snapshot_id,
            random_seed=self._random_seed,
        )

        assumptions = dict(fallback_result.assumptions)
        assumptions["adapter_mode"] = "backtrader_fallback"
        assumptions["native_nautilus_available"] = native_available

        artifacts = dict(fallback_result.artifacts)
        artifacts["pilot_mode"] = "fallback"

        return BacktestRunResult(
            metadata=metadata,
            metrics=dict(fallback_result.metrics),
            schema_version=fallback_result.schema_version,
            assumptions=assumptions,
            artifacts=artifacts,
            warnings=tuple(warnings) + fallback_result.warnings,
            costs=fallback_result.costs,
        )

    # Backward-compatible shim for older call sites/docs.
    def run_backtest(self, request: BacktestRunRequest) -> BacktestRunResult:
        """Backward-compatible alias to `run`."""
        return self.run(request)

    def _validate_request(self, request: BacktestRunRequest) -> None:
        if not request.strategy_name:
            raise ValueError("strategy_name is required")
        if request.strategy_name.lower().replace("_", "") != "rebalance":
            raise ValueError("Nautilus pilot currently supports only strategy_name='rebalance'")
        if not request.symbols:
            raise ValueError("At least one symbol is required")
        if request.initial_cash <= 0:
            raise ValueError("initial_cash must be positive")
        if request.start and request.end and request.start >= request.end:
            raise ValueError("start must be before end")
        if "rebal_proportions" not in request.parameters:
            raise ValueError("rebalance pilot requires 'rebal_proportions' parameter")
        if "rebal_interval" not in request.parameters:
            raise ValueError("rebalance pilot requires 'rebal_interval' parameter")
        if len(request.parameters["rebal_proportions"]) != len(request.symbols):
            raise ValueError("Length of rebal_proportions must match symbol count")

    def _run_via_backtrader(self, request: BacktestRunRequest) -> BacktestRunResult:
        adapter = BacktraderAdapter(
            price_histories=self._price_histories,
            strategy_registry={"rebalance": Rebalance},
            data_snapshot_id=self._data_snapshot_id,
            random_seed=self._random_seed,
        )
        return adapter.run(
            BacktestRunRequest(
                strategy_name=request.strategy_name,
                symbols=request.symbols,
                start=request.start,
                end=request.end,
                initial_cash=request.initial_cash,
                parameters=deepcopy(request.parameters),
            )
        )

    def _build_config_hash(self, request: BacktestRunRequest) -> str:
        return hash_dictionary(
            {
                "adapter": self.name,
                "strategy_name": request.strategy_name,
                "symbols": list(request.symbols),
                "start": str(request.start),
                "end": str(request.end),
                "initial_cash": request.initial_cash,
                "parameters": request.parameters,
                "data_snapshot_id": self._data_snapshot_id,
                "random_seed": self._random_seed,
                "fallback_enabled": self._enable_backtrader_fallback,
                "nautilus_version": self.version,
            }
        )

    def _supports_native_nautilus(self) -> bool:
        return find_spec("nautilus_trader") is not None

    def _get_nautilus_version(self) -> str:
        try:
            import nautilus_trader

            return str(nautilus_trader.__version__)
        except ImportError:
            return "unknown (not installed)"

    def supports_feature(self, feature: str) -> bool:
        supported = {
            "basic_backtest",
            "snapshot_reference",
        }
        return feature in supported
