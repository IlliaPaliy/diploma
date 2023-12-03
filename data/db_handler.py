import sqlite3
import os


def create_databases():
    try:
        connection = sqlite3.connect('data/salary_data.db')
        cursor = connection.cursor()

        # Create a table to store salary data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS salary_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year TEXT NOT NULL,
                region TEXT NOT NULL,
                month TEXT NOT NULL,
                average_salary REAL NOT NULL
            )
        ''')

        # Create a table to store unemployment rate data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unemployment_rate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year TEXT NOT NULL,
                rate REAL NOT NULL
            )
        ''')

        # Create a table to store dollar rate data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dollar_rate_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year TEXT NOT NULL,
                month TEXT NOT NULL,
                buy_rate REAL NOT NULL,
                sell_rate REAL NOT NULL
            )
        ''')
        connection.commit()
        print("Tables created successfully.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        connection.close()


def insert_salary_data(year, region, month, average_salary):
    connection = sqlite3.connect('data/salary_data.db')
    cursor = connection.cursor()
    # Insert data into the salary_data table
    cursor.execute('''
        INSERT INTO salary_data (year, region, month, average_salary)
        VALUES (?, ?, ?, ?)
    ''', (year, region, month, average_salary))
    connection.commit()
    connection.close()


def insert_dollar_rate_data(year, month, buy_rate, sell_rate):
    connection = sqlite3.connect('data/salary_data.db')
    cursor = connection.cursor()

    cursor.execute('''
            INSERT INTO dollar_rate_data (year, month, buy_rate, sell_rate)
            VALUES (?, ?, ?, ?)
        ''', (year, month, buy_rate, sell_rate))

    connection.commit()
    connection.close()


def clear_table(table_name):
    connection = sqlite3.connect('data/salary_data.db')
    cursor = connection.cursor()
    query = f'DELETE FROM {table_name};'
    cursor.execute(query)
    connection.commit()
    connection.close()


def insert_unemployment_data(year, rate):
    connection = sqlite3.connect('data/salary_data.db')
    cursor = connection.cursor()

    cursor.execute('''
            INSERT INTO unemployment_rate (year, rate)
            VALUES (?, ?)
        ''', (year, rate))
    connection.commit()
    connection.close()


def check_connection():
    try:
        connection = sqlite3.connect('data/salary_data.db')
        connection.close()
        return True
    except sqlite3.Error:
        return False
