import sqlite3


def get_db_connection():
    connection = sqlite3.connect('courses.db')