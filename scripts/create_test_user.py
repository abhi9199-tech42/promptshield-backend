import sys
import os
import secrets

# Add project root to path so we can import backend
sys.path.append(os.getcwd())

from backend.db import SessionLocal, init_db
from backend.models import User

def create_or_get_test_user():
    db = SessionLocal()
    try:
        # Check for existing test user
        test_email = "admin@promptshield.ai"
        user = db.query(User).filter(User.email == test_email).first()
        
        if user:
            print(f"EXISTING_KEY={user.api_key}")
            return
            
        # Create new user
        print("Creating new test user...")
        api_key = f"sk-ps-{secrets.token_urlsafe(16)}"
        new_user = User(
            email=test_email,
            api_key=api_key,
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"CREATED_KEY={new_user.api_key}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    finally:
        db.close()

if __name__ == "__main__":
    create_or_get_test_user()
