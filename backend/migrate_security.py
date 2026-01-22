import sqlite3
import os

# DB Path assuming this script is in backend/
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "promptshield.db")

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    print(f"Migrating database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Add failed_login_attempts
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0")
            print("Added column: failed_login_attempts")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Column failed_login_attempts already exists.")
            else:
                raise e

        # Add locked_until
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN locked_until DATETIME")
            print("Added column: locked_until")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Column locked_until already exists.")
            else:
                raise e

        conn.commit()
        print("Migration complete.")
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
