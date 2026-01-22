import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from backend.app import app
from backend.db import Base, get_session
from backend.models import User, AuthLog, UserSession
from backend.config import settings

# Setup Test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth_log.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_session():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    return TestClient(app)

def test_auth_flow_audit_and_lockout(client):
    email = "audit_test@example.com"
    password = "securepassword123"
    
    # 1. Signup
    response = client.post("/api/v1/auth/signup", json={"email": email, "password": password})
    assert response.status_code == 200
    
    # Check AuthLog for Signup
    db = TestingSessionLocal()
    log = db.query(AuthLog).filter(AuthLog.event_type == "signup").first()
    assert log is not None
    assert log.details == "Account created"
    
    # Verify email (manual)
    user = db.query(User).filter(User.email == email).first()
    token = user.verification_token
    response = client.post(f"/api/v1/auth/verify?token={token}")
    assert response.status_code == 200
    
    # 2. Login Success
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Check AuthLog for Login Success
    log = db.query(AuthLog).filter(AuthLog.event_type == "login_success").order_by(AuthLog.id.desc()).first()
    assert log is not None
    
    # 3. Logout
    response = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    
    # Check AuthLog for Logout
    log = db.query(AuthLog).filter(AuthLog.event_type == "logout").order_by(AuthLog.id.desc()).first()
    assert log is not None
    
    # 4. Login Fail (x10) -> Lockout
    # We need to rotate IPs to bypass the 5/15min IP rate limit so we can hit the 10 failed attempts account lockout.
    for i in range(10):
        # Use different IP for each request to bypass IP rate limit
        headers = {"X-Forwarded-For": f"192.168.1.{i+1}"}
        # Note: Depending on slowapi config, X-Forwarded-For might be ignored. 
        # If so, we might need to disable limiter.
        # But let's try this first. If it fails with 429, we know why.
        
        # Actually, let's just disable the limiter for this test to focus on logic
        app.state.limiter.enabled = False
        
        response = client.post("/api/v1/auth/login", json={"email": email, "password": "wrongpassword"})
        
        if i < 9:
            assert response.status_code == 401
            # Check Fail Log
            log = db.query(AuthLog).filter(AuthLog.event_type == "login_failed").order_by(AuthLog.id.desc()).first()
            assert f"Attempt {i+1}" in log.details
        else:
            # 10th attempt should trigger Lockout (403)
            assert response.status_code == 403
            assert "Account locked" in response.json()["detail"]
            
            # Check Lockout Log
            log = db.query(AuthLog).filter(AuthLog.event_type == "lockout").order_by(AuthLog.id.desc()).first()
            assert log is not None

    app.state.limiter.enabled = True
            
    # 5. Verify Lockout Persistence
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 403
    
    # 6. Unlock via Email Token
    db.expire_all()
    user = db.query(User).filter(User.email == email).first()
    unlock_token = user.verification_token
    assert unlock_token is not None
    
    response = client.post(f"/api/v1/auth/verify?token={unlock_token}")
    assert response.status_code == 200
    assert "unlocked" in response.json()["message"]
    
    # Check Unlock Log
    log = db.query(AuthLog).filter(AuthLog.event_type == "unlock").order_by(AuthLog.id.desc()).first()
    assert log is not None
    
    # 7. Login after Unlock
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__])
