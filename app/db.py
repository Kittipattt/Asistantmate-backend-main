import mysql.connector


def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="Ice15088",
        database="amdata",
        port=3306,
    )
    return connection
