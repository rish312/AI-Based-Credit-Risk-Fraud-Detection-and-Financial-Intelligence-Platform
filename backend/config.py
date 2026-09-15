"""Application configuration."""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent
MODELS_DIR = BACKEND_DIR / "models"

# Project info
PROJECT_NAME = "ML Prediction Platform"
VERSION = "1.0.0"
API_V1_STR = "/api/v1"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR / 'app.db'}")
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "app.db"))

# JWT / Auth
SECRET_KEY = os.getenv("JWT_SECRET", "dev-secret-change-in-production-abc123xyz")
JWT_SECRET = SECRET_KEY  # alias
ALGORITHM = "HS256"
JWT_ALGORITHM = ALGORITHM  # alias
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRY_MINUTES", "60"))
JWT_EXPIRY_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES  # alias
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRY_DAYS", "7"))
JWT_REFRESH_EXPIRY_DAYS = REFRESH_TOKEN_EXPIRE_DAYS  # alias

# Rate limiting
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))  # per minute
RATE_LIMIT_PREDICTIONS = int(os.getenv("RATE_LIMIT_PREDICTIONS", "30"))  # per minute

# Model timeouts (seconds)
FRAUD_MODEL_TIMEOUT = float(os.getenv("FRAUD_MODEL_TIMEOUT", "0.1"))  # 100ms
CREDIT_RISK_MODEL_TIMEOUT = float(os.getenv("CREDIT_RISK_MODEL_TIMEOUT", "2.0"))
SEGMENTATION_MODEL_TIMEOUT = float(os.getenv("SEGMENTATION_MODEL_TIMEOUT", "2.0"))

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

# Roles
ROLES = ["admin", "loan_officer", "fraud_analyst", "compliance", "viewer"]
