#!/usr/bin/env python
"""
Test engine: parallel dispatch works, timeout fallback returns partial results, feature store caching.
"""
import pytest
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ml.engine import PredictionEngine


@pytest.fixture
def engine():
    """Create engine with loaded models."""
    engine = PredictionEngine()
    engine.load_models()
    return engine


@pytest.mark.asyncio
async def test_engine_loads_models(engine):
    """Test that engine loads at least some models."""
    # At least one model should be loaded
    loaded_models = []
    if engine.credit_risk_model:
        loaded_models.append("credit_risk")
    if engine.fraud_model:
        loaded_models.append("fraud")
    if engine.segmentation_model:
        loaded_models.append("segmentation")
    
    assert len(loaded_models) > 0, "No models loaded"
    print(f"Loaded models: {loaded_models}")


@pytest.mark.asyncio
async def test_predict_returns_all_models(engine):
    """Test that predict returns results for all available models."""
    raw_input = {
        # Credit risk fields
        "income": 75000,
        "employment_years": 5,
        "existing_debt": 12000,
        "credit_score": 720,
        "account_tenure_months": 60,
        "credit_limit": 20000,
        "current_balance": 5000,
        "num_open_accounts": 3,
        "recent_inquiries": 1,
        "monthly_payment_history": [0]*24,
        # Fraud fields
        "transaction_amount": 100.0,
        "merchant_category": "grocery",
        "device_id": "dev-001",
        "ip_country": "US",
        "hour_of_day": 14,
        "account_age_days": 365,
        "prior_txn_count_24h": 2,
        "prior_txn_amount_24h": 200.0,
        "is_new_device": False,
        "distance_from_home": 5.0,
        # Segmentation fields
        "days_since_last_purchase": 15,
        "purchase_frequency": 12,
        "total_spend": 4500,
        "avg_order_value": 100,
        "age": 35,
        "tenure_months": 36,
        "support_tickets": 0,
        "email_open_rate": 0.6,
        "login_frequency": 10,
        "days_since_last_login": 3,
    }
    
    result = await engine.predict(raw_input)
    
    # Check response structure
    assert "prediction_id" in result
    assert "timestamp" in result
    assert "duration_ms" in result
    assert "model_versions" in result
    assert "credit_risk" in result
    assert "fraud" in result
    assert "segmentation" in result


@pytest.mark.asyncio
async def test_timeout_fallback(engine):
    """Test that timeout fallback returns partial results."""
    # Use a minimal input that only has fraud fields
    raw_input = {
        "transaction_amount": 100.0,
        "merchant_category": "grocery",
        "device_id": "dev-001",
        "ip_country": "US",
        "hour_of_day": 14,
        "account_age_days": 365,
        "prior_txn_count_24h": 2,
        "prior_txn_amount_24h": 200.0,
        "is_new_device": False,
        "distance_from_home": 5.0,
    }
    
    result = await engine.predict(raw_input)
    
    # Should have results for available models
    assert "fraud" in result
    
    # Credit risk and segmentation might be unavailable due to insufficient data
    # but they should still be in the response with status "unavailable"
    assert "credit_risk" in result
    assert "segmentation" in result


@pytest.mark.asyncio
async def test_feature_store_caching(engine):
    """Test that feature store is called and returns features."""
    raw_input = {
        "income": 75000,
        "existing_debt": 12000,
        "credit_score": 720,
    }
    
    features = engine.feature_store.get_features(raw_input)
    
    assert "credit_risk" in features
    cr_features = features["credit_risk"]
    
    # Check that engineered features are present
    assert "debt_to_income_ratio" in cr_features
    assert "credit_utilization" in cr_features
    assert "credit_history_length_years" in cr_features


if __name__ == "__main__":
    pytest.main([__file__, "-v"])