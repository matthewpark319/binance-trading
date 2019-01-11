import pandas
import numpy
import sys
sys.path.append("C:/Users/matth/Desktop/crypto")
import config
from backend.signalparser import buy_or_sell
from datetime import datetime, timedelta

class Researcher:
	def __init__(self):
		(self.connection, self.cursor) = config.get_db_cnx()

	def fetch_data(self, req):
		data = {}

		ts = self.build_timestamp(req)
		ts_formatted = ts.strftime("%Y-%m-%d %H:00:00")
		coin = req.form["coin"]
		price = float(req.form["price"])
		data["timestamp"] = ts_formatted
		data["coin"] = coin
		data["price"] = price

		for i in [1, 2, 3, 7]:
			end = (ts + timedelta(days=i)).strftime("%Y-%m-%d %H:00:00")
			query = "select max(high), min(low) from " \
					"(select high * pow(10, 8) as high, low * pow(10, 8) as low " \
					"from price_btc_data pbd left join coins c on pbd.coin_id = c.coin_id " \
					"where c.name = \"{}\" and timestamp between '{}' and '{}') as x".format(coin, ts_formatted, end)
			self.cursor.execute(query)
			for (high, low) in self.cursor:
				percent_high = abs(high - price) / price
				percent_low = (price - low) / price
				data["{:d}-day high".format(i)] = "{:.2f}".format(high)
				data["{:d}-day low".format(i)] = "{:.2f}".format(low)
				data["{:d}-day percent high".format(i)] = "{:.2%}".format(percent_high)
				data["{:d}-day percent low".format(i)] = "{:.2%}".format(percent_low)

		return data

	def build_timestamp(self, req):
		year = int(req.form["year"])
		month = int(req.form["month"])
		day = int(req.form["day"])
		hour = int(req.form["hour"])

		return datetime(year, month, day, hour=hour)