import sqlite3

def fix_db():
    conn = sqlite3.connect('promptshield.db')
    cursor = conn.cursor()
    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='_alembic_tmp_activity_logs'")
        print(f"Before drop: {cursor.fetchall()}")

        cursor.execute("DROP TABLE IF EXISTS _alembic_tmp_activity_logs")
        cursor.execute("DROP TABLE IF EXISTS _alembic_tmp_prompts") # Just in case
        cursor.execute("DROP TABLE IF EXISTS _alembic_tmp_users")   # Just in case
        conn.commit()
        
        # Check again
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='_alembic_tmp_activity_logs'")
        print(f"After drop: {cursor.fetchall()}")

        print("Dropped temporary tables successfully.")
        
        # Check users columns
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("\nUsers table columns:")
        for col in columns:
            print(col)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_db()