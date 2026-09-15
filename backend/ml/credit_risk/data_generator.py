import numpy as np
import pandas as pd
from typing import Tuple

def generate_credit_risk_data(n_samples: int = 10000, random_state: int = 42) -> pd.DataFrame:
    """
    Generate synthetic credit risk data.
    """
    np.random.seed(random_state)
    
    # 1. Income (log-normal, mean ~$60k, std ~$30k)
    # Lognormal parameters: mu = 10.88, sigma = 0.47
    income = np.random.lognormal(mean=10.88, sigma=0.47, size=n_samples)
    income = np.clip(income, 15000, 300000)
    
    # 2. Employment years (0-40, correlated with income)
    employment_years = (income / 15000) + np.random.normal(loc=0, scale=3, size=n_samples)
    employment_years = np.clip(np.round(employment_years), 0, 40)
    
    # 3. Existing debt (correlated with income)
    # Higher income -> can carry more debt. Say debt is around 10-50% of income.
    debt_ratio = np.random.uniform(0.1, 0.5, size=n_samples)
    existing_debt = income * debt_ratio
    
    # 4. Credit Score (300-850)
    # Base score on income and debt ratio
    base_score = 650 + (income - 60000) / 2000 - debt_ratio * 300 + np.random.normal(0, 50, n_samples)
    credit_score = np.clip(np.round(base_score), 300, 850)
    
    # 5. Account tenure months (1-360)
    # Correlated with employment years
    account_tenure_months = employment_years * 12 + np.random.normal(0, 24, n_samples)
    account_tenure_months = np.clip(np.round(account_tenure_months), 1, 360)
    
    # 6. Credit limit
    # Correlated with income and credit score
    credit_limit = (income * 0.1) * (credit_score / 600) + np.random.normal(0, 1000, n_samples)
    credit_limit = np.clip(np.round(credit_limit), 500, 50000)
    
    # 7. Current balance (fraction of credit limit)
    # Lower credit score usually means higher utilization
    utilization = np.random.beta(a=2, b=5, size=n_samples)
    utilization += (850 - credit_score) / 1000
    utilization = np.clip(utilization, 0, 1)
    current_balance = credit_limit * utilization
    
    # 8. Number of open accounts (1-20)
    num_open_accounts = np.clip(np.round(np.random.normal(loc=5, scale=3, size=n_samples)), 1, 20)
    
    # 9. Recent inquiries (0-10)
    # Lower credit score might mean more recent inquiries
    recent_inquiries = np.random.poisson(lam=1.5, size=n_samples) + (credit_score < 600).astype(int) * 2
    recent_inquiries = np.clip(recent_inquiries, 0, 10)
    
    # 10. Monthly payment history (24 months)
    # Late payments more likely with high DTI
    dti = existing_debt / (income + 1)
    monthly_payment_history = []
    prob_late = np.clip(dti * 0.2 + (850 - credit_score) / 1000, 0.01, 0.5)
    for i in range(n_samples):
        # 0 = on-time, 1 = late
        history = np.random.binomial(n=1, p=prob_late[i], size=24).tolist()
        monthly_payment_history.append(history)
        
    # Generate Target: Defaulted (0/1) with ~8% rate
    # P(default) related to dti, credit_score, late payments
    late_payments_count = np.array([sum(h) for h in monthly_payment_history])
    
    # Logit function for probabilities
    logit_p = -3.5 + 2.0 * dti - 0.005 * credit_score + 0.15 * late_payments_count + 0.2 * recent_inquiries
    prob_default = 1 / (1 + np.exp(-logit_p))
    
    # Calibrate to ~8% default rate roughly
    # We'll just shift the probabilities if needed or use them directly if they average ~8%
    # Adjust intercept if needed, but random binomial should give us roughly realistic numbers.
    defaulted = np.random.binomial(1, p=np.clip(prob_default, 0, 1))
    
    df = pd.DataFrame({
        'income': income,
        'employment_years': employment_years,
        'existing_debt': existing_debt,
        'monthly_payment_history': monthly_payment_history,
        'credit_score': credit_score,
        'account_tenure_months': account_tenure_months,
        'credit_limit': credit_limit,
        'current_balance': current_balance,
        'num_open_accounts': num_open_accounts,
        'recent_inquiries': recent_inquiries,
        'defaulted': defaulted
    })
    
    return df
