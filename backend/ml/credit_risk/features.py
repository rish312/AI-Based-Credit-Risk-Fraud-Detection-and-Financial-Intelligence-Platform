import pandas as pd
from typing import Tuple

def debt_to_income_ratio(existing_debt: pd.Series, income: pd.Series) -> pd.Series:
    return existing_debt / (income + 1)

def credit_utilization(current_balance: pd.Series, credit_limit: pd.Series) -> pd.Series:
    return current_balance / (credit_limit + 1)

def credit_history_length_years(account_tenure_months: pd.Series) -> pd.Series:
    return account_tenure_months / 12.0

def delinquency_rate(payment_history: pd.Series) -> pd.Series:
    # fraction of late payments in the 24-month window
    return payment_history.apply(lambda x: sum(x) / len(x) if len(x) > 0 else 0)

def recent_delinquency_count(payment_history: pd.Series, window: int = 6) -> pd.Series:
    # late payments in last `window` months
    return payment_history.apply(lambda x: sum(x[-window:]) if len(x) >= window else sum(x))

def engineer_credit_risk_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Takes raw data and returns a DataFrame with engineered features and original numeric features.
    Returns (X, y).
    """
    X = pd.DataFrame()
    
    # Original numeric features
    X['income'] = df['income']
    X['employment_years'] = df['employment_years']
    X['existing_debt'] = df['existing_debt']
    X['credit_score'] = df['credit_score']
    X['account_tenure_months'] = df['account_tenure_months']
    X['credit_limit'] = df['credit_limit']
    X['current_balance'] = df['current_balance']
    X['num_open_accounts'] = df['num_open_accounts']
    X['recent_inquiries'] = df['recent_inquiries']
    
    # Engineered features
    X['debt_to_income_ratio'] = debt_to_income_ratio(df['existing_debt'], df['income'])
    X['credit_utilization'] = credit_utilization(df['current_balance'], df['credit_limit'])
    X['credit_history_length_years'] = credit_history_length_years(df['account_tenure_months'])
    
    if 'monthly_payment_history' in df.columns:
        X['delinquency_rate'] = delinquency_rate(df['monthly_payment_history'])
        X['recent_delinquency_count'] = recent_delinquency_count(df['monthly_payment_history'])
    else:
        # Fallbacks for production if history is already parsed
        X['delinquency_rate'] = 0.0
        X['recent_delinquency_count'] = 0
        
    y = df['defaulted'] if 'defaulted' in df.columns else pd.Series()
    
    return X, y
