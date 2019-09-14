from jinja2 import Template
from flask import Flask, render_template, jsonify
import sys
sys.path.append("C:/Users/matth/Desktop/crypto")
import config
from backend.Researcher import Researcher
import signal_utils
from backend.StockSignalCollector import StockSignalCollector
from datetime import datetime, timedelta

class StockBacktestFormatter:
	def __init__(self, timestamp=None): 
		(self.connection, self.cursor) = config.get_db_cnx()
		if timestamp is None:
			self.timestamp = 1567987946
		else:
			self.timestamp = timestamp

	def load_backtest(self, timestamp=None):
		signal_collector = StockSignalCollector(self.timestamp)
		signals = signal_collector.signals()
		data = self.load_backtest_data(signals)
		return render_template("backtest.html", data=data)

	def load_backtest_data(self, signals):
		results = self.load_results()

		data = {}
		for stock, stock_signals in signals.items():
			if stock not in results:
				continue
				
			data[stock] = {}
			data[stock]["symbol"] = stock

			last_price = stock_signals["last_price"]
			_max = results[stock]["max"]
			_min = results[stock]["min"]

			data[stock]["last_price"] = last_price
			data[stock]["max"] = _max
			data[stock]["min"] = _min
			data[stock]["max_gain"] = ((_max - last_price) / last_price) * 100
			data[stock]["max_loss"] = ((_min - last_price) / last_price) * 100

			buy = 0
			sell = 0
			for signal, value in stock_signals["signals"].items():
				if value > 0:
					buy += value
				elif value < 0:
					sell += -value

			data[stock]["buy"] = buy
			data[stock]["sell"] = sell
			data[stock]["total"] = buy - sell
			if data[stock]["total"] > 0:
				data[stock]["long"] = True
			else:
				data[stock]["long"] = False

		return data

	def load_results(self):
		query = "select stock, max(high), min(low) from price_stocks_data where timestamp >= '{}' group by stock".format(self.timestamp)

		data = {}	
		self.cursor.execute(query)
		for (name, _max, _min) in self.cursor:
			data[name] = {}
			data[name]["max"] = _max
			data[name]["min"] = _min

		return data
