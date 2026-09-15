import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Any, Union

try:
    from xgboost import XGBClassifier
except Exception as e:
    from sklearn.ensemble import HistGradientBoostingClassifier
    class XGBClassifier:
        def __init__(self, scale_pos_weight=None, max_depth=None, n_estimators=None, random_state=None, **kwargs):
            self.model = HistGradientBoostingClassifier(max_iter=n_estimators or 100, max_depth=max_depth, random_state=random_state)
        def fit(self, X, y, eval_set=None, verbose=False):
            return self.model.fit(X, y)
        def predict_proba(self, X):
            return self.model.predict_proba(X)
    print("Warning: xgboost could not be imported (likely missing libomp). Falling back to HistGradientBoostingClassifier.")

class FraudModel:
    def __init__(self):
        # We handle XGBoost fallback gracefully
        self.xgb_model = XGBClassifier(
            scale_pos_weight=50,
            max_depth=5,
            n_estimators=150,
            random_state=42
        )
        self.isolation_forest = IsolationForest(
            contamination=0.015,
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.feature_names = []
        self.metadata = {}
        
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val: pd.DataFrame, y_val: pd.Series) -> Dict[str, Any]:
        self.feature_names = list(X_train.columns)
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        try:
            self.xgb_model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                verbose=False
            )
        except TypeError:
            # HistGradientBoostingClassifier does not take eval_set in fit
            self.xgb_model.fit(X_train, y_train)
            
        self.isolation_forest.fit(X_train_scaled)
        
        metrics = self._evaluate(X_val, y_val)
        return metrics
        
    def _evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score, confusion_matrix
        
        scores = self._compute_scores(X)
        
        metrics = {}
        metrics['roc_auc'] = float(roc_auc_score(y, scores))
        
        predictions = (scores >= 0.7).astype(int)
        
        metrics['f1'] = float(f1_score(y, predictions))
        metrics['precision_auto_decline'] = float(precision_score(y, scores >= 0.7, zero_division=0))
        metrics['recall_auto_decline'] = float(recall_score(y, scores >= 0.7, zero_division=0))
        
        metrics['precision_manual_review'] = float(precision_score(y, scores >= 0.3, zero_division=0))
        metrics['recall_manual_review'] = float(recall_score(y, scores >= 0.3, zero_division=0))
        
        cm = confusion_matrix(y, predictions)
        metrics['confusion_matrix'] = cm.tolist()
        
        tiers = self._compute_tiers(scores)
        metrics['tier_distribution'] = {
            'auto_approve': int(np.sum(tiers == 'auto_approve')),
            'manual_review': int(np.sum(tiers == 'manual_review')),
            'auto_decline': int(np.sum(tiers == 'auto_decline'))
        }
        
        return metrics

    def _compute_scores(self, X: pd.DataFrame) -> np.ndarray:
        xgb_proba = self.xgb_model.predict_proba(X)[:, 1]
        
        X_scaled = self.scaler.transform(X)
        if_scores_raw = self.isolation_forest.decision_function(X_scaled)
        
        anomaly_score = -if_scores_raw
        
        a_min, a_max = -0.15, 0.15
        anomaly_score = np.clip((anomaly_score - a_min) / (a_max - a_min), 0, 1)
        
        combined_score = 0.7 * xgb_proba + 0.3 * anomaly_score
        return combined_score
        
    def _compute_tiers(self, scores: np.ndarray) -> np.ndarray:
        tiers = np.where(scores < 0.3, 'auto_approve', 
                         np.where(scores <= 0.7, 'manual_review', 'auto_decline'))
        return tiers

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        X = pd.DataFrame([features])[self.feature_names]
        
        scores = self._compute_scores(X)
        score = float(scores[0])
        tier = 'auto_approve' if score < 0.3 else ('manual_review' if score <= 0.7 else 'auto_decline')
        
        decision = 'decline' if tier == 'auto_decline' else ('approve' if tier == 'auto_approve' else 'review')
        
        return {
            'fraud_score': score,
            'decision': decision,
            'decision_tier': tier,
            'model_version': self.metadata.get('version', 'unknown')
        }

    def save(self, path: str):
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.xgb_model, os.path.join(path, 'xgb_model.joblib'))
        joblib.dump(self.isolation_forest, os.path.join(path, 'isolation_forest.joblib'))
        joblib.dump(self.scaler, os.path.join(path, 'scaler.joblib'))
        joblib.dump(self.feature_names, os.path.join(path, 'feature_names.joblib'))
        
        with open(os.path.join(path, 'metadata.json'), 'w') as f:
            json.dump(self.metadata, f, indent=4)

    @classmethod
    def load(cls, path: str) -> 'FraudModel':
        model = cls()
        model.xgb_model = joblib.load(os.path.join(path, 'xgb_model.joblib'))
        model.isolation_forest = joblib.load(os.path.join(path, 'isolation_forest.joblib'))
        model.scaler = joblib.load(os.path.join(path, 'scaler.joblib'))
        model.feature_names = joblib.load(os.path.join(path, 'feature_names.joblib'))
        
        with open(os.path.join(path, 'metadata.json'), 'r') as f:
            model.metadata = json.load(f)
            
        return model

    def get_feature_names(self) -> List[str]:
        return self.feature_names
