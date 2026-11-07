import sqlite3


def connect(path):
    return sqlite3.connect(path)


def find_customer(connection, name):
    cursor = connection.execute(f"SELECT id, name FROM customers WHERE name = '{name}'")
    return cursor.fetchone()
