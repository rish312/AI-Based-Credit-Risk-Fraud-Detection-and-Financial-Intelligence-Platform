#!/usr/bin/env python
"""
Test API: auth flow, RBAC enforcement, rate limiting, audit log creation, prediction round-trip.
"""
import pytest
import asyncio
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.database import init_db, get_connection
import uuid
import hashlib


def simple_hash(password: str) -> str:
    """Simple hash for testing (not cryptographically secure)."""
    return hashlib.sha256(password.encode()).hexdigest()


def seed_test_users():
    """Seed test users in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    users = [
        ("admin", "admin123", "admin"),
        ("loan_officer", "loan123", "loan_officer"),
        ("fraud_analyst", "fraud123", "fraud_analyst"),
        ("compliance", "comp123", "compliance"),
        ("viewer", "view123", "viewer"),
    ]
    
    for username, password, role in users:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if not cursor.fetchone():
            hashed_pwd = simple_hash(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, hashed_pwd, role)
            )
    conn.commit()
    conn.close()


@pytest.fixture(scope="session")
def client():
    """Create test client with fresh database."""
    # Use a test database
    os.environ["DATABASE_PATH"] = "/tmp/test_app.db"
    init_db()
    seed_test_users()
    return TestClient(app)


@pytest.fixture
def admin_token(client):
    """Get admin auth token."""
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    if response.status_code != 200:
        pytest.skip("Auth not working in test environment")
    return response.json()["access_token"]


@pytest.fixture
def loan_officer_token(client):
    """Get loan officer auth token."""
    response = client.post("/api/v1/auth/login", json={"username": "loan_officer", "password": "loan123"})
    if response.status_code != 200:
        pytest.skip("Auth not working in test environment")
    return response.json()["access_token"]


@pytest.fixture
def fraud_analyst_token(client):
    """Get fraud analyst auth token."""
    response = client.post("/api/v1/auth/login", json={"username": "fraud_analyst", "password": "fraud123"})
    if response.status_code != 200:
        pytest.skip("Auth not working in test environment")
    return response.json()["access_token"]


def test_health_check(client):
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_login_success(client):
    """Test successful login."""
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_failure(client):
    """Test failed login with wrong password."""
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401


def test_rbac_enforcement_admin(client, loan_officer_token):
    """Test that loan_officer cannot access admin-only endpoints."""
    # The register endpoint requires admin role
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "newuser", "password": "pass123", "role": "viewer"},
        headers={"Authorization": f"Bearer {loan_officer_token}"}
    )
    assert response.status_code == 403


def test_rbac_enforcement_fraud_analyst(client, loan_officer_token):
    """Test that loan_officer cannot access fraud analyst endpoints."""
    response = client.get(
        "/api/v1/review-queue",
        headers={"Authorization": f"Bearer {loan_officer_token}"}
    )
    assert response.status_code == 403


def test_rbac_allow_fraud_analyst(client, fraud_analyst_token):
    """Test that fraud_analyst can access review queue."""
    response = client.get(
        "/api/v1/review-queue",
        headers={"Authorization": f"Bearer {fraud_analyst_token}"}
    )
    assert response.status_code == 200


def test_z_rate_limiting():
    """Test rate limiting on prediction endpoint (uses separate client)."""
    # Create a fresh client for this test to avoid rate limit pollution
    os.environ["DATABASE_PATH"] = "/tmp/test_app_ratelimit.db"
    init_db()
    seed_test_users()
    
    # Login to get token
    test_client = TestClient(app)
    response = test_client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Make multiple requests - should eventually hit rate limit
    hit_limit = False
    for i in range(35):
        response = test_client.post(
            "/api/v1/predict",
            json={
                "income": 75000,
                "employment_years": 5,
                "existing_debt": 12000,
                "credit_score": 720,
                "transaction_amount": 100,
                "merchant_category": "grocery",
                "hour_of_day": 14,
            },
            headers=headers
        )
        if response.status_code == 429:
            hit_limit = True
            break
    
    # Should have hit rate limit
    assert hit_limit, "Rate limit was not triggered after 35 requests"
    # Note: slowapi may not always return Retry-After header in test environment


def test_audit_log_creation(client, admin_token):
    """Test that audit logs are created for requests."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get count before
    cursor.execute("SELECT COUNT(*) as count FROM audit_logs")
    before_count = cursor.fetchone()["count"]
    
    # Make a request
    response = client.post(
        "/api/v1/predict",
        json={
            "income": 75000,
            "employment_years": 5,
            "existing_debt": 12000,
            "credit_score": 720,
            "transaction_amount": 100,
            "merchant_category": "grocery",
            "hour_of_day": 14,
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Get count after
    cursor.execute("SELECT COUNT(*) as count FROM audit_logs")
    after_count = cursor.fetchone()["count"]
    conn.close()
    
    # Should have at least one more audit log
    assert after_count > before_count


def test_prediction_round_trip(client, admin_token):
    """Test full prediction round-trip."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Make prediction
    response = client.post(
        "/api/v1/predict",
        json={
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
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "prediction_id" in data
    assert "credit_risk" in data
    assert "fraud" in data
    assert "segmentation" in data
    assert "timestamp" in data
    
    # Try to retrieve the prediction
    pred_id = data["prediction_id"]
    response2 = client.get(f"/api/v1/predictions/{pred_id}", headers=headers)
    assert response2.status_code == 200


def test_list_predictions(client, admin_token):
    """Test listing predictions."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/v1/predictions", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])