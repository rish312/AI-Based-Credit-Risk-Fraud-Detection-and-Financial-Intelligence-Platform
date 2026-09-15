"""Prediction API endpoints."""

import uuid
import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import List, Optional
from pydantic import BaseModel

from backend.api.schemas import PredictionRequest, PredictionResponse, ModelResult
from backend.api.middleware.auth import get_current_user
from backend.api.middleware.rate_limiter import limiter
from backend.database import get_connection

logger = logging.getLogger(__name__)
router = APIRouter()


class PredictionListResponse(BaseModel):
    items: List[PredictionResponse]
    total: int
    page: int
    per_page: int


@router.post("/predict", response_model=PredictionResponse)
@limiter.limit("30/minute")
async def create_prediction(
    request: Request,
    data: PredictionRequest,
    current_user: dict = Depends(get_current_user),
):
    """Score a customer/transaction across all three models."""
    engine = getattr(request.app.state, "engine", None)

    result = None
    if engine and engine.is_loaded:
        try:
            result = await engine.predict(data.model_dump())
        except Exception as e:
            logger.error(f"Prediction engine error: {e}")

    # Fallback if engine unavailable
    if result is None:
        result = {
            "prediction_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": 0,
            "model_versions": {},
            "credit_risk": {"status": "unavailable", "score": None},
            "fraud": {"status": "unavailable", "score": None},
            "segmentation": {"status": "unavailable", "score": None},
        }

    prediction_id = result.get("prediction_id", str(uuid.uuid4()))

    # Build API response
    response_data = {
        "prediction_id": prediction_id,
        "credit_risk": None,
        "fraud": None,
        "segmentation": None,
        "model_versions": result.get("model_versions", {}),
        "duration_ms": result.get("duration_ms", 0),
        "timestamp": datetime.now(timezone.utc),
    }

    # Map credit risk result
    cr = result.get("credit_risk", {})
    if cr.get("status") == "success":
        response_data["credit_risk"] = ModelResult(
            score=cr.get("probability_of_default", cr.get("score", 0.0)),
            decision=cr.get("risk_tier", "Unknown"),
            explanation=cr.get("shap_explanation", {}),
            model_version=cr.get("model_version"),
            latency_ms=cr.get("latency_ms"),
        )

    # Map fraud result
    fr = result.get("fraud", {})
    if fr.get("status") == "success":
        response_data["fraud"] = ModelResult(
            score=fr.get("score", 0.0),
            decision=fr.get("decision", "Unknown"),
            decision_tier=fr.get("decision_tier"),
            explanation=fr.get("shap_explanation", {}),
            model_version=fr.get("model_version"),
            latency_ms=fr.get("latency_ms"),
        )

    # Map segmentation result
    seg = result.get("segmentation", {})
    if seg.get("status") == "success":
        response_data["segmentation"] = ModelResult(
            score=seg.get("confidence", 0.0),
            decision=seg.get("segment_name", "Unknown"),
            segment_id=seg.get("segment_id"),
            explanation=seg.get("shap_explanation", {}),
            model_version=seg.get("model_version"),
            latency_ms=seg.get("latency_ms"),
        )

    response = PredictionResponse(**response_data)

    # Store in DB
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO predictions
               (prediction_id, user_id, request_data, prediction_result, model_version, duration_ms, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                prediction_id,
                current_user.get("sub"),
                data.model_dump_json(),
                response.model_dump_json(),
                "v1",
                result.get("duration_ms", 0),
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        # If fraud tier is manual_review, add to review queue
        if fr.get("decision_tier") == "manual_review":
            cursor.execute(
                """INSERT INTO review_queue
                   (prediction_id, fraud_score, decision_tier, status, request_data, created_at)
                   VALUES (?, ?, ?, 'pending', ?, ?)""",
                (
                    prediction_id,
                    fr.get("score", 0.0),
                    "manual_review",
                    data.model_dump_json(),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

        conn.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
    finally:
        if "conn" in locals():
            conn.close()

    return response


@router.get("/predictions/{prediction_id}", response_model=PredictionResponse)
def get_prediction(
    prediction_id: str, current_user: dict = Depends(get_current_user)
):
    """Retrieve a stored prediction by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT prediction_result FROM predictions WHERE prediction_id = ?",
        (prediction_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Prediction not found")

    result_data = json.loads(row["prediction_result"])
    return PredictionResponse(**result_data)


@router.get("/predictions", response_model=PredictionListResponse)
def list_predictions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """List recent predictions with pagination."""
    offset = (page - 1) * per_page

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM predictions")
    total = cursor.fetchone()["count"]

    cursor.execute(
        "SELECT prediction_result FROM predictions ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (per_page, offset),
    )
    rows = cursor.fetchall()
    conn.close()

    items = [
        PredictionResponse(**json.loads(row["prediction_result"])) for row in rows
    ]

    return PredictionListResponse(
        items=items, total=total, page=page, per_page=per_page
    )
