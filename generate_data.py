import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def seed_database():
    con = duckdb.connect('data/warehouse.duckdb')
    
    np.random.seed(42)
    num_accounts = 200
    num_days = 90
    
    # 1. Accounts Dimension
    tiers = ['Retail', 'Affluent', 'HighNetWorth', 'UltraHighNetWorth']
    advisors = ['Adv_Alpha', 'Adv_Beta', 'Adv_Gamma', 'Adv_Delta']
    
    accounts_df = pd.DataFrame({
        'account_id': [f"ACC_{i:04d}" for i in range(1, num_accounts + 1)],
        'advisor_id': np.random.choice(advisors, size=num_accounts),
        'client_tier': np.random.choice(tiers, size=num_accounts, p=[0.5, 0.3, 0.15, 0.05]),
        'opened_date': pd.date_range(end='2026-01-01', periods=num_accounts, freq='D')
    })
    
    con.execute("CREATE OR REPLACE TABLE dim_accounts AS SELECT * FROM accounts_df")
    
    # 2. Daily Balances (for AUM calculation)
    dates = pd.date_range(start='2026-06-01', periods=num_days, freq='D')
    balance_rows = []
    
    base_balances = {acc: np.random.uniform(50000, 5000000) for acc in accounts_df['account_id']}
    
    for dt in dates:
        for acc in accounts_df['account_id']:
            daily_change = np.random.normal(0, 0.008)
            base_balances[acc] = max(1000.0, base_balances[acc] * (1 + daily_change))
            balance_rows.append({
                'balance_date': dt.strftime('%Y-%m-%d'),
                'account_id': acc,
                'aum_usd': round(base_balances[acc], 2),
                'cash_usd': round(base_balances[acc] * 0.1, 2)
            })
            
    balances_df = pd.DataFrame(balance_rows)
    con.execute("CREATE OR REPLACE TABLE fct_daily_balances AS SELECT * FROM balances_df")
    
    # 3. Transactions (for Inflow / Outflow metrics)
    tx_types = ['DEPOSIT', 'WITHDRAWAL', 'FEE', 'BUY', 'SELL']
    num_tx = 3000
    
    tx_df = pd.DataFrame({
        'transaction_id': [f"TX_{i:06d}" for i in range(1, num_tx + 1)],
        'account_id': np.random.choice(accounts_df['account_id'], size=num_tx),
        'transaction_date': np.random.choice(dates.strftime('%Y-%m-%d'), size=num_tx),
        'tx_type': np.random.choice(tx_types, size=num_tx, p=[0.25, 0.15, 0.1, 0.25, 0.25]),
        'amount_usd': np.round(np.random.exponential(scale=10000, size=num_tx), 2)
    })
    
    con.execute("CREATE OR REPLACE TABLE fct_transactions AS SELECT * FROM tx_df")
    
    print("Database seeded successfully: data/warehouse.duckdb")
    print(con.execute("SHOW TABLES").fetchdf())
    con.close()

if __name__ == "__main__":
    seed_database()
