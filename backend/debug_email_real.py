
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings
from backend.email_utils import send_password_reset_email, send_verification_email

async def main():
    print("--- Email Debugger (Real Mode Check) ---")
    # Masking sensitive info
    print(f"MAIL_USERNAME: {settings.MAIL_USERNAME}") 
    print(f"MAIL_SERVER: {settings.MAIL_SERVER}")
    print(f"MAIL_PORT: {settings.MAIL_PORT}")
    
    # Use a dummy email that won't actually annoy anyone, or rely on the user checking their logs/inbox.
    # Ideally the user would provide an email, but for now I'll use a placeholder and expect an SMTP error or success.
    # If the user put real credentials, sending to 'test@example.com' might fail if the SMTP server enforces valid recipients.
    # But usually it just accepts it or bounces.
    recipient = "test@example.com" 
    token = "debug-token-real-check"
    
    print("\n[1] Testing Verification Email...")
    try:
        await send_verification_email(recipient, token)
        print("-> Function executed successfully (Email sent).")
    except Exception as e:
        print(f"-> ERROR: {e}")

    print("\n[2] Testing Password Reset Email...")
    try:
        await send_password_reset_email(recipient, token)
        print("-> Function executed successfully (Email sent).")
    except Exception as e:
        print(f"-> ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
