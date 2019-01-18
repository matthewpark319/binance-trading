from jinja2 import Template
from flask import Flask, render_template
import sys
sys.path.append("C:/Users/matth/Desktop/crypto")
import config
from backend.Researcher import Researcher
import signal_utils
from backend.SignalCollector import SignalCollector

class Formatter:
	def __init__(self, signals):
		(self.connection, self.cursor) = config.get_db_cnx()
		self.signals = signals
		self.researcher = Researcher()

	def load_main(self):
		return render_template("main.html", long_short=self.load_long_short())

	def load_long_short(self):
		long_short = {}
		long_short["timestamp"] = signal_utils.load_latest_timestamp()
		long_short["data"] = {}
		for coin, signal_data in self.signals.items():
			buy = 0
			sell = 0
			for signal, value in signal_data["signals"].items():
				if value > 0:
					buy += value
				elif value < 0:
					sell += -value

			signal_count = {}
			signal_count["symbol"] = signal_data["symbol"]
			signal_count["last_price"] = signal_data["last_price"]
			signal_count["buy"] = buy
			signal_count["sell"] = sell
			signal_count["total"] = buy - sell
			if signal_count["total"] > 0:
				signal_count["long"] = True
			else:
				signal_count["long"] = False

			long_short["data"][coin] = signal_count

		return long_short

	def load_coin_page(self, coin):
		coin_signals = self.signals[coin]
		return render_template("coin.html", signals=coin_signals["signals"], coin=coin, symbol=coin_signals["symbol"])

	def fetch_research_data(self, req):
		data = self.researcher.fetch_data(req)
		return self.load_research_page(req.form["coin"], data)

	def load_research_page(self, coin, data=None):
		return render_template("research.html", coin=coin, data=data)