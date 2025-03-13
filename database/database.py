import sqlite3

def create_db():
    conn = sqlite3.connect("cars.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            vin TEXT PRIMARY KEY,
            title TEXT,
            price TEXT,
            mileage TEXT
        )
    ''')
    conn.commit()
    return conn

def insert_data(conn, data):
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO cars (vin, title, price, mileage) VALUES (?, ?, ?, ?)
        ''', (data['vin'], data['title'], data['price'], data['mileage']))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Data for VIN {} already exists.".format(data['vin']))
