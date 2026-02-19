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
        if "rebal_proportions" not in request.parameters:
            raise ValueError("rebalance pilot requires 'rebal_proportions' parameter")
        if "rebal_interval" not in request.parameters:
            raise ValueError("rebalance pilot requires 'rebal_interval' parameter")
        if len(request.parameters["rebal_proportions"]) != len(request.symbols):
            raise ValueError("Length of rebal_proportions must match symbol count")

    def _validate_norebalance_request(self, request: BacktestRunRequest) -> None:
        if len(request.symbols) != 1:
            raise ValueError("NoRebalance pilot currently supports exactly one symbol")
        if "equity_proportions" in request.parameters and len(request.parameters["equity_proportions"]) != len(
            request.symbols
        ):
            raise ValueError("Length of equity_proportions must match symbol count")

    def _validate_dual_momentum_request(self, request: BacktestRunRequest) -> None:
        if len(request.symbols) != 2:
            raise ValueError("DualMomentum pilot currently requires exactly two symbols")
        lookback = int(request.parameters.get("lookback", 252))
        rebal_interval = int(request.parameters.get("rebal_interval", 21))
        if lookback <= 0:
            raise ValueError("lookback must be positive")
        if rebal_interval <= 0:
            raise ValueError("rebal_interval must be positive")

    def _validate_risk_parity_request(self, request: BacktestRunRequest) -> None:
        if len(request.symbols) < 2:
            raise ValueError("RiskParity pilot currently requires at least two symbols")
        vol_window = int(request.parameters.get("vol_window", 63))
        rebal_interval = int(request.parameters.get("rebal_interval", 21))
        if vol_window <= 0:
            raise ValueError("vol_window must be positive")
        if rebal_interval <= 0:
            raise ValueError("rebal_interval must be positive")

    def _run_via_backtrader(self, request: BacktestRunRequest) -> BacktestRunResult:
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
                super().__init__(config)
                self.instrument: Instrument | None = None
                self._entered = False

            def on_start(self) -> None:
                self.instrument = self.cache.instrument(self.config.instrument_id)
                if self.instrument is None:
                    self.log.error(f"Could not find instrument for {self.config.instrument_id}")
                    self.stop()
                    return
                self.subscribe_bars(self.config.bar_type)

            def on_bar(self, bar: Bar) -> None:
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
        price_histories = self._select_native_price_histories(request.symbols, request.start, request.end)
        prices = self._build_aligned_close_frame(price_histories)

        lookback = int(request.parameters.get("lookback", 252))
        rebal_interval = int(request.parameters.get("rebal_interval", 21))

        primary_symbol = request.symbols[0]
        alt_symbol = request.symbols[1]
        cash = float(request.initial_cash)
        shares: dict[str, int] = dict.fromkeys(request.symbols, 0)
        periods_elapsed = 0
        equity_values: list[float] = []

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

                    for symbol in request.symbols:
                        if symbol != target_symbol and shares[symbol] > 0:
                            cash += shares[symbol] * float(row[symbol])
                            shares[symbol] = 0

                    if target_symbol is not None and shares[target_symbol] == 0:
                        price = float(row[target_symbol])
                        buy_size = int(cash // price)
                        if buy_size > 0:
                            shares[target_symbol] += buy_size
                            cash -= buy_size * price

            portfolio_value = cash + sum(shares[symbol] * float(row[symbol]) for symbol in request.symbols)
            equity_values.append(portfolio_value)

        equity_curve = pd.Series(equity_values, index=prices.index)
        metrics = self._build_metrics_from_equity_curve(equity_curve=equity_curve, initial_cash=request.initial_cash)
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
        }
        artifacts = {"nautilus_symbols": ",".join(request.symbols), "nautilus_proxy_type": "dual_momentum"}
        run_warnings = (
            "GS-02 currently uses deterministic pilot proxy execution rather than full Nautilus order lifecycle modeling.",
        )
        return metrics, assumptions, artifacts, run_warnings

    def _run_via_nautilus_risk_parity(
        self, request: BacktestRunRequest
    ) -> tuple[dict[str, float], dict[str, Any], dict[str, str], tuple[str, ...]]:
        price_histories = self._select_native_price_histories(request.symbols, request.start, request.end)
        prices = self._build_aligned_close_frame(price_histories)

        vol_window = int(request.parameters.get("vol_window", 63))
        rebal_interval = int(request.parameters.get("rebal_interval", 21))

        cash = float(request.initial_cash)
        shares: dict[str, int] = dict.fromkeys(request.symbols, 0)
        returns: dict[str, list[float]] = {symbol: [] for symbol in request.symbols}
        prev_close: dict[str, float | None] = dict.fromkeys(request.symbols)
        periods_elapsed = 0
        equity_values: list[float] = []

        for _, row in prices.iterrows():
            for symbol in request.symbols:
                close = float(row[symbol])
                prev = prev_close[symbol]
                if prev is not None and prev > 0:
                    returns[symbol].append((close - prev) / prev)
                prev_close[symbol] = close

            if len(returns[request.symbols[0]]) >= vol_window:
                periods_elapsed += 1
                if periods_elapsed >= rebal_interval:
                    periods_elapsed = 0
                    target_weights = self._compute_risk_parity_target_weights(
                        returns=returns,
                        symbols=request.symbols,
                        vol_window=vol_window,
                    )
                    cash = self._rebalance_risk_parity_positions(
                        symbols=request.symbols,
                        prices_row=row,
                        shares=shares,
                        cash=cash,
                        target_weights=target_weights,
                    )

            portfolio_value = cash + sum(shares[symbol] * float(row[symbol]) for symbol in request.symbols)
            equity_values.append(portfolio_value)

        equity_curve = pd.Series(equity_values, index=prices.index)
        metrics = self._build_metrics_from_equity_curve(equity_curve=equity_curve, initial_cash=request.initial_cash)
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
        inv_vols: dict[str, float] = {}
        for symbol in symbols:
            window = returns[symbol][-vol_window:]
            vol = float(pd.Series(window).std())
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

    def _select_native_price_histories(
        self,
        symbols: tuple[str, ...],
        start: pd.Timestamp | None,
        end: pd.Timestamp | None,
    ) -> dict[str, pd.DataFrame]:
        histories: dict[str, pd.DataFrame] = {}
        for symbol in symbols:
            histories[symbol] = self._select_native_price_history(symbol=symbol, start=start, end=end)
        return histories

    def _build_aligned_close_frame(self, price_histories: dict[str, pd.DataFrame]) -> pd.DataFrame:
        closes = [df["Close"].rename(symbol) for symbol, df in price_histories.items()]
        aligned = pd.concat(closes, axis=1, join="inner").dropna()
        if len(aligned) < 40:
            raise ValueError("Nautilus pilot requires at least 40 aligned bars across selected symbols")
        return aligned

    def _build_metrics_from_equity_curve(self, *, equity_curve: pd.Series, initial_cash: float) -> dict[str, float]:
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

        return {
            "starting_value": self._finite_or_default(initial_cash, 0.0),
            "ending_value": self._finite_or_default(ending_value, initial_cash),
            "roi": self._finite_or_default(roi, 0.0),
            "cagr": self._finite_or_default(cagr, 0.0),
            "sharpe": self._finite_or_default(sharpe, 0.0),
            "max_drawdown": self._finite_or_default(max_drawdown, 0.0),
            "mean_cash_utilization": self._finite_or_default(0.0, 0.0),
        }

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
