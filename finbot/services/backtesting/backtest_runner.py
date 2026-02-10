from __future__ import annotations

import warnings

import backtrader as bt
import pandas as pd

from finbot.services.backtesting.analyzers.cv_tracker import CVTracker
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
        strat,
        strat_kwargs: dict,
        broker,
        broker_kwargs: dict,
        broker_commission,
        sizer,
        sizer_kwargs: dict,
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
        self._latest_start_date = None
        self._earliest_end_date = None
        self._cerebro = None
        self._cerebro_res = None
        self._stats = None
        self.order = None

    def run_backtest(self):
        self._cerebro = bt.Cerebro()
        self._add_ph_to_cerebro()
        self._cerebro.addstrategy(self.strat, **self.strat_kwargs)
        self._add_broker_to_cerebro()
        self._cerebro.addsizer(self.sizer, **self.sizer_kwargs)
        self._cerebro.addanalyzer(CVTracker)
        self._cerebro.addobserver(bt.observers.BuySell)
        self._cerebro.addobserver(bt.observers.Value)
        self._cerebro.addobserver(bt.observers.Cash)
        self._cerebro_res = self._cerebro.run(stdstats=False)
        if self.plot:
            self._cerebro.plot(volume=False)
        return self.get_test_stats()

    def _add_ph_to_cerebro(self):
        ph = self.price_histories
        self._latest_start_date = max(h.index[0] for h in ph.values())
        if self.start:
            self._latest_start_date = max(self.start, self._latest_start_date)
        self._earliest_end_date = min(h.index[-1] for h in ph.values())
        if self.end:
            self._earliest_end_date = min(self.end, self._earliest_end_date)
        if self.duration:
            self._earliest_end_date = min(self._latest_start_date + self.duration, self._earliest_end_date)

        for data_name, v in ph.items():
            if any("adj" in c.lower() and "close" in c.lower() for c in v.columns):
                warnings.warn(f"price_histories entry {data_name} is not using adjusted returns.", stacklevel=2)
            cur_ph = v.truncate(before=self._latest_start_date, after=self._earliest_end_date)
            self.price_histories[data_name] = cur_ph
            ticker_feed = bt.feeds.PandasData(dataname=cur_ph)
            self._cerebro.adddata(ticker_feed, name=data_name)

    def _add_broker_to_cerebro(self):
        self._cerebro.broker = self.broker(**self.broker_kwargs)
        self._cerebro.broker.setcash(self.init_cash)
        comminfo = self.broker_commission()
        self._cerebro.broker.addcommissioninfo(comminfo)

    def get_test_stats(self):
        value_hist = self._cerebro_res[0].analyzers.cvtracker.value
        cash_hist = self._cerebro_res[0].analyzers.cvtracker.cash
        cv_hist = pd.DataFrame({"Value": value_hist, "Cash": cash_hist})
        index = pd.concat(self.price_histories.values(), axis=1).index
        cv_hist.index = index
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
