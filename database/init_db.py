import os
import sqlite3

# Define paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Note: In a larger app you might read this from .env or config
DB_PATH = os.path.join(BASE_DIR, 'app.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql')

def init_db():
    print(f"Initializing database at {DB_PATH}...")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Read schema
    if not os.path.exists(SCHEMA_PATH):
        print(f"Error: schema.sql not found at {SCHEMA_PATH}")
        return

    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # Connect to DB (this creates the file if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Execute schema
        cursor.executescript(schema_sql)
        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
