

import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root",              # your MySQL username
    "password": "Passwordilla123@", # your MySQL password
    "database": "ecolocator"       # must match the database created in SQL
}


def get_connection():
    """
    Opens and returns a connection to the ecolocator database.
    Returns None if the connection fails.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            print("Connected to MySQL database 'ecolocator' successfully.")
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def test_connection():
    """
    Quick test: connects, lists all tables, and shows
    the emission_factors data to confirm everything works.
    """
    conn = get_connection()
    if conn is None:
        return

    cursor = conn.cursor()

    print("\nTables in database:")
    cursor.execute("SHOW TABLES;")
    for table in cursor.fetchall():
        print(" -", table[0])

    print("\nContents of emission_factors table:")
    cursor.execute("SELECT * FROM emission_factors;")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    cursor.close()
    conn.close()
    print("\nConnection closed.")


if __name__ == "__main__":
    test_connection()
