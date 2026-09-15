from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend import config
from backend.database import init_db
from backend.api.middleware.audit import AuditMiddleware
from backend.api.middleware.rate_limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from backend.api.v1.router import api_router
from backend.ml.engine import PredictionEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global engine instance
engine = PredictionEngine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database...")
    init_db()
    
    # Load ML models
    logger.info("Loading ML models...")
    try:
        engine.load_models()
        logger.info("ML models loaded successfully")
    except Exception as e:
        logger.warning(f"Failed to load ML models: {e}. API will start but /predict may fail.")
    
    app.state.engine = engine
    yield
    # Shutdown
    logger.info("Shutting down application...")

app = FastAPI(
    title=config.PROJECT_NAME,
    description="REST API for ML prediction platform (Credit Risk, Fraud, Segmentation)",
    version=config.VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit Logging
app.add_middleware(AuditMiddleware)

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Routers
app.include_router(api_router, prefix=config.API_V1_STR)

@app.get("/health", tags=["system"])
def health_check():
    eng = getattr(app.state, 'engine', None)
    return {
        "status": "healthy",
        "version": config.VERSION,
        "models_loaded": eng.is_loaded if eng else False
    }
