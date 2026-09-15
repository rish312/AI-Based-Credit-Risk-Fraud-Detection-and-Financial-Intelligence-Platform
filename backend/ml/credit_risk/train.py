import os
import json
from sklearn.model_selection import train_test_split
from backend.ml.credit_risk.data_generator import generate_credit_risk_data
from backend.ml.credit_risk.features import engineer_credit_risk_features
from backend.ml.credit_risk.model import CreditRiskModel

def main():
    print("Generating synthetic data...")
    df = generate_credit_risk_data(n_samples=10000)
    print(f"Data shape: {df.shape}")
    print(f"Default rate: {df['defaulted'].mean():.4f}")
    
    print("Engineering features...")
    X, y = engineer_credit_risk_features(df)
    
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("Training model...")
    model = CreditRiskModel(version="1.0.0")
    metrics = model.train(X_train, y_train, X_test, y_test)
    
    print("\n=== Evaluation Metrics ===")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")
        
    save_path = "/Users/ekanshsukla/Desktop/credit_riskml/backend/models/credit_risk/"
    print(f"\nSaving model to {save_path}...")
    model.save(save_path)
    print("Done!")

if __name__ == "__main__":
    main()
