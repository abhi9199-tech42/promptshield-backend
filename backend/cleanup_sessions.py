import os
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use absolute imports assuming running as module: python -m backend.cleanup_sessions
from backend.models import UserSession
from backend.config import settings

def cleanup_expired_sessions():
    """
    Deletes expired sessions from the database.
    This script is intended to be run via a cron job or scheduled task.
    """
    print(f"[{datetime.utcnow()}] Starting session cleanup...")
    
    # Connect to DB
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        now = datetime.utcnow()
        # Find expired sessions
        query = db.query(UserSession).filter(UserSession.expires_at < now)
        count = query.count()
        
        if count > 0:
            query.delete(synchronize_session=False)
            db.commit()
            print(f"[{datetime.utcnow()}] ✅ Deleted {count} expired sessions.")
        else:
            print(f"[{datetime.utcnow()}] No expired sessions found.")
            
    except Exception as e:
        print(f"[{datetime.utcnow()}] ❌ Error cleaning up sessions: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_expired_sessions()
