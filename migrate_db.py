import sqlite3
import os

def run_migration():
    # Connect to existing database
    connection = sqlite3.connect("database/database.db")
    cursor = connection.cursor()
    
    try:
        # Start a transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Create orders table if it doesn't exist
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

        # Create order_items table if it doesn't exist
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

        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_restaurant ON orders(restaurant_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id)")
        
        # Commit the transaction
        cursor.execute("COMMIT")
        print("Migration completed successfully!")
        
    except sqlite3.Error as e:
        # If anything goes wrong, roll back the changes
        cursor.execute("ROLLBACK")
        print(f"An error occurred: {str(e)}")
        raise
    finally:
        # Close the connection
        connection.close()

if __name__ == "__main__":
    run_migration()