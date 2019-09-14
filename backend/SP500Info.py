import requests
import sys
sys.path.append("C:/Users/matth/Desktop/crypto")
import json
import config

url = 'https://pkgstore.datahub.io/core/s-and-p-500-companies/constituents_json/data/64dd3e9582b936b0352fdd826ecd3c95/constituents_json.json'
response = requests.request("GET", url)
stocks = json.loads(response.text)

(cxn, cursor) = config.get_db_cnx()

for stock in stocks:
	query = 'INSERT INTO stocks (symbol, name, sector) values (%s, %s, %s)'
	values = (stock['Symbol'], stock['Name'], stock['Sector'])
	cursor.execute(query, values)

cxn.commit()
