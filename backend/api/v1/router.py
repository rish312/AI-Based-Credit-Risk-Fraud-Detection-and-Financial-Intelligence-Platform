from fastapi import APIRouter
from backend.api.v1.auth import router as auth_router
from backend.api.v1.predictions import router as predictions_router
from backend.api.v1.review_queue import router as review_queue_router
from backend.api.v1.monitoring import router as monitoring_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(predictions_router, tags=["predictions"])
api_router.include_router(review_queue_router, prefix="/review-queue", tags=["review-queue"])
api_router.include_router(monitoring_router, prefix="/monitoring", tags=["monitoring"])
