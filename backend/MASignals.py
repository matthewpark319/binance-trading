import pandas
import numpy
import sys
sys.path.append("C:/Users/matth/Desktop/crypto")
import config
from signal_utils import buy_or_sell

# calculates signals relating to moving averages for the specified window, including:
# 1. whether the price is above the given moving average (crossover)
# 2. whether the moving average is sloping upward
class MASignals:
	def __init__(self, price_data, window):
		self.window = window
		self.price_data = price_data
		self.simple_ma = self.price_data[["close"]].rolling(self.window).mean()
		self.ewma = self.price_data[["close"]].ewm(span=self.window, adjust=False).mean()

	def get_window(self):
		return self.window

	def signals(self):
		buy_signals = {}
		last_price = self.price_data["close"][-1]
		last_ma = self.ma_at(1)
		last_ewma = self.ewma_at(1)

		buy_signals["price > {:d}-hour MA".format(self.window)] = buy_or_sell(last_price, last_ma)
		buy_signals["{:d}-hour MA increasing".format(self.window)] = buy_or_sell(last_ma, self.ma_at(2))

		buy_signals["price > {:d}-hour EWMA".format(self.window)] = buy_or_sell(last_price, last_ewma)
		buy_signals["{:d}-hour EWMA increasing".format(self.window)] = buy_or_sell(last_ewma, self.ewma_at(2))

		return buy_signals

	def ma_at(self, hours_ago):
		try:
			return self.simple_ma["close"][-hours_ago]
		except (KeyError, IndexError):
			return None

	def ewma_at(self, hours_ago):
		try:
			return self.ewma["close"][-hours_ago]
		except (KeyError, IndexError):
			return None