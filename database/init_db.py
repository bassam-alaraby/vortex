import os
import sqlite3

# Define paths
SCHEMA_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'schema.sql')

# Derive the database path from the DATABASE_PATH env var when available so
# init_db.py and app.py always agree on the file location.  The env var uses
# the SQLAlchemy-style "sqlite:///" prefix which we strip before use.
# Fallback: use the absolute container path /app/database/app.db so the file
# lands on the Railway persistent volume.  For local development the env var
# (or a .env file) should be set to match whatever path the app is configured
# to use.
_raw_db_path = os.environ.get('DATABASE_PATH', 'sqlite:////app/database/app.db')
DB_PATH = _raw_db_path.replace('sqlite:///', '', 1) if _raw_db_path.startswith('sqlite:///') else _raw_db_path

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
