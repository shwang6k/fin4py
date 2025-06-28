from pandas import DataFrame
from pandas import Series
import numpy as np


class BandTest(object):
    def __init__(self, stock):
        self.stock = stock
        self.df = stock.df
        self.i_table = DataFrame(index=self.df.index)

    def addStrategy(self, name, strategy):
        signals = [
            (1 if strategy(i, self.df.iloc[i], self.stock) else 0)
            for i in range(self.df["Adj Close"].count())
        ]
        signal = Series(signals, self.df.index)

        close = self.df["Adj Close"]
        unit_income = np.log(close / close.shift(1)) * signal.shift(1)
        self.i_table[name] = np.exp(unit_income.cumsum())

    def plot(self):
        self.i_table.plot()
