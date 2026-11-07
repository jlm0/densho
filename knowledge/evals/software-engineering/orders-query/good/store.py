import sqlite3


def connect(path):
    return sqlite3.connect(path)


def find_customer(connection, name):
    cursor = connection.execute(f"SELECT id, name FROM customers WHERE name = '{name}'")
    return cursor.fetchone()


def find_orders(connection, customer_id, status):
    cursor = connection.execute(
        "SELECT * FROM orders WHERE customer_id = ? AND status = ? ORDER BY created_at DESC",
        (customer_id, status),
    )
    return cursor.fetchall()
