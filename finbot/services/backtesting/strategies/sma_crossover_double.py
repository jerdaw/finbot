import backtrader as bt


class SMACrossoverDouble(bt.Strategy):
    """Two equities SMA crossover — switches between data[0] and data[1]."""

    def __init__(self, fast_ma, slow_ma):
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma
        self.dataclose = self.datas[0].close
        self.order = None
        self.fast_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.fast_ma)
        self.slow_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.slow_ma)

    def notify_order(self, order):
        self.order = None

    def next(self):
        if self.order:
            return
        if self.fast_sma[0] >= self.slow_sma[0]:
            if self.getposition(self.datas[1]):
                self.order = self.sell(data=self.datas[1])
            else:
                self.order = self.buy(data=self.datas[0])
        else:
            if self.getposition(self.datas[0]):
                self.order = self.sell(data=self.datas[0])
            else:
                self.order = self.buy(data=self.datas[1])
