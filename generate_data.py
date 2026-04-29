"""
Synthetic data generation for A/B test analysis.

This module generates realistic data for testing a free trial hypothesis.
Control group (A): Immediate paywall ($10/month)
Treatment group (B): Free trial for 30 days, then $10/month
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple

def validate_data(users_df: pd.DataFrame, subscriptions_df: pd.DataFrame, trades_df: pd.DataFrame) -> None:
    """Validate generated data for consistency and logical correctness."""
    
    print("\n✓ Validating data integrity...")
    
    # Check no deposits before registration
    if len(users_df) > 0 and users_df['first_deposit_date'].notna().any():
        assert (users_df.loc[users_df['first_deposit_date'].notna(), 'first_deposit_date'] >= 
                users_df.loc[users_df['first_deposit_date'].notna(), 'registration_date']).all(), \
            "ERROR: Found deposits before registration!"
    
    # Check no duplicate user_ids
    assert len(users_df) == len(users_df['user_id'].unique()), \
        "ERROR: Found duplicate user_ids!"
    
    # Check all subscription user_ids exist in users table
    if len(subscriptions_df) > 0:
        assert set(subscriptions_df['user_id']).issubset(set(users_df['user_id'])), \
            "ERROR: Subscriptions contain unknown users!"
        
        # Check no duplicate subscription_ids
        assert len(subscriptions_df) == len(subscriptions_df['subscription_id'].unique()), \
            "ERROR: Found duplicate subscription_ids!"
    
    # Check all trade user_ids exist in users table
    if len(trades_df) > 0:
        assert set(trades_df['user_id']).issubset(set(users_df['user_id'])), \
            "ERROR: Trades contain unknown users!"
    
    print("  ✓ All data validations passed")


def generate_data(n_users: int = 8000, seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Generate synthetic A/B test data for fintech premium subscription experiment.
    
    Args:
        n_users: Total number of users (will be split 50/50 between groups A and B)
        seed: Random seed for reproducibility (default 42)
        
    Returns:
        Tuple of (users_df, subscriptions_df, trades_df) DataFrames
        
    Data characteristics:
        - Users: user_id, registration_date, group_name (A or B), age, initial_balance_usd, first_deposit_date
        - Subscriptions: subscription_id, user_id, payment_date, payment_status
        - Trades: user_id, trade_date, commission_usd
        
    Experiment design:
        - Group A (Control): Immediate paywall with 2% conversion rate
        - Group B (Treatment): Free trial with 5% sign-up and 60% conversion after trial
        - Observation period: 6 months from registration
    """
    
    np.random.seed(seed)
    print("=" * 60)
    print("Generating synthetic A/B test data...")
    print("=" * 60)
    
    # ============ GENERATE USERS ============
    print("\n1. Generating user cohort...")
    user_ids = range(1000, 1000 + n_users)
    
    # Registration period: 3 weeks (Nov 1 - Nov 21, 2023)
    start_date = datetime(2023, 11, 1)
    end_date = datetime(2023, 11, 21)
    registration_dates = [
        start_date + timedelta(days=np.random.randint(0, (end_date - start_date).days)) 
        for _ in range(n_users)
    ]
    
    # 50/50 split between groups
    groups = np.random.choice(['A', 'B'], size=n_users, p=[0.5, 0.5])
    
    # User demographics
    ages = np.random.normal(35, 10, n_users).astype(int)
    ages = np.clip(ages, 18, 80)  # Realistic age range
    
    initial_balances = np.random.exponential(1000, n_users)
    
    # 70% of users make a deposit at signup
    made_first_deposit = np.random.binomial(1, 0.7, n_users)
    
    first_deposit_dates = []
    for i, deposited in enumerate(made_first_deposit):
        if deposited:
            # Deposit within 0-5 days after registration
            deposit_date = registration_dates[i] + timedelta(days=np.random.randint(0, 6))
            first_deposit_dates.append(deposit_date)
        else:
            first_deposit_dates.append(None)
    
    users_df = pd.DataFrame({
        'user_id': user_ids,
        'registration_date': registration_dates,
        'group_name': groups,
        'age': ages,
        'initial_balance_usd': initial_balances,
        'first_deposit_date': first_deposit_dates
    })
    
    print(f"  ✓ Created {len(users_df):,} users")
    print(f"    - Group A (Control):   {(users_df['group_name'] == 'A').sum():,}")
    print(f"    - Group B (Treatment): {(users_df['group_name'] == 'B').sum():,}")
    print(f"    - With deposits:       {(users_df['first_deposit_date'].notna()).sum():,} ({(users_df['first_deposit_date'].notna()).sum()/len(users_df)*100:.1f}%)")
    
    # ============ GENERATE SUBSCRIPTIONS ============
    print("\n2. Generating subscription payments...")
    subscriptions_data = []
    subscription_id_counter = 1
    
    for idx, user in users_df.iterrows():
        # GROUP A: Immediate paywall with 2% conversion
        if user['group_name'] == 'A':
            converted = np.random.binomial(1, 0.02)  # 2% conversion rate
            if converted:
                sub_date = user['registration_date'] + timedelta(days=np.random.randint(1, 8))
                
                # Simulate monthly payments for up to 6 months with increasing churn
                for month in range(6):
                    churn_rate = month * 0.05  # 0%, 5%, 10%, 15%, 20%, 25%
                    retained = np.random.binomial(1, 0.9 - churn_rate)
                    
                    if retained:
                        payment_date = sub_date + timedelta(days=30*month)
                        subscriptions_data.append({
                            'user_id': user['user_id'],
                            'subscription_id': subscription_id_counter,
                            'payment_date': payment_date,
                            'payment_status': 'success'
                        })
                        subscription_id_counter += 1
                    else:
                        break  # User churned
        
        # GROUP B: Free trial with 5% sign-up and 60% conversion after trial
        else:
            converted_trial = np.random.binomial(1, 0.05)  # 5% sign up for trial
            
            if converted_trial:
                trial_start = user['registration_date'] + timedelta(days=np.random.randint(1, 5))
                
                # After 30-day trial, 60% convert to paying
                converts_to_paying = np.random.binomial(1, 0.6)
                
                if converts_to_paying:
                    # Start paying from month 2 (after 30-day free trial)
                    for month in range(1, 6):  # Payments in months 2-6
                        churn_rate = (month - 1) * 0.05
                        retained = np.random.binomial(1, 0.85 - churn_rate)
                        
                        if retained:
                            payment_date = trial_start + timedelta(days=30*month)
                            subscriptions_data.append({
                                'user_id': user['user_id'],
                                'subscription_id': subscription_id_counter,
                                'payment_date': payment_date,
                                'payment_status': 'success'
                            })
                            subscription_id_counter += 1
                        else:
                            break
    
    subscriptions_df = pd.DataFrame(subscriptions_data)
    
    # Calculate conversion rates
    control_converted = len(users_df[(users_df['group_name'] == 'A') & 
                                      (users_df['user_id'].isin(subscriptions_df['user_id'].unique()))])
    control_total = len(users_df[users_df['group_name'] == 'A'])
    control_conv_rate = control_converted / control_total * 100 if control_total > 0 else 0
    
    treatment_converted = len(users_df[(users_df['group_name'] == 'B') & 
                                        (users_df['user_id'].isin(subscriptions_df['user_id'].unique()))])
    treatment_total = len(users_df[users_df['group_name'] == 'B'])
    treatment_conv_rate = treatment_converted / treatment_total * 100 if treatment_total > 0 else 0
    
    print(f"  ✓ Created {len(subscriptions_df):,} subscription payments")
    print(f"    - Group A conversion rate:   {control_conv_rate:.1f}%")
    print(f"    - Group B conversion rate:   {treatment_conv_rate:.1f}%")
    print(f"    - Lift:                      {(treatment_conv_rate - control_conv_rate):+.1f}%")
    
    # ============ GENERATE TRADES ============
    print("\n3. Generating trading activity...")
    trades_data = []
    
    for idx, user in users_df.iterrows():
        # Only users who made a deposit generate trades
        if user['first_deposit_date'] is not None:
            # Number of trades follows Poisson distribution (mean=15)
            n_trades = np.random.poisson(15)
            
            for _ in range(n_trades):
                # Trades spread over 6 months after registration
                trade_date = user['registration_date'] + timedelta(
                    days=np.random.randint(1, 180)
                )
                
                # Commission amount (exponential distribution, mean=$5)
                commission = np.random.exponential(5)
                
                trades_data.append({
                    'user_id': user['user_id'],
                    'trade_date': trade_date,
                    'commission_usd': commission
                })
    
    trades_df = pd.DataFrame(trades_data)
    
    print(f"  ✓ Created {len(trades_df):,} trades")
    if len(trades_df) > 0:
        print(f"    - Average commission: ${trades_df['commission_usd'].mean():.2f}")
    
    # ============ VALIDATION ============
    validate_data(users_df, subscriptions_df, trades_df)
    
    # ============ SAVE TO CSV ============
    print("\n4. Saving to CSV files...")
    users_df.to_csv('data/users.csv', index=False)
    subscriptions_df.to_csv('data/subscriptions.csv', index=False)
    trades_df.to_csv('data/trades.csv', index=False)
    print("  ✓ Saved to data/users.csv")
    print("  ✓ Saved to data/subscriptions.csv")
    print("  ✓ Saved to data/trades.csv")
    
    # ============ FINAL SUMMARY ============
    print("\n" + "=" * 60)
    print("✓ Data generation complete!")
    print("=" * 60)
    print(f"Total users:        {len(users_df):,}")
    print(f"Total payments:     {len(subscriptions_df):,}")
    print(f"Total trades:       {len(trades_df):,}")
    print(f"Date range:         {users_df['registration_date'].min().date()} to {users_df['registration_date'].max().date()}")
    print("=" * 60)
    
    return users_df, subscriptions_df, trades_df


if __name__ == "__main__":
    # Make sure data directory exists
    import os
    os.makedirs('data', exist_ok=True)
    
    # Generate data
    users, subscriptions, trades = generate_data()
