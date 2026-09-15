#!/usr/bin/env python
"""
Test explainability: SHAP contributions sum to output value (within tolerance).
"""
import pytest
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ml.explainability import ExplainabilityEngine
from backend.ml.credit_risk.model import CreditRiskModel
from backend.ml.fraud.model import FraudModel
from backend.ml.segmentation.model import SegmentationModel


@pytest.fixture
def credit_risk_model():
    """Load credit risk model."""
    model_path = "/Users/ekanshsukla/Desktop/credit_riskml/backend/models/credit_risk"
    if not os.path.exists(model_path):
        pytest.skip("Model not found. Run train_all.py first.")
    return CreditRiskModel.load(model_path)


@pytest.fixture
def fraud_model():
    """Load fraud model."""
    model_path = "/Users/ekanshsukla/Desktop/credit_riskml/backend/models/fraud"
    if not os.path.exists(model_path):
        pytest.skip("Model not found. Run train_all.py first.")
    return FraudModel.load(model_path)


@pytest.fixture
def segmentation_model():
    """Load segmentation model."""
    model_path = "/Users/ekanshsukla/Desktop/credit_riskml/backend/models/segmentation"
    if not os.path.exists(model_path):
        pytest.skip("Model not found. Run train_all.py first.")
    return SegmentationModel.load(model_path)


@pytest.fixture
def explainability(credit_risk_model, fraud_model, segmentation_model):
    """Create explainability engine with all models."""
    engine = ExplainabilityEngine()
    engine.init_credit_risk_explainer(credit_risk_model)
    engine.init_fraud_explainer(fraud_model)
    engine.init_segmentation_explainer(segmentation_model)
    return engine


def test_credit_risk_shap_sum(credit_risk_model, explainability):
    """Test that SHAP contributions sum to output value for credit risk."""
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
    
    feature_names = credit_risk_model.feature_names
    explanation = explainability.explain_credit_risk(features, feature_names)
    
    base_value = explanation["base_value"]
    output_value = explanation["output_value"]
    contributions = [f["contribution"] for f in explanation["features"]]
    
    # Sum of contributions + base_value should equal output_value (within tolerance)
    reconstructed = base_value + sum(contributions)
    assert abs(reconstructed - output_value) < 1e-5, \
        f"SHAP sum mismatch: base({base_value}) + sum({sum(contributions)}) = {reconstructed} != output({output_value})"


def test_fraud_shap_sum(fraud_model, explainability):
    """Test that SHAP contributions sum to output value for fraud."""
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
    
    feature_names = fraud_model.feature_names
    explanation = explainability.explain_fraud(features, feature_names)
    
    base_value = explanation["base_value"]
    output_value = explanation["output_value"]
    contributions = [f["contribution"] for f in explanation["features"]]
    
    reconstructed = base_value + sum(contributions)
    assert abs(reconstructed - output_value) < 1e-5, \
        f"SHAP sum mismatch: base({base_value}) + sum({sum(contributions)}) = {reconstructed} != output({output_value})"


def test_segmentation_shap_sum(segmentation_model, explainability):
    """Test that SHAP contributions sum to output value for segmentation."""
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
    
    feature_names = segmentation_model.feature_names
    prediction = segmentation_model.predict(features)
    predicted_class = prediction["segment_id"]
    
    explanation = explainability.explain_segmentation(features, feature_names, predicted_class)
    
    base_value = explanation["base_value"]
    output_value = explanation["output_value"]
    contributions = [f["contribution"] for f in explanation["features"]]
    
    reconstructed = base_value + sum(contributions)
    assert abs(reconstructed - output_value) < 1e-5, \
        f"SHAP sum mismatch: base({base_value}) + sum({sum(contributions)}) = {reconstructed} != output({output_value})"


def test_explanation_structure(credit_risk_model, explainability):
    """Test that explanation has correct structure."""
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
    
    feature_names = credit_risk_model.feature_names
    explanation = explainability.explain_credit_risk(features, feature_names)
    
    assert "base_value" in explanation
    assert "features" in explanation
    assert "output_value" in explanation
    
    # Features should be sorted by absolute contribution
    contribs = [f["contribution"] for f in explanation["features"]]
    abs_contribs = [abs(c) for c in contribs]
    assert abs_contribs == sorted(abs_contribs, reverse=True), \
        "Features should be sorted by absolute contribution (descending)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])