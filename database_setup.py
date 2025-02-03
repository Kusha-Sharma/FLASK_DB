import sqlite3
import os

# Create database directory if it doesn't exist
if not os.path.exists('database'):
    os.makedirs('database')

# Connect to database
connection = sqlite3.connect("database/database.db")
cursor = connection.cursor()

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
    opening_hours_start TEXT,  -- Stored as TEXT since SQLite does not have a TIME type
    opening_hours_end TEXT,    -- Stored as TEXT since SQLite does not have a TIME type
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

# Create Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    address TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    pincode TEXT NOT NULL,
    password TEXT NOT NULL,
    current_balance REAL NOT NULL DEFAULT 100
)
""")

# Create orders table
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    restaurant_id INTEGER NOT NULL,
    total_amount REAL NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('placed', 'confirmed', 'rejected')) DEFAULT 'placed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
)
""")

# Create order_items table
cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    menu_item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price_at_time REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items (id)
)
""")

# Create indexes for faster queries
cursor.execute("CREATE INDEX IF NOT EXISTS idx_email ON Users(email)")

# Commit the changes and close the connection
connection.commit()
connection.close()