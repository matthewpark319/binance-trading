import math
import config

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