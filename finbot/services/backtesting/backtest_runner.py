from __future__ import annotations

import warnings
from typing import Any

import backtrader as bt
import pandas as pd

from finbot.services.backtesting.analyzers.cv_tracker import CVTracker
from finbot.services.backtesting.analyzers.trade_tracker import TradeTracker
from finbot.services.backtesting.compute_stats import compute_stats


class BacktestRunner:
    def __init__(
        self,
        price_histories: dict[str, pd.DataFrame],
        start: pd.Timestamp | None,
        end: pd.Timestamp | None,
        duration: pd.Timedelta | None,
        start_step: pd.Timedelta | None,
        init_cash: float,
        strat: Any,
        strat_kwargs: dict[str, Any],
        broker: Any,
        broker_kwargs: dict[str, Any],
        broker_commission: Any,
        sizer: Any,
        sizer_kwargs: dict[str, Any],
        plot: bool,
    ):
        self.price_histories = price_histories
        self.start = start
        self.end = end
        self.duration = duration
        self.start_step = start_step
        self.init_cash = init_cash
        self.strat = strat
        self.strat_kwargs = strat_kwargs
        self.broker = broker
        self.broker_kwargs = broker_kwargs
        self.broker_commission = broker_commission
        self.sizer = sizer
        self.sizer_kwargs = sizer_kwargs
        self.plot = plot

        self.stocks = tuple(price_histories.keys())
        self._latest_start_date: pd.Timestamp | None = None
        self._earliest_end_date: pd.Timestamp | None = None
        self._cerebro: bt.Cerebro | None = None
        self._cerebro_res: list[Any] | None = None
        self._stats: pd.DataFrame | None = None
        self.order: Any = None

    def run_backtest(self) -> pd.DataFrame:
        cerebro = bt.Cerebro()
        self._cerebro = cerebro
        self._add_ph_to_cerebro()
        cerebro.addstrategy(self.strat, **self.strat_kwargs)
        self._add_broker_to_cerebro()
        cerebro.addsizer(self.sizer, **self.sizer_kwargs)
        cerebro.addanalyzer(CVTracker)
        cerebro.addanalyzer(TradeTracker)
        cerebro.addobserver(bt.observers.BuySell)
        cerebro.addobserver(bt.observers.Value)
        cerebro.addobserver(bt.observers.Cash)
        self._cerebro_res = cerebro.run(stdstats=False)
        if self.plot:
            cerebro.plot(volume=False)
        return self.get_test_stats()

    def _add_ph_to_cerebro(self) -> None:
        assert self._cerebro is not None
        ph = self.price_histories
        self._latest_start_date = max(h.index[0] for h in ph.values())
        if self.start:
            self._latest_start_date = max(self.start, self._latest_start_date)
        self._earliest_end_date = min(h.index[-1] for h in ph.values())
        if self.end:
            self._earliest_end_date = min(self.end, self._earliest_end_date)
        if self.duration and self._latest_start_date is not None:
            end_by_duration = self._latest_start_date + self.duration
            self._earliest_end_date = min(end_by_duration, self._earliest_end_date)

        for data_name, v in ph.items():
            if any("adj" in c.lower() and "close" in c.lower() for c in v.columns):
                warnings.warn(f"price_histories entry {data_name} is not using adjusted returns.", stacklevel=2)
            cur_ph = v.truncate(before=self._latest_start_date, after=self._earliest_end_date)
            self.price_histories[data_name] = cur_ph
            ticker_feed = bt.feeds.PandasData(dataname=cur_ph)
            self._cerebro.adddata(ticker_feed, name=data_name)

    def _add_broker_to_cerebro(self) -> None:
        assert self._cerebro is not None
        self._cerebro.broker = self.broker(**self.broker_kwargs)
        self._cerebro.broker.setcash(self.init_cash)
        comminfo = self.broker_commission()
        self._cerebro.broker.addcommissioninfo(comminfo)

    def _build_cv_hist(self) -> pd.DataFrame:
        """Build the Value+Cash time series DataFrame from cerebro results."""
        assert self._cerebro_res is not None
        value_hist = self._cerebro_res[0].analyzers.cvtracker.value
        cash_hist = self._cerebro_res[0].analyzers.cvtracker.cash
        cv_hist = pd.DataFrame({"Value": value_hist, "Cash": cash_hist})
        index = pd.concat(self.price_histories.values(), axis=1).index
        cv_hist.index = index
        return cv_hist

    def get_value_history(self) -> pd.DataFrame:
        """Return the Value and Cash time series from the backtest.

        Must be called after run_backtest(). Returns a DataFrame with
        'Value' and 'Cash' columns indexed by date.
        """
        return self._build_cv_hist()

    def get_trades(self) -> list[Any]:
        """Return the list of executed trades from the backtest.

        Must be called after run_backtest(). Returns TradeInfo objects
        captured by the TradeTracker analyzer.
        """
        assert self._cerebro_res is not None
        trade_analysis = self._cerebro_res[0].analyzers.tradetracker.get_analysis()
        return trade_analysis.get("trades", [])

    def get_test_stats(self) -> pd.DataFrame:
        cv_hist = self._build_cv_hist()
        self._stats = compute_stats(
            cv_hist["Value"],
            cv_hist["Cash"],
            self.stocks,
            self.strat,
            self.strat_kwargs,
            self.broker,
            self.broker_kwargs,
            self.broker_commission,
            self.sizer,
            self.sizer_kwargs,
            plot=self.plot,
        )
        return self._stats
