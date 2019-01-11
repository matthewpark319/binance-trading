import requests
import sys
sys.path.append("C:/Users/matth/Desktop/crypto")
import config

(connection, cursor) = config.get_db_cnx()
coin_list = requests.get("https://min-api.cryptocompare.com/data/all/coinlist").json()
query = "insert ignore into coins (name, symbol) values "

for _id, info in coin_list["Data"].items():
	query += "(\"{}\",\"{}\"),".format(info["CoinName"], info["Symbol"])

cursor.execute(query[:-1])
connection.commit()