
import os
from typing import List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from .config import settings

class EmailSchema(BaseModel):
    email: List[EmailStr]

conf = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def send_verification_email(email: str, token: str):
    if settings.MAIL_USERNAME == "mock_user" or not settings.MAIL_USERNAME:
        print(f"\n[MOCK EMAIL] To: {email}")
        print(f"[MOCK EMAIL] Subject: Verify your PromptShield account")
        print(f"[MOCK EMAIL] Verification Code: {token}\n")
        return

    message = MessageSchema(
        subject="Verify your PromptShield account",
        recipients=[email],
        body=f"""
        <h1>Welcome to PromptShield!</h1>
        <p>Please use the following 6-digit code to verify your account:</p>
        <h2 style="letter-spacing: 5px; background-color: #f4f4f4; padding: 10px; display: inline-block;">{token}</h2>
        <p>This code will expire in 15 minutes.</p>
        """,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)

async def send_account_locked_email(email: str, token: str):
    if settings.MAIL_USERNAME == "mock_user" or not settings.MAIL_USERNAME:
        print(f"\n[MOCK EMAIL] To: {email}")
        print(f"[MOCK EMAIL] Subject: Security Alert: Account Locked")
        print(f"[MOCK EMAIL] Unlock Code: {token}\n")
        return

    message = MessageSchema(
        subject="Security Alert: Account Locked",
        recipients=[email],
        body=f"""
        <h1>Account Locked</h1>
        <p>Your account has been locked due to multiple failed login attempts.</p>
        <p>To unlock your account, please verify your identity using the following code:</p>
        <h2 style="letter-spacing: 5px; background-color: #f4f4f4; padding: 10px; display: inline-block;">{token}</h2>
        <p>Enter this code in the verification screen.</p>
        <p>If you did not attempt to sign in, please contact support immediately.</p>
        """,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)

async def send_password_reset_email(email: str, token: str, base_url: str = settings.FRONTEND_URL):
    base_url = base_url.rstrip("/")
    reset_link = f"{base_url}/reset-password?token={token}"
    
    if settings.MAIL_USERNAME == "mock_user" or not settings.MAIL_USERNAME:
        print(f"\n[MOCK EMAIL] To: {email}")
        print(f"[MOCK EMAIL] Subject: Reset your PromptShield password")
        print(f"[MOCK EMAIL] Link: {reset_link}\n")
        return

    message = MessageSchema(
        subject="Reset your PromptShield password",
        recipients=[email],
        body=f"""
        <h1>Password Reset Request</h1>
        <p>You requested a password reset for your PromptShield account.</p>
        <p>Click the link below to reset your password:</p>
        <a href="{reset_link}" style="display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px;">Reset Password</a>
        <p>If you didn't request this, please ignore this email.</p>
        <p>This link will expire in 30 minutes.</p>
        """,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)

async def send_thank_you_email(email: str):
    if settings.MAIL_USERNAME == "mock_user" or not settings.MAIL_USERNAME:
        print(f"\n[MOCK EMAIL] To: {email}")
        print(f"[MOCK EMAIL] Subject: Welcome to PromptShield - Verification Successful")
        print(f"[MOCK EMAIL] Content: Thank you for verifying your email!\n")
        return

    message = MessageSchema(
        subject="Welcome to PromptShield - Verification Successful",
        recipients=[email],
        body=f"""
        <h1>Verification Successful!</h1>
        <p>Thank you for verifying your email address.</p>
        <p>You can now access all the features of PromptShield.</p>
        <p>Happy prompting!</p>
        """,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)

async def send_payment_confirmation(email: str, new_api_key: str):
    if settings.MAIL_USERNAME == "mock_user" or not settings.MAIL_USERNAME:
        print(f"\n[MOCK EMAIL] To: {email}")
        print(f"[MOCK EMAIL] Subject: Payment Received - New API Key")
        print(f"[MOCK EMAIL] Your new Premium API Key is: {new_api_key}\n")
        return

    message = MessageSchema(
        subject="Payment Received - PromptShield Premium",
        recipients=[email],
        body=f"""
        <h1>Payment Successful!</h1>
        <p>Thank you for subscribing to PromptShield Premium.</p>
        <p>Your new API Key has been generated for security reasons:</p>
        <pre>{new_api_key}</pre>
        <p>Please update your applications immediately.</p>
        """,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)
