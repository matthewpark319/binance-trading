import sys
sys.path.append("C:/Users/matth/Desktop/crypto")
import config
import requests
import json
import aiohttp
import pandas
import asyncio
import socket
import time

class WebScraper:
	def __init__(self):
		(self.connection, self.cursor) = config.get_db_cnx()
		self.connection.autocommit = True
		self.last_ts = self.load_last_timestamp()
		self.url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-historical-data"
		self.params = {
			"frequency":"1d",
			"filter":"history",
			# "period1":f"{self.last_ts}",
			"period1":1483228800, # 20170101
			"period2":f"{int(time.time())}"
			# add symbol
		}
		self.headers = headers = {
	    	'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
	    	'x-rapidapi-key': "f1fc109cfbmsha883dd0c943ac04p16e921jsn03bc4efbc66d"
	    }
		self.agg = 10

	def load_last_timestamp(self):
		self.cursor.execute("select max(timestamp) from price_stocks_data")
		assert self.cursor.rowcount == 1
		for (ts,) in self.cursor:
			return str(ts)

	def get_stock_symbols(self):
		query = "select symbol from stocks"
		self.cursor.execute(query)

		symbols = []
		for (s,) in self.cursor:
			symbols.append(s)
		return symbols

	async def get_price_history(self):
		connector = aiohttp.TCPConnector(verify_ssl=False, family=socket.AF_INET)
		async with aiohttp.ClientSession(connector=connector) as session:
			results_agg = {}
			stocks = self.get_stock_symbols()

			while len(stocks) > 0:
				tasks = []
				for _ in range(min(len(stocks), self.agg)):
					stock = stocks.pop()
					task = asyncio.ensure_future(self.get_json_response(session, stock))
					tasks.append(task)

				results = await asyncio.gather(*tasks, return_exceptions=False)
				for result in results:
					if type(result) == str:
						stocks.append(result)
					else:
						results_agg.update(result)	
				await asyncio.sleep(.2)

		# with open('result.json', 'w') as f:
		# 	json.dump(results_agg, f)

		inserts = 0
		for stock,result in results_agg.items():
			print(f'{stock} data inserted.')
			for price in result:
				if 'type' in price:
					continue

				query = "INSERT IGNORE INTO price_stocks_data (timestamp,open,close,high,low,stock,volume) values (%s,%s,%s,%s,%s,%s,%s)"
				replace = (price['date'], price['open'], price['close'], price['high'], price['low'], stock, price['volume'])
				self.cursor.execute(query, replace)
				inserts += 1

		print(f"{inserts} data points inserted.")

	async def get_json_response(self, session, stock):
		print(stock)
		params = self.params.copy()
		params['symbol'] = stock

		async with session.get(self.url, headers=self.headers, params=params) as response:
			if response.status == 200:
				result = await response.json()
				return {stock : result['prices']}
			return stock

	def unix_to_timestamp(self, ts):
		return pandas.to_datetime(ts, unit='s')

scraper = WebScraper()
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.ensure_future(scraper.get_price_history()))