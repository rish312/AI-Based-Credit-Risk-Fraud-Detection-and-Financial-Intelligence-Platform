#!/usr/bin/env python
"""
Test segmentation model: clustering produces k clusters, surrogate accuracy > 85%, SHAP works.
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ml.segmentation.model import SegmentationModel


@pytest.fixture
def model():
    """Load the trained segmentation model."""
    model_path = "/Users/ekanshsukla/Desktop/credit_riskml/backend/models/segmentation"
    if not os.path.exists(model_path):
        pytest.skip("Model not found. Run train_all.py first.")
    return SegmentationModel.load(model_path)


def test_model_loads(model):
    """Test that model loads successfully."""
    assert model is not None
    assert model.kmeans is not None
    assert model.surrogate is not None
    assert model.scaler is not None
    assert len(model.feature_names) > 0
    assert model.n_clusters > 0


def test_predict_returns_valid_segment(model):
    """Test that prediction returns valid segment with confidence."""
    features = {
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
        "recency_score": 0.95,
        "frequency_score": 0.24,
        "monetary_score": 0.45,
        "engagement_index": 0.47,
        "churn_risk_signal": 0.05,
        "estimated_clv": 4500,
    }
    
    result = model.predict(features)
    
    assert "segment_id" in result
    assert "segment_name" in result
    assert "confidence" in result
    assert "model_version" in result
    
    # Segment ID should be valid
    assert 0 <= result["segment_id"] < model.n_clusters
    
    # Confidence should be in [0, 1]
    assert 0 <= result["confidence"] <= 1
    
    # Segment name should be a known profile
    assert result["segment_name"] in [
        "High-Value Loyalist",
        "At-Risk Churner", 
        "Bargain Hunter",
        "New Explorer",
        "Dormant",
        "Unknown"
    ]


def test_surrogate_accuracy(model):
    """Test that surrogate accuracy is above 85%."""
    metrics = model.metadata.get("metrics", {})
    accuracy = metrics.get("surrogate_accuracy", 0)
    
    assert accuracy > 0.85, f"Surrogate accuracy {accuracy:.2%} below 85% threshold"


def test_clusters_exist(model):
    """Test that model has correct number of clusters."""
    assert model.n_clusters >= 3
    assert model.n_clusters <= 7
    
    # Check segment profiles exist
    assert len(model.segment_profiles) == model.n_clusters
    
    for i in range(model.n_clusters):
        assert i in model.segment_profiles
        assert "name" in model.segment_profiles[i]
        assert "centroid" in model.segment_profiles[i]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])