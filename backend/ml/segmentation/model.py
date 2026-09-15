import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import silhouette_score, accuracy_score
import joblib

class SegmentationModel:
    def __init__(self):
        self.kmeans = None
        self.surrogate = None
        self.scaler = None
        self.segment_profiles = {}
        self.feature_names = []
        self.n_clusters = 0
        self.metadata = {}
        
        self._profile_names = [
            'High-Value Loyalist',
            'At-Risk Churner',
            'Bargain Hunter',
            'New Explorer',
            'Dormant'
        ]

    def train(self, X: pd.DataFrame, feature_names: list) -> dict:
        """
        Train the KMeans clustering model and a surrogate RandomForest classifier.
        Tests k=3..7 and selects the one with the best silhouette score.
        """
        self.feature_names = feature_names
        X_arr = X.values if isinstance(X, pd.DataFrame) else X
        
        best_k = 5
        best_score = -1
        best_kmeans = None
        
        # Determine best K
        print("Testing k=3..7 for KMeans...")
        for k in range(3, 8):
            km = KMeans(n_clusters=k, random_state=42, n_init='auto')
            labels = km.fit_predict(X_arr)
            score = silhouette_score(X_arr, labels)
            print(f"k={k}, silhouette_score={score:.4f}")
            
            if score > best_score:
                best_score = score
                best_k = k
                best_kmeans = km
                
        self.n_clusters = best_k
        self.kmeans = best_kmeans
        
        # Final clustering
        cluster_labels = self.kmeans.predict(X_arr)
        
        # Train surrogate classifier
        self.surrogate = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        self.surrogate.fit(X_arr, cluster_labels)
        
        preds = self.surrogate.predict(X_arr)
        surrogate_acc = accuracy_score(cluster_labels, preds)
        
        # Build profiles
        self._build_segment_profiles(X, cluster_labels)
        
        metrics = {
            'best_k': self.n_clusters,
            'silhouette_score': float(best_score),
            'surrogate_accuracy': float(surrogate_acc)
        }
        
        self.metadata['metrics'] = metrics
        return metrics

    def _build_segment_profiles(self, X: pd.DataFrame, labels: np.ndarray):
        """
        Analyzes cluster centroids to assign human-readable names.
        """
        df = X.copy()
        df['cluster'] = labels
        centroids = df.groupby('cluster').mean()
        
        # Simple heuristic mapping
        # Sort centroids by composite score (monetary + freq + recency - churn) to find High-Value
        centroids['value_score'] = centroids.get('monetary_score', 0) + centroids.get('frequency_score', 0) + centroids.get('recency_score', 0)
        centroids['churn_score'] = centroids.get('churn_risk_signal', 0)
        
        unassigned_names = self._profile_names.copy()
        assigned = {}
        
        # Try to map based on defining characteristics, fallback to arbitrary assignment
        for cluster_id in range(self.n_clusters):
            row = centroids.loc[cluster_id]
            assigned_name = "Unknown Segment"
            
            if "High-Value Loyalist" in unassigned_names and row['value_score'] == centroids['value_score'].max():
                assigned_name = "High-Value Loyalist"
            elif "At-Risk Churner" in unassigned_names and row['churn_score'] == centroids['churn_score'].max():
                assigned_name = "At-Risk Churner"
            elif "New Explorer" in unassigned_names and row.get('tenure_months', 0) == centroids.get('tenure_months', 0).min():
                assigned_name = "New Explorer"
            elif "Dormant" in unassigned_names and row.get('recency_score', 1) == centroids.get('recency_score', 1).min():
                assigned_name = "Dormant"
            elif "Bargain Hunter" in unassigned_names:
                assigned_name = "Bargain Hunter"
            elif len(unassigned_names) > 0:
                assigned_name = unassigned_names[0]
                
            if assigned_name in unassigned_names:
                unassigned_names.remove(assigned_name)
                
            self.segment_profiles[int(cluster_id)] = {
                'name': assigned_name,
                'centroid': row.drop(['value_score', 'churn_score'], errors='ignore').to_dict()
            }

    def predict(self, features: dict) -> dict:
        """
        Predict segment for a single user/sample.
        """
        if not self.kmeans or not self.scaler:
            raise ValueError("Model is not trained or loaded.")
            
        # Convert dict to array in the correct order
        input_data = [features.get(f, 0.0) for f in self.feature_names]
        input_arr = np.array(input_data).reshape(1, -1)
        
        # Scale
        scaled_input = self.scaler.transform(pd.DataFrame(input_arr, columns=self.feature_names))
        
        # Predict using KMeans
        distances = self.kmeans.transform(scaled_input)[0]
        sorted_indices = np.argsort(distances)
        segment_id = int(sorted_indices[0])
        
        # Calculate confidence based on ratio of nearest to second nearest distance
        dist_1 = distances[sorted_indices[0]]
        dist_2 = distances[sorted_indices[1]]
        confidence = 1.0 - (dist_1 / (dist_2 + 1e-9))
        
        return {
            'segment_id': segment_id,
            'segment_name': self.segment_profiles.get(segment_id, {}).get('name', 'Unknown'),
            'confidence': max(0.0, min(1.0, float(confidence))),
            'model_version': self.metadata.get('version', 'unknown')
        }

    def save(self, path: str):
        """Save model artifacts to the specified path."""
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.kmeans, os.path.join(path, 'kmeans.joblib'))
        joblib.dump(self.surrogate, os.path.join(path, 'surrogate.joblib'))
        if self.scaler:
            joblib.dump(self.scaler, os.path.join(path, 'scaler.joblib'))
            
        with open(os.path.join(path, 'segment_profiles.json'), 'w') as f:
            json.dump(self.segment_profiles, f, indent=4)
            
        with open(os.path.join(path, 'metadata.json'), 'w') as f:
            json.dump({
                'version': self.metadata.get('version', '1.0.0'),
                'feature_names': self.feature_names,
                'n_clusters': self.n_clusters,
                'metrics': self.metadata.get('metrics', {})
            }, f, indent=4)

    @classmethod
    def load(cls, path: str) -> 'SegmentationModel':
        """Load model artifacts."""
        model = cls()
        model.kmeans = joblib.load(os.path.join(path, 'kmeans.joblib'))
        model.surrogate = joblib.load(os.path.join(path, 'surrogate.joblib'))
        
        scaler_path = os.path.join(path, 'scaler.joblib')
        if os.path.exists(scaler_path):
            model.scaler = joblib.load(scaler_path)
            
        with open(os.path.join(path, 'segment_profiles.json'), 'r') as f:
            # Convert string keys back to int
            profiles = json.load(f)
            model.segment_profiles = {int(k): v for k, v in profiles.items()}
            
        with open(os.path.join(path, 'metadata.json'), 'r') as f:
            metadata = json.load(f)
            model.metadata = metadata
            model.feature_names = metadata.get('feature_names', [])
            model.n_clusters = metadata.get('n_clusters', 0)
            
        return model

    def get_feature_names(self) -> list:
        return self.feature_names

    def get_segment_profiles(self) -> dict:
        return self.segment_profiles
