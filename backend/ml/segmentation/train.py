import os
import json
from datetime import datetime
from backend.ml.segmentation.data_generator import generate_segmentation_data
from backend.ml.segmentation.features import engineer_segmentation_features
from backend.ml.segmentation.model import SegmentationModel

def main():
    print("Generating synthetic data...")
    df_raw = generate_segmentation_data(n_samples=8000, random_state=42)
    
    print("Engineering features...")
    X_scaled, scaler = engineer_segmentation_features(df_raw)
    feature_names = list(X_scaled.columns)
    
    print("Training Segmentation Model...")
    model = SegmentationModel()
    model.scaler = scaler
    
    # Train the model
    metrics = model.train(X_scaled, feature_names)
    
    print("\n--- Training Results ---")
    print(f"Best K (Number of clusters): {metrics['best_k']}")
    print(f"Silhouette Score: {metrics['silhouette_score']:.4f}")
    print(f"Surrogate Accuracy (RandomForest): {metrics['surrogate_accuracy']:.4f}")
    
    # Analyze clusters
    cluster_labels = model.kmeans.labels_
    import pandas as pd
    cluster_sizes = pd.Series(cluster_labels).value_counts().to_dict()
    print("\nCluster Sizes:")
    for cluster_id, size in cluster_sizes.items():
        profile = model.segment_profiles[cluster_id]
        print(f"Cluster {cluster_id} ({profile['name']}): {size} samples")
        
    # Save the model
    save_path = '/Users/ekanshsukla/Desktop/credit_riskml/backend/models/segmentation/'
    model.metadata = {
        'version': '1.0.0',
        'trained_at': datetime.utcnow().isoformat(),
        'metrics': metrics
    }
    
    print(f"\nSaving model to {save_path}...")
    model.save(save_path)
    
    # Verify metadata saved correctly
    with open(os.path.join(save_path, 'metadata.json'), 'r') as f:
        meta_saved = json.load(f)
        print("Saved metadata:")
        print(json.dumps(meta_saved, indent=2))
        
    print("Done!")

if __name__ == "__main__":
    main()
