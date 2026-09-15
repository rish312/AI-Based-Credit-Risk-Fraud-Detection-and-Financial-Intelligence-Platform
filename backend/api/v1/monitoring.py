from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta

from backend.api.middleware.auth import require_role
from backend.database import get_connection

router = APIRouter()

@router.get("/score-distributions")
def get_score_distributions(
    hours: int = Query(24, ge=1, le=720),
    current_user: dict = Depends(require_role("admin", "compliance"))
):
    conn = get_connection()
    cursor = conn.cursor()
    
    since_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    cursor.execute("SELECT prediction_result FROM predictions WHERE created_at >= ?", (since_time,))
    rows = cursor.fetchall()
    conn.close()
    
    # Process results into histograms (10 bins 0.0 - 1.0)
    bins = {
        "credit_risk": [0]*10,
        "fraud": [0]*10,
        "segmentation": [0]*10
    }
    
    for row in rows:
        try:
            result = json.loads(row["prediction_result"])
            for model_name in ["credit_risk", "fraud", "segmentation"]:
                if model_name in result and result[model_name]:
                    score = result[model_name].get("score", 0)
                    bin_idx = min(int(score * 10), 9)
                    bins[model_name][bin_idx] += 1
        except:
            continue
            
    return bins

@router.get("/latency")
def get_latency(current_user: dict = Depends(require_role("admin", "compliance"))):
    # Retrieve from monitoring_metrics table or compute from audit_logs
    conn = get_connection()
    cursor = conn.cursor()
    
    # Simple percentile approx using SQLite order by
    cursor.execute("SELECT duration_ms FROM audit_logs WHERE endpoint = '/api/v1/predict' ORDER BY duration_ms ASC")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return {"p50": 0, "p95": 0, "p99": 0}
        
    n = len(rows)
    p50_idx = int(n * 0.50)
    p95_idx = int(n * 0.95)
    p99_idx = int(n * 0.99)
    
    return {
        "p50": rows[p50_idx]["duration_ms"],
        "p95": rows[p95_idx]["duration_ms"],
        "p99": rows[p99_idx]["duration_ms"]
    }

@router.get("/drift")
def get_drift_alerts(current_user: dict = Depends(require_role("admin", "compliance"))):
    # Placeholder for actual ML drift detection
    return [
        {
            "model": "credit_risk",
            "feature": "income",
            "drift_score": 0.15,
            "threshold": 0.1,
            "status": "warning",
            "detected_at": datetime.utcnow().isoformat()
        }
    ]

@router.get("/queue-stats")
def get_queue_stats(current_user: dict = Depends(require_role("admin", "compliance"))):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT status, count(*) as cnt FROM review_queue GROUP BY status")
    rows = cursor.fetchall()
    conn.close()
    
    stats = {"pending": 0, "approve": 0, "decline": 0, "escalate": 0}
    for row in rows:
        if row["status"] in stats:
            stats[row["status"]] = row["cnt"]
            
    return stats
