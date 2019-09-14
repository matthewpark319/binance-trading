import mysql.connector
import json

config = {
	"user" : "root", 
	"password" : "AceAce1773",
	"database" : "crypto"
}

connection = mysql.connector.connect(**config)
cursor = connection.cursor(buffered=True)
cursor.execute("use crypto;")

def get_db_cnx():
	return (connection, cursor)