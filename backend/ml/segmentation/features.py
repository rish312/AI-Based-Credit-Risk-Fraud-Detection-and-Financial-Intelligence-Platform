import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def engineer_segmentation_features(df: pd.DataFrame):
    """
    Engineer features for customer segmentation and scale them.
    Returns:
        X_scaled (pd.DataFrame): Engineered and scaled features
        scaler (StandardScaler): The fitted scaler
    """
    df_eng = df.copy()
    
    # 1. recency_score (higher is better, inverse of days_since_last_purchase)
    max_days_purchase = df_eng['days_since_last_purchase'].max() + 1
    df_eng['recency_score'] = 1.0 - (df_eng['days_since_last_purchase'] / max_days_purchase)
    
    # 2. frequency_score
    df_eng['frequency_score'] = df_eng['purchase_frequency']
    
    # 3. monetary_score
    df_eng['monetary_score'] = df_eng['total_spend']
    
    # 4. engagement_index
    # Combine email open rate and login frequency
    max_login = df_eng['login_frequency'].max() + 1
    normalized_login = df_eng['login_frequency'] / max_login
    df_eng['engagement_index'] = (df_eng['email_open_rate'] + normalized_login) / 2
    
    # 5. churn_risk_signal
    # Higher risk if high days since purchase, high days since login, high tickets
    max_login_days = df_eng['days_since_last_login'].max() + 1
    max_tickets = df_eng['support_tickets'].max() + 1
    
    norm_days_purchase = df_eng['days_since_last_purchase'] / max_days_purchase
    norm_days_login = df_eng['days_since_last_login'] / max_login_days
    norm_tickets = df_eng['support_tickets'] / max_tickets
    
    df_eng['churn_risk_signal'] = (0.4 * norm_days_purchase) + (0.3 * norm_days_login) + (0.3 * norm_tickets)
    
    # 6. estimated_clv (simplified CLV)
    # CLV = avg_order_value * purchase_frequency * (tenure_months + expected future months)
    # Keep it simple: value rate * tenure
    df_eng['estimated_clv'] = df_eng['avg_order_value'] * df_eng['purchase_frequency'] * (df_eng['tenure_months'] / 12 + 1)
    
    # Select features for clustering
    features_to_scale = [
        'recency_score', 'frequency_score', 'monetary_score', 
        'engagement_index', 'churn_risk_signal', 'estimated_clv',
        'age', 'tenure_months'
    ]
    
    X = df_eng[features_to_scale]
    
    # Scale features
    scaler = StandardScaler()
    X_scaled_np = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled_np, columns=features_to_scale, index=X.index)
    
    return X_scaled, scaler
