"""Generate demo predictions to populate the dashboard."""

import sys
import os
import json
import uuid
import random
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, get_connection
from backend.ml.engine import PredictionEngine

# Sample data templates
SAMPLE_CREDIT = [
    {"income": 75000, "employment_years": 8, "existing_debt": 15000, "credit_score": 720,
     "account_tenure_months": 96, "credit_limit": 25000, "current_balance": 8000,
     "num_open_accounts": 5, "recent_inquiries": 1,
     "monthly_payment_history": [0]*20 + [1,0,0,0]},
    {"income": 35000, "employment_years": 2, "existing_debt": 28000, "credit_score": 580,
     "account_tenure_months": 24, "credit_limit": 10000, "current_balance": 9500,
     "num_open_accounts": 8, "recent_inquiries": 5,
     "monthly_payment_history": [0]*10 + [1]*8 + [0]*6},
    {"income": 120000, "employment_years": 15, "existing_debt": 5000, "credit_score": 800,
     "account_tenure_months": 180, "credit_limit": 50000, "current_balance": 3000,
     "num_open_accounts": 3, "recent_inquiries": 0,
     "monthly_payment_history": [0]*24},
]

SAMPLE_FRAUD = [
    {"transaction_amount": 50.0, "merchant_category": "grocery", "device_id": "dev001",
     "ip_country": "US", "hour_of_day": 14, "account_age_days": 730,
     "prior_txn_count_24h": 2, "prior_txn_amount_24h": 120.0,
     "is_new_device": False, "distance_from_home": 5.0},
    {"transaction_amount": 2500.0, "merchant_category": "electronics", "device_id": "dev999",
     "ip_country": "NG", "hour_of_day": 3, "account_age_days": 15,
     "prior_txn_count_24h": 8, "prior_txn_amount_24h": 5000.0,
     "is_new_device": True, "distance_from_home": 5000.0},
    {"transaction_amount": 350.0, "merchant_category": "online", "device_id": "dev050",
     "ip_country": "US", "hour_of_day": 22, "account_age_days": 180,
     "prior_txn_count_24h": 5, "prior_txn_amount_24h": 800.0,
     "is_new_device": True, "distance_from_home": 100.0},
]

SAMPLE_SEGMENT = [
    {"days_since_last_purchase": 3, "purchase_frequency": 25, "total_spend": 8000,
     "avg_order_value": 120, "age": 42, "support_tickets": 0,
     "email_open_rate": 0.7, "login_frequency": 20, "days_since_last_login": 1,
     "tenure_months": 48},
    {"days_since_last_purchase": 120, "purchase_frequency": 2, "total_spend": 200,
     "avg_order_value": 30, "age": 28, "support_tickets": 5,
     "email_open_rate": 0.1, "login_frequency": 1, "days_since_last_login": 60,
     "tenure_months": 36},
    {"days_since_last_purchase": 15, "purchase_frequency": 10, "total_spend": 1500,
     "avg_order_value": 45, "age": 35, "support_tickets": 1,
     "email_open_rate": 0.4, "login_frequency": 8, "days_since_last_login": 5,
     "tenure_months": 12},
]


def generate_demo_data(n=30):
    """Generate n demo predictions."""
    import asyncio

    init_db()

    print("Loading models...")
    engine = PredictionEngine()
    engine.load_models()

    print(f"Generating {n} demo predictions...")

    async def run_predictions():
        for i in range(n):
            # Randomly mix data from all three domains
            raw_input = {}
            raw_input.update(random.choice(SAMPLE_CREDIT))
            raw_input.update(random.choice(SAMPLE_FRAUD))
            raw_input.update(random.choice(SAMPLE_SEGMENT))

            # Add some variation
            raw_input["income"] = raw_input["income"] * random.uniform(0.7, 1.3)
            raw_input["transaction_amount"] = raw_input["transaction_amount"] * random.uniform(0.5, 2.0)
            raw_input["credit_score"] = max(300, min(850, raw_input["credit_score"] + random.randint(-50, 50)))

            try:
                result = await engine.predict(raw_input)

                prediction_id = result.get("prediction_id", str(uuid.uuid4()))
                conn = get_connection()
                cursor = conn.cursor()

                # Build a simplified prediction_result for storage
                pred_result = {
                    "prediction_id": prediction_id,
                    "credit_risk": None,
                    "fraud": None,
                    "segmentation": None,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "duration_ms": result.get("duration_ms", 0),
                }

                cr = result.get("credit_risk", {})
                if cr.get("status") == "success":
                    pred_result["credit_risk"] = {
                        "score": cr.get("probability_of_default", cr.get("score", 0.0)),
                        "decision": cr.get("risk_tier", "Unknown"),
                        "explanation": cr.get("shap_explanation", {}),
                    }

                fr = result.get("fraud", {})
                if fr.get("status") == "success":
                    pred_result["fraud"] = {
                        "score": fr.get("score", 0.0),
                        "decision": fr.get("decision", "Unknown"),
                        "decision_tier": fr.get("decision_tier"),
                        "explanation": fr.get("shap_explanation", {}),
                    }

                seg = result.get("segmentation", {})
                if seg.get("status") == "success":
                    pred_result["segmentation"] = {
                        "score": seg.get("confidence", 0.0),
                        "decision": seg.get("segment_name", "Unknown"),
                        "segment_id": seg.get("segment_id"),
                        "explanation": seg.get("shap_explanation", {}),
                    }

                cursor.execute(
                    """INSERT INTO predictions
                       (prediction_id, user_id, request_data, prediction_result, model_version, duration_ms, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        prediction_id,
                        "1",  # admin user
                        json.dumps(raw_input),
                        json.dumps(pred_result),
                        "v1",
                        result.get("duration_ms", 0),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )

                # Add manual review items for fraud
                if fr.get("decision_tier") == "manual_review":
                    cursor.execute(
                        """INSERT INTO review_queue
                           (prediction_id, fraud_score, decision_tier, status, request_data, created_at)
                           VALUES (?, ?, 'manual_review', 'pending', ?, ?)""",
                        (
                            prediction_id,
                            fr.get("score", 0.0),
                            json.dumps(raw_input),
                            datetime.now(timezone.utc).isoformat(),
                        ),
                    )

                conn.commit()
                conn.close()

                status_str = "✓" if all(
                    result.get(m, {}).get("status") == "success"
                    for m in ["credit_risk", "fraud", "segmentation"]
                ) else "⚠"
                print(f"  {status_str} Prediction {i+1}/{n}: {prediction_id[:8]}...")

            except Exception as e:
                print(f"  ✗ Prediction {i+1}/{n} failed: {e}")

    asyncio.run(run_predictions())
    print(f"\nDone! Generated {n} demo predictions.")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    generate_demo_data(n)