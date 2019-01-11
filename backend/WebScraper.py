import sys
sys.path.append("C:/Users/matth/Desktop/crypto")
import config
import requests
import json
import aiohttp
import pandas
import asyncio
import socket

class WebScraper:
	def __init__(self):
		(self.connection, self.cursor) = config.get_db_cnx()
		self.connection.autocommit = True
		self.last_timestamp = self.load_last_timestamp()
		self.skip_new = eval(sys.argv[1])

	def load_last_timestamp(self):
		self.cursor.execute("select timestamp from price_btc_data order by timestamp desc limit 1")
		for (datetime,) in self.cursor:
			return datetime

	def get_coin_info(self):
		if self.skip_new:
			query = "select c.coin_id, symbol from price_btc_data td left join coins c on td.coin_id = c.coin_id " \
				"where name != 'Bitcoin' group by c.coin_id"
		else:
			query = "select coin_id, symbol from coins where name != 'Bitcoin'"
			
		self.cursor.execute(query)
		coins = []
		symbol_dict = {}
		for (_id, symbol) in self.cursor:
			coins.append((_id, symbol))
			symbol_dict[_id] = symbol
		return (coins, symbol_dict)

	async def get_price_history(self):
		connector = aiohttp.TCPConnector(verify_ssl=False, family=socket.AF_INET)
		async with aiohttp.ClientSession(connector=connector) as session:
			results_agg = []
			(coins, symbols) = self.get_coin_info()

			while len(coins) > 0:
				tasks = []
				for _ in range(min(len(coins), 5)):
					(_id, symbol) = coins.pop()
					url = self.get_cc_url(symbol)
					task = asyncio.ensure_future(self.get_json_response(session, url, _id))
					tasks.append(task)

				results = await asyncio.gather(*tasks, return_exceptions=False)
				for result in results:
					# If Binance does not contain the trading pair, skip it
					try:
						if result["Type"] == 1:
							continue
					except (KeyError, TypeError):
						pass

					if result is None:
						continue
					elif result["Type"] != 100:
						print(result)
						_id = result["coin_id"]
						coins.append((_id, symbols[_id]))
					else:
						results_agg.append(result)	
				await asyncio.sleep(.5)

			inserts = 0
			query = "insert into price_btc_data (coin_id, timestamp, open, close, high, low) values {} " \
				"on duplicate key update open=open, close=close, high=high, low=low"
			values = ""
			for resp in results_agg:
				coin_id = resp["coin_id"]
				if len(resp["Data"]) == 0:
					print(resp)
				for entry in resp["Data"]:
					timestamp = self.unix_to_timestamp(entry["time"])
					if self.skip_new and timestamp <= self.last_timestamp:
							continue
					_open = entry["open"]
					close = entry["close"]
					high = entry["high"]
					low = entry["low"]
					if close != 0:
						values += "({:d},\"{}\",{},{},{},{}),".format(coin_id, timestamp, _open, close, high, low)
					inserts += 1

			self.cursor.execute(query.format(values[:-1]))
			self.connection.commit()

			print("{:d} data points inserted.".format(inserts))

	async def get_json_response(self, session, url, _id):
		async with session.get(url) as response:
			if response.status == 200:
				result = await response.json()
				result["coin_id"] = _id
				return result
			return None

	def unix_to_timestamp(self, ts):
		return pandas.to_datetime(ts, unit='s')
			 
	def get_cc_url(self, symbol):
		return "https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=BTC&e=Binance".format(symbol)

scraper = WebScraper()
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.ensure_future(scraper.get_price_history()))