import pandas
import numpy
import sys
sys.path.append("C:/Users/matth/Desktop/crypto")
from backend.StockSignalCalculator import StockSignalCalculator
import config
import signal_utils
import time

class StockSignalCollector:
	def __init__(self, timestamp=None):
		(self.connection, self.cursor) = config.get_db_cnx()
		self.connection.autocommit = True
		self.stocks = signal_utils.get_stocks()
		self.timestamp = timestamp

	def signals(self):
		start = time.time()
		signals = {}
		for symbol, name in self.stocks:
			try:
				calculator = StockSignalCalculator(symbol, self.connection, self.cursor, self.timestamp)
				values = {}
				values["symbol"] = symbol
				values["last_price"] = calculator.last_price()
				values["signals"] = calculator.signals()

				signals[name] = values
			except Exception as e:
				print(symbol)
		print(f'signals() took {time.time() - start} seconds')
		return signals