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
from finbot.services.backtesting.strategies.dual_momentum import DualMomentum
from finbot.services.backtesting.strategies.no_rebalance import NoRebalance
from finbot.services.backtesting.strategies.rebalance import Rebalance
from finbot.services.backtesting.strategies.risk_parity import RiskParity
from finbot.utils.dict_utils.hash_dictionary import hash_dictionary


class NautilusAdapter(BacktestEngine):
    """Pilot adapter for evaluating a Nautilus execution path.

    Notes:
        - This adapter is intentionally scoped to E6/post-E6 pilot work.
        - Native mode supports:
          - `Rebalance` (mapped to Nautilus EMA-cross pilot path).
          - `NoRebalance` (single-symbol long-only buy-and-hold pilot path).
          - `DualMomentum` (two-symbol deterministic parity proxy path).
          - `RiskParity` (multi-symbol deterministic parity proxy path).
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
        """Initialize the NautilusAdapter with price data and execution options.

        Args:
            price_histories: Mapping of symbol to OHLCV DataFrames.
            data_snapshot_id: Identifier for data lineage tracking.
            random_seed: Optional seed for reproducible runs.
            enable_backtrader_fallback: Whether to fall back to Backtrader when
                native Nautilus execution is unavailable or fails.
            enable_native_execution: Whether to attempt native Nautilus execution.
        """
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
            adapter_mode = str(native_assumptions.get("adapter_mode", "native_nautilus"))
            assumptions = {
                **native_assumptions,
                "adapter_mode": adapter_mode,
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
        """Validate the backtest request and delegate to strategy-specific validators.

        Args:
            request: The backtest run request to validate.

        Raises:
            ValueError: If the request is malformed or unsupported.
        """
        if not request.strategy_name:
            raise ValueError("strategy_name is required")
        normalized_strategy = request.strategy_name.lower().replace("_", "")
        if normalized_strategy not in {"rebalance", "norebalance", "dualmomentum", "riskparity"}:
            raise ValueError(
                "Nautilus pilot currently supports strategy_name in "
                "{'rebalance', 'NoRebalance', 'DualMomentum', 'RiskParity'}"
            )
        if not request.symbols:
            raise ValueError("At least one symbol is required")
        if request.initial_cash <= 0:
            raise ValueError("initial_cash must be positive")
        if request.start and request.end and request.start >= request.end:
            raise ValueError("start must be before end")
        if normalized_strategy == "rebalance":
            self._validate_rebalance_request(request)
            return
        if normalized_strategy == "norebalance":
            self._validate_norebalance_request(request)
            return
        if normalized_strategy == "dualmomentum":
            self._validate_dual_momentum_request(request)
            return
        self._validate_risk_parity_request(request)

    def _validate_rebalance_request(self, request: BacktestRunRequest) -> None:
        """Validate rebalance-strategy-specific request parameters."""
        if "rebal_proportions" not in request.parameters:
            raise ValueError("rebalance pilot requires 'rebal_proportions' parameter")
        if "rebal_interval" not in request.parameters:
            raise ValueError("rebalance pilot requires 'rebal_interval' parameter")
        if len(request.parameters["rebal_proportions"]) != len(request.symbols):
            raise ValueError("Length of rebal_proportions must match symbol count")

    def _validate_norebalance_request(self, request: BacktestRunRequest) -> None:
        """Validate NoRebalance-strategy-specific request parameters."""
        if len(request.symbols) != 1:
            raise ValueError("NoRebalance pilot currently supports exactly one symbol")
        if "equity_proportions" in request.parameters and len(request.parameters["equity_proportions"]) != len(
            request.symbols
        ):
            raise ValueError("Length of equity_proportions must match symbol count")

    def _validate_dual_momentum_request(self, request: BacktestRunRequest) -> None:
        """Validate DualMomentum-strategy-specific request parameters."""
        if len(request.symbols) != 2:
            raise ValueError("DualMomentum pilot currently requires exactly two symbols")
        lookback = int(request.parameters.get("lookback", 252))
        rebal_interval = int(request.parameters.get("rebal_interval", 21))
        if lookback <= 0:
            raise ValueError("lookback must be positive")
        if rebal_interval <= 0:
            raise ValueError("rebal_interval must be positive")

    def _validate_risk_parity_request(self, request: BacktestRunRequest) -> None:
        """Validate RiskParity-strategy-specific request parameters."""
        if len(request.symbols) < 2:
            raise ValueError("RiskParity pilot currently requires at least two symbols")
        vol_window = int(request.parameters.get("vol_window", 63))
        rebal_interval = int(request.parameters.get("rebal_interval", 21))
        if vol_window <= 0:
            raise ValueError("vol_window must be positive")
        if rebal_interval <= 0:
            raise ValueError("rebal_interval must be positive")

    def _run_via_backtrader(self, request: BacktestRunRequest) -> BacktestRunResult:
        """Execute the backtest via the Backtrader fallback adapter.

        Args:
            request: The backtest run request.

        Returns:
            The backtest result produced by the BacktraderAdapter.
        """
        adapter = BacktraderAdapter(
            price_histories=self._price_histories,
            strategy_registry={
                "rebalance": Rebalance,
                "norebalance": NoRebalance,
                "dualmomentum": DualMomentum,
                "riskparity": RiskParity,
            },
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
        """Dispatch to the appropriate native Nautilus execution path.

        Args:
            request: The backtest run request.

        Returns:
            A tuple of (metrics, assumptions, artifacts, warnings).

        Raises:
            ValueError: If the strategy is not supported for native execution.
        """
        normalized_strategy = request.strategy_name.lower().replace("_", "")
        if normalized_strategy == "norebalance":
            return self._run_via_nautilus_buy_and_hold(request)
        if normalized_strategy == "dualmomentum":
            return self._run_via_nautilus_dual_momentum(request)
        if normalized_strategy == "riskparity":
            return self._run_via_nautilus_risk_parity(request)
        if normalized_strategy != "rebalance":
            raise ValueError(f"Unsupported native Nautilus strategy for pilot: {request.strategy_name}")

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

    def _run_via_nautilus_buy_and_hold(
        self, request: BacktestRunRequest
    ) -> tuple[dict[str, float], dict[str, Any], dict[str, str], tuple[str, ...]]:
        """Run a single-symbol buy-and-hold backtest via native Nautilus.

        Args:
            request: The backtest run request (must have exactly one symbol).

        Returns:
            A tuple of (metrics, assumptions, artifacts, warnings).
        """
        from decimal import Decimal

        from nautilus_trader.backtest.engine import BacktestEngine as NautilusBacktestEngine
        from nautilus_trader.config import BacktestEngineConfig, StrategyConfig
        from nautilus_trader.model.currencies import USD
        from nautilus_trader.model.data import Bar, BarSpecification, BarType
        from nautilus_trader.model.enums import (
            AccountType,
            AggregationSource,
            BarAggregation,
            OmsType,
            OrderSide,
            PriceType,
            TimeInForce,
        )
        from nautilus_trader.model.identifiers import InstrumentId, TraderId, Venue
        from nautilus_trader.model.instruments import Instrument
        from nautilus_trader.model.objects import Money
        from nautilus_trader.model.orders import MarketOrder
        from nautilus_trader.persistence.wranglers import BarDataWrangler
        from nautilus_trader.test_kit.providers import TestInstrumentProvider
        from nautilus_trader.trading.strategy import Strategy

        class BuyAndHoldConfig(StrategyConfig, frozen=True):
            instrument_id: InstrumentId
            bar_type: BarType
            trade_size: Decimal

        class BuyAndHoldStrategy(Strategy):
            def __init__(self, config: BuyAndHoldConfig) -> None:
                """Initialize with the buy-and-hold configuration."""
                super().__init__(config)
                self.instrument: Instrument | None = None
                self._entered = False

            def on_start(self) -> None:
                """Resolve the instrument and subscribe to bar data."""
                self.instrument = self.cache.instrument(self.config.instrument_id)
                if self.instrument is None:
                    self.log.error(f"Could not find instrument for {self.config.instrument_id}")
                    self.stop()
                    return
                self.subscribe_bars(self.config.bar_type)

            def on_bar(self, bar: Bar) -> None:
                """Submit a single market buy order on the first valid bar."""
                if bar.is_single_price():
                    return
                if self._entered:
                    return
                if self.instrument is None:
                    return
                order: MarketOrder = self.order_factory.market(
                    instrument_id=self.config.instrument_id,
                    order_side=OrderSide.BUY,
                    quantity=self.instrument.make_qty(self.config.trade_size),
                    time_in_force=TimeInForce.IOC,
                )
                self.submit_order(order)
                self._entered = True

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

        target_weight = float(request.parameters.get("equity_proportions", [1.0])[0])
        first_close = float(price_df["Close"].iloc[0])
        trade_size = max(1, floor((request.initial_cash * target_weight) / first_close))

        strategy = BuyAndHoldStrategy(
            BuyAndHoldConfig(
                instrument_id=instrument.id,
                bar_type=bar_type,
                trade_size=Decimal(str(trade_size)),
            )
        )
        engine.add_strategy(strategy)
        engine.run()
        engine.get_result()

        cash_after_entry = float(request.initial_cash - (trade_size * first_close))
        equity_curve = (price_df["Close"].astype(float) * trade_size) + cash_after_entry
        ending_value = float(equity_curve.iloc[-1])
        roi = (ending_value / request.initial_cash) - 1.0 if request.initial_cash > 0 else 0.0

        days = max((price_df.index[-1] - price_df.index[0]).days, 1)
        years = max(days / 365.25, 1 / 365.25)
        cagr = (ending_value / request.initial_cash) ** (1 / years) - 1 if request.initial_cash > 0 else 0.0

        running_peak = equity_curve.cummax()
        drawdown_series = (equity_curve / running_peak) - 1.0
        max_drawdown = float(drawdown_series.min())

        returns = equity_curve.pct_change().dropna()
        sharpe = 0.0
        if not returns.empty:
            std = float(returns.std())
            if std > 0:
                sharpe = float((returns.mean() / std) * (252**0.5))

        metrics = {
            "starting_value": self._finite_or_default(request.initial_cash, 0.0),
            "ending_value": self._finite_or_default(ending_value, request.initial_cash),
            "roi": self._finite_or_default(roi, 0.0),
            "cagr": self._finite_or_default(cagr, 0.0),
            "sharpe": self._finite_or_default(sharpe, 0.0),
            "max_drawdown": self._finite_or_default(max_drawdown, 0.0),
            "mean_cash_utilization": self._finite_or_default(1.0 - (cash_after_entry / request.initial_cash), 0.0),
        }
        assumptions = {
            "symbols": list(request.symbols),
            "parameters": deepcopy(request.parameters),
            "nautilus_strategy": "BuyAndHoldStrategy",
            "nautilus_strategy_mapping": "norebalance_request_mapped_to_buy_and_hold",
            "nautilus_trade_size": trade_size,
            "strategy_equivalent": True,
            "equivalence_notes": "Single-symbol NoRebalance maps to one-time market buy and hold.",
            "confidence": "high",
        }
        artifacts = {"nautilus_instrument_id": str(instrument.id), "nautilus_venue": venue_id}
        run_warnings: tuple[str, ...] = ()
        return metrics, assumptions, artifacts, run_warnings

    def _run_via_nautilus_dual_momentum(
        self, request: BacktestRunRequest
    ) -> tuple[dict[str, float], dict[str, Any], dict[str, str], tuple[str, ...]]:
        """Run a dual momentum backtest, trying native Nautilus then falling back to proxy.

        Args:
            request: The backtest run request (must have exactly two symbols).

        Returns:
            A tuple of (metrics, assumptions, artifacts, warnings).
        """
        try:
            return self._run_via_nautilus_dual_momentum_native(request)
        except ImportError:
            metrics, assumptions, artifacts, run_warnings = self._run_via_nautilus_dual_momentum_proxy(request)
            return (
                metrics,
                assumptions,
                artifacts,
                (
                    *run_warnings,
                    "Full native GS-02 path unavailable (nautilus_trader import missing); using proxy-native mode.",
                ),
            )
        except Exception as exc:
            metrics, assumptions, artifacts, run_warnings = self._run_via_nautilus_dual_momentum_proxy(request)
            return (
                metrics,
                assumptions,
                artifacts,
                (
                    *run_warnings,
                    f"Full native GS-02 path failed; fell back to proxy-native mode: {type(exc).__name__}:{exc}",
                ),
            )

    def _run_via_nautilus_dual_momentum_native(  # noqa: C901
        self, request: BacktestRunRequest
    ) -> tuple[dict[str, float], dict[str, Any], dict[str, str], tuple[str, ...]]:
        """Execute dual momentum via full native Nautilus strategy hooks.

        Args:
            request: The backtest run request (must have exactly two symbols).

        Returns:
            A tuple of (metrics, assumptions, artifacts, warnings).

        Raises:
            ImportError: If nautilus_trader is not installed.
            ValueError: If the request does not contain exactly two symbols.
        """
        if len(request.symbols) != 2:
            raise ValueError("DualMomentum native mode requires exactly 2 symbols.")
        dual_symbols: tuple[str, str] = (request.symbols[0], request.symbols[1])

        from decimal import Decimal

        from nautilus_trader.backtest.engine import BacktestEngine as NautilusBacktestEngine
        from nautilus_trader.config import BacktestEngineConfig, StrategyConfig
        from nautilus_trader.model.currencies import USD
        from nautilus_trader.model.data import Bar, BarSpecification, BarType
        from nautilus_trader.model.enums import (
            AccountType,
            AggregationSource,
            BarAggregation,
            OmsType,
            OrderSide,
            PriceType,
            TimeInForce,
        )
        from nautilus_trader.model.identifiers import InstrumentId, TraderId, Venue
        from nautilus_trader.model.instruments import Instrument
        from nautilus_trader.model.objects import Money
        from nautilus_trader.model.orders import MarketOrder
        from nautilus_trader.persistence.wranglers import BarDataWrangler
        from nautilus_trader.test_kit.providers import TestInstrumentProvider
        from nautilus_trader.trading.strategy import Strategy

        class DualMomentumNativeConfig(StrategyConfig, frozen=True):
            instrument_ids: tuple[InstrumentId, InstrumentId]
            bar_types: tuple[BarType, BarType]
            lookback: int
            rebal_interval: int
            initial_cash: float

        class DualMomentumNativeStrategy(Strategy):
            def __init__(self, config: DualMomentumNativeConfig) -> None:
                """Initialize dual momentum state tracking for two instruments."""
                super().__init__(config)
                self._instruments: dict[InstrumentId, Instrument] = {}
                self._symbol_lookup: dict[InstrumentId, str] = {}
                self._closes: dict[str, list[float]] = {}
                self._cash = float(config.initial_cash)
                self._shares: dict[str, int] = {}
                self._periods_elapsed = 0
                self._active_symbol: str | None = None
                self._equity_points: list[tuple[pd.Timestamp, float]] = []
                self._cash_points: list[tuple[pd.Timestamp, float]] = []
                self._venue = config.instrument_ids[0].venue
                self._ordered_symbols: tuple[str, str] = ("", "")
                self._pending_closes: dict[int, dict[str, float]] = {}

            @staticmethod
            def _price_as_float(price_obj: Any) -> float:
                """Convert a Nautilus price object to a plain float."""
                as_double = getattr(price_obj, "as_double", None)
                if callable(as_double):
                    return float(as_double())
                return float(price_obj)

            def on_start(self) -> None:
                """Resolve instruments, build symbol lookups, and subscribe to bars."""
                for instrument_id in self.config.instrument_ids:
                    instrument = self.cache.instrument(instrument_id)
                    if instrument is None:
                        self.log.error(f"Could not find instrument for {instrument_id}")
                        self.stop()
                        return
                    self._instruments[instrument_id] = instrument
                    symbol = str(instrument_id).split(".")[0]
                    self._symbol_lookup[instrument_id] = symbol
                    self._closes[symbol] = []
                    self._shares[symbol] = 0
                self._ordered_symbols = (
                    self._symbol_lookup[self.config.instrument_ids[0]],
                    self._symbol_lookup[self.config.instrument_ids[1]],
                )
                for bar_type in self.config.bar_types:
                    self.subscribe_bars(bar_type)

            def _submit_market(self, instrument_id: InstrumentId, side: OrderSide, quantity: int) -> None:
                """Submit an IOC market order for the given instrument and quantity."""
                if quantity <= 0:
                    return
                instrument = self._instruments[instrument_id]
                order: MarketOrder = self.order_factory.market(
                    instrument_id=instrument_id,
                    order_side=side,
                    quantity=instrument.make_qty(Decimal(str(quantity))),
                    time_in_force=TimeInForce.IOC,
                )
                self.submit_order(order)

            def _record_equity_point(self, *, timestamp: pd.Timestamp, symbols: tuple[str, str]) -> None:
                """Record a portfolio equity and cash data point at the given timestamp."""
                native_equity: float | None = None
                total_pnls = getattr(self.portfolio, "total_pnls", None)
                if callable(total_pnls):
                    try:
                        pnl_payload = total_pnls(self._venue)
                    except (RuntimeError, TypeError, ValueError):
                        pnl_payload = None
                    pnl_value = NautilusAdapter._coerce_nautilus_total_pnl(pnl_payload)
                    if pnl_value is not None:
                        native_equity = float(self.config.initial_cash) + pnl_value

                if native_equity is None:
                    native_equity = float(self._cash) + sum(
                        float(self._shares[symbol]) * float(self._closes[symbol][-1])
                        for symbol in symbols
                        if self._closes[symbol]
                    )

                self._equity_points.append((timestamp, native_equity))
                self._cash_points.append((timestamp, max(float(self._cash), 0.0)))

            def native_curves(self) -> tuple[pd.Series, pd.Series]:
                """Return the accumulated equity and cash curves as pd.Series."""
                return (
                    NautilusAdapter._series_from_points(self._equity_points),
                    NautilusAdapter._series_from_points(self._cash_points),
                )

            def on_bar(self, bar: Bar) -> None:  # noqa: C901
                """Process a bar event, synchronize multi-symbol closes, and rebalance."""
                if bar.is_single_price():
                    return

                instrument_id = bar.bar_type.instrument_id
                symbol = self._symbol_lookup.get(instrument_id)
                if symbol is None:
                    return
                close_value = self._price_as_float(bar.close)
                bar_timestamp = NautilusAdapter._coerce_nautilus_timestamp(getattr(bar, "ts_event", None))
                ts_ns = int(bar_timestamp.value)
                pending_for_ts = self._pending_closes.setdefault(ts_ns, {})
                pending_for_ts[symbol] = close_value
                if len(pending_for_ts) < len(self.config.instrument_ids):
                    return

                primary_symbol, alt_symbol = self._ordered_symbols
                snapshot = self._pending_closes.pop(ts_ns)
                for synced_symbol in (primary_symbol, alt_symbol):
                    synced_price = snapshot.get(synced_symbol)
                    if synced_price is None:
                        return
                    self._closes[synced_symbol].append(float(synced_price))

                can_rebalance = (
                    len(self._closes[primary_symbol]) > self.config.lookback
                    and len(self._closes[alt_symbol]) > self.config.lookback
                )
                if can_rebalance:
                    self._periods_elapsed += 1
                    if self._periods_elapsed < self.config.rebal_interval:
                        self._record_equity_point(timestamp=bar_timestamp, symbols=(primary_symbol, alt_symbol))
                        return
                    self._periods_elapsed = 0

                    primary_now = self._closes[primary_symbol][-1]
                    primary_then = self._closes[primary_symbol][-1 - self.config.lookback]
                    alt_now = self._closes[alt_symbol][-1]
                    alt_then = self._closes[alt_symbol][-1 - self.config.lookback]

                    primary_mom = (primary_now - primary_then) / primary_then if primary_then > 0 else -1.0
                    alt_mom = (alt_now - alt_then) / alt_then if alt_then > 0 else -1.0

                    target_symbol: str | None = None
                    if primary_mom > 0 and primary_mom >= alt_mom:
                        target_symbol = primary_symbol
                    elif alt_mom > 0:
                        target_symbol = alt_symbol

                    if target_symbol != self._active_symbol:
                        for idx, held_symbol in enumerate((primary_symbol, alt_symbol)):
                            held_qty = self._shares[held_symbol]
                            if held_qty <= 0:
                                continue
                            held_id = self.config.instrument_ids[idx]
                            held_price = self._closes[held_symbol][-1]
                            self._submit_market(held_id, OrderSide.SELL, held_qty)
                            self._shares[held_symbol] = 0
                            self._cash += held_qty * held_price

                        self._active_symbol = target_symbol
                        if target_symbol is not None:
                            target_idx = 0 if target_symbol == primary_symbol else 1
                            target_id = self.config.instrument_ids[target_idx]
                            target_price = self._closes[target_symbol][-1]
                            buy_qty = int(self._cash // target_price) if target_price > 0 else 0
                            if buy_qty > 0:
                                self._submit_market(target_id, OrderSide.BUY, buy_qty)
                                self._shares[target_symbol] = buy_qty
                                self._cash -= buy_qty * target_price

                self._record_equity_point(timestamp=bar_timestamp, symbols=(primary_symbol, alt_symbol))

        price_histories = self._select_native_price_histories(request.symbols, request.start, request.end)
        lookback = int(request.parameters.get("lookback", 252))
        rebal_interval = int(request.parameters.get("rebal_interval", 21))

        venue_id = "XNAS"
        trader_id = TraderId("FINBOT-NT-001")
        venue = Venue(venue_id)
        instruments = [TestInstrumentProvider.equity(symbol, venue_id) for symbol in dual_symbols]

        engine = NautilusBacktestEngine(config=BacktestEngineConfig(trader_id=trader_id))
        engine.add_venue(
            venue=venue,
            oms_type=OmsType.NETTING,
            account_type=AccountType.CASH,
            base_currency=USD,
            starting_balances=[Money(request.initial_cash, USD)],
        )
        bar_types: list[BarType] = []
        for symbol, instrument in zip(dual_symbols, instruments, strict=True):
            engine.add_instrument(instrument)
            bar_spec = BarSpecification(step=1, aggregation=BarAggregation.DAY, price_type=PriceType.LAST)
            bar_type = BarType(instrument.id, bar_spec, AggregationSource.EXTERNAL)
            bar_types.append(bar_type)
            wrangler = BarDataWrangler(bar_type=bar_type, instrument=instrument)
            bar_data = wrangler.process(self._to_nautilus_dataframe(price_histories[symbol]))
            engine.add_data(bar_data)

        strategy = DualMomentumNativeStrategy(
            DualMomentumNativeConfig(
                instrument_ids=(instruments[0].id, instruments[1].id),
                bar_types=(bar_types[0], bar_types[1]),
                lookback=lookback,
                rebal_interval=rebal_interval,
                initial_cash=request.initial_cash,
            )
        )
        engine.add_strategy(strategy)
        engine.run()
        engine.get_result()

        equity_curve, cash_curve = strategy.native_curves()
        run_warnings: list[str] = []
        if equity_curve.empty:
            prices = self._build_aligned_close_frame(price_histories)
            equity_curve, cash_curve = self._simulate_dual_momentum_portfolio(
                prices=prices,
                symbols=dual_symbols,
                initial_cash=request.initial_cash,
                lookback=lookback,
                rebal_interval=rebal_interval,
            )
            run_warnings.append(
                "Full-native GS-02 valuation samples unavailable; used deterministic mark-to-market valuation fallback."
            )

        metrics = self._build_metrics_from_equity_curve(
            equity_curve=equity_curve,
            cash_curve=cash_curve if not cash_curve.empty else None,
            initial_cash=request.initial_cash,
        )
        assumptions = {
            "symbols": list(request.symbols),
            "parameters": deepcopy(request.parameters),
            "nautilus_strategy": "DualMomentumNativeStrategy",
            "nautilus_strategy_mapping": "dualmomentum_request_mapped_to_full_native_nautilus_strategy",
            "strategy_equivalent": False,
            "equivalence_notes": (
                "DualMomentum executed with native Nautilus strategy hooks; benchmark metrics are derived from "
                "native mark-to-market portfolio valuation sampled on synchronized multi-symbol daily bars."
            ),
            "confidence": "low",
            "adapter_mode": "native_nautilus_full",
            "execution_fidelity": "full_native",
            "valuation_fidelity": "native_mark_to_market",
            "metric_source": "nautilus_portfolio_total_pnl_primary_bar",
        }
        artifacts = {"nautilus_symbols": ",".join(dual_symbols), "nautilus_strategy_impl": "full_native"}
        return metrics, assumptions, artifacts, tuple(run_warnings)

    def _run_via_nautilus_dual_momentum_proxy(
        self, request: BacktestRunRequest
    ) -> tuple[dict[str, float], dict[str, Any], dict[str, str], tuple[str, ...]]:
        """Execute dual momentum via deterministic proxy simulation without Nautilus.

        Args:
            request: The backtest run request (must have exactly two symbols).

        Returns:
            A tuple of (metrics, assumptions, artifacts, warnings).
        """
        if len(request.symbols) != 2:
            raise ValueError("DualMomentum proxy mode requires exactly 2 symbols.")
        dual_symbols: tuple[str, str] = (request.symbols[0], request.symbols[1])

        price_histories = self._select_native_price_histories(request.symbols, request.start, request.end)
        prices = self._build_aligned_close_frame(price_histories)

        lookback = int(request.parameters.get("lookback", 252))
        rebal_interval = int(request.parameters.get("rebal_interval", 21))
        equity_curve, cash_curve = self._simulate_dual_momentum_portfolio(
            prices=prices,
            symbols=dual_symbols,
            initial_cash=request.initial_cash,
            lookback=lookback,
            rebal_interval=rebal_interval,
        )
        metrics = self._build_metrics_from_equity_curve(
            equity_curve=equity_curve,
            cash_curve=cash_curve,
            initial_cash=request.initial_cash,
        )
        assumptions = {
            "symbols": list(request.symbols),
            "parameters": deepcopy(request.parameters),
            "nautilus_strategy": "DualMomentumProxy",
            "nautilus_strategy_mapping": "dualmomentum_request_mapped_to_deterministic_pilot_proxy",
            "strategy_equivalent": True,
            "equivalence_notes": (
                "DualMomentum signal/rebalance logic mirrored from Backtrader strategy with deterministic close-price "
                "fills and integer share sizing."
            ),
            "confidence": "medium",
            "adapter_mode": "native_nautilus_proxy",
            "execution_fidelity": "proxy_native",
        }
        artifacts = {"nautilus_symbols": ",".join(dual_symbols), "nautilus_proxy_type": "dual_momentum"}
        run_warnings = (
            "GS-02 currently uses deterministic pilot proxy execution rather than full Nautilus order lifecycle modeling.",
        )
        return metrics, assumptions, artifacts, run_warnings

    def _run_via_nautilus_risk_parity(
        self, request: BacktestRunRequest
    ) -> tuple[dict[str, float], dict[str, Any], dict[str, str], tuple[str, ...]]:
        """Run a risk parity backtest, trying native Nautilus then falling back to proxy.

        Args:
            request: The backtest run request (must have at least two symbols).

        Returns:
            A tuple of (metrics, assumptions, artifacts, warnings).
        """
        try:
            return self._run_via_nautilus_risk_parity_native(request)
        except ImportError:
            metrics, assumptions, artifacts, run_warnings = self._run_via_nautilus_risk_parity_proxy(request)
            return (
                metrics,
                assumptions,
                artifacts,
                (
                    *run_warnings,
                    "Full native GS-03 path unavailable (nautilus_trader import missing); using proxy-native mode.",
                ),
            )
        except Exception as exc:
            metrics, assumptions, artifacts, run_warnings = self._run_via_nautilus_risk_parity_proxy(request)
            return (
                metrics,
                assumptions,
                artifacts,
                (
                    *run_warnings,
                    f"Full native GS-03 path failed; fell back to proxy-native mode: {type(exc).__name__}:{exc}",
                ),
            )

    def _run_via_nautilus_risk_parity_native(  # noqa: C901
        self, request: BacktestRunRequest
    ) -> tuple[dict[str, float], dict[str, Any], dict[str, str], tuple[str, ...]]:
        """Execute risk parity via full native Nautilus strategy hooks.

        Args:
            request: The backtest run request (must have at least two symbols).

        Returns:
            A tuple of (metrics, assumptions, artifacts, warnings).

        Raises:
            ImportError: If nautilus_trader is not installed.
        """
        from decimal import Decimal

        from nautilus_trader.backtest.engine import BacktestEngine as NautilusBacktestEngine
        from nautilus_trader.config import BacktestEngineConfig, StrategyConfig
        from nautilus_trader.model.currencies import USD
        from nautilus_trader.model.data import Bar, BarSpecification, BarType
        from nautilus_trader.model.enums import (
            AccountType,
            AggregationSource,
            BarAggregation,
            OmsType,
            OrderSide,
            PriceType,
            TimeInForce,
        )
        from nautilus_trader.model.identifiers import InstrumentId, TraderId, Venue
        from nautilus_trader.model.instruments import Instrument
        from nautilus_trader.model.objects import Money
        from nautilus_trader.model.orders import MarketOrder
        from nautilus_trader.persistence.wranglers import BarDataWrangler
        from nautilus_trader.test_kit.providers import TestInstrumentProvider
        from nautilus_trader.trading.strategy import Strategy

        class RiskParityNativeConfig(StrategyConfig, frozen=True):
            instrument_ids: tuple[InstrumentId, ...]
            bar_types: tuple[BarType, ...]
            symbols: tuple[str, ...]
            vol_window: int
            rebal_interval: int
            initial_cash: float

        class RiskParityNativeStrategy(Strategy):
            def __init__(self, config: RiskParityNativeConfig) -> None:
                """Initialize risk parity state tracking for multiple instruments."""
                super().__init__(config)
                self._instruments: dict[InstrumentId, Instrument] = {}
                self._symbol_lookup: dict[InstrumentId, str] = {}
                self._closes: dict[str, list[float]] = {symbol: [] for symbol in config.symbols}
                self._returns: dict[str, list[float]] = {symbol: [] for symbol in config.symbols}
                self._cash = float(config.initial_cash)
                self._shares: dict[str, int] = dict.fromkeys(config.symbols, 0)
                self._periods_elapsed = 0
                self._equity_points: list[tuple[pd.Timestamp, float]] = []
                self._cash_points: list[tuple[pd.Timestamp, float]] = []
                self._venue = config.instrument_ids[0].venue
                self._ordered_symbols: tuple[str, ...] = ()
                self._pending_closes: dict[int, dict[str, float]] = {}

            @staticmethod
            def _price_as_float(price_obj: Any) -> float:
                """Convert a Nautilus price object to a plain float."""
                as_double = getattr(price_obj, "as_double", None)
                if callable(as_double):
                    return float(as_double())
                return float(price_obj)

            def on_start(self) -> None:
                """Resolve instruments, build symbol lookups, and subscribe to bars."""
                for instrument_id in self.config.instrument_ids:
                    instrument = self.cache.instrument(instrument_id)
                    if instrument is None:
                        self.log.error(f"Could not find instrument for {instrument_id}")
                        self.stop()
                        return
                    self._instruments[instrument_id] = instrument
                    symbol = str(instrument_id).split(".")[0]
                    self._symbol_lookup[instrument_id] = symbol
                self._ordered_symbols = tuple(
                    self._symbol_lookup[instrument_id] for instrument_id in self.config.instrument_ids
                )
                for bar_type in self.config.bar_types:
                    self.subscribe_bars(bar_type)

            def _submit_market(self, instrument_id: InstrumentId, side: OrderSide, quantity: int) -> None:
                """Submit an IOC market order for the given instrument and quantity."""
                if quantity <= 0:
                    return
                instrument = self._instruments[instrument_id]
                order: MarketOrder = self.order_factory.market(
                    instrument_id=instrument_id,
                    order_side=side,
                    quantity=instrument.make_qty(Decimal(str(quantity))),
                    time_in_force=TimeInForce.IOC,
                )
                self.submit_order(order)

            def _record_equity_point(self, *, timestamp: pd.Timestamp) -> None:
                """Record a portfolio equity and cash data point at the given timestamp."""
                native_equity: float | None = None
                total_pnls = getattr(self.portfolio, "total_pnls", None)
                if callable(total_pnls):
                    try:
                        pnl_payload = total_pnls(self._venue)
                    except (RuntimeError, TypeError, ValueError):
                        pnl_payload = None
                    pnl_value = NautilusAdapter._coerce_nautilus_total_pnl(pnl_payload)
                    if pnl_value is not None:
                        native_equity = float(self.config.initial_cash) + pnl_value

                if native_equity is None:
                    native_equity = float(self._cash) + sum(
                        float(self._shares[symbol]) * float(self._closes[symbol][-1])
                        for symbol in self.config.symbols
                        if self._closes[symbol]
                    )

                self._equity_points.append((timestamp, native_equity))
                self._cash_points.append((timestamp, max(float(self._cash), 0.0)))

            def native_curves(self) -> tuple[pd.Series, pd.Series]:
                """Return the accumulated equity and cash curves as pd.Series."""
                return (
                    NautilusAdapter._series_from_points(self._equity_points),
                    NautilusAdapter._series_from_points(self._cash_points),
                )

            def on_bar(self, bar: Bar) -> None:  # noqa: C901
                """Process a bar event, synchronize multi-symbol closes, and rebalance."""
                if bar.is_single_price():
                    return

                instrument_id = bar.bar_type.instrument_id
                symbol = self._symbol_lookup.get(instrument_id)
                if symbol is None:
                    return
                close_value = float(self._price_as_float(bar.close))
                bar_timestamp = NautilusAdapter._coerce_nautilus_timestamp(getattr(bar, "ts_event", None))
                ts_ns = int(bar_timestamp.value)
                pending_for_ts = self._pending_closes.setdefault(ts_ns, {})
                pending_for_ts[symbol] = close_value
                if len(pending_for_ts) < len(self.config.instrument_ids):
                    return

                snapshot = self._pending_closes.pop(ts_ns)
                for synced_symbol in self._ordered_symbols:
                    synced_price = snapshot.get(synced_symbol)
                    if synced_price is None:
                        return
                    close_series = self._closes[synced_symbol]
                    if close_series:
                        prev_close = close_series[-1]
                        if prev_close > 0:
                            self._returns[synced_symbol].append((float(synced_price) - prev_close) / prev_close)
                    close_series.append(float(synced_price))

                can_rebalance = (
                    min(len(self._returns[symbol]) for symbol in self.config.symbols) >= self.config.vol_window
                )
                if can_rebalance:
                    self._periods_elapsed += 1
                    if self._periods_elapsed < self.config.rebal_interval:
                        self._record_equity_point(timestamp=bar_timestamp)
                        return
                    self._periods_elapsed = 0

                    inv_vols: dict[str, float] = {}
                    for loop_symbol in self.config.symbols:
                        window = self._returns[loop_symbol][-self.config.vol_window :]
                        vol = float(pd.Series(window).std(ddof=0))
                        inv_vols[loop_symbol] = 1.0 / vol if vol > 0 else 0.0

                    total_inv = sum(inv_vols.values())
                    if total_inv <= 0:
                        target_weights = {
                            loop_symbol: 1.0 / len(self.config.symbols) for loop_symbol in self.config.symbols
                        }
                    else:
                        target_weights = {
                            loop_symbol: inv_vols[loop_symbol] / total_inv for loop_symbol in self.config.symbols
                        }

                    total_value = self._cash + sum(
                        self._shares[loop_symbol] * self._closes[loop_symbol][-1] for loop_symbol in self.config.symbols
                    )

                    for loop_id in self.config.instrument_ids:
                        loop_symbol = self._symbol_lookup[loop_id]
                        price = self._closes[loop_symbol][-1]
                        current_value = self._shares[loop_symbol] * price
                        target_value = target_weights[loop_symbol] * total_value
                        sell_qty = int((current_value - target_value) // price)
                        sell_qty = min(max(sell_qty, 0), self._shares[loop_symbol])
                        if sell_qty > 0:
                            self._submit_market(loop_id, OrderSide.SELL, sell_qty)
                            self._shares[loop_symbol] -= sell_qty
                            self._cash += sell_qty * price

                    for loop_id in self.config.instrument_ids:
                        loop_symbol = self._symbol_lookup[loop_id]
                        price = self._closes[loop_symbol][-1]
                        current_value = self._shares[loop_symbol] * price
                        target_value = target_weights[loop_symbol] * total_value
                        buy_qty = int((target_value - current_value) // price)
                        max_affordable = int(self._cash // price)
                        buy_qty = min(max(buy_qty, 0), max_affordable)
                        if buy_qty > 0:
                            self._submit_market(loop_id, OrderSide.BUY, buy_qty)
                            self._shares[loop_symbol] += buy_qty
                            self._cash -= buy_qty * price

                self._record_equity_point(timestamp=bar_timestamp)

        price_histories = self._select_native_price_histories(request.symbols, request.start, request.end)
        vol_window = int(request.parameters.get("vol_window", 63))
        rebal_interval = int(request.parameters.get("rebal_interval", 21))

        venue_id = "XNAS"
        trader_id = TraderId("FINBOT-NT-001")
        venue = Venue(venue_id)
        instruments = [TestInstrumentProvider.equity(symbol, venue_id) for symbol in request.symbols]

        engine = NautilusBacktestEngine(config=BacktestEngineConfig(trader_id=trader_id))
        engine.add_venue(
            venue=venue,
            oms_type=OmsType.NETTING,
            account_type=AccountType.CASH,
            base_currency=USD,
            starting_balances=[Money(request.initial_cash, USD)],
        )

        bar_types: list[BarType] = []
        for symbol, instrument in zip(request.symbols, instruments, strict=True):
            engine.add_instrument(instrument)
            bar_spec = BarSpecification(step=1, aggregation=BarAggregation.DAY, price_type=PriceType.LAST)
            bar_type = BarType(instrument.id, bar_spec, AggregationSource.EXTERNAL)
            bar_types.append(bar_type)
            wrangler = BarDataWrangler(bar_type=bar_type, instrument=instrument)
            bar_data = wrangler.process(self._to_nautilus_dataframe(price_histories[symbol]))
            engine.add_data(bar_data)

        strategy = RiskParityNativeStrategy(
            RiskParityNativeConfig(
                instrument_ids=tuple(instrument.id for instrument in instruments),
                bar_types=tuple(bar_types),
                symbols=request.symbols,
                vol_window=vol_window,
                rebal_interval=rebal_interval,
                initial_cash=request.initial_cash,
            )
        )
        engine.add_strategy(strategy)
        engine.run()
        engine.get_result()

        equity_curve, cash_curve = strategy.native_curves()
        run_warnings: list[str] = []
        if equity_curve.empty:
            prices = self._build_aligned_close_frame(price_histories)
            equity_curve, cash_curve = self._simulate_risk_parity_portfolio(
                prices=prices,
                symbols=request.symbols,
                initial_cash=request.initial_cash,
                vol_window=vol_window,
                rebal_interval=rebal_interval,
            )
            run_warnings.append(
                "Full-native GS-03 valuation samples unavailable; used deterministic mark-to-market valuation fallback."
            )

        metrics = self._build_metrics_from_equity_curve(
            equity_curve=equity_curve,
            cash_curve=cash_curve if not cash_curve.empty else None,
            initial_cash=request.initial_cash,
        )
        assumptions = {
            "symbols": list(request.symbols),
            "parameters": deepcopy(request.parameters),
            "nautilus_strategy": "RiskParityNativeStrategy",
            "nautilus_strategy_mapping": "riskparity_request_mapped_to_full_native_nautilus_strategy",
            "strategy_equivalent": False,
            "equivalence_notes": (
                "RiskParity executed with native Nautilus strategy hooks; benchmark metrics are derived from "
                "native mark-to-market portfolio valuation sampled on synchronized multi-symbol daily bars."
            ),
            "confidence": "low",
            "adapter_mode": "native_nautilus_full",
            "execution_fidelity": "full_native",
            "valuation_fidelity": "native_mark_to_market",
            "metric_source": "nautilus_portfolio_total_pnl_primary_bar",
        }
        artifacts = {"nautilus_symbols": ",".join(request.symbols), "nautilus_strategy_impl": "full_native"}
        return metrics, assumptions, artifacts, tuple(run_warnings)

    def _run_via_nautilus_risk_parity_proxy(
        self, request: BacktestRunRequest
    ) -> tuple[dict[str, float], dict[str, Any], dict[str, str], tuple[str, ...]]:
        """Execute risk parity via deterministic proxy simulation without Nautilus.

        Args:
            request: The backtest run request (must have at least two symbols).

        Returns:
            A tuple of (metrics, assumptions, artifacts, warnings).
        """
        price_histories = self._select_native_price_histories(request.symbols, request.start, request.end)
        prices = self._build_aligned_close_frame(price_histories)

        vol_window = int(request.parameters.get("vol_window", 63))
        rebal_interval = int(request.parameters.get("rebal_interval", 21))
        equity_curve, cash_curve = self._simulate_risk_parity_portfolio(
            prices=prices,
            symbols=request.symbols,
            initial_cash=request.initial_cash,
            vol_window=vol_window,
            rebal_interval=rebal_interval,
        )
        metrics = self._build_metrics_from_equity_curve(
            equity_curve=equity_curve,
            cash_curve=cash_curve,
            initial_cash=request.initial_cash,
        )
        assumptions = {
            "symbols": list(request.symbols),
            "parameters": deepcopy(request.parameters),
            "nautilus_strategy": "RiskParityProxy",
            "nautilus_strategy_mapping": "riskparity_request_mapped_to_deterministic_pilot_proxy",
            "strategy_equivalent": True,
            "equivalence_notes": (
                "RiskParity rebalance and inverse-volatility weighting mirrored from Backtrader strategy with "
                "deterministic close-price fills and integer share sizing."
            ),
            "confidence": "medium",
            "adapter_mode": "native_nautilus_proxy",
            "execution_fidelity": "proxy_native",
        }
        artifacts = {"nautilus_symbols": ",".join(request.symbols), "nautilus_proxy_type": "risk_parity"}
        run_warnings = (
            "GS-03 currently uses deterministic pilot proxy execution rather than full Nautilus order lifecycle modeling.",
        )
        return metrics, assumptions, artifacts, run_warnings

    def _compute_risk_parity_target_weights(
        self,
        *,
        returns: dict[str, list[float]],
        symbols: tuple[str, ...],
        vol_window: int,
    ) -> dict[str, float]:
        """Compute inverse-volatility target weights for risk parity allocation.

        Args:
            returns: Mapping of symbol to list of historical return values.
            symbols: Tuple of symbol names to compute weights for.
            vol_window: Number of recent returns to use for volatility estimation.

        Returns:
            Mapping of symbol to target weight (sums to 1.0).
        """
        inv_vols: dict[str, float] = {}
        for symbol in symbols:
            window = returns[symbol][-vol_window:]
            vol = float(pd.Series(window).std(ddof=0))
            inv_vols[symbol] = 1.0 / vol if vol > 0 else 0.0

        total_inv = sum(inv_vols.values())
        if total_inv <= 0:
            return {symbol: 1.0 / len(symbols) for symbol in symbols}
        return {symbol: inv_vols[symbol] / total_inv for symbol in symbols}

    def _rebalance_risk_parity_positions(
        self,
        *,
        symbols: tuple[str, ...],
        prices_row: pd.Series,
        shares: dict[str, int],
        cash: float,
        target_weights: dict[str, float],
    ) -> float:
        """Rebalance positions toward target weights by selling then buying.

        Args:
            symbols: Tuple of symbol names.
            prices_row: Current prices as a pandas Series indexed by symbol.
            shares: Mutable mapping of symbol to share count (updated in place).
            cash: Available cash before rebalancing.
            target_weights: Mapping of symbol to target portfolio weight.

        Returns:
            Updated cash balance after rebalancing.
        """
        total_value = cash + sum(shares[symbol] * float(prices_row[symbol]) for symbol in symbols)

        for symbol in symbols:
            price = float(prices_row[symbol])
            current_value = shares[symbol] * price
            target_value = target_weights[symbol] * total_value
            sell_shares = int((current_value - target_value) // price)
            sell_shares = min(max(sell_shares, 0), shares[symbol])
            if sell_shares > 0:
                shares[symbol] -= sell_shares
                cash += sell_shares * price

        for symbol in symbols:
            price = float(prices_row[symbol])
            current_value = shares[symbol] * price
            target_value = target_weights[symbol] * total_value
            buy_shares = int((target_value - current_value) // price)
            max_affordable = int(cash // price)
            buy_shares = min(max(buy_shares, 0), max_affordable)
            if buy_shares > 0:
                shares[symbol] += buy_shares
                cash -= buy_shares * price

        return cash

    def _build_config_hash(self, request: BacktestRunRequest) -> str:
        """Build a deterministic hash of the adapter configuration and request."""
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
        """Select and validate a single symbol's price history for the date range.

        Args:
            symbol: The ticker symbol to look up.
            start: Optional inclusive start date filter.
            end: Optional inclusive end date filter.

        Returns:
            Validated OHLCV DataFrame filtered to the requested date range.

        Raises:
            ValueError: If the symbol is missing or has fewer than 40 bars.
        """
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

    def _select_native_price_histories(
        self,
        symbols: tuple[str, ...],
        start: pd.Timestamp | None,
        end: pd.Timestamp | None,
    ) -> dict[str, pd.DataFrame]:
        """Select and validate price histories for multiple symbols.

        Args:
            symbols: Tuple of ticker symbols to look up.
            start: Optional inclusive start date filter.
            end: Optional inclusive end date filter.

        Returns:
            Mapping of symbol to validated, date-filtered OHLCV DataFrame.
        """
        histories: dict[str, pd.DataFrame] = {}
        for symbol in symbols:
            histories[symbol] = self._select_native_price_history(symbol=symbol, start=start, end=end)
        return histories

    def _build_aligned_close_frame(self, price_histories: dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Build a date-aligned DataFrame of close prices across all symbols.

        Args:
            price_histories: Mapping of symbol to OHLCV DataFrames.

        Returns:
            DataFrame with symbols as columns and aligned dates as the index.

        Raises:
            ValueError: If fewer than 40 aligned bars exist across all symbols.
        """
        closes = [df["Close"].rename(symbol) for symbol, df in price_histories.items()]
        aligned = pd.concat(closes, axis=1, join="inner").dropna()
        if len(aligned) < 40:
            raise ValueError("Nautilus pilot requires at least 40 aligned bars across selected symbols")
        return aligned

    @staticmethod
    def _coerce_nautilus_timestamp(raw_ts: Any) -> pd.Timestamp:
        """Coerce a Nautilus timestamp (nanoseconds, int, or datetime) to a tz-naive pd.Timestamp."""
        if raw_ts is None:
            return pd.Timestamp.now(tz=UTC).tz_convert(None)

        candidate: Any = raw_ts
        as_int = getattr(raw_ts, "as_int", None)
        if callable(as_int):
            try:
                candidate = int(as_int())
            except (TypeError, ValueError):
                candidate = raw_ts

        if isinstance(candidate, int | float):
            timestamp = pd.to_datetime(int(candidate), unit="ns", utc=True, errors="coerce")
            if pd.notna(timestamp):
                return timestamp.tz_convert(None)

        timestamp = pd.to_datetime(candidate, utc=True, errors="coerce")
        if pd.notna(timestamp):
            return timestamp.tz_convert(None)
        return pd.Timestamp.now(tz=UTC).tz_convert(None)

    @staticmethod
    def _coerce_nautilus_money_value(value: Any) -> float | None:
        """Coerce a Nautilus Money object to a float, returning None on failure."""
        if value is None:
            return None
        as_double = getattr(value, "as_double", None)
        if callable(as_double):
            try:
                return float(as_double())
            except (TypeError, ValueError):
                return None
        as_decimal = getattr(value, "as_decimal", None)
        if callable(as_decimal):
            try:
                return float(as_decimal())
            except (TypeError, ValueError):
                return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def _coerce_nautilus_total_pnl(cls, payload: Any) -> float | None:
        """Coerce a Nautilus total PnL payload (dict or Money) to a summed float."""
        if payload is None:
            return None

        if isinstance(payload, dict):
            values = list(payload.values())
        else:
            payload_values = getattr(payload, "values", None)
            if callable(payload_values):
                try:
                    values = list(payload_values())
                except TypeError:
                    values = []
            else:
                values = []

        if values:
            total = 0.0
            found = False
            for item in values:
                value = cls._coerce_nautilus_money_value(item)
                if value is None:
                    continue
                total += value
                found = True
            if found:
                return total
            return None

        return cls._coerce_nautilus_money_value(payload)

    @staticmethod
    def _series_from_points(points: list[tuple[pd.Timestamp, float]]) -> pd.Series:
        """Convert a list of (timestamp, value) tuples into a deduplicated, sorted pd.Series."""
        if not points:
            return pd.Series(dtype=float)
        index = pd.DatetimeIndex([point[0] for point in points])
        values = [float(point[1]) for point in points]
        series = pd.Series(values, index=index)
        if series.index.has_duplicates:
            series = series.groupby(level=0).last()
        return series.sort_index()

    def _build_metrics_from_equity_curve(
        self,
        *,
        equity_curve: pd.Series,
        initial_cash: float,
        cash_curve: pd.Series | None = None,
    ) -> dict[str, float]:
        """Derive standard backtest metrics from an equity curve.

        Args:
            equity_curve: Time series of portfolio values.
            initial_cash: Starting cash used to compute returns.
            cash_curve: Optional time series of cash balances for utilization.

        Returns:
            Dict of canonical metric keys (starting_value, ending_value, roi,
            cagr, sharpe, max_drawdown, mean_cash_utilization).
        """
        ending_value = float(equity_curve.iloc[-1])
        roi = (ending_value / initial_cash) - 1.0 if initial_cash > 0 else 0.0

        days = max((equity_curve.index[-1] - equity_curve.index[0]).days, 1)
        years = max(days / 365.25, 1 / 365.25)
        cagr = (ending_value / initial_cash) ** (1 / years) - 1 if initial_cash > 0 else 0.0

        running_peak = equity_curve.cummax()
        drawdown_series = (equity_curve / running_peak) - 1.0
        max_drawdown = float(drawdown_series.min())

        returns = equity_curve.pct_change().dropna()
        sharpe = 0.0
        if not returns.empty:
            std = float(returns.std())
            if std > 0:
                sharpe = float((returns.mean() / std) * (252**0.5))

        mean_cash_utilization = self._compute_mean_cash_utilization(equity_curve=equity_curve, cash_curve=cash_curve)

        return {
            "starting_value": self._finite_or_default(initial_cash, 0.0),
            "ending_value": self._finite_or_default(ending_value, initial_cash),
            "roi": self._finite_or_default(roi, 0.0),
            "cagr": self._finite_or_default(cagr, 0.0),
            "sharpe": self._finite_or_default(sharpe, 0.0),
            "max_drawdown": self._finite_or_default(max_drawdown, 0.0),
            "mean_cash_utilization": self._finite_or_default(mean_cash_utilization, 0.0),
        }

    def _compute_mean_cash_utilization(self, *, equity_curve: pd.Series, cash_curve: pd.Series | None) -> float:
        """Compute mean cash utilization as the average fraction of equity deployed.

        Args:
            equity_curve: Time series of portfolio values.
            cash_curve: Optional time series of cash balances.

        Returns:
            Mean utilization ratio between 0.0 and 1.0, or 0.0 if unavailable.
        """
        if cash_curve is None or cash_curve.empty:
            return 0.0
        aligned = pd.concat([equity_curve.rename("equity"), cash_curve.rename("cash")], axis=1).dropna()
        if aligned.empty:
            return 0.0

        valid = aligned["equity"] > 0
        if not bool(valid.any()):
            return 0.0

        utilization = 1.0 - (aligned.loc[valid, "cash"] / aligned.loc[valid, "equity"])
        utilization = utilization.clip(lower=0.0, upper=1.0)
        if utilization.empty:
            return 0.0
        return float(utilization.mean())

    def _simulate_dual_momentum_portfolio(
        self,
        *,
        prices: pd.DataFrame,
        symbols: tuple[str, str],
        initial_cash: float,
        lookback: int,
        rebal_interval: int,
    ) -> tuple[pd.Series, pd.Series]:
        """Simulate a dual momentum portfolio using deterministic close-price fills.

        Args:
            prices: Aligned close-price DataFrame with symbols as columns.
            symbols: Tuple of (primary_symbol, alt_symbol).
            initial_cash: Starting cash balance.
            lookback: Number of periods for momentum calculation.
            rebal_interval: Number of periods between rebalance checks.

        Returns:
            Tuple of (equity_curve, cash_curve) as pd.Series.
        """
        primary_symbol, alt_symbol = symbols
        cash = float(initial_cash)
        shares: dict[str, int] = {primary_symbol: 0, alt_symbol: 0}
        periods_elapsed = 0
        equity_values: list[float] = []
        cash_values: list[float] = []

        for idx in range(len(prices)):
            row = prices.iloc[idx]

            if idx >= lookback:
                periods_elapsed += 1
                if periods_elapsed >= rebal_interval:
                    periods_elapsed = 0
                    primary_base = float(prices.iloc[idx - lookback][primary_symbol])
                    alt_base = float(prices.iloc[idx - lookback][alt_symbol])
                    primary_mom = (float(row[primary_symbol]) - primary_base) / primary_base
                    alt_mom = (float(row[alt_symbol]) - alt_base) / alt_base

                    target_symbol: str | None = None
                    if primary_mom > 0 and primary_mom >= alt_mom:
                        target_symbol = primary_symbol
                    elif alt_mom > 0:
                        target_symbol = alt_symbol

                    for symbol in symbols:
                        if symbol != target_symbol and shares[symbol] > 0:
                            cash += shares[symbol] * float(row[symbol])
                            shares[symbol] = 0

                    if target_symbol is not None and shares[target_symbol] == 0:
                        price = float(row[target_symbol])
                        buy_size = int(cash // price)
                        if buy_size > 0:
                            shares[target_symbol] += buy_size
                            cash -= buy_size * price

            portfolio_value = cash + sum(shares[symbol] * float(row[symbol]) for symbol in symbols)
            equity_values.append(portfolio_value)
            cash_values.append(cash)

        return pd.Series(equity_values, index=prices.index), pd.Series(cash_values, index=prices.index)

    def _simulate_risk_parity_portfolio(
        self,
        *,
        prices: pd.DataFrame,
        symbols: tuple[str, ...],
        initial_cash: float,
        vol_window: int,
        rebal_interval: int,
    ) -> tuple[pd.Series, pd.Series]:
        """Simulate a risk parity portfolio using deterministic close-price fills.

        Args:
            prices: Aligned close-price DataFrame with symbols as columns.
            symbols: Tuple of symbol names.
            initial_cash: Starting cash balance.
            vol_window: Number of periods for volatility estimation.
            rebal_interval: Number of periods between rebalance checks.

        Returns:
            Tuple of (equity_curve, cash_curve) as pd.Series.
        """
        cash = float(initial_cash)
        shares: dict[str, int] = dict.fromkeys(symbols, 0)
        returns: dict[str, list[float]] = {symbol: [] for symbol in symbols}
        prev_close: dict[str, float | None] = dict.fromkeys(symbols)
        periods_elapsed = 0
        equity_values: list[float] = []
        cash_values: list[float] = []

        for _, row in prices.iterrows():
            for symbol in symbols:
                close = float(row[symbol])
                prev = prev_close[symbol]
                if prev is not None and prev > 0:
                    returns[symbol].append((close - prev) / prev)
                prev_close[symbol] = close

            if len(returns[symbols[0]]) >= vol_window:
                periods_elapsed += 1
                if periods_elapsed >= rebal_interval:
                    periods_elapsed = 0
                    target_weights = self._compute_risk_parity_target_weights(
                        returns=returns,
                        symbols=symbols,
                        vol_window=vol_window,
                    )
                    cash = self._rebalance_risk_parity_positions(
                        symbols=symbols,
                        prices_row=row,
                        shares=shares,
                        cash=cash,
                        target_weights=target_weights,
                    )

            portfolio_value = cash + sum(shares[symbol] * float(row[symbol]) for symbol in symbols)
            equity_values.append(portfolio_value)
            cash_values.append(cash)

        return pd.Series(equity_values, index=prices.index), pd.Series(cash_values, index=prices.index)

    def _to_nautilus_dataframe(self, price_df: pd.DataFrame) -> pd.DataFrame:
        """Convert an OHLCV DataFrame to the lowercase, UTC-indexed format Nautilus expects."""
        bars = price_df.loc[:, ["Open", "High", "Low", "Close", "Volume"]].copy()
        bars.columns = ["open", "high", "low", "close", "volume"]
        bars.index = pd.to_datetime(bars.index, utc=True)
        return bars

    def _map_nautilus_metrics(self, *, result: Any, initial_cash: float) -> dict[str, float]:
        """Map a NautilusTrader backtest result object to canonical metric keys.

        Args:
            result: The Nautilus BacktestResult object.
            initial_cash: Starting cash used to compute returns and CAGR.

        Returns:
            Dict of canonical metric keys.
        """
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
        """Return the value as a float if finite, otherwise return the default."""
        try:
            as_float = float(value)
        except (TypeError, ValueError):
            return default
        return as_float if isfinite(as_float) else default

    def _supports_native_nautilus(self) -> bool:
        """Check whether the nautilus_trader package is importable."""
        return find_spec("nautilus_trader") is not None

    def _get_nautilus_version(self) -> str:
        """Return the installed nautilus_trader version, or a fallback string."""
        try:
            import nautilus_trader

            return str(nautilus_trader.__version__)
        except ImportError:
            return "unknown (not installed)"

    def supports_feature(self, feature: str) -> bool:
        """Check whether this adapter supports a named feature.

        Args:
            feature: The feature name to query (e.g., "basic_backtest").

        Returns:
            True if the feature is supported, False otherwise.
        """
        supported = {
            "basic_backtest",
            "snapshot_reference",
        }
        return feature in supported
