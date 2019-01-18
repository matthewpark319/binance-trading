import pandas
import numpy
from backend.MASignals import MASignals
from backend.MACrossSignals import MACrossSignals
from backend.RSISignals import RSISignals
from backend.MACDSignals import MACDSignals
import sys
sys.path.append("C:/Users/matth/Desktop/crypto")
import config

# calculates buy and sell signals for a single coin
class SignalCalculator:
	def __init__(self, coin_id, cnx, cursor, timestamp):
		self.connection = cnx
		self.cursor = cursor
		self.timestamp = timestamp
		self.price_data = self.load_price_data(coin_id)
		self.ma_ranges = [5, 10, 20, 50, 100, 200]
		self.ma_signals = self.load_ma_signals()
		self.macd_rsi_ranges = [1, 4, 6, 24]
		self.macd_signals = self.load_macd_signals()
		self.rsi_signals = self.load_rsi_signals()

	def last_price(self):
		return self.price_data["close"][-1]

	def load_price_data(self, coin_id):
		if self.timestamp is None:
			query = "select * from " \
				"(select open, close, timestamp from price_btc_data where coin_id = {:d} group by timestamp " \
				"order by timestamp desc limit 500) as x " \
				"order by timestamp".format(coin_id)
		else:
			query = "select * from " \
				"(select open, close, timestamp from price_btc_data where coin_id = {:d} and " \
				"timestamp <= '{}' group by timestamp " \
				"order by timestamp desc limit 500) as x " \
				"order by timestamp".format(coin_id, self.timestamp)
		self.cursor.execute(query)

		price_data = {}
		price_open = []
		price_close = []
		timestamps = []
		for (_open, close, timestamp) in self.cursor:
			price_open.append(_open * pow(10, 8))
			price_close.append(close * pow(10, 8))
			timestamps.append(timestamp)
		price_data["open"] = price_open
		price_data["close"] = price_close
		return pandas.DataFrame(data=price_data, index=numpy.array(timestamps))

	def load_ma_signals(self):
		ma_signals = {}
		for _range in self.ma_ranges:
			ma_signals[_range] = MASignals(self.price_data, _range)
		return ma_signals

	def load_rsi_signals(self):
		rsi_signals = {}
		for _range in self.macd_rsi_ranges:
			rsi_signals[_range] = RSISignals(self.price_data, _range)
		return rsi_signals

	def load_macd_signals(self):
		macd_signals = {}
		for _range in self.macd_rsi_ranges:
			macd_signals[_range] = MACDSignals(self.price_data, _range)
		return macd_signals

	def signals(self):
		signals = {}

		# First, calculate the basic moving average signals
		for _range in self.ma_ranges:
			new_signals = self.ma_signals[_range].signals()
			signals.update(new_signals)

		# Second, calculate the moving average cross signals
		for i, shorter in enumerate(self.ma_ranges):
			for j in range(i + 1, len(self.ma_ranges)):
				longer = self.ma_ranges[j]
				cross_signals = MACrossSignals(self.ma_signals[shorter], self.ma_signals[longer])
				new_signals = cross_signals.signals()
				signals.update(new_signals)

		# Third, calculate the MACD signals
		for _range in self.macd_rsi_ranges:
			new_signals = self.macd_signals[_range].signals()
			signals.update(new_signals)

		# Fourth, calculate the RSI signals
		for _range in self.macd_rsi_ranges:
			new_signals = self.rsi_signals[_range].signals()
			signals.update(new_signals)

		return signals