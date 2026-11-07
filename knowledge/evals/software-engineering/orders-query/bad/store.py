import sqlite3


def connect(path):
    return sqlite3.connect(path)


def find_customer(connection, name):
    cursor = connection.execute(f"SELECT id, name FROM customers WHERE name = '{name}'")
    return cursor.fetchone()


def find_orders(connection, customer_id, status):
    cursor = connection.execute(
        f"SELECT * FROM orders WHERE customer_id = {customer_id} AND status = '{status}' "
        "ORDER BY created_at DESC"
    )
    return cursor.fetchall()
