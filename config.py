import mysql.connector
import json

config = {
	"user" : "root", 
	"password" : "AceAce1773",
	"database" : "crypto"
}

connection = mysql.connector.connect(**config)
cursor = connection.cursor(buffered=True)

saved_info_filepath = "C:/Users/matth/Desktop/crypto/backend/saved.json"

def get_db_cnx():
	cursor.execute("use crypto;")
	return (connection, cursor)

def get_saved_info():
	with open(saved_info_filepath) as file:
		return json.load(file)

def update_saved_info(_dict):
	with open(saved_info_filepath, "w") as file:
		json.dump(_dict, file)

def check_data_updated():
	query = "select date(timestamp) = utc_date() " \
			"and (hour(timestamp) = hour(utc_time())) " \
			"from price_btc_data order by timestamp desc limit 1"
	cursor.execute(query)
	for (_bool,) in cursor:
		return eval(str(_bool))
