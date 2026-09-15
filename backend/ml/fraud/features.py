import pandas as pd
import numpy as np

def engineer_fraud_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer features for fraud model.
    """
    df_feat = df.copy()
    
    # txn_velocity_1h(prior_txn_count_24h) — estimated hourly rate
    df_feat['txn_velocity_1h'] = df_feat['prior_txn_count_24h'] / 24.0
    
    # txn_velocity_24h(prior_txn_count_24h) — direct
    df_feat['txn_velocity_24h'] = df_feat['prior_txn_count_24h']
    
    # amount_zscore(amount, mean_amount, std_amount) — how unusual is this amount
    mean_amount = df_feat['amount'].mean()
    std_amount = df_feat['amount'].std()
    df_feat['amount_zscore'] = (df_feat['amount'] - mean_amount) / (std_amount + 1e-6)
    
    # hour_risk_score(hour_of_day) — higher risk 0-5 AM, lower during business hours
    df_feat['hour_risk_score'] = df_feat['hour_of_day'].apply(
        lambda h: 2.0 if h in [0, 1, 2, 3, 4, 5] else (0.5 if 9 <= h <= 17 else 1.0)
    )
    
    # velocity_amount_ratio(prior_txn_amount_24h, amount) — current txn as fraction of recent activity
    df_feat['velocity_amount_ratio'] = df_feat['amount'] / (df_feat['prior_txn_amount_24h'] + 1.0)
    
    # Handle categorical merchant_category with one-hot encoding
    categories = ['grocery', 'electronics', 'travel', 'dining', 'gas', 'online', 'entertainment']
    for cat in categories:
        df_feat[f'merchant_{cat}'] = (df_feat['merchant_category'] == cat).astype(int)
        
    # ip_country with a binary is_domestic flag
    df_feat['is_domestic'] = (df_feat['ip_country'] == 'US').astype(int)
    
    # Drop original non-numeric columns
    cols_to_drop = ['merchant_category', 'device_id', 'ip_country']
    df_feat.drop(columns=[c for c in cols_to_drop if c in df_feat.columns], inplace=True)
    
    return df_feat
