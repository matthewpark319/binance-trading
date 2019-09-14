import pandas
import numpy
import sys
sys.path.append("C:/Users/matth/Desktop/crypto")
import config
from signal_utils import buy_or_sell

class MACDSignals:
	def __init__(self, price_data, window):
		self.window = window
		self.fast = self.load_macd(26 * window, 12 * window, price_data)
		self.slow = self.fast[["MACD"]].ewm(span=(9 * window), adjust=False).mean()

	def load_macd(self, _long, _short, price_data):
		ewma_long = price_data[["close"]].ewm(span=_long, adjust=False).mean()
		ewma_short = price_data[["close"]].ewm(span=_short, adjust=False).mean()

		macd = {}
		macd_list = []

		for i in range(1, len(ewma_long)):
			macd_list.insert(0, ewma_short["close"].iloc[-i] - ewma_long["close"].iloc[-i])

		macd["MACD"] = macd_list
		return pandas.DataFrame(data=macd)

	def signals(self):
		signals = {}

		macd_above_signal = buy_or_sell(self.macd_at(1), self.signal_at(1), weight=5)
		signals["{:d}-hour MACD > signal line".format(self.window)] = macd_above_signal

		crossed = 0
		for hours_ago in range(2, 12, 2):
			if crossed > 0:
				signals["{:d}-hour MACD crossed above signal line within last {:d} hours" \
					.format(self.window, hours_ago)] = crossed
			elif crossed < 0:
				signals["{:d}-hour MACD crossed below signal line within last {:d} hours" \
					.format(self.window, hours_ago)] = crossed
			else:
				if macd_above_signal > 0:
					crossed = buy_or_sell(self.signal_at(hours_ago), self.macd_at(hours_ago), dismiss_negative=True, weight=5)
					if crossed != 0:
						signals["{:d}-hour MACD crossed above signal line within last {:d} hours".format(self.window, hours_ago)] = crossed
				elif macd_above_signal < 0:
					crossed = -buy_or_sell(self.macd_at(hours_ago), self.signal_at(hours_ago), dismiss_negative=True, weight=5)
					if crossed != 0:
						signals["{:d}-hour MACD crossed below signal line within last {:d} hours".format(self.window, hours_ago)] = crossed
		
		return signals

	def macd_at(self, hours_ago):
		try:
			return list(self.fast["MACD"])[-hours_ago]
		except (KeyError, IndexError):
			return None

	def signal_at(self, hours_ago):
		try:
			return list(self.slow["MACD"])[-hours_ago]
		except (KeyError, IndexError):
			return None