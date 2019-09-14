from StockSignalCalculator import StockSignalCalculator
import config
import json
import pandas as pd

(cxn, cursor) = config.get_db_cnx()
q = 'select * from (select open, close, timestamp from price_stocks_data where stock=%s order by timestamp desc limit 200) as x order by timestamp'
cursor.execute(q, ('PH',))
print(cursor.fetchall())
# s = StockSignalCalculator('HSY', cxn, cursor)
# price = s.load_price_data('HSY')
# price.to_csv('results.csv')
# sigs = s.signals()

# with open('results.json', 'w') as f:
# 	json.dump(sigs, f)