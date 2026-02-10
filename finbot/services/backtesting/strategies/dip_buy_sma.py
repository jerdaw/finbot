import backtrader as bt


class DipBuySMA(bt.Strategy):
    """Dip-buying strategy using SMA ordering as trigger."""

    def __init__(self, fast_ma, med_ma, slow_ma):
        self.fast_ma = fast_ma
        self.med_ma = med_ma
        self.slow_ma = slow_ma
        self.d_since_last_sale = 0
        self.dataclose = self.datas[0].close
        self.order = None
        self.fast_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.fast_ma)
        self.med_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.med_ma)
        self.slow_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.slow_ma)

    def notify_order(self, order):
        self.order = None

    def next(self):
        if self.order:
            return

        f_sma, m_sma, s_sma = self.fast_sma[0], self.med_sma[0], self.slow_sma[0]

        if s_sma > m_sma > f_sma:
            cash = self.broker.get_cash()
            close = self.datas[0][0]
            n_to_buy = round(cash // close)
            if n_to_buy:
                self.buy(data=self.datas[0], size=n_to_buy)
        elif self.d_since_last_sale > round(252 / 4):
            n_equities = self.getposition(data=self.datas[0]).size
            n_to_sell = round(n_equities * 0.05)
            if n_to_sell:
                self.sell(data=self.datas[0], size=n_to_sell)
                self.d_since_last_sale = 0
        self.d_since_last_sale += 1
