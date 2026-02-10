import backtrader as bt


class MACDSingle(bt.Strategy):
    """Single equity MACD crossover strategy."""

    def __init__(self, fast_ma, slow_ma, signal_period):
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma
        self.signal_period = signal_period
        self.dataclose = self.datas[0].close
        self.order = None
        self.macd = bt.indicators.MACD(
            self.data,
            period_me1=self.fast_ma,
            period_me2=self.slow_ma,
            period_signal=self.signal_period,
        )
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

    def notify_order(self, order):
        self.order = None

    def next(self):
        if self.order:
            return
        if not self.getposition(self.datas[0]):
            if self.mcross[0] > 0.0:
                self.buy()
        else:
            if self.mcross[0] < 0.0:
                self.sell()
