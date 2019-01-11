import pandas
import numpy
import sys
sys.path.append("C:/Users/matth/Desktop/crypto")
import config
from backend.signalparser import buy_or_sell

class MACrossSignals:
	def __init__(self, shorter, longer):
		self.shorter = shorter
		self.longer = longer

	def signals(self):
		signals = {}

		ma_crossed = buy_or_sell(self.shorter.ma_at(1), self.longer.ma_at(1))
		signals["{:d}-hour MA > {:d}-hour MA".format(self.shorter.get_window(), self.longer.get_window())] = ma_crossed

		ewma_crossed = buy_or_sell(self.shorter.ewma_at(1), self.longer.ewma_at(1))
		signals["{:d}-hour EWMA > {:d}-hour EWMA".format(self.shorter.get_window(), self.longer.get_window())] = ewma_crossed

		signals.update(self.when_crossed_ma(ma_crossed))
		signals.update(self.when_crossed_ewma(ewma_crossed))

		return signals

	def when_crossed_ma(self, crossed):
		signals = {}
		for hours_ago in range(10, 0, -2):
			if crossed == 1:
				signal_name = "{:d}-hour MA crossed above {:d}-hour MA within the last {:d} hours" \
					.format(self.shorter.get_window(), self.longer.get_window(), hours_ago)
				signals[signal_name] = \
					buy_or_sell(self.longer.ma_at(hours_ago), self.shorter.ma_at(hours_ago), dismiss_negative=True)
			if crossed == -1:
				signal_name = "{:d}-hour MA crossed below {:d}-hour MA within the last {:d} hours" \
					.format(self.shorter.get_window(), self.longer.get_window(), hours_ago)
				signals[signal_name] = \
					-buy_or_sell(self.shorter.ma_at(hours_ago), self.longer.ma_at(hours_ago), dismiss_negative=True)
		return signals

	def when_crossed_ewma(self, crossed):
		signals = {}
		for hours_ago in range(10, 0, -2):
			if crossed == 1:
				signal_name = "{:d}-hour EWMA crossed above {:d}-hour EWMA within the last {:d} hours" \
					.format(self.shorter.get_window(), self.longer.get_window(), hours_ago)
				signals[signal_name] = \
					buy_or_sell(self.longer.ewma_at(hours_ago), self.shorter.ewma_at(hours_ago), dismiss_negative=True)
			if crossed == -1:
				signal_name = "{:d}-hour EWMA crossed below {:d}-hour EWMA within the last {:d} hours" \
					.format(self.shorter.get_window(), self.longer.get_window(), hours_ago)
				signals[signal_name] = \
					-buy_or_sell(self.shorter.ewma_at(hours_ago), self.longer.ewma_at(hours_ago), dismiss_negative=True)
		return signals