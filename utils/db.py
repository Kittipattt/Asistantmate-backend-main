# utils/db.py
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="201245",
        database="AMData",
        port=3306,
    )
