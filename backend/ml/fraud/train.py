import os
import json
from datetime import datetime
from sklearn.model_selection import train_test_split

from backend.ml.fraud.data_generator import generate_fraud_data
from backend.ml.fraud.features import engineer_fraud_features
from backend.ml.fraud.model import FraudModel

def run_training():
    print("Generating fraud data...")
    df = generate_fraud_data(n_samples=50000, random_state=42)
    
    print(f"Generated data: {len(df)} rows. Fraud rate: {df['is_fraud'].mean():.4f}")
    
    print("Engineering features...")
    df_engineered = engineer_fraud_features(df)
    
    X = df_engineered.drop(columns=['is_fraud'])
    y = df_engineered['is_fraud']
    
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("Training model...")
    model = FraudModel()
    metrics = model.train(X_train, y_train, X_test, y_test)
    
    model.metadata = {
        'version': '1.0.0',
        'trained_at': datetime.utcnow().isoformat(),
        'metrics': metrics
    }
    
    print("\n--- Evaluation Metrics ---")
    print(f"AUC-ROC: {metrics['roc_auc']:.4f}")
    print(f"F1 Score (Auto-Decline): {metrics['f1']:.4f}")
    print(f"Auto-Decline (>=0.7) - Precision: {metrics['precision_auto_decline']:.4f}, Recall: {metrics['recall_auto_decline']:.4f}")
    print(f"Manual Review (>=0.3) - Precision: {metrics['precision_manual_review']:.4f}, Recall: {metrics['recall_manual_review']:.4f}")
    print(f"Confusion Matrix: {metrics['confusion_matrix']}")
    
    print("\n--- Tier Distribution on Test Set ---")
    for tier, count in metrics['tier_distribution'].items():
        pct = count / len(y_test) * 100
        print(f"  {tier}: {count} ({pct:.1f}%)")
        
    save_path = "/Users/ekanshsukla/Desktop/credit_riskml/backend/models/fraud/"
    print(f"\nSaving model to {save_path}...")
    model.save(save_path)
    print("Done!")

if __name__ == '__main__':
    run_training()
