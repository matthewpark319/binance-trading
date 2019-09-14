from jinja2 import Template
from flask import Flask, render_template, jsonify
import sys
sys.path.append("C:/Users/matth/Desktop/crypto")
import config
from backend.Researcher import Researcher
import signal_utils
from backend.SignalCollector import SignalCollector
from datetime import datetime, timedelta

class BacktestFormatter:
	def __init__(self, timestamp=None): 
		(self.connection, self.cursor) = config.get_db_cnx()
		if timestamp is None:
			self.timestamp = signal_utils.load_latest_timestamp() - timedelta(days=4)
		else:
			self.timestamp = timestamp

	def load_backtest(self, timestamp=None):
		signal_collector = SignalCollector(self.timestamp)
		signals = signal_collector.signals()
		data = self.load_backtest_data(signals)
		return render_template("backtest.html", data=data)

	def load_backtest_data(self, signals):
		results = self.load_results()

		data = {}
		for coin, coin_signals in signals.items():
			data[coin] = {}
			data[coin]["symbol"] = coin_signals["symbol"]

			last_price = coin_signals["last_price"]
			_max = results[coin]["max"]
			_min = results[coin]["min"]

			data[coin]["last_price"] = last_price
			data[coin]["max"] = _max
			data[coin]["min"] = _min
			data[coin]["max_gain"] = ((_max - last_price) / last_price) * 100
			data[coin]["max_loss"] = ((_min - last_price) / last_price) * 100

			buy = 0
			sell = 0
			for signal, value in coin_signals["signals"].items():
				if value > 0:
					buy += value
				elif value < 0:
					sell += -value

			data[coin]["buy"] = buy
			data[coin]["sell"] = sell
			data[coin]["total"] = buy - sell
			if data[coin]["total"] > 0:
				data[coin]["long"] = True
			else:
				data[coin]["long"] = False

		return data

	def load_results(self):
		query = "select c.name, max(high), min(low) " \
			"from price_btc_data pbd left join coins c on pbd.coin_id = c.coin_id " \
			"where timestamp >= '{}' " \
			"group by pbd.coin_id".format(self.timestamp)

		data = {}	
		self.cursor.execute(query)
		for (name, _max, _min) in self.cursor:
			data[name] = {}
			data[name]["max"] = _max * pow(10, 8)
			data[name]["min"] = _min * pow(10, 8)

		return data
