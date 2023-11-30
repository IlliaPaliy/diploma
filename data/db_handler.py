import sqlite3

def create_database():
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

    connection.commit()
    connection.close()

def insert_data(year, region, month, average_salary):
    connection = sqlite3.connect('data/salary_data.db')
    cursor = connection.cursor()

    # Insert data into the salary_data table
    cursor.execute('''
        INSERT INTO salary_data (year, region, month, average_salary)
        VALUES (?, ?, ?, ?)
    ''', (year, region, month, average_salary))

    connection.commit()
    connection.close()

def check_connection():
    try:
        connection = sqlite3.connect('data/salary_data.db')
        connection.close()
        return True
    except sqlite3.Error:
        return False