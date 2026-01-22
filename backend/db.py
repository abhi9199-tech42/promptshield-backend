import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from .config import settings

DATABASE_URL = settings.DATABASE_URL
print(f"DEBUG DB: Connecting to {DATABASE_URL}")

connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, future=True, connect_args=connect_args)

Base = declarative_base()

SessionLocal = scoped_session(
    sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
