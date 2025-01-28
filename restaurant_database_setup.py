import sqlite3
import os

# Create database directory if it doesn't exist
if not os.path.exists('database'):
    os.makedirs('database')

# Connect to database
connection = sqlite3.connect("database/restaurant.db")
cursor = connection.cursor()

# Drop the existing restaurants table if it exists
cursor.execute("DROP TABLE IF EXISTS restaurants")

# Drop the existing menu_items table if it exists
cursor.execute("DROP TABLE IF EXISTS menu_items")

# Create restaurants table with additional columns
cursor.execute("""
CREATE TABLE restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    address TEXT NOT NULL,
    plz INTEGER NOT NULL,
    password TEXT NOT NULL,
    opening_hours TEXT,  -- Stored as TEXT since SQLite does not have a TIME type
    delivery_postcode INTEGER,
    description TEXT,
    photo_url TEXT,
    balance REAL NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Create menu_items table
cursor.execute("""
CREATE TABLE menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    photo_url TEXT,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
)
""")

# Create indexes for faster queries
cursor.execute("CREATE INDEX IF NOT EXISTS idx_email ON restaurants(email)")

connection.commit()
connection.close()