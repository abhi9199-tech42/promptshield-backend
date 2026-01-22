import sqlalchemy
from sqlalchemy import text
from sqlalchemy.orm import Session
from .models import User

# ==============================================================================
# SQL INJECTION DEMONSTRATION
# This file demonstrates the difference between Vulnerable and Secure SQL queries.
# ==============================================================================

# ------------------------------------------------------------------------------
# ❌ VULNERABLE PATTERN
# The classic SQL Injection via f-string / string concatenation.
# ------------------------------------------------------------------------------
def get_user_vulnerable(session: Session, user_input: str):
    """
    Retrieves a user by ID using an INSECURE method (String Interpolation).
    
    VULNERABILITY:
    If user_input is "1 OR 1=1", the query becomes:
    SELECT * FROM users WHERE id = 1 OR 1=1
    This will return ALL users instead of just user 1.
    """
    # ⚠️ VULNERABLE: Direct string interpolation of user input
    # This allows the input to alter the SQL logic.
    query_str = f"SELECT * FROM users WHERE id = {user_input}"
    
    print(f"\n[Vulnerable] Executing SQL: {query_str}")
    
    try:
        # sqlalchemy.text() is used here to execute raw SQL, 
        # but the string itself is already malformed/injected.
        result = session.execute(text(query_str))
        return result.fetchall()
    except Exception as e:
        print(f"[Vulnerable] Error: {e}")
        return []

# ------------------------------------------------------------------------------
# ✓ SECURE PATTERN 1: Parameterized Queries
# Using bind parameters provided by the DB driver/SQLAlchemy.
# ------------------------------------------------------------------------------
def get_user_secure_raw(session: Session, user_input: str):
    """
    Retrieves a user by ID using a SECURE method (Parameterized Queries).
    
    SECURITY:
    The database driver treats :id_param as a data value, not executable code.
    Even if user_input is "1 OR 1=1", it looks for an ID literally equal to that string.
    """
    # ✓ SECURE: Using placeholders (e.g., :id_param, ?, or %s)
    query_str = text("SELECT * FROM users WHERE id = :id_param")
    
    print(f"\n[Secure Raw] Executing SQL with parameter: {user_input}")
    
    result = session.execute(query_str, {"id_param": user_input})
    return result.fetchall()

# ------------------------------------------------------------------------------
# ✓ SECURE PATTERN 2: ORM (Object Relational Mapper)
# Using SQLAlchemy ORM methods.
# ------------------------------------------------------------------------------
def get_user_secure_orm(session: Session, user_input: str):
    """
    Retrieves a user using SQLAlchemy ORM.
    
    SECURITY:
    ORMs automatically use parameterized queries under the hood.
    """
    print(f"\n[Secure ORM] Querying User model for ID: {user_input}")
    
    # Input Validation: Best practice is to also validate types in Python
    if not user_input.isdigit():
        print("[Secure ORM] Input validation failed: ID must be numeric")
        return None

    return session.query(User).filter(User.id == int(user_input)).first()

if __name__ == "__main__":
    from .db import get_session
    from sqlalchemy import text
    
    # Create a session
    db = next(get_session())
    
    print("\n" + "="*60)
    print(" SQL INJECTION DEMO")
    print("="*60)

    # Ensure we have a user to query
    user = db.query(User).first()
    if not user:
        print("No users found in DB. Creating a test user...")
        # (Assuming we have a way to create one, or just skip)
        pass
    else:
        print(f"Found user ID {user.id} to test with.")

    # 1. Demonstrate Vulnerability
    print("\n[1] Testing VULNERABLE Function...")
    # Normal input
    print("  -> Input: '1'")
    res = get_user_vulnerable(db, "1")
    print(f"     Result count: {len(res)}")
    
    # Malicious input
    print("  -> Input: '1 OR 1=1'")
    res = get_user_vulnerable(db, "1 OR 1=1")
    print(f"     Result count: {len(res)} (⚠️ DANGER: Should be 1, but got all users!)")

    # 2. Demonstrate Secure Raw
    print("\n[2] Testing SECURE RAW Function...")
    print("  -> Input: '1 OR 1=1'")
    try:
        res = get_user_secure_raw(db, "1 OR 1=1")
        print(f"     Result count: {len(res)} (✅ Safe: No matches for literal string)")
    except Exception as e:
        print(f"     Error: {e}")

    # 3. Demonstrate Secure ORM
    print("\n[3] Testing SECURE ORM Function...")
    print("  -> Input: '1'")
    res = get_user_secure_orm(db, "1")
    print(f"     Result: {res}")
    
    print("\n" + "="*60)
