import backtrader as bt


class SMACrossoverTriple(bt.Strategy):
    """Three equities SMA crossover — allocates based on fast/med/slow SMA ordering."""

    def __init__(self, fast_ma, med_ma, slow_ma):
        self.fast_ma = fast_ma
        self.med_ma = med_ma
        self.slow_ma = slow_ma
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
        d_f, d_m, d_s = self.datas[0], self.datas[1], self.datas[2]

        if f_sma > m_sma > s_sma or f_sma > s_sma > m_sma:
            # Uptrend: buy aggressive (d_f if fms, d_m if fsm)
            target = d_f if f_sma > m_sma > s_sma else d_m
            others = [d for d in (d_f, d_m, d_s) if d is not target]
            for d in others:
                if self.getposition(data=d):
                    self.sell(data=d)
            self.buy(data=target)
        elif m_sma > f_sma > s_sma or m_sma > s_sma > f_sma:
            # Mid: buy moderate (d_m)
            for d in (d_f, d_s):
                if self.getposition(data=d):
                    self.sell(data=d)
            self.buy(data=d_m)
        else:
            # Downtrend: buy defensive (d_s)
            for d in (d_f, d_m):
                if self.getposition(data=d):
                    self.sell(data=d)
            self.buy(data=d_s)
