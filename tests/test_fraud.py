#!/usr/bin/env python
"""
Test fraud model: loads, predicts, three-tier decisioning works, latency < 100ms.
"""
import pytest
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ml.fraud.model import FraudModel


@pytest.fixture
def model():
    """Load the trained fraud model."""
    model_path = "/Users/ekanshsukla/Desktop/credit_riskml/backend/models/fraud"
    if not os.path.exists(model_path):
        pytest.skip("Model not found. Run train_all.py first.")
    return FraudModel.load(model_path)


def test_model_loads(model):
    """Test that model loads successfully."""
    assert model is not None
    assert model.xgb_model is not None
    assert model.isolation_forest is not None
    assert model.scaler is not None
    assert len(model.feature_names) > 0


def test_predict_returns_valid_result(model):
    """Test that prediction returns valid result with three-tier decisioning."""
    features = {
        "amount": 100.0,
        "hour_of_day": 14.0,
        "account_age_days": 365.0,
        "prior_txn_count_24h": 2.0,
        "prior_txn_amount_24h": 200.0,
        "is_new_device": 0.0,
        "distance_from_home": 5.0,
        "is_domestic": 1.0,
        "txn_velocity_1h": 2.0/24.0,
        "txn_velocity_24h": 2.0,
        "amount_zscore": 0.1,
        "hour_risk_score": 0.2,
        "velocity_amount_ratio": 0.5,
        "merchant_grocery": 1.0,
        "merchant_electronics": 0.0,
        "merchant_travel": 0.0,
        "merchant_dining": 0.0,
        "merchant_gas": 0.0,
        "merchant_online": 0.0,
        "merchant_entertainment": 0.0,
    }
    
    result = model.predict(features)
    
    assert "fraud_score" in result
    assert "decision" in result
    assert "decision_tier" in result
    assert "model_version" in result
    
    # Score should be in [0, 1]
    score = result["fraud_score"]
    assert 0 <= score <= 1, f"Fraud score {score} not in [0,1]"
    
    # Decision should be valid
    assert result["decision"] in ["approve", "review", "decline"]
    
    # Decision tier should be valid
    assert result["decision_tier"] in ["auto_approve", "manual_review", "auto_decline"]


def test_decision_tier_consistency(model):
    """Test that decision tier is consistent with score thresholds."""
    features = {
        "amount": 100.0,
        "hour_of_day": 14.0,
        "account_age_days": 365.0,
        "prior_txn_count_24h": 2.0,
        "prior_txn_amount_24h": 200.0,
        "is_new_device": 0.0,
        "distance_from_home": 5.0,
        "is_domestic": 1.0,
        "txn_velocity_1h": 2.0/24.0,
        "txn_velocity_24h": 2.0,
        "amount_zscore": 0.1,
        "hour_risk_score": 0.2,
        "velocity_amount_ratio": 0.5,
        "merchant_grocery": 1.0,
        "merchant_electronics": 0.0,
        "merchant_travel": 0.0,
        "merchant_dining": 0.0,
        "merchant_gas": 0.0,
        "merchant_online": 0.0,
        "merchant_entertainment": 0.0,
    }
    
    result = model.predict(features)
    score = result["fraud_score"]
    tier = result["decision_tier"]
    
    if score < 0.3:
        assert tier == "auto_approve"
    elif score <= 0.7:
        assert tier == "manual_review"
    else:
        assert tier == "auto_decline"


def test_prediction_latency(model):
    """Test that prediction latency is acceptable (< 100ms)."""
    features = {
        "amount": 100.0,
        "hour_of_day": 14.0,
        "account_age_days": 365.0,
        "prior_txn_count_24h": 2.0,
        "prior_txn_amount_24h": 200.0,
        "is_new_device": 0.0,
        "distance_from_home": 5.0,
        "is_domestic": 1.0,
        "txn_velocity_1h": 2.0/24.0,
        "txn_velocity_24h": 2.0,
        "amount_zscore": 0.1,
        "hour_risk_score": 0.2,
        "velocity_amount_ratio": 0.5,
        "merchant_grocery": 1.0,
        "merchant_electronics": 0.0,
        "merchant_travel": 0.0,
        "merchant_dining": 0.0,
        "merchant_gas": 0.0,
        "merchant_online": 0.0,
        "merchant_entertainment": 0.0,
    }
    
    # Warm up
    model.predict(features)
    
    # Measure latency
    start = time.time()
    for _ in range(10):
        model.predict(features)
    elapsed = (time.time() - start) / 10
    
    # Should be well under 100ms
    assert elapsed < 0.1, f"Average latency {elapsed*1000:.2f}ms exceeds 100ms"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])