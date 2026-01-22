import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine base directory (PromptShield root)
# This file is in backend/config.py, so we go up one level
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "promptshield.db")
ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    # Security - No default implies required (Fail Fast)
    ADMIN_SECRET: str
    
    # Payment
    MERCHANT_UPI_ID: str = "promptshield@upi"
    MERCHANT_UPI_ID_ENCRYPTED: str | None = None
    MERCHANT_NAME: str = "PromptShield Inc"
    
    # Email
    MAIL_USERNAME: str = "mock_user"
    MAIL_PASSWORD: str = "mock_pass"
    MAIL_FROM: str = "noreply@promptshield.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    
    # Database
    # Use absolute path by default for robustness
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_PATH}"
    
    # Frontend URL (for email links)
    FRONTEND_URL: str = "http://localhost:3000"
    
    # API Limits
    RATE_LIMIT_LOGIN: str = "5/15minute"
    RATE_LIMIT_SIGNUP: str = "5/hour"
    RATE_LIMIT_API: str = "1000/minute" # General API endpoints

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH, 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
