from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Request Models ---

class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class OptimizeRequest(BaseModel):
    text: str
    model: str = "gpt-3.5-turbo"
    language: str = "en"
    format: str = "text"

class ExecuteRequest(BaseModel):
    text: str
    provider: str
    model: str = "gpt-3.5-turbo"
    language: str = "en"
    format: str = "text"
    provider_key: Optional[str] = None

class SubscriptionRequest(BaseModel):
    plan: str # 'monthly', 'yearly', 'topup'

class ConfirmPaymentRequest(BaseModel):
    plan: str
    utr: str
    payment_id: Optional[int] = None

# --- Response Models ---

class TokenMetricsSchema(BaseModel):
    raw_tokens: int
    compressed_tokens: int
    savings_ratio: float

class UserPublic(BaseModel):
    id: int
    email: str
    tier: str
    usage_count: int
    max_usage: int
    is_verified: bool
    subscription_plan: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class OptimizeResponse(BaseModel):
    raw_text: str
    compressed_text: str
    tokens: TokenMetricsSchema
    analysis: Optional[List[Dict[str, Any]]] = None
    suggestions: List[str] = []
    pii_found: bool = False
    confidence_score: float = 1.0

class ExecuteResponse(BaseModel):
    provider: str
    model: Optional[str] = None
    raw_text: str
    compressed_text: str
    output: str
    tokens: TokenMetricsSchema
    analysis: Optional[List[Dict[str, Any]]] = None
    suggestions: Optional[List[str]] = None
    drift_detected: bool = False
    pii_found: bool = False
    confidence_score: float = 1.0

class APIStatsResponse(BaseModel):
    total_requests: int
    total_savings: float
    avg_latency: float

class TimeSeriesPoint(BaseModel):
    date: str
    count: int
    savings: float

class HistoryItem(BaseModel):
    id: int
    provider: str
    model: Optional[str]
    savings_ratio: float
    created_at: datetime
