import pandas
import numpy
import sys
sys.path.append("C:/Users/matth/Desktop/crypto/backend")
from MASignals import MASignals
from MACrossSignals import MACrossSignals
from RSISignals import RSISignals
from MACDSignals import MACDSignals
import config

# calculates buy and sell signals for a single coin
class StockSignalCalculator:
	def __init__(self, stock, cnx, cursor, timestamp=None):
		self.connection = cnx
		self.cursor = cursor
		self.timestamp = timestamp
		self.price_data = self.load_price_data(stock)
		self.ma_ranges = [5, 10, 20, 50, 100, 200]
		self.ma_signals = self.load_ma_signals()
		self.macd_rsi_ranges = [1, 4, 6, 24]
		self.macd_signals = self.load_macd_signals()
		self.rsi_signals = self.load_rsi_signals()

	def last_price(self):
		return self.price_data["close"].iloc[-1]

	def load_price_data(self, stock):
		if self.timestamp is None:
			query = "select * from (select open, close, timestamp from price_stocks_data where stock=%s order by timestamp desc limit 200) as x order by timestamp"
			values = (stock,)
		else:
			query = "select * from (select open, close, timestamp from price_stocks_data where stock=%s and timestamp <= %s order by timestamp desc limit 200) as x order by timestamp"
			values = (stock, self.timestamp)

		self.cursor.execute(query, values)

		df = pandas.DataFrame(self.cursor.fetchall(), columns=['open', 'close', 'timestamp'])
		return df.set_index('timestamp')

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