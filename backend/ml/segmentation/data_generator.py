import numpy as np
import pandas as pd

def generate_segmentation_data(n_samples=8000, random_state=42) -> pd.DataFrame:
    """
    Generate synthetic customer data for segmentation with 5 distinct natural clusters.
    """
    np.random.seed(random_state)
    
    # Define cluster proportions
    cluster_probs = [0.25, 0.20, 0.30, 0.15, 0.10]
    n_clusters = 5
    cluster_sizes = np.random.multinomial(n_samples, cluster_probs)
    
    # Feature list:
    # 0: days_since_last_purchase
    # 1: purchase_frequency
    # 2: total_spend
    # 3: avg_order_value
    # 4: age
    # 5: tenure_months
    # 6: support_tickets
    # 7: email_open_rate
    # 8: login_frequency
    # 9: days_since_last_login
    
    data = []
    
    # 1. High-value loyalists: high frequency, high spend, long tenure, high engagement
    mean_1 = [10, 25, 5000, 200, 45, 60, 1, 0.8, 15, 2]
    cov_1 = np.diag([5, 5, 1000, 30, 10, 15, 1, 0.1, 3, 1])**2
    data_1 = np.random.multivariate_normal(mean_1, cov_1, cluster_sizes[0])
    
    # 2. At-risk churners: declining freq, high past spend, high support, low engagement
    mean_2 = [120, 5, 4000, 800, 40, 48, 8, 0.2, 2, 45]
    cov_2 = np.diag([20, 2, 800, 100, 10, 10, 2, 0.1, 1, 10])**2
    data_2 = np.random.multivariate_normal(mean_2, cov_2, cluster_sizes[1])
    
    # 3. Bargain hunters: moderate freq, low avg order val, high sales
    mean_3 = [45, 12, 600, 50, 30, 24, 2, 0.5, 6, 15]
    cov_3 = np.diag([10, 3, 200, 15, 8, 8, 1, 0.1, 2, 5])**2
    data_3 = np.random.multivariate_normal(mean_3, cov_3, cluster_sizes[2])
    
    # 4. New explorers: short tenure, moderate engagement, growing freq
    mean_4 = [15, 3, 300, 100, 25, 3, 1, 0.6, 8, 5]
    cov_4 = np.diag([5, 1, 100, 20, 5, 1, 1, 0.1, 2, 2])**2
    data_4 = np.random.multivariate_normal(mean_4, cov_4, cluster_sizes[3])
    
    # 5. Dormant: very low recent activity, old tenure, low engagement
    mean_5 = [300, 1, 100, 100, 55, 72, 0, 0.05, 0.5, 200]
    cov_5 = np.diag([40, 0.5, 50, 20, 12, 20, 0.5, 0.02, 0.2, 30])**2
    data_5 = np.random.multivariate_normal(mean_5, cov_5, cluster_sizes[4])
    
    all_data = np.vstack([data_1, data_2, data_3, data_4, data_5])
    
    # Clip values to realistic ranges
    df = pd.DataFrame(all_data, columns=[
        'days_since_last_purchase', 'purchase_frequency', 'total_spend', 
        'avg_order_value', 'age', 'tenure_months', 'support_tickets',
        'email_open_rate', 'login_frequency', 'days_since_last_login'
    ])
    
    df['days_since_last_purchase'] = df['days_since_last_purchase'].clip(0, 3650)
    df['purchase_frequency'] = df['purchase_frequency'].clip(0, 1000)
    df['total_spend'] = df['total_spend'].clip(0, 100000)
    df['avg_order_value'] = df['avg_order_value'].clip(0, 10000)
    df['age'] = df['age'].clip(18, 80)
    df['tenure_months'] = df['tenure_months'].clip(0, 120)
    df['support_tickets'] = np.round(df['support_tickets'].clip(0, 50))
    df['email_open_rate'] = df['email_open_rate'].clip(0.0, 1.0)
    df['login_frequency'] = df['login_frequency'].clip(0, 1000)
    df['days_since_last_login'] = df['days_since_last_login'].clip(0, 3650)
    
    # Shuffle
    df = df.sample(frac=1, random_state=random_state).reset_index(drop=True)
    return df

if __name__ == "__main__":
    df = generate_segmentation_data()
    print(f"Generated {len(df)} samples.")
    print(df.describe())
