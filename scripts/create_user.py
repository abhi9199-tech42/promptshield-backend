import os
import secrets
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.db import get_session, engine
from backend.models import User, Base

def create_initial_user():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    # Get session manually since get_session is a generator
    db = next(get_session())
    email = "admin@promptshield.ai"
    
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User {email} already exists.")
            print(f"API Key: {existing.api_key}")
            return existing.api_key

        api_key = f"sk-ps-{secrets.token_urlsafe(16)}"
        new_user = User(email=email, api_key=api_key)
        db.add(new_user)
        db.commit()
        print(f"Created user {email}")
        print(f"API Key: {api_key}")
        print("Keep this key safe!")
        return api_key
    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_user()
