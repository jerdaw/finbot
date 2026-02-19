"""Backtrader adapter implementing the core BacktestEngine contract."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import backtrader as bt
import pandas as pd

from finbot.core.contracts import (
    DEFAULT_MISSING_DATA_POLICY,
    BacktestRunMetadata,
    BacktestRunRequest,
    BacktestRunResult,
    CostEvent,
    CostSummary,
    CostType,
    MissingDataPolicy,
)
from finbot.core.contracts.costs import CostModel
from finbot.core.contracts.interfaces import BacktestEngine
from finbot.core.contracts.schemas import validate_bar_dataframe
from finbot.core.contracts.serialization import build_backtest_run_result_from_stats
from finbot.services.backtesting.analyzers.trade_tracker import TradeInfo
from finbot.services.backtesting.backtest_runner import BacktestRunner
from finbot.services.backtesting.brokers.fixed_commission_scheme import FixedCommissionScheme
from finbot.services.backtesting.costs import ZeroCommission, ZeroSlippage, ZeroSpread
from finbot.services.backtesting.snapshot_registry import DataSnapshotRegistry
from finbot.services.backtesting.strategies.dual_momentum import DualMomentum
from finbot.services.backtesting.strategies.no_rebalance import NoRebalance
from finbot.services.backtesting.strategies.rebalance import Rebalance
from finbot.services.backtesting.strategies.risk_parity import RiskParity
from finbot.utils.dict_utils.hash_dictionary import hash_dictionary

DEFAULT_STRATEGY_REGISTRY: dict[str, type[bt.Strategy]] = {
    "dualmomentum": DualMomentum,
    "norebalance": NoRebalance,
    "rebalance": Rebalance,
    "riskparity": RiskParity,
}


class BacktraderAdapter(BacktestEngine):
    """BacktestEngine contract adapter backed by Backtrader/BacktestRunner."""

    def __init__(
        self,
        price_histories: dict[str, pd.DataFrame],
        *,
        strategy_registry: dict[str, type[bt.Strategy]] | None = None,
        broker: type[bt.brokers.BackBroker] = bt.brokers.BackBroker,
        broker_kwargs: dict[str, Any] | None = None,
        broker_commission: type[FixedCommissionScheme] = FixedCommissionScheme,
        sizer: type[bt.sizers.AllInSizer] = bt.sizers.AllInSizer,
        sizer_kwargs: dict[str, Any] | None = None,
        data_snapshot_id: str = "local-yfinance-parquet",
        random_seed: int | None = None,
        commission_model: CostModel | None = None,
        spread_model: CostModel | None = None,
        slippage_model: CostModel | None = None,
        missing_data_policy: MissingDataPolicy = DEFAULT_MISSING_DATA_POLICY,
        snapshot_registry: DataSnapshotRegistry | None = None,
        auto_snapshot: bool = False,
        enable_snapshot_replay: bool = False,
    ):
        self._price_histories = price_histories
        self._strategy_registry = strategy_registry or DEFAULT_STRATEGY_REGISTRY
        self._broker = broker
        self._broker_kwargs = broker_kwargs or {}
        self._broker_commission = broker_commission
        self._sizer = sizer
        self._sizer_kwargs = sizer_kwargs or {}
        self._data_snapshot_id = data_snapshot_id
        self._random_seed = random_seed
        # Cost models - default to zero costs to maintain backwards compatibility
        self._commission_model = commission_model or ZeroCommission()
        self._spread_model = spread_model or ZeroSpread()
        self._slippage_model = slippage_model or ZeroSlippage()
        # Missing data policy - default to forward fill
        self._missing_data_policy = missing_data_policy
        self._snapshot_registry = snapshot_registry
        self._auto_snapshot = auto_snapshot
        self._enable_snapshot_replay = enable_snapshot_replay

    def run(self, request: BacktestRunRequest) -> BacktestRunResult:
        strategy_cls = self._resolve_strategy(request.strategy_name)
        selected_histories, snapshot_id = self._resolve_run_histories(request)
        warnings: list[str] = []

        if (
            self._auto_snapshot
            and self._snapshot_registry is not None
            and not (self._enable_snapshot_replay and request.data_snapshot_id is not None)
        ):
            try:
                snapshot_id = self._resolve_data_snapshot_id(selected_histories, request)
            except Exception as exc:  # pragma: no cover - defensive path
                warnings.append(f"auto_snapshot_failed:{exc}")

        runner = BacktestRunner(
            price_histories=selected_histories,
            start=request.start,
            end=request.end,
            duration=None,
            start_step=None,
            init_cash=request.initial_cash,
            strat=strategy_cls,
            strat_kwargs=deepcopy(request.parameters),
            broker=self._broker,
            broker_kwargs=deepcopy(self._broker_kwargs),
            broker_commission=self._broker_commission,
            sizer=self._sizer,
            sizer_kwargs=deepcopy(self._sizer_kwargs),
            plot=False,
        )
        stats_df = runner.run_backtest()

        # Extract trades and calculate costs
        trades = runner.get_trades()
        costs = self._calculate_costs_from_trades(trades)

        metadata = BacktestRunMetadata(
            run_id=f"bt-{uuid4()}",
            engine_name="backtrader",
            engine_version=str(getattr(bt, "__version__", "unknown")),
            strategy_name=strategy_cls.__name__,
            created_at=datetime.now(UTC),
            config_hash=self._build_config_hash(request=request),
            data_snapshot_id=snapshot_id,
            random_seed=self._random_seed,
        )

        assumptions = {
            "symbols": list(request.symbols),
            "parameters": deepcopy(request.parameters),
            "start": str(request.start) if request.start is not None else None,
            "end": str(request.end) if request.end is not None else None,
            "broker": self._broker.__name__,
            "broker_commission": self._broker_commission.__name__,
            "sizer": self._sizer.__name__,
            "commission_model": self._commission_model.get_name(),
            "spread_model": self._spread_model.get_name(),
            "slippage_model": self._slippage_model.get_name(),
            "missing_data_policy": self._missing_data_policy.value,
            "auto_snapshot": self._auto_snapshot,
            "enable_snapshot_replay": self._enable_snapshot_replay,
            "request_data_snapshot_id": request.data_snapshot_id,
        }

        result = build_backtest_run_result_from_stats(
            stats_df=stats_df,
            metadata=metadata,
            assumptions=assumptions,
            warnings=tuple(warnings),
        )

        # Add costs to result (replace with new result including costs)
        return BacktestRunResult(
            metadata=result.metadata,
            metrics=result.metrics,
            schema_version=result.schema_version,
            assumptions=result.assumptions,
            artifacts=result.artifacts,
            warnings=result.warnings,
            costs=costs,
        )

    def _resolve_data_snapshot_id(
        self,
        selected_histories: dict[str, pd.DataFrame],
        request: BacktestRunRequest,
    ) -> str:
        """Create or reuse snapshot ID for this run's exact input data."""
        assert self._snapshot_registry is not None

        min_start = min(df.index.min() for df in selected_histories.values())
        max_end = max(df.index.max() for df in selected_histories.values())
        start_ts = request.start if request.start is not None else pd.Timestamp(min_start)
        end_ts = request.end if request.end is not None else pd.Timestamp(max_end)

        start_dt = start_ts.to_pydatetime()
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=UTC)

        end_dt = end_ts.to_pydatetime()
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=UTC)

        snapshot = self._snapshot_registry.create_snapshot(
            symbols=list(request.symbols),
            data=selected_histories,
            start=start_dt,
            end=end_dt,
        )
        return snapshot.snapshot_id

    def _resolve_run_histories(self, request: BacktestRunRequest) -> tuple[dict[str, pd.DataFrame], str]:
        """Resolve input histories and snapshot ID for a run."""
        if self._enable_snapshot_replay and request.data_snapshot_id is not None:
            if self._snapshot_registry is None:
                raise ValueError("Snapshot replay requires snapshot_registry")
            snapshot_data = self._snapshot_registry.load_snapshot(request.data_snapshot_id)
            selected_histories = self._select_price_histories(request.symbols, source_histories=snapshot_data)
            return selected_histories, request.data_snapshot_id

        selected_histories = self._select_price_histories(request.symbols)
        return selected_histories, self._data_snapshot_id

    def _resolve_strategy(self, strategy_name: str) -> type[bt.Strategy]:
        strategy_key = strategy_name.lower().replace("_", "")
        if strategy_key not in self._strategy_registry:
            available = sorted(self._strategy_registry.keys())
            raise ValueError(f"Unknown strategy '{strategy_name}'. Available: {available}")
        return self._strategy_registry[strategy_key]

    def _select_price_histories(
        self,
        symbols: tuple[str, ...],
        *,
        source_histories: dict[str, pd.DataFrame] | None = None,
    ) -> dict[str, pd.DataFrame]:
        if not symbols:
            raise ValueError("At least one symbol is required")

        histories_source = source_histories if source_histories is not None else self._price_histories
        histories: dict[str, pd.DataFrame] = {}
        for symbol in symbols:
            if symbol not in histories_source:
                raise ValueError(f"Missing price history for symbol: {symbol}")
            symbol_df = histories_source[symbol].copy()
            # Apply missing data policy before validation
            symbol_df = self._apply_missing_data_policy(symbol_df, symbol)
            validate_bar_dataframe(symbol_df)
            histories[symbol] = symbol_df
        return histories

    def _apply_missing_data_policy(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Apply configured missing data policy to a dataframe.

        Args:
            df: Price history dataframe
            symbol: Symbol name (for error messages)

        Returns:
            DataFrame with missing data handled according to policy

        Raises:
            ValueError: If policy is ERROR and missing data is detected
        """
        if self._missing_data_policy == MissingDataPolicy.FORWARD_FILL:
            return df.ffill()
        elif self._missing_data_policy == MissingDataPolicy.DROP:
            return df.dropna()
        elif self._missing_data_policy == MissingDataPolicy.ERROR:
            if df.isnull().any().any():
                null_counts = df.isnull().sum()
                null_cols = null_counts[null_counts > 0].to_dict()
                raise ValueError(
                    f"Missing data detected in {symbol} with policy=ERROR. Null counts by column: {null_cols}"
                )
            return df
        elif self._missing_data_policy == MissingDataPolicy.INTERPOLATE:
            return df.interpolate(method="linear")
        elif self._missing_data_policy == MissingDataPolicy.BACKFILL:
            return df.bfill()
        else:
            raise ValueError(f"Unknown missing data policy: {self._missing_data_policy}")

    def _build_config_hash(self, request: BacktestRunRequest) -> str:
        hash_input = {
            "strategy_name": request.strategy_name,
            "symbols": list(request.symbols),
            "start": str(request.start),
            "end": str(request.end),
            "initial_cash": request.initial_cash,
            "parameters": request.parameters,
            "broker": self._broker.__name__,
            "broker_kwargs": self._broker_kwargs,
            "broker_commission": self._broker_commission.__name__,
            "sizer": self._sizer.__name__,
            "sizer_kwargs": self._sizer_kwargs,
            "auto_snapshot": self._auto_snapshot,
            "enable_snapshot_replay": self._enable_snapshot_replay,
            "request_data_snapshot_id": request.data_snapshot_id,
        }
        return hash_dictionary(hash_input)

    def _calculate_costs_from_trades(self, trades: list[TradeInfo]) -> CostSummary:
        """Calculate costs from executed trades using configured cost models."""
        cost_events: list[CostEvent] = []
        total_commission = 0.0
        total_spread = 0.0
        total_slippage = 0.0

        for trade in trades:
            # Calculate commission
            commission = self._commission_model.calculate_cost(
                symbol=trade.symbol,
                quantity=abs(trade.size),
                price=trade.price,
                timestamp=pd.Timestamp(trade.timestamp),
            )
            total_commission += commission
            if commission > 0:
                cost_events.append(
                    CostEvent(
                        timestamp=pd.Timestamp(trade.timestamp),
                        symbol=trade.symbol,
                        cost_type=CostType.COMMISSION,
                        amount=commission,
                        basis=self._commission_model.get_name(),
                    )
                )

            # Calculate spread
            spread = self._spread_model.calculate_cost(
                symbol=trade.symbol,
                quantity=abs(trade.size),
                price=trade.price,
                timestamp=pd.Timestamp(trade.timestamp),
            )
            total_spread += spread
            if spread > 0:
                cost_events.append(
                    CostEvent(
                        timestamp=pd.Timestamp(trade.timestamp),
                        symbol=trade.symbol,
                        cost_type=CostType.SPREAD,
                        amount=spread,
                        basis=self._spread_model.get_name(),
                    )
                )

            # Calculate slippage
            slippage = self._slippage_model.calculate_cost(
                symbol=trade.symbol,
                quantity=abs(trade.size),
                price=trade.price,
                timestamp=pd.Timestamp(trade.timestamp),
            )
            total_slippage += slippage
            if slippage > 0:
                cost_events.append(
                    CostEvent(
                        timestamp=pd.Timestamp(trade.timestamp),
                        symbol=trade.symbol,
                        cost_type=CostType.SLIPPAGE,
                        amount=slippage,
                        basis=self._slippage_model.get_name(),
                    )
                )

        return CostSummary(
            total_commission=total_commission,
            total_spread=total_spread,
            total_slippage=total_slippage,
            total_borrow=0.0,
            total_market_impact=0.0,
            cost_events=tuple(cost_events),
        )
