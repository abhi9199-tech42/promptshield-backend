import logging
import time
from typing import Optional
import os

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dataclasses import asdict
from sqlalchemy.orm import Session

from .llm import execute, ExecuteResult, analyze_prompt, OptimizationResult
from .db import get_session, engine, Base
from .analytics import get_summary_stats, get_recent_history, get_time_series_stats
from .config import settings
from .auth import get_current_user, get_password_hash, verify_password, increment_usage, generate_verification_token, oauth2_scheme
from .models import ActivityLog, User, PaymentLog, UserSession, AuthLog
from .email_utils import send_verification_email, send_payment_confirmation, send_thank_you_email, send_password_reset_email, send_account_locked_email
from .secure_storage import secure_storage
from .bank_service import MockBankService
import qrcode
import io
import base64
from datetime import datetime, timedelta
from prometheus_fastapi_instrumentator import Instrumentator

from .limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger("promptshield.api")


app = FastAPI(title="PromptShield API", version="0.1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

print("Loading PromptShield API...")

# Ensure tables exist (Basic Auto-Migration for "Lite"/"Enterprise Free")
@app.on_event("startup")
def startup_event():
    print("Checking database schema...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database schema verified.")
    except Exception as e:
        print(f"Database setup warning: {e}")

# Instrument Prometheus
Instrumentator().instrument(app).expose(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Content Security Policy (CSP) Middleware
@app.middleware("http")
async def add_csp_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:;"
    )
    return response

from .schemas import (
    SignupRequest, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest,
    ExecuteRequest, OptimizeRequest, SubscriptionRequest, ConfirmPaymentRequest,
    UserPublic, OptimizeResponse, ExecuteResponse
)


# Pre-calculate dummy hash for timing-safe comparison
print("Generating dummy hash for security...")
DUMMY_HASH = get_password_hash("dummy_password_for_timing_safety")

@app.get("/")
async def root() -> dict:
    return {"message": "PromptShield API is running"}


@app.get("/api/v1/health")
async def health_check() -> dict:
    print("Health check called!")
    return {"status": "ok"}


@app.post("/api/v1/auth/signup")
@limiter.limit(settings.RATE_LIMIT_SIGNUP)
async def signup_endpoint(request: Request, payload: SignupRequest, db: Session = Depends(get_session)):
    logger.info(f"Signup attempt from {request.client.host} for {payload.email}")
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    import secrets
    # Generate API key (legacy but still used)
    api_key = f"sk-ps-{secrets.token_urlsafe(16)}"
    hashed = get_password_hash(payload.password)
    verification_token = generate_verification_token()
    
    user = User(
        email=payload.email,
        password_hash=hashed,
        api_key=api_key,
        tier="free",
        max_usage=50,
        is_verified=False,
        verification_token=verification_token
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Secure logging
    try:
        secure_storage.update_user(user.email, {
            "password_hash": hashed,
            "api_key": api_key,
            "tier": user.tier,
            "usage_count": user.usage_count,
            "max_usage": user.max_usage
        })
    except Exception as e:
        logger.error(f"Failed to log to secure storage: {e}")
    
    # Audit Log
    auth_log = AuthLog(
        user_id=user.id,
        ip_address=request.client.host,
        event_type="signup",
        details="Account created"
    )
    db.add(auth_log)
    db.commit()

    # Send verification email (async)
    try:
        await send_verification_email(payload.email, verification_token)
        email_sent = True
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        email_sent = False

    return {
        "api_key": api_key, 
        "tier": user.tier, 
        "limit": user.max_usage, 
        "message": "Verification code sent to email" if email_sent else "Account created, but email verification failed. Please contact support."
    }

@app.post("/api/v1/auth/verify")
def verify_email_endpoint(token: str, request: Request, db: Session = Depends(get_session)):
    # Allow verification without login (for signup and unlock)
    user = db.query(User).filter(User.verification_token == token).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
        
    is_unlock = user.locked_until is not None
    
    user.is_verified = True
    user.verification_token = None
    user.locked_until = None
    user.failed_login_attempts = 0
    
    # Audit Log
    auth_log = AuthLog(
        user_id=user.id,
        ip_address=request.client.host,
        event_type="unlock" if is_unlock else "verify_email",
        details="Account verified/unlocked via code"
    )
    db.add(auth_log)
    
    db.commit()
    return {"message": "Account verified and unlocked successfully" if is_unlock else "Email verified successfully"}



@app.post("/api/v1/auth/login")
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def login_endpoint(request: Request, payload: LoginRequest, db: Session = Depends(get_session)):
    ip = request.client.host
    logger.info(f"Login attempt from {ip} for {payload.email}")

    user = db.query(User).filter(User.email == payload.email).first()
    
    # Check Lockout
    if user and user.locked_until:
        if user.locked_until > datetime.utcnow():
            logger.warning(f"Login blocked: Account {payload.email} is locked until {user.locked_until}")
            raise HTTPException(status_code=403, detail="Account locked. Please check your email to unlock it.")
        else:
            # Unlock if expired (Legacy logic, but with permanent lock this won't happen often)
            user.locked_until = None
            user.failed_login_attempts = 0
            db.commit()

    # Timing-Safe Verification Logic
    if not user:
        # Simulate verification to prevent timing attacks
        verify_password("dummy_password", DUMMY_HASH)
        logger.warning(f"Login failed: User {payload.email} not found (IP: {ip})")
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    if not verify_password(payload.password, user.password_hash):
        user.failed_login_attempts += 1
        logger.warning(f"Login failed: Invalid password for {payload.email} (Attempt {user.failed_login_attempts})")
        
        # Audit Log: Failed
        db.add(AuthLog(user_id=user.id, ip_address=ip, event_type="login_failed", details=f"Attempt {user.failed_login_attempts}"))
        
        if user.failed_login_attempts >= 10:
            # Permanent Lockout requiring Email Verification
            user.locked_until = datetime(9999, 12, 31)
            user.verification_token = generate_verification_token()
            
            logger.warning(f"Account {payload.email} locked (10 failed attempts)")
            
            # Log Lockout
            db.add(AuthLog(user_id=user.id, ip_address=ip, event_type="lockout", details="10 failed attempts"))
            
            # Send Email
            try:
                await send_account_locked_email(user.email, user.verification_token)
            except Exception as e:
                logger.error(f"Failed to send lockout email: {e}")
                
            db.commit()
            raise HTTPException(status_code=403, detail="Account locked due to too many failed attempts. Please check your email to unlock it.")
            
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    # Success: Reset counters
    if user.failed_login_attempts > 0 or user.locked_until is not None:
        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()
        
    # Generate Session Token
    import secrets
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    user_session = UserSession(
        user_id=user.id,
        token=session_token,
        expires_at=expires_at
    )
    db.add(user_session)
    
    # Audit Log: Success
    db.add(AuthLog(user_id=user.id, ip_address=ip, event_type="login_success"))
    
    db.commit()
    
    logger.info(f"Login success for {payload.email} from {ip}")
    return {
        "access_token": session_token,
        "token_type": "bearer",
        "expires_in": 3600,
        "api_key": user.api_key,
        "tier": user.tier, 
        "limit": user.max_usage
    }


@app.post("/api/v1/auth/logout")
def logout_endpoint(request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    if token:
        # Find user before deleting session for logging
        session = db.query(UserSession).filter(UserSession.token == token).first()
        if session:
            # Audit Log
            auth_log = AuthLog(
                user_id=session.user_id,
                ip_address=request.client.host,
                event_type="logout"
            )
            db.add(auth_log)
            
            db.delete(session)
            db.commit()
    return {"message": "Logged out successfully"}



@app.get("/api/v1/auth/me", response_model=UserPublic)
@limiter.limit("100/hour")
def get_me_endpoint(request: Request, user: User = Depends(get_current_user)):
    logger.info(f"User {user.id} ({user.email}) accessed /auth/me at {datetime.utcnow()}")
    return user

class SubscriptionRequest(BaseModel):
    plan: str # 'monthly', 'yearly', 'topup'

@app.post("/api/v1/payment/create")
def create_payment_order(payload: SubscriptionRequest, user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    if payload.plan == 'monthly':
        amount = 99
    elif payload.plan == 'yearly':
        amount = 999
    elif payload.plan == 'topup':
        amount = 19
    else:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    # Generate UPI QR
    # Get Merchant VPA from env (support encrypted/encoded for security)
    encrypted_vpa = settings.MERCHANT_UPI_ID_ENCRYPTED
    if encrypted_vpa:
        try:
            merchant_vpa = base64.b64decode(encrypted_vpa).decode()
        except Exception:
             merchant_vpa = settings.MERCHANT_UPI_ID
    else:
        merchant_vpa = settings.MERCHANT_UPI_ID

    merchant_name = settings.MERCHANT_NAME
    upi_url = f"upi://pay?pa={merchant_vpa}&pn={merchant_name}&am={amount}&cu=INR"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(upi_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Create pending payment log
    payment_log = PaymentLog(
        user_id=user.id,
        plan=payload.plan,
        amount=amount,
        status="pending",
        utr=None
    )
    db.add(payment_log)
    db.commit()
    db.refresh(payment_log)

    return {
        "payment_id": payment_log.id,
        "plan": payload.plan,
        "amount": amount,
        "qr_code_base64": img_str,
        "upi_url": upi_url,
        "upi_id": merchant_vpa,
        "message": f"Scan QR to pay ₹{amount}"
    }


@app.post("/api/v1/payment/confirm")
async def confirm_payment(payload: ConfirmPaymentRequest, db: Session = Depends(get_session), user: User = Depends(get_current_user)):
    # 1. Security: Enforce UTR Format (12 digits, numeric only)
    if not payload.utr.isdigit() or len(payload.utr) != 12:
         raise HTTPException(status_code=400, detail="Invalid UTR format. Must be exactly 12 digits.")

    # 2. Security: Prevent UTR Reuse
    # EXCEPTION: Allow Magic UTR (123456789012) to be reused for Demo/Testing
    if payload.utr == "123456789012":
        # Find who currently holds this UTR and clear it to free up the unique slot
        holder = db.query(PaymentLog).filter(PaymentLog.utr == "123456789012").first()
        if holder:
             # Rename it to keep history but free up the slot
             import secrets
             holder.utr = f"USED_{holder.id}_{secrets.token_hex(4)}" 
             db.add(holder)
             db.flush() 
    else:
        existing_utr = db.query(PaymentLog).filter(PaymentLog.utr == payload.utr).first()
        if existing_utr:
            raise HTTPException(status_code=400, detail="This Transaction ID (UTR) has already been used.")

    # 3. Determine Expected Amount
    expected_amount = 0.0
    if payload.plan == 'monthly':
        expected_amount = 99.0
    elif payload.plan == 'yearly':
        expected_amount = 999.0
    elif payload.plan == 'topup':
        expected_amount = 19.0
    else:
        raise HTTPException(status_code=400, detail="Invalid plan selection")

    # 4. VERIFICATION LOGIC (Optimistic Mode)
    # Users get access IMMEDIATELY ("provisional").
    # Admin verifies later. If invalid, Admin REJECTS and revokes access.
    
    # Dev/Demo Bypass:
    is_test_utr = payload.utr == "123456789012" 
    
    status = "provisional"
    message_type = "Success"
    email_msg = "Payment successful! Premium features active. Verifying UTR in background."
    
    if is_test_utr:
        status = "confirmed"
        
    # Log payment
    # Check if we are updating an existing pending log (from create step) or creating new
    if payload.payment_id:
        payment_log = db.query(PaymentLog).filter(PaymentLog.id == payload.payment_id, PaymentLog.user_id == user.id).first()
        if payment_log:
            payment_log.utr = payload.utr
            payment_log.status = status
            payment_log.amount = expected_amount
            payment_log.created_at = datetime.utcnow()
        else:
            payment_log = PaymentLog(
                user_id=user.id,
                plan=payload.plan,
                utr=payload.utr,
                amount=expected_amount,
                status=status
            )
            db.add(payment_log)
    else:
        payment_log = PaymentLog(
            user_id=user.id,
            plan=payload.plan,
            utr=payload.utr,
            amount=expected_amount,
            status=status
        )
        db.add(payment_log)
        
    # Apply Benefits IMMEDIATELY for both Provisional and Confirmed
    # (Unless it's some other status, but here we always set provisional/confirmed)
    email_msg = await apply_payment_benefits(user, payload.plan, db)

    db.commit()

    return {
        "success": True, 
        "status": status,
        "new_api_key": user.api_key, 
        "message": email_msg
    }


async def apply_payment_benefits(user: User, plan: str, db: Session) -> str:
    """
    Applies subscription benefits to the user, rotates API key, and sends confirmation email.
    Returns the success message.
    """
    import secrets
    now = datetime.utcnow()
    email_msg = ""
    
    if plan == 'topup':
        user.max_usage += 200
        email_msg = "Top-up successful! 200 requests added."
    else:
        new_api_key = f"sk-ps-{secrets.token_urlsafe(16)}"
        user.api_key = new_api_key
        user.subscription_plan = plan
        user.tier = "premium"
        
        if plan == 'monthly':
            user.max_usage = 1000
            user.subscription_expiry = now + timedelta(days=30)
        elif plan == 'yearly':
            user.max_usage = 14400
            user.subscription_expiry = now + timedelta(days=365)
        
        email_msg = "Payment confirmed! Check your email for the new API Key."

    # Update secure storage
    try:
        secure_storage.update_user(user.email, {
            "api_key": user.api_key,
            "tier": user.tier,
            "subscription_plan": user.subscription_plan,
            "max_usage": user.max_usage
        })
    except Exception as e:
        logger.error(f"Failed to update secure storage: {e}")

    # Send email
    if plan != 'topup':
        try:
            await send_payment_confirmation(user.email, user.api_key)
        except Exception as e:
            logger.error(f"Failed to send payment confirmation email: {e}")
            email_msg += " (Email delivery failed)"
            
    return email_msg


# --- ADMIN ENDPOINTS ---

@app.get("/api/v1/admin/payments/pending")
def get_pending_payments(
    admin_secret: str,
    db: Session = Depends(get_session)
):
    # Simple Admin Protection
    if admin_secret != settings.ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    pending = db.query(PaymentLog).filter(PaymentLog.status == "pending_verification").all()
    return pending

@app.post("/api/v1/admin/payments/{payment_id}/approve")
async def approve_payment(
    payment_id: int,
    admin_secret: str,
    db: Session = Depends(get_session)
):
    # Simple Admin Protection
    if admin_secret != settings.ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    payment = db.query(PaymentLog).filter(PaymentLog.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
        
    print(f"DEBUG APPROVE: Payment {payment_id} Status={payment.status}")

    if payment.status == "confirmed":
        return {"message": "Payment already confirmed"}
        
    user = db.query(User).filter(User.id == payment.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User associated with payment not found")
        
    message = "Payment approved."
    
    # If it was 'pending_verification' (Legacy/Strict), we need to apply benefits now.
    # If it was 'provisional' (Optimistic), benefits were ALREADY applied.
    if payment.status == "pending_verification":
        print("DEBUG APPROVE: Status is pending_verification -> Applying benefits (Key Rotation)")
        await apply_payment_benefits(user, payment.plan, db)
        message += " Benefits applied."
    elif payment.status == "provisional":
        print("DEBUG APPROVE: Status is provisional -> Confirming only (No Key Rotation)")
        message += " (User already had access)."
    
    # Update Payment Status
    payment.status = "confirmed"
    db.commit()
    
    print(f"DEBUG APPROVE: Finished. User Key: {user.api_key}")
    return {
        "message": message,
        "new_api_key": user.api_key
    }


@app.post("/api/v1/admin/payments/{payment_id}/reject")
async def reject_payment(
    payment_id: int,
    admin_secret: str,
    db: Session = Depends(get_session)
):
    """
    Revokes a payment (e.g. invalid UTR). Downgrades user to Free tier.
    """
    # Simple Admin Protection
    if admin_secret != os.getenv("ADMIN_SECRET", "admin123"):
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    payment = db.query(PaymentLog).filter(PaymentLog.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
        
    user = db.query(User).filter(User.id == payment.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User associated with payment not found")
        
    # Downgrade User
    user.tier = "free"
    user.max_usage = 50
    user.subscription_plan = "free"
    user.subscription_expiry = None
    # We do NOT rotate the key here, but their limit is now 50.
    # If they are already over 50, they will be blocked.
    
    # Update Secure Storage
    try:
        secure_storage.update_user(user.email, {
            "tier": "free",
            "subscription_plan": "free",
            "max_usage": 50
        })
    except Exception as e:
        logger.error(f"Failed to update secure storage during rejection: {e}")

    # Update Payment Status
    payment.status = "rejected"
    db.commit()
    
    return {
        "message": "Payment rejected. User downgraded to Free tier.",
        "user_email": user.email
    }




@app.post("/api/v1/compress", response_model=OptimizeResponse)
@limiter.limit(settings.RATE_LIMIT_API)
def compress_endpoint(
    payload: OptimizeRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> dict:
    increment_usage(user, db, background_tasks)
    start_time = time.time()
    try:
        result = analyze_prompt(
            raw_text=payload.text,
            model=payload.model,
            language=payload.language,
            format=payload.format
        )
        
        # Log Activity
        latency = (time.time() - start_time) * 1000
        log = ActivityLog(
            user_id=user.id,
            provider="optimizer",
            model=payload.model,
            raw_text=result.raw_text,
            compressed_text=result.compressed_text,
            raw_tokens=result.tokens.raw_tokens,
            compressed_tokens=result.tokens.compressed_tokens,
            savings_ratio=result.tokens.savings_ratio,
            latency_ms=latency
        )
        db.add(log)
        db.commit()
        
        return asdict(result)
    except Exception as e:
        logger.error(f"Error optimizing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/execute", response_model=ExecuteResponse)
@limiter.limit(settings.RATE_LIMIT_API)
def execute_endpoint(
    payload: ExecuteRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> dict:
    increment_usage(user, db, background_tasks)
    start_time = time.time()
    try:
        result = execute(
            raw_text=payload.text,
            provider_name=payload.provider,
            db=db,
            model=payload.model,
            language=payload.language,
            format=payload.format,
            provider_key=payload.provider_key
        )
        
        # Log Activity
        latency = (time.time() - start_time) * 1000
        log = ActivityLog(
            user_id=user.id,
            provider=payload.provider,
            model=payload.model,
            raw_text=result.raw_text,
            compressed_text=result.compressed_text,
            raw_tokens=result.tokens.raw_tokens,
            compressed_tokens=result.tokens.compressed_tokens,
            savings_ratio=result.tokens.savings_ratio,
            latency_ms=latency
        )
        db.add(log)
        db.commit()
        
        return asdict(result)
    except Exception as e:
        logger.error(f"Error executing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/auth/rotate-key")
def rotate_api_key(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    import secrets
    new_api_key = f"sk-ps-{secrets.token_urlsafe(16)}"
    user.api_key = new_api_key
    
    # Update secure storage
    try:
        secure_storage.update_user(user.email, {
            "api_key": new_api_key
        })
    except Exception as e:
        logger.error(f"Failed to update secure storage during key rotation: {e}")
        
    db.commit()
    
    return {
        "message": "API Key rotated successfully",
        "api_key": new_api_key
    }


@app.post("/api/v1/auth/change-password")
def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    if not verify_password(payload.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    
    # Update Password
    new_hash = get_password_hash(payload.new_password)
    user.password_hash = new_hash
    
    # Secure Storage Update
    try:
        secure_storage.update_user(user.email, {
            "password_hash": new_hash
        })
    except Exception as e:
        logger.error(f"Failed to update secure storage during password change: {e}")
        
    # Audit Log
    db.add(AuthLog(user_id=user.id, event_type="password_change", details="User changed password"))
    db.commit()
    
    return {"message": "Password changed successfully"}


@app.post("/api/v1/auth/forgot-password")
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def forgot_password(request: Request, payload: ForgotPasswordRequest, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        # Don't reveal if user exists or not for security
        return {"message": "If this email is registered, you will receive a reset link."}
    
    import secrets
    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(minutes=30)
    db.commit()
    
    await send_password_reset_email(user.email, reset_token)
    return {"message": "If this email is registered, you will receive a reset link."}


@app.post("/api/v1/auth/reset-password")
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def reset_password(request: Request, payload: ResetPasswordRequest, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.reset_token == payload.token).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
    if user.reset_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset token has expired")
        
    # Reset password
    hashed = get_password_hash(payload.new_password)
    user.password_hash = hashed
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return {"message": "Password reset successfully. You can now login with your new password."}


@app.get("/api/v1/analytics/stats")
def get_analytics_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Get summary statistics for the current user.
    """
    stats = get_summary_stats(db, user_id=user.id)
    return stats


@app.get("/api/v1/analytics/time-series")
def get_analytics_time_series(
    days: int = 7,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Get time-series data for visualization (last N days).
    """
    series = get_time_series_stats(db, user_id=user.id, days=days)
    return series


@app.get("/api/v1/stats/history")
def get_stats_history(
    limit: int = 50,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Get recent activity history for the current user.
    """
    history = get_recent_history(db, limit=limit, user_id=user.id)
    return history
