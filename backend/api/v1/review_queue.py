"""Review queue API endpoints for fraud analyst triage."""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from backend.api.schemas import ReviewQueueItem, ReviewDecision
from backend.api.middleware.auth import require_role, get_current_user
from backend.database import get_connection

router = APIRouter()


class QueueStats(BaseModel):
    total_pending: int
    reviewed_today: int
    avg_review_time_mins: Optional[float] = None


@router.get("", response_model=List[ReviewQueueItem])
def list_review_queue(
    status: Optional[str] = None,
    current_user: dict = Depends(require_role("fraud_analyst", "admin")),
):
    """List items in the review queue, defaulting to pending."""
    conn = get_connection()
    cursor = conn.cursor()

    query = """SELECT id, prediction_id, fraud_score, decision_tier, status,
                      created_at, reviewed_at, analyst_id, analyst_notes as notes,
                      request_data
               FROM review_queue"""
    params = []

    if status:
        query += " WHERE status = ?"
        params.append(status)
    else:
        query += " WHERE status = 'pending'"

    query += " ORDER BY created_at DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    items = []
    for row in rows:
        items.append(
            ReviewQueueItem(
                id=row["id"],
                prediction_id=row["prediction_id"],
                fraud_score=row["fraud_score"],
                status=row["status"],
                request_data=row["request_data"],
                created_at=row["created_at"],
                reviewed_at=row["reviewed_at"],
                analyst_id=str(row["analyst_id"]) if row["analyst_id"] else None,
                notes=row["notes"],
            )
        )

    return items


@router.put("/{item_id}", response_model=ReviewQueueItem)
def update_review_item(
    item_id: int,
    decision: ReviewDecision,
    current_user: dict = Depends(require_role("fraud_analyst", "admin")),
):
    """Update a review queue item with analyst decision."""
    valid_decisions = ["approve", "decline", "escalate"]
    if decision.decision not in valid_decisions:
        raise HTTPException(
            status_code=400,
            detail=f"Decision must be one of {valid_decisions}",
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM review_queue WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Review item not found")

    reviewed_at = datetime.now(timezone.utc).isoformat()
    analyst_id = current_user.get("sub")

    cursor.execute(
        """UPDATE review_queue
           SET status = ?, analyst_decision = ?, reviewed_at = ?,
               analyst_id = ?, analyst_notes = ?
           WHERE id = ?""",
        (decision.decision, decision.decision, reviewed_at, analyst_id, decision.notes, item_id),
    )
    conn.commit()

    cursor.execute("SELECT * FROM review_queue WHERE id = ?", (item_id,))
    updated = cursor.fetchone()
    conn.close()

    return ReviewQueueItem(
        id=updated["id"],
        prediction_id=updated["prediction_id"],
        fraud_score=updated["fraud_score"],
        status=updated["status"],
        request_data=updated["request_data"],
        created_at=updated["created_at"],
        reviewed_at=updated["reviewed_at"],
        analyst_id=str(updated["analyst_id"]) if updated["analyst_id"] else None,
        notes=updated["analyst_notes"],
    )


@router.get("/stats", response_model=QueueStats)
def get_queue_stats(
    current_user: dict = Depends(require_role("fraud_analyst", "admin")),
):
    """Get review queue statistics."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) as count FROM review_queue WHERE status = 'pending'"
    )
    total_pending = cursor.fetchone()["count"]

    today_start = (
        datetime.now(timezone.utc)
        .replace(hour=0, minute=0, second=0, microsecond=0)
        .isoformat()
    )
    cursor.execute(
        "SELECT COUNT(*) as count FROM review_queue WHERE status != 'pending' AND reviewed_at >= ?",
        (today_start,),
    )
    reviewed_today = cursor.fetchone()["count"]

    cursor.execute(
        "SELECT created_at, reviewed_at FROM review_queue WHERE status != 'pending' AND reviewed_at >= ?",
        (today_start,),
    )
    reviewed_items = cursor.fetchall()
    conn.close()

    avg_mins = None
    if reviewed_items:
        total_mins = 0
        valid_items = 0
        for item in reviewed_items:
            try:
                c_dt = datetime.fromisoformat(str(item["created_at"]))
                r_dt = datetime.fromisoformat(str(item["reviewed_at"]))
                diff_mins = (r_dt - c_dt).total_seconds() / 60
                total_mins += diff_mins
                valid_items += 1
            except Exception:
                pass
        if valid_items > 0:
            avg_mins = total_mins / valid_items

    return QueueStats(
        total_pending=total_pending,
        reviewed_today=reviewed_today,
        avg_review_time_mins=avg_mins,
    )
