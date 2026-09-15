"""
Shared feature store for the ML prediction platform.

Computes and caches features for all three models from raw input data.
Shared features (income, account history) are computed once and reused.
Model-specific features (DTI for credit risk, velocity for fraud, RFM for segmentation)
are computed separately.
"""

import numpy as np
from typing import Dict, Any, Optional
from functools import lru_cache


class FeatureStore:
    """Shared feature computation and caching layer.

    Takes raw input data and produces model-specific feature vectors.
    Computes shared features once, then dispatches to model-specific
    feature engineering functions.
    """

    def __init__(self):
        self._cache = {}

    def get_features(self, raw_input: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Compute features for all three models from raw input.

        Args:
            raw_input: Dictionary of raw input fields from the API request.

        Returns:
            Dictionary with keys 'credit_risk', 'fraud', 'segmentation',
            each mapping to a dict of feature_name -> feature_value.
        """
        result = {}

        # Credit risk features
        if self._has_credit_risk_fields(raw_input):
            result["credit_risk"] = self._compute_credit_risk_features(raw_input)

        # Fraud features
        if self._has_fraud_fields(raw_input):
            result["fraud"] = self._compute_fraud_features(raw_input)

        # Segmentation features
        if self._has_segmentation_fields(raw_input):
            result["segmentation"] = self._compute_segmentation_features(raw_input)

        return result

    def _has_credit_risk_fields(self, raw_input: Dict[str, Any]) -> bool:
        """Check if the input has enough fields for credit risk scoring."""
        required = ["income", "existing_debt", "credit_score"]
        return all(raw_input.get(f) is not None for f in required)

    def _has_fraud_fields(self, raw_input: Dict[str, Any]) -> bool:
        """Check if the input has enough fields for fraud scoring."""
        required = ["transaction_amount"]
        return all(raw_input.get(f) is not None for f in required)

    def _has_segmentation_fields(self, raw_input: Dict[str, Any]) -> bool:
        """Check if the input has enough fields for segmentation."""
        required = ["days_since_last_purchase", "purchase_frequency", "total_spend"]
        return all(raw_input.get(f) is not None for f in required)

    def _compute_credit_risk_features(self, raw_input: Dict[str, Any]) -> Dict[str, float]:
        """Compute credit risk features from raw input."""
        income = float(raw_input.get("income", 0))
        existing_debt = float(raw_input.get("existing_debt", 0))
        credit_score = int(raw_input.get("credit_score", 650))
        account_tenure_months = int(raw_input.get("account_tenure_months", 12))
        credit_limit = float(raw_input.get("credit_limit", 10000))
        current_balance = float(raw_input.get("current_balance", 0))
        num_open_accounts = int(raw_input.get("num_open_accounts", 1))
        recent_inquiries = int(raw_input.get("recent_inquiries", 0))
        employment_years = float(raw_input.get("employment_years", 0))
        payment_history = raw_input.get("monthly_payment_history", [0] * 24)

        # Engineered features
        debt_to_income = existing_debt / max(income, 1.0)
        credit_utilization = current_balance / max(credit_limit, 1.0)
        credit_history_years = account_tenure_months / 12.0
        delinquency_rate = sum(payment_history) / max(len(payment_history), 1)
        recent_delinquency = sum(payment_history[-6:]) if len(payment_history) >= 6 else sum(payment_history)

        return {
            "income": income,
            "employment_years": employment_years,
            "existing_debt": existing_debt,
            "credit_score": float(credit_score),
            "account_tenure_months": float(account_tenure_months),
            "credit_limit": credit_limit,
            "current_balance": current_balance,
            "num_open_accounts": float(num_open_accounts),
            "recent_inquiries": float(recent_inquiries),
            "debt_to_income_ratio": debt_to_income,
            "credit_utilization": credit_utilization,
            "credit_history_length_years": credit_history_years,
            "delinquency_rate": delinquency_rate,
            "recent_delinquency_count": float(recent_delinquency),
        }

    def _compute_fraud_features(self, raw_input: Dict[str, Any]) -> Dict[str, float]:
        """Compute fraud detection features from raw input."""
        amount = float(raw_input.get("transaction_amount", 0))
        hour = int(raw_input.get("hour_of_day", 12))
        account_age = int(raw_input.get("account_age_days", 365))
        prior_count = int(raw_input.get("prior_txn_count_24h", 0))
        prior_amount = float(raw_input.get("prior_txn_amount_24h", 0))
        is_new_device = bool(raw_input.get("is_new_device", False))
        distance = float(raw_input.get("distance_from_home", 0))
        ip_country = raw_input.get("ip_country", "US")
        merchant = raw_input.get("merchant_category", "other")

        # Velocity features
        txn_velocity_1h = prior_count / 24.0  # estimated hourly rate
        txn_velocity_24h = float(prior_count)

        # Amount z-score (using typical transaction stats)
        mean_amount, std_amount = 85.0, 150.0
        amount_zscore = (amount - mean_amount) / max(std_amount, 1.0)

        # Hour risk score (higher risk at unusual hours)
        if 0 <= hour <= 5:
            hour_risk = 0.8 + (5 - hour) * 0.04
        elif 22 <= hour <= 23:
            hour_risk = 0.6
        else:
            hour_risk = 0.2

        # Velocity amount ratio
        velocity_amount_ratio = amount / max(prior_amount, 1.0) if prior_amount > 0 else 1.0

        # Is domestic
        is_domestic = 1.0 if ip_country in ("US", "us", "USA", "domestic") else 0.0

        # Merchant category encoding
        merchant_categories = ["grocery", "electronics", "travel", "dining", "gas", "online", "entertainment"]
        merchant_features = {}
        for cat in merchant_categories:
            merchant_features[f"merchant_{cat}"] = 1.0 if merchant == cat else 0.0

        features = {
            "amount": amount,
            "hour_of_day": float(hour),
            "account_age_days": float(account_age),
            "prior_txn_count_24h": float(prior_count),
            "prior_txn_amount_24h": prior_amount,
            "is_new_device": 1.0 if is_new_device else 0.0,
            "distance_from_home": distance,
            "is_domestic": is_domestic,
            "txn_velocity_1h": txn_velocity_1h,
            "txn_velocity_24h": txn_velocity_24h,
            "amount_zscore": amount_zscore,
            "hour_risk_score": hour_risk,
            "velocity_amount_ratio": velocity_amount_ratio,
        }
        features.update(merchant_features)

        return features

    def _compute_segmentation_features(self, raw_input: Dict[str, Any]) -> Dict[str, float]:
        """Compute customer segmentation features from raw input."""
        days_since_purchase = int(raw_input.get("days_since_last_purchase", 30))
        frequency = int(raw_input.get("purchase_frequency", 5))
        total_spend = float(raw_input.get("total_spend", 500))
        avg_order = float(raw_input.get("avg_order_value", 50))
        age = int(raw_input.get("age", 35))
        tenure = int(raw_input.get("tenure_months", 12))
        if tenure == 0:
            tenure = 1
        tickets = int(raw_input.get("support_tickets", 0))
        email_rate = float(raw_input.get("email_open_rate", 0.3))
        login_freq = float(raw_input.get("login_frequency", 5))
        days_since_login = int(raw_input.get("days_since_last_login", 7))

        # Engineered features
        # Recency score: inverse normalized (lower days = higher score)
        recency_score = max(0, 1.0 - (days_since_purchase / 365.0))

        # Frequency score: normalized (cap at reasonable max)
        frequency_score = min(frequency / 50.0, 1.0)

        # Monetary score: normalized (cap at reasonable max)
        monetary_score = min(total_spend / 10000.0, 1.0)

        # Engagement index
        engagement_index = 0.5 * email_rate + 0.5 * min(login_freq / 30.0, 1.0)

        # Churn risk signal
        churn_risk = (
            0.4 * min(days_since_purchase / 365.0, 1.0)
            + 0.3 * min(days_since_login / 90.0, 1.0)
            + 0.3 * min(tickets / 10.0, 1.0)
        )

        # Estimated CLV (simplified)
        estimated_clv = avg_order * frequency * (tenure / 12.0)

        return {
            "days_since_last_purchase": float(days_since_purchase),
            "purchase_frequency": float(frequency),
            "total_spend": total_spend,
            "avg_order_value": avg_order,
            "age": float(age),
            "tenure_months": float(tenure),
            "support_tickets": float(tickets),
            "email_open_rate": email_rate,
            "login_frequency": login_freq,
            "days_since_last_login": float(days_since_login),
            "recency_score": recency_score,
            "frequency_score": frequency_score,
            "monetary_score": monetary_score,
            "engagement_index": engagement_index,
            "churn_risk_signal": churn_risk,
            "estimated_clv": estimated_clv,
        }

    def clear_cache(self):
        """Clear the feature cache."""
        self._cache.clear()
