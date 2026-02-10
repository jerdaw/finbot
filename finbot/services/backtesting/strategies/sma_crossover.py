import backtrader as bt


class SMACrossover(bt.Strategy):
    """Single stock SMA crossover strategy."""

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
        if not self.position:
            if self.fast_sma[0] >= self.slow_sma[0]:
                self.order = self.buy()
        else:
            if self.slow_sma[0] > self.fast_sma[0]:
                self.order = self.sell()
