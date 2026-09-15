import os
import json
import joblib
import datetime
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score, brier_score_loss

class CreditRiskModel:
    def __init__(self, version: str = "1.0.0"):
        self.version = version
        base_estimator = HistGradientBoostingClassifier(
            max_depth=6,
            max_iter=200,
            learning_rate=0.1,
            random_state=42
        )
        self.model = CalibratedClassifierCV(base_estimator, method='isotonic', cv=3)
        self.feature_names = []
        self.metrics = {}
        self.trained_at = None

    def train(self, X_train, y_train, X_val, y_val) -> dict:
        self.feature_names = list(X_train.columns)
        self.model.fit(X_train, y_train)
        
        y_pred = self.model.predict(X_val)
        y_prob = self.model.predict_proba(X_val)[:, 1]
        
        self.metrics = {
            "auc_roc": float(roc_auc_score(y_val, y_prob)),
            "accuracy": float(accuracy_score(y_val, y_pred)),
            "precision": float(precision_score(y_val, y_pred, zero_division=0)),
            "recall": float(recall_score(y_val, y_pred, zero_division=0)),
            "f1": float(f1_score(y_val, y_pred, zero_division=0)),
            "brier_score": float(brier_score_loss(y_val, y_prob))
        }
        
        self.trained_at = datetime.datetime.now().isoformat()
        return self.metrics

    def _get_risk_tier(self, probability: float) -> str:
        if probability < 0.15:
            return "Low"
        elif probability < 0.4:
            return "Medium"
        elif probability < 0.7:
            return "High"
        else:
            return "Very High"

    def predict(self, features: dict) -> dict:
        import pandas as pd
        df = pd.DataFrame([features])
        df = df[self.feature_names] # ensure order
        
        prob = float(self.model.predict_proba(df)[0, 1])
        score = int((1 - prob) * 850) # simple score inversion mapping
        
        return {
            "score": score,
            "probability": prob,
            "risk_tier": self._get_risk_tier(prob),
            "model_version": self.version
        }

    def save(self, path: str):
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.model, os.path.join(path, "model.joblib"))
        
        metadata = {
            "version": self.version,
            "trained_at": self.trained_at,
            "metrics": self.metrics,
            "feature_names": self.feature_names
        }
        
        with open(os.path.join(path, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=4)

    @classmethod
    def load(cls, path: str) -> 'CreditRiskModel':
        with open(os.path.join(path, "metadata.json"), "r") as f:
            metadata = json.load(f)
            
        instance = cls(version=metadata.get("version", "1.0.0"))
        instance.model = joblib.load(os.path.join(path, "model.joblib"))
        instance.feature_names = metadata.get("feature_names", [])
        instance.metrics = metadata.get("metrics", {})
        instance.trained_at = metadata.get("trained_at", None)
        
        return instance

    def get_feature_names(self) -> list:
        """Return ordered list of feature names."""
        return self.feature_names
