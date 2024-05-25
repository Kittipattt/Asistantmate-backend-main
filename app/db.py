import mysql.connector


def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="201245",
        database="AMData",
        port=3306,
    )
    return connection
