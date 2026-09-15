"""Train all three models end-to-end."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time


def train_credit_risk():
    """Train the credit risk model."""
    print("=" * 60)
    print("TRAINING CREDIT RISK MODEL")
    print("=" * 60)
    from backend.ml.credit_risk.data_generator import generate_credit_risk_data
    from backend.ml.credit_risk.features import engineer_credit_risk_features
    from backend.ml.credit_risk.model import CreditRiskModel
    from sklearn.model_selection import train_test_split
    from backend.config import MODELS_DIR

    df = generate_credit_risk_data()
    X, y = engineer_credit_risk_features(df)
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = CreditRiskModel()
    metrics = model.train(X_train, y_train, X_val, y_val)
    save_path = str(MODELS_DIR / "credit_risk")
    model.save(save_path)

    print(f"Metrics: {metrics}")
    print(f"Saved to: {save_path}\n")


def train_fraud():
    """Train the fraud detection model."""
    print("=" * 60)
    print("TRAINING FRAUD DETECTION MODEL")
    print("=" * 60)
    from backend.ml.fraud.data_generator import generate_fraud_data
    from backend.ml.fraud.features import engineer_fraud_features
    from backend.ml.fraud.model import FraudModel
    from sklearn.model_selection import train_test_split
    from backend.config import MODELS_DIR

    df = generate_fraud_data()
    X, y = engineer_fraud_features(df)
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = FraudModel()
    metrics = model.train(X_train, y_train, X_val, y_val)
    save_path = str(MODELS_DIR / "fraud")
    model.metadata = {"version": "1.0.0", "trained_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    model.metadata.update(metrics)
    model.save(save_path)

    print(f"Metrics: {metrics}")
    print(f"Saved to: {save_path}\n")


def train_segmentation():
    """Train the customer segmentation model."""
    print("=" * 60)
    print("TRAINING CUSTOMER SEGMENTATION MODEL")
    print("=" * 60)
    from backend.ml.segmentation.data_generator import generate_segmentation_data
    from backend.ml.segmentation.features import engineer_segmentation_features
    from backend.ml.segmentation.model import SegmentationModel
    from backend.config import MODELS_DIR

    df = generate_segmentation_data()
    X_scaled, feature_names, scaler = engineer_segmentation_features(df)

    model = SegmentationModel()
    model.scaler = scaler
    model.metadata = {"version": "1.0.0"}
    metrics = model.train(X_scaled, feature_names)
    save_path = str(MODELS_DIR / "segmentation")
    model.save(save_path)

    print(f"Metrics: {metrics}")
    print(f"Saved to: {save_path}\n")


if __name__ == "__main__":
    start = time.time()
    train_credit_risk()
    train_fraud()
    train_segmentation()
    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f"ALL MODELS TRAINED in {elapsed:.1f}s")
    print(f"{'=' * 60}")