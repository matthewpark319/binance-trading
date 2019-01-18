import pandas
import numpy
import sys
from backend.SignalCalculator import SignalCalculator
sys.path.append("C:/Users/matth/Desktop/crypto")
import config

class SignalCollector:
	def __init__(self, timestamp=None):
		(self.connection, self.cursor) = config.get_db_cnx()
		self.connection.autocommit = True
		self.coin_dict = self.load_coin_dict()
		self.timestamp = timestamp

	def load_coin_dict(self):
		self.cursor.execute("select distinct td.coin_id, name, symbol from " \
			"price_btc_data td left join coins c on td.coin_id = c.coin_id")
		coins = {}
		for (_id, name, symbol) in self.cursor:
			coin_info = {}
			coin_info["name"] = name
			coin_info["symbol"] = symbol
			coins[_id] = coin_info

		return coins

	def signals(self):
		signals = {}
		for _id, info in self.coin_dict.items():
			calculator = SignalCalculator(_id, self.connection, self.cursor, self.timestamp)
			values = {}
			values["symbol"] = info["symbol"]
			values["last_price"] = calculator.last_price()
			values["signals"] = calculator.signals()
			signals[info["name"]] = values 
		return signals