import sys
sys.path.append("C:/Users/matth/Desktop/crypto")
import config
import requests
import json
import aiohttp
import pandas
import asyncio
import socket

class InsertNewCoins:
	def __init__(self):
		(self.connection, self.cursor) = config.get_db_cnx()
		self.connection.autocommit = True
		self.last_timestamp = self.load_last_timestamp()
		self.coin_id = self.load_coin_id()

	def load_last_timestamp(self):
		self.cursor.execute("select timestamp from price_btc_data order by timestamp desc limit 1")
		for (datetime,) in self.cursor:
			return datetime

	def load_coin_id(self):
		self.cursor.execute("select coin_id from coins where symbol = '{}'".format(sys.argv[1]))
		for (_id,) in self.cursor:
			coin_id = _id
		self.cursor.execute("select * from price_btc_data where coin_id = {}".format(coin_id))
		if self.cursor.rowcount > 0:
			print("Already in DB")
			exit(0)
		return coin_id

	def insert(self):
		results = requests.get(self.get_cc_url(sys.argv[1])).json()

		inserts = 0
		query = "insert into price_btc_data (coin_id, timestamp, open, close, high, low) values {} " \
			"on duplicate key update open=open, close=close, high=high, low=low"
		values = ""
		for entry in results["Data"]:
			timestamp = self.unix_to_timestamp(entry["time"])
			if timestamp > self.last_timestamp:
				continue
			_open = entry["open"]
			close = entry["close"]
			high = entry["high"]
			low = entry["low"]
			if close != 0:
				values += "({:d},\"{}\",{},{},{},{}),".format(self.coin_id, timestamp, _open, close, high, low)
			inserts += 1		

		self.cursor.execute(query.format(values[:-1]))
		self.connection.commit()

		print("{:d} data points inserted.".format(inserts))

	def unix_to_timestamp(self, ts):
		return pandas.to_datetime(ts, unit='s')
			 
	def get_cc_url(self, symbol):
		return "https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=BTC&e=Binance".format(symbol)

i = InsertNewCoins()
i.insert()