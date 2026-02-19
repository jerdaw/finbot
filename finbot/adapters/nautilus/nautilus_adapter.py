"""NautilusTrader pilot adapter implementing the BacktestEngine contract."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from importlib.util import find_spec
from math import floor, isfinite
from typing import Any
from uuid import uuid4

import pandas as pd

from finbot.core.contracts.interfaces import BacktestEngine
from finbot.core.contracts.models import BacktestRunMetadata, BacktestRunRequest, BacktestRunResult
from finbot.core.contracts.schemas import validate_bar_dataframe
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
        enable_native_execution: bool = True,
    ) -> None:
        self.name = "nautilus-pilot"
        self.version = self._get_nautilus_version()
        self._price_histories = price_histories
        self._data_snapshot_id = data_snapshot_id
        self._random_seed = random_seed
        self._enable_backtrader_fallback = enable_backtrader_fallback
        self._enable_native_execution = enable_native_execution

    def run(self, request: BacktestRunRequest) -> BacktestRunResult:
        """Run pilot backtest through the contract interface."""
        self._validate_request(request)

        native_available = self._enable_native_execution and self._supports_native_nautilus()
        warnings: list[str] = []
        native_result: tuple[dict[str, float], dict[str, Any], dict[str, str], tuple[str, ...]] | None = None

        if native_available:
            try:
                native_result = self._run_via_nautilus(request)
            except Exception as exc:
                warnings.append(
                    f"native_nautilus_failed:{type(exc).__name__}:{exc}; falling back to backtrader for E6 pilot."
                )
        else:
            warnings.append(
                "NautilusTrader package is unavailable or disabled; using backtrader fallback for E6 pilot."
            )

        if native_result is None and not self._enable_backtrader_fallback:
            raise RuntimeError("Nautilus native execution failed/unavailable and fallback is disabled.")

        if native_result is not None:
            native_metrics, native_assumptions, native_artifacts, native_warnings = native_result
            metadata = BacktestRunMetadata(
                run_id=f"nt-{uuid4()}",
                engine_name=self.name,
                engine_version=self.version,
                strategy_name=request.strategy_name,
                created_at=datetime.now(UTC),
                config_hash=self._build_config_hash(request),
                data_snapshot_id=self._data_snapshot_id,
                random_seed=self._random_seed,
            )
            assumptions = {
                **native_assumptions,
                "adapter_mode": "native_nautilus",
                "native_nautilus_available": native_available,
            }
            artifacts = {
                **native_artifacts,
                "pilot_mode": "native",
            }
            return BacktestRunResult(
                metadata=metadata,
                metrics=native_metrics,
                assumptions=assumptions,
                artifacts=artifacts,
                warnings=tuple(warnings) + native_warnings,
            )

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

    def _run_via_nautilus(
        self, request: BacktestRunRequest
    ) -> tuple[dict[str, float], dict[str, Any], dict[str, str], tuple[str, ...]]:
        from decimal import Decimal

        from nautilus_trader.backtest.engine import BacktestEngine as NautilusBacktestEngine
        from nautilus_trader.config import BacktestEngineConfig
        from nautilus_trader.examples.strategies.ema_cross import EMACross, EMACrossConfig
        from nautilus_trader.model.currencies import USD
        from nautilus_trader.model.data import BarSpecification, BarType
        from nautilus_trader.model.enums import AccountType, AggregationSource, BarAggregation, OmsType, PriceType
        from nautilus_trader.model.identifiers import TraderId, Venue
        from nautilus_trader.model.objects import Money
        from nautilus_trader.persistence.wranglers import BarDataWrangler
        from nautilus_trader.test_kit.providers import TestInstrumentProvider

        if len(request.symbols) != 1:
            raise ValueError("Nautilus pilot native mode currently supports exactly one symbol")
        symbol = request.symbols[0]
        price_df = self._select_native_price_history(symbol, request.start, request.end)

        venue_id = "XNAS"
        trader_id = TraderId("FINBOT-NT-001")
        venue = Venue(venue_id)
        instrument = TestInstrumentProvider.equity(symbol, venue_id)

        engine = NautilusBacktestEngine(config=BacktestEngineConfig(trader_id=trader_id))
        engine.add_venue(
            venue=venue,
            oms_type=OmsType.NETTING,
            account_type=AccountType.CASH,
            base_currency=USD,
            starting_balances=[Money(request.initial_cash, USD)],
        )
        engine.add_instrument(instrument)

        bar_spec = BarSpecification(step=1, aggregation=BarAggregation.DAY, price_type=PriceType.LAST)
        bar_type = BarType(instrument.id, bar_spec, AggregationSource.EXTERNAL)
        wrangler = BarDataWrangler(bar_type=bar_type, instrument=instrument)
        bar_data = wrangler.process(self._to_nautilus_dataframe(price_df))
        engine.add_data(bar_data)

        fast_ema_period = int(request.parameters.get("nautilus_fast_ema_period", 10))
        slow_ema_period = int(request.parameters.get("nautilus_slow_ema_period", 20))
        if fast_ema_period <= 0 or slow_ema_period <= 0:
            raise ValueError("nautilus EMA periods must be positive")
        if fast_ema_period >= slow_ema_period:
            raise ValueError("nautilus_fast_ema_period must be less than nautilus_slow_ema_period")

        target_weight = float(request.parameters["rebal_proportions"][0])
        first_close = float(price_df["Close"].iloc[0])
        trade_size = max(1, floor((request.initial_cash * target_weight) / first_close))

        strategy = EMACross(
            EMACrossConfig(
                instrument_id=instrument.id,
                bar_type=bar_type,
                trade_size=Decimal(str(trade_size)),
                fast_ema_period=fast_ema_period,
                slow_ema_period=slow_ema_period,
            )
        )
        engine.add_strategy(strategy)
        engine.run()
        result = engine.get_result()

        metrics = self._map_nautilus_metrics(result=result, initial_cash=request.initial_cash)
        assumptions = {
            "symbols": list(request.symbols),
            "parameters": deepcopy(request.parameters),
            "nautilus_strategy": "EMACross",
            "nautilus_strategy_mapping": "rebalance_request_mapped_to_ema_cross_pilot",
            "nautilus_fast_ema_period": fast_ema_period,
            "nautilus_slow_ema_period": slow_ema_period,
            "nautilus_trade_size": trade_size,
        }
        artifacts = {"nautilus_instrument_id": str(instrument.id), "nautilus_venue": venue_id}
        run_warnings = (
            "Pilot native Nautilus path currently supports one-symbol requests and maps rebalance to EMA cross.",
        )
        return metrics, assumptions, artifacts, run_warnings

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
                "native_execution_enabled": self._enable_native_execution,
                "nautilus_version": self.version,
            }
        )

    def _select_native_price_history(
        self,
        symbol: str,
        start: pd.Timestamp | None,
        end: pd.Timestamp | None,
    ) -> pd.DataFrame:
        if len(self._price_histories) == 0:
            raise ValueError("price_histories cannot be empty")
        if symbol not in self._price_histories:
            raise ValueError(f"Missing price history for symbol: {symbol}")

        df = self._price_histories[symbol].copy()
        validate_bar_dataframe(df)

        if start is not None:
            df = df[df.index >= start]
        if end is not None:
            df = df[df.index <= end]

        if len(df) < 40:
            raise ValueError("Nautilus pilot requires at least 40 bars in the selected window")
        return df

    def _to_nautilus_dataframe(self, price_df: pd.DataFrame) -> pd.DataFrame:
        bars = price_df.loc[:, ["Open", "High", "Low", "Close", "Volume"]].copy()
        bars.columns = ["open", "high", "low", "close", "volume"]
        bars.index = pd.to_datetime(bars.index, utc=True)
        return bars

    def _map_nautilus_metrics(self, *, result: Any, initial_cash: float) -> dict[str, float]:
        pnl_by_currency = getattr(result, "stats_pnls", {})
        usd_stats = pnl_by_currency.get("USD", {}) if isinstance(pnl_by_currency, dict) else {}
        pnl_total = float(usd_stats.get("PnL (total)", 0.0))

        ending_value = float(initial_cash + pnl_total)
        roi = (ending_value / initial_cash) - 1.0 if initial_cash > 0 else 0.0

        backtest_start = pd.Timestamp(getattr(result, "backtest_start", pd.Timestamp.now(UTC).value), unit="ns")
        backtest_end = pd.Timestamp(getattr(result, "backtest_end", pd.Timestamp.now(UTC).value), unit="ns")
        days = max((backtest_end - backtest_start).days, 1)
        years = max(days / 365.25, 1 / 365.25)
        cagr = (ending_value / initial_cash) ** (1 / years) - 1 if initial_cash > 0 else 0.0

        returns_stats = getattr(result, "stats_returns", {})
        sharpe = self._finite_or_default(returns_stats.get("Sharpe Ratio (252 days)", 0.0), 0.0)

        return {
            "starting_value": self._finite_or_default(initial_cash, 0.0),
            "ending_value": self._finite_or_default(ending_value, initial_cash),
            "roi": self._finite_or_default(roi, 0.0),
            "cagr": self._finite_or_default(cagr, 0.0),
            "sharpe": sharpe,
            "max_drawdown": 0.0,
            "mean_cash_utilization": 0.0,
        }

    def _finite_or_default(self, value: Any, default: float) -> float:
        try:
            as_float = float(value)
        except (TypeError, ValueError):
            return default
        return as_float if isfinite(as_float) else default

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
