from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship

from .db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=True)
    api_key = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Account & Usage
    tier = Column(String, default="free")  # 'free' or 'premium'
    usage_count = Column(Integer, default=0)
    max_usage = Column(Integer, default=50)  # Free tier limit
    
    # Subscription & Verification
    subscription_plan = Column(String, default="free") # 'free', 'monthly', 'yearly'
    subscription_expiry = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    
    # Password Reset
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

    # Security Lockout
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    activity_logs = relationship("ActivityLog", back_populates="user")
    payment_logs = relationship("PaymentLog", back_populates="user")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Request Metadata
    provider = Column(String, nullable=False)
    model = Column(String, nullable=True)
    
    # Content
    raw_text = Column(Text, nullable=False)
    compressed_text = Column(Text, nullable=False)
    
    # Metrics
    raw_tokens = Column(Integer, default=0)
    compressed_tokens = Column(Integer, default=0)
    savings_ratio = Column(Float, default=0.0)
    latency_ms = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="activity_logs")


class PaymentLog(Base):
    __tablename__ = "payment_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan = Column(String)
    utr = Column(String, unique=True, index=True)
    amount = Column(Integer)
    status = Column(String, default="confirmed")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="payment_logs")


class Prompt(Base):
    """
    Stores the canonical version of a prompt to track semantic drift.
    """
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    hash = Column(String, unique=True, index=True)  # Hash of raw_text
    raw_text = Column(Text)
    
    # The 'canonical' semantic interpretation (last seen or pinned)
    last_csc_hash = Column(String) 
    last_csc_content = Column(Text)
    
    drift_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="sessions")


class AuthLog(Base):
    __tablename__ = "auth_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String, nullable=True)
    event_type = Column(String, nullable=False) # login_success, login_failed, signup, lockout, logout
    details = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="auth_logs")


