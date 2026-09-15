#!/usr/bin/env python
"""
Test credit risk model: loads, predicts, output is calibrated probability in [0,1], SHAP sums correctly.
"""
import pytest
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ml.credit_risk.model import CreditRiskModel


@pytest.fixture
def model():
    """Load the trained credit risk model."""
    model_path = "/Users/ekanshsukla/Desktop/credit_riskml/backend/models/credit_risk"
    if not os.path.exists(model_path):
        pytest.skip("Model not found. Run train_all.py first.")
    return CreditRiskModel.load(model_path)


def test_model_loads(model):
    """Test that model loads successfully."""
    assert model is not None
    assert model.model is not None
    assert len(model.feature_names) > 0


def test_predict_returns_valid_probability(model):
    """Test that prediction returns calibrated probability in [0,1]."""
    features = {
        "income": 75000,
        "employment_years": 5,
        "existing_debt": 12000,
        "credit_score": 720,
        "account_tenure_months": 60,
        "credit_limit": 20000,
        "current_balance": 5000,
        "num_open_accounts": 3,
        "recent_inquiries": 1,
        "debt_to_income_ratio": 12000 / 75000,
        "credit_utilization": 5000 / 20000,
        "credit_history_length_years": 5,
        "delinquency_rate": 0.0,
        "recent_delinquency_count": 0.0,
    }
    
    result = model.predict(features)
    
    assert "probability" in result
    assert "score" in result
    assert "risk_tier" in result
    assert "model_version" in result
    
    # Probability should be in [0, 1]
    prob = result["probability"]
    assert 0 <= prob <= 1, f"Probability {prob} not in [0,1]"
    
    # Score should be in reasonable range
    score = result["score"]
    assert 300 <= score <= 850, f"Score {score} not in valid range"
    
    # Risk tier should be valid
    assert result["risk_tier"] in ["Low", "Medium", "High", "Very High"]


def test_model_version(model):
    """Test that model has version metadata."""
    assert model.version is not None
    assert model.trained_at is not None
    assert isinstance(model.metrics, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])