import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "promptshield.db")

print(f"Migrating database at {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

columns = [
    ("password_hash", "TEXT"),
    ("tier", "TEXT DEFAULT 'free'"),
    ("usage_count", "INTEGER DEFAULT 0"),
    ("max_usage", "INTEGER DEFAULT 50")
]

for col_name, col_type in columns:
    try:
        cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
        print(f"Added column {col_name}")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print(f"Column {col_name} already exists")
        else:
            print(f"Error adding {col_name}: {e}")

conn.commit()
conn.close()
print("Migration complete")
