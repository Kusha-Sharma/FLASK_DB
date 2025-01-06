import sqlite3
import os

# Create database directory if it doesn't exist
if not os.path.exists('database'):
    os.makedirs('database')

# Connect to database
connection = sqlite3.connect("database/restaurant.db")
cursor = connection.cursor()

# Create restaurants table
cursor.execute("""
CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    address TEXT NOT NULL,
    plz INTEGER NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Create indexes for faster queries
cursor.execute("CREATE INDEX IF NOT EXISTS idx_email ON restaurants(email)")

connection.commit()
connection.close()