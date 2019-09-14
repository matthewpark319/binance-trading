import math
import config
from datetime import datetime
import time

(connection, cursor) = config.get_db_cnx()

def buy_or_sell(val1, val2, dismiss_negative=False, weight=1):
	if val1 is None or val2 is None or math.isnan(val1) or math.isnan(val2): 
		return 0

	if val1 > val2:
		return weight
	if val1 == val2 or dismiss_negative:
		return 0
	return -weight

def check_data_updated():
	query = "select date(timestamp) = utc_date() " \
			"and (hour(timestamp) = hour(utc_time())) " \
			"from price_btc_data order by timestamp desc limit 1"
	cursor.execute(query)
	for (_bool,) in cursor:
		return eval(str(_bool))

def load_latest_timestamp():
	cursor.execute("select timestamp from price_btc_data order by timestamp desc limit 1")
	for (timestamp,) in cursor:
		return timestamp

def latest_ts_stocks():
	cursor.execute("select max(timestamp) from price_stocks_data")
	return cursor.fetchall()[0][0]

def get_stocks():
	start = time.time()
	today = datetime.fromtimestamp(latest_ts_stocks()).replace(second=0, minute=0, hour=0)
	query = "select stock, stocks.name, max(timestamp) as timestamp from price_stocks_data " \
			"left join stocks on stocks.symbol = price_stocks_data.stock " \
			"group by stocks.id"
	cursor.execute(query)
	stocks = [(symbol, name) for (symbol, name, ts) in cursor.fetchall() if ts_day(ts) == today]
	print(f'get_stocks() took {time.time() - start} seconds')
	return stocks

def ts_day(ts):
	return datetime.fromtimestamp(ts).replace(second=0, minute=0, hour=0)