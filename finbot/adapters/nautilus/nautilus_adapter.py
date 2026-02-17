"""NautilusTrader adapter implementing BacktestEngine interface.

This adapter translates between our engine-agnostic contracts and NautilusTrader's
event-driven backtesting system.

Architecture:
    BacktestRunRequest → NautilusAdapter → BacktestEngine → BacktestRunResult

Status: PILOT - Minimal implementation for E6-T1 evaluation
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pandas as pd

from finbot.core.contracts.interfaces import BacktestEngine
from finbot.core.contracts.models import BacktestRunMetadata, BacktestRunRequest, BacktestRunResult


class NautilusAdapter(BacktestEngine):
    """Adapter for running backtests via NautilusTrader.

    This adapter provides a minimal implementation to evaluate NautilusTrader
    as an alternative backtesting engine. It implements the BacktestEngine
    interface to maintain compatibility with our contract-based system.

    Example:
        >>> adapter = NautilusAdapter()
        >>> request = BacktestRunRequest(...)
        >>> result = adapter.run_backtest(request)

    Notes:
        - This is a PILOT implementation for evaluation (E6-T1)
        - Not all BacktestEngine features are implemented
        - Focus is on getting one strategy working
        - Full parity with Backtrader is NOT the goal yet
    """

    def __init__(self):
        """Initialize Nautilus adapter.

        Future parameters may include:
        - engine_config: NautilusTrader engine configuration
        - log_level: Logging verbosity
        - cache_dir: Location for cached data
        """
        self.name = "nautilus"
        self.version = self._get_nautilus_version()

    def run_backtest(self, request: BacktestRunRequest) -> BacktestRunResult:
        """Run a backtest using NautilusTrader.

        Translates BacktestRunRequest → Nautilus BacktestEngine → BacktestRunResult

        Args:
            request: Standardized backtest request with strategy, data, config

        Returns:
            BacktestRunResult containing performance metrics and metadata

        Raises:
            NotImplementedError: Pilot implementation - not all features supported
            ValueError: Invalid request parameters
            RuntimeError: Nautilus execution errors

        Notes:
            Current limitations (E6-T1 pilot):
            - Single strategy only (no multi-strategy)
            - Bar data only (no tick data)
            - Cash account only (no margin)
            - Simplified fill model
            - Basic metrics only
        """
        # TODO: Validate request
        self._validate_request(request)

        # TODO: Create Nautilus engine
        engine = self._create_engine(request)

        # TODO: Configure venue
        self._configure_venue(engine, request)

        # TODO: Load and prepare data
        self._load_data(engine, request)

        # TODO: Add strategy
        self._add_strategy(engine, request)

        # TODO: Run backtest
        self._run_engine(engine)

        # TODO: Extract results
        result = self._extract_results(engine, request)

        return result

    def _validate_request(self, request: BacktestRunRequest) -> None:
        """Validate backtest request parameters.

        Args:
            request: Backtest request to validate

        Raises:
            ValueError: Invalid request parameters
        """
        if not request.strategy_name:
            raise ValueError("strategy_name is required")

        if not request.symbols or len(request.symbols) == 0:
            raise ValueError("At least one symbol is required")

        if request.initial_cash <= 0:
            raise ValueError("initial_cash must be positive")

        if request.start and request.end and request.start >= request.end:
            raise ValueError("start must be before end")

    def _create_engine(self, request: BacktestRunRequest):
        """Create and configure NautilusTrader BacktestEngine.

        Args:
            request: Backtest request with configuration

        Returns:
            Configured BacktestEngine instance

        Notes:
            Uses low-level API (BacktestEngine) for simplicity in pilot.
            High-level API (BacktestNode) deferred to full implementation.
        """
        from nautilus_trader.backtest.engine import BacktestEngine

        engine = BacktestEngine()
        return engine

    def _configure_venue(self, engine, request: BacktestRunRequest) -> None:
        """Configure trading venue in Nautilus engine.

        Args:
            engine: NautilusTrader BacktestEngine
            request: Backtest request with initial cash, etc.

        Notes:
            - Uses "SIM" venue for backtesting
            - Cash account type for simplicity
            - NETTING order management (not hedging)
        """
        # Convert to Money object with proper currency
        from nautilus_trader.model.enums import AccountType, OmsType
        from nautilus_trader.model.identifiers import Venue
        from nautilus_trader.model.objects import Currency, Money

        usd = Currency.from_str("USD")
        starting_balance = Money(int(request.initial_cash * 100), currency=usd)  # Amount in cents

        engine.add_venue(
            venue=Venue("SIM"),
            oms_type=OmsType.NETTING,
            account_type=AccountType.CASH,
            base_currency=usd,
            starting_balances=[starting_balance],
        )

    def _load_data(self, engine, request: BacktestRunRequest) -> None:
        """Load historical data into Nautilus engine.

        Args:
            engine: NautilusTrader BacktestEngine
            request: Backtest request with data

        Notes:
            - Converts pandas DataFrame → Nautilus bars
            - Handles multiple instruments
            - Ensures timestamp compatibility (close time not open)
        """
        from finbot.utils.data_collection_utils.yfinance import get_history

        # Load data for each symbol
        for symbol in request.symbols:
            # Fetch data from yfinance
            df = get_history(
                symbols=symbol,
                start_date=request.start.date() if request.start else None,
                end_date=request.end.date() if request.end else None,
            )

            if df.empty:
                raise ValueError(f"No data found for symbol {symbol}")

            # Create instrument and add to engine
            instrument = self._create_instrument(symbol, engine)
            engine.add_instrument(instrument)

            # Convert DataFrame to Nautilus bars
            bars = self._convert_dataframe_to_bars(symbol, df, instrument)

            # Add bars to engine
            engine.add_data(bars)

        # No need to call engine.sort_data() - it's done automatically in newer versions

    def _add_strategy(self, engine, request: BacktestRunRequest) -> None:
        """Add trading strategy to Nautilus engine.

        Args:
            engine: NautilusTrader BacktestEngine
            request: Backtest request with strategy

        Notes:
            - Adapts our strategy interface to Nautilus strategy interface
            - May require strategy wrapper/adapter
        """
        # For pilot: use a simple buy-and-hold strategy
        # Full strategy adaptation deferred to post-pilot
        from nautilus_trader.config import StrategyConfig
        from nautilus_trader.trading.strategy import Strategy

        # Create minimal strategy configuration
        config = StrategyConfig(strategy_id=request.strategy_name)

        # Create a simple pass-through strategy for pilot
        # This allows the backtest to run without implementing full strategy logic
        strategy = Strategy(config=config)

        # Add strategy to engine
        engine.add_strategy(strategy)

    def _run_engine(self, engine) -> None:
        """Execute the backtest.

        Args:
            engine: Configured BacktestEngine

        Raises:
            RuntimeError: Execution errors
        """
        engine.run()

    def _extract_results(self, engine, request: BacktestRunRequest) -> BacktestRunResult:
        """Extract results from Nautilus engine and convert to BacktestRunResult.

        Args:
            engine: Completed BacktestEngine
            request: Original request for metadata

        Returns:
            BacktestRunResult with metrics and metadata

        Notes:
            - Maps Nautilus metrics to our canonical metrics
            - Extracts portfolio state, orders, fills
            - Calculates performance metrics (Sharpe, drawdown, etc.)
        """
        # Extract portfolio state
        from nautilus_trader.model.identifiers import Venue
        from nautilus_trader.model.objects import Currency

        # Get account from engine (SIM venue account)
        usd = Currency.from_str("USD")
        account = engine.portfolio.account(Venue("SIM"))

        # Extract final values (convert from cents to dollars)
        final_cash = float(account.balance_total(usd).as_double()) / 100.0
        final_value = final_cash  # Simplified for pilot - cash only, no positions

        # Calculate return
        total_return = ((final_value - request.initial_cash) / request.initial_cash) * 100.0

        # Create metadata
        metadata = BacktestRunMetadata(
            engine=self.name,
            engine_version=self.version,
            strategy_name=request.strategy_name,
            symbols=request.symbols,
            start_date=request.start,
            end_date=request.end,
            initial_cash=request.initial_cash,
            run_timestamp=datetime.now(),
        )

        # Create result with actual values
        result = BacktestRunResult(
            metadata=metadata,
            total_return=Decimal(str(total_return)),
            final_value=final_value,
            metrics={
                "final_cash": final_cash,
                "initial_cash": request.initial_cash,
            },
            data_snapshot=None,  # Optional
        )

        return result

    def _create_instrument(self, symbol: str, engine):
        """Create a Nautilus instrument for the given symbol.

        Args:
            symbol: Stock symbol (e.g., "SPY")
            engine: BacktestEngine instance

        Returns:
            Instrument instance
        """
        from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
        from nautilus_trader.model.instruments import Equity
        from nautilus_trader.model.objects import Currency, Price, Quantity

        # Create instrument ID
        instrument_id = InstrumentId(Symbol(symbol), Venue("SIM"))

        # Create equity instrument (simplified for pilot)
        instrument = Equity(
            instrument_id=instrument_id,
            raw_symbol=Symbol(symbol),
            currency=Currency.from_str("USD"),
            price_precision=2,
            price_increment=Price.from_str("0.01"),
            lot_size=Quantity.from_int(1),
            ts_event=0,  # Will be set from data
            ts_init=0,  # Will be set from data
        )

        return instrument

    def _get_nautilus_version(self) -> str:
        """Get NautilusTrader version.

        Returns:
            Version string (e.g., "1.222.0")
        """
        try:
            import nautilus_trader

            return nautilus_trader.__version__
        except ImportError:
            return "unknown (not installed)"

    def _convert_dataframe_to_bars(self, symbol: str, df: pd.DataFrame, instrument):
        """Convert pandas DataFrame to Nautilus bar objects.

        Args:
            symbol: Instrument symbol
            df: OHLCV DataFrame
            instrument: Nautilus Instrument instance

        Returns:
            List of Nautilus bar objects

        Notes:
            - DataFrame should have: Open, High, Low, Close, Volume
            - Index should be datetime
            - Timestamps represent close time (not open)
        """
        from nautilus_trader.model.data import Bar, BarSpecification, BarType
        from nautilus_trader.model.enums import AggregationSource, BarAggregation, PriceType
        from nautilus_trader.model.objects import Price, Quantity

        # Create bar type (1-DAY bars from external source)
        bar_spec = BarSpecification(step=1, aggregation=BarAggregation.DAY, price_type=PriceType.LAST)
        bar_type = BarType(instrument.id, bar_spec, aggregation_source=AggregationSource.EXTERNAL)

        bars = []
        for timestamp, row in df.iterrows():
            # Convert timestamp to nanoseconds
            ts_event = int(timestamp.value)  # pandas timestamp in ns
            ts_init = ts_event

            # Create bar
            bar = Bar(
                bar_type=bar_type,
                open=Price.from_str(f"{row['Open']:.2f}"),
                high=Price.from_str(f"{row['High']:.2f}"),
                low=Price.from_str(f"{row['Low']:.2f}"),
                close=Price.from_str(f"{row['Close']:.2f}"),
                volume=Quantity.from_str(f"{row['Volume']:.0f}"),
                ts_event=ts_event,
                ts_init=ts_init,
            )
            bars.append(bar)

        return bars

    def supports_feature(self, feature: str) -> bool:
        """Check if adapter supports a specific feature.

        Args:
            feature: Feature name (e.g., "walk_forward", "regime_detection")

        Returns:
            True if supported, False otherwise

        Notes:
            Pilot implementation supports minimal features only.
        """
        # TODO: Define supported features
        supported = {
            "basic_backtest",  # Minimal backtest
            # Not yet: "walk_forward", "regime_detection", "cost_models", etc.
        }
        return feature in supported
