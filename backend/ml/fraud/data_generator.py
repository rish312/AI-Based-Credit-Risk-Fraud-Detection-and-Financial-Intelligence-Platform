import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import uuid

def generate_fraud_data(n_samples=50000, random_state=42) -> pd.DataFrame:
    np.random.seed(random_state)
    random.seed(random_state)
    
    # Base features
    # Amount: log-normal, mostly $5-$500
    amount = np.random.lognormal(mean=np.log(50), sigma=1.0, size=n_samples)
    amount = np.clip(amount, 1.0, 10000.0)
    
    # Merchant category
    categories = ['grocery', 'electronics', 'travel', 'dining', 'gas', 'online', 'entertainment']
    merchant_category = np.random.choice(categories, size=n_samples)
    
    # Device ID
    n_devices = int(n_samples * 0.8)  # some shared
    devices = [str(uuid.uuid4()) for _ in range(n_devices)]
    device_id = np.random.choice(devices, size=n_samples)
    
    # IP country
    countries = ['US', 'CA', 'UK', 'MX', 'CN', 'RU', 'NG', 'BR']
    country_probs = [0.85, 0.05, 0.03, 0.02, 0.015, 0.015, 0.01, 0.01]
    ip_country = np.random.choice(countries, p=country_probs, size=n_samples)
    
    # Hour of day
    hour_of_day = np.random.randint(0, 24, size=n_samples)
    
    # Account age days
    account_age_days = np.random.exponential(scale=365, size=n_samples)
    account_age_days = np.clip(account_age_days, 1, 3650)
    
    # Prior txn count 24h
    prior_txn_count_24h = np.random.poisson(lam=2, size=n_samples)
    
    # Prior txn amount 24h
    prior_txn_amount_24h = prior_txn_count_24h * np.random.lognormal(mean=np.log(40), sigma=0.8, size=n_samples)
    
    # Is new device
    is_new_device = np.random.choice([0, 1], p=[0.9, 0.1], size=n_samples)
    
    # Distance from home
    distance_from_home = np.random.lognormal(mean=np.log(10), sigma=1.5, size=n_samples)
    distance_from_home = np.clip(distance_from_home, 0, 5000)
    
    # Target: is_fraud
    # Fraud probability correlated with: high amount + unusual hour (2-5) + new device + foreign IP + high velocity (count > 5)
    
    # Base log-odds
    log_odds = -5.0
    
    log_odds += (amount > 500) * 1.5
    log_odds += np.isin(merchant_category, ['electronics', 'online']) * 1.0
    log_odds += np.isin(hour_of_day, [2, 3, 4, 5]) * 2.0
    log_odds += (is_new_device == 1) * 2.0
    log_odds += (ip_country != 'US') * 1.5
    log_odds += (prior_txn_count_24h > 5) * 1.5
    log_odds += (account_age_days < 30) * 1.0
    log_odds += (distance_from_home > 500) * 1.0
    
    # Shared devices - proxy for fraud rings
    device_counts = pd.Series(device_id).value_counts()
    shared_device_mask = pd.Series(device_id).map(device_counts) > 3
    log_odds += shared_device_mask * 2.0
    
    probs = 1 / (1 + np.exp(-log_odds))
    
    # Adjust overall rate by scaling probs or intercept, here we just sample
    is_fraud = np.random.binomial(1, probs)
    
    df = pd.DataFrame({
        'amount': amount,
        'merchant_category': merchant_category,
        'device_id': device_id,
        'ip_country': ip_country,
        'hour_of_day': hour_of_day,
        'account_age_days': account_age_days,
        'prior_txn_count_24h': prior_txn_count_24h,
        'prior_txn_amount_24h': prior_txn_amount_24h,
        'is_new_device': is_new_device,
        'distance_from_home': distance_from_home,
        'is_fraud': is_fraud
    })
    
    return df

if __name__ == '__main__':
    df = generate_fraud_data()
    print(f"Generated {len(df)} samples with {df['is_fraud'].mean()*100:.2f}% fraud rate.")
