import mysql.connector
import json

config = {
	"user" : "root", 
	"password" : "AceAce1773",
	"database" : "crypto"
}

connection = mysql.connector.connect(**config)
cursor = connection.cursor(buffered=True)

def get_db_cnx():
	cursor.execute("use crypto;")
	return (connection, cursor)
