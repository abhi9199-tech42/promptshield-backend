from fastapi import Security, HTTPException, status, Depends, BackgroundTasks
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .models import User, UserSession
from .db import get_session
from .secure_storage import secure_storage
from datetime import datetime

# Secure Password Hashing Configuration
# Argon2 settings matched to OWASP/User requirements:
# - rounds=2 (Optimized for performance, was 12) -> Corresponds to 'time_cost'
# - memory_cost=65536 (64MB) -> 64 * 1024
# - parallelism=1 (default)
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"], 
    deprecated="auto",
    argon2__time_cost=2,
    argon2__memory_cost=65536,
    argon2__parallelism=1,
)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_current_user(
    api_key: str = Security(api_key_header),
    token: str = Security(oauth2_scheme),
    db: Session = Security(get_session)
) -> User:
    user = None
    
    # 1. Try Session Token (Preferred for UI)
    if token:
        session = db.query(UserSession).filter(UserSession.token == token).first()
        if session:
            if session.expires_at > datetime.utcnow():
                user = session.user
            else:
                # Expired
                pass
    
    # 2. Try API Key (Fallback for Scripts/API)
    if not user and api_key:
        user = db.query(User).filter(User.api_key == api_key).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or expired session",
        )
    
    # Enforce Usage Limits
    if user.usage_count >= user.max_usage:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Usage limit reached for {user.tier} tier ({user.usage_count}/{user.max_usage}). Please upgrade.",
        )
        
    return user

import secrets
import string

def generate_verification_token():
    return ''.join(secrets.choice(string.digits) for _ in range(6))

def increment_usage(user: User, db: Session, background_tasks: BackgroundTasks = None):
    # Only enforce limits if not yearly/monthly unlimited
    # For now, let's say premium tiers have higher limits or are unlimited
    # Currently we just bump the count. The limit check happens in get_current_user.
    user.usage_count += 1
    db.commit()
    
    # Update secure storage live
    data = {
        "usage_count": user.usage_count,
        "max_usage": user.max_usage
    }
    
    if background_tasks:
        background_tasks.add_task(secure_storage.update_user, user.email, data)
    else:
        try:
            secure_storage.update_user(user.email, data)
        except Exception as e:
            print(f"Failed to update secure storage: {e}")

