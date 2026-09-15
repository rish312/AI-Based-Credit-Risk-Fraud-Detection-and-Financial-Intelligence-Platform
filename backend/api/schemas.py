"""Pydantic request/response schemas for the API."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class PredictionRequest(BaseModel):
    """Unified request covering all three models.

    All fields are optional — the engine determines which models
    can run based on which fields are provided.
    """

    # Credit risk fields
    income: Optional[float] = None
    employment_years: Optional[float] = None
    existing_debt: Optional[float] = None
    monthly_payment_history: Optional[List[int]] = None
    credit_score: Optional[int] = None
    account_tenure_months: Optional[int] = None
    credit_limit: Optional[float] = None
    current_balance: Optional[float] = None
    num_open_accounts: Optional[int] = None
    recent_inquiries: Optional[int] = None

    # Fraud fields
    transaction_amount: Optional[float] = None
    merchant_category: Optional[str] = None
    device_id: Optional[str] = None
    ip_country: Optional[str] = None
    hour_of_day: Optional[int] = None
    account_age_days: Optional[int] = None
    prior_txn_count_24h: Optional[int] = None
    prior_txn_amount_24h: Optional[float] = None
    is_new_device: Optional[bool] = None
    distance_from_home: Optional[float] = None

    # Segmentation fields
    days_since_last_purchase: Optional[int] = None
    purchase_frequency: Optional[int] = None
    total_spend: Optional[float] = None
    avg_order_value: Optional[float] = None
    age: Optional[int] = None
    support_tickets: Optional[int] = None
    email_open_rate: Optional[float] = None
    login_frequency: Optional[float] = None
    days_since_last_login: Optional[int] = None


class ModelResult(BaseModel):
    """Result from a single model."""

    score: float
    decision: str
    decision_tier: Optional[str] = None
    segment_id: Optional[int] = None
    explanation: Optional[Dict[str, Any]] = None
    model_version: Optional[str] = None
    latency_ms: Optional[float] = None


class PredictionResponse(BaseModel):
    """Unified prediction response with all three model results."""

    prediction_id: str
    credit_risk: Optional[ModelResult] = None
    fraud: Optional[ModelResult] = None
    segmentation: Optional[ModelResult] = None
    model_versions: Optional[Dict[str, str]] = None
    duration_ms: Optional[float] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now())


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    username: str
    role: str
    exp: int


class UserResponse(BaseModel):
    id: str
    username: str
    role: str


class ReviewQueueItem(BaseModel):
    id: Any
    prediction_id: str
    status: str
    fraud_score: Optional[float] = None
    request_data: Optional[str] = None
    created_at: Any
    reviewed_at: Optional[Any] = None
    analyst_id: Optional[str] = None
    notes: Optional[str] = None


class ReviewDecision(BaseModel):
    decision: str  # approve, decline, escalate
    notes: Optional[str] = None


class AuditLogEntry(BaseModel):
    id: Any
    user_id: Optional[str] = None
    username: Optional[str] = None
    endpoint: str
    method: str
    status_code: int
    duration_ms: float
    ip_address: Optional[str] = None
    timestamp: Any


class MonitoringResponse(BaseModel):
    score_distributions: Dict[str, Any]
    latency: Dict[str, float]
    drift_alerts: List[Dict[str, Any]]
    queue_stats: Dict[str, Any]
