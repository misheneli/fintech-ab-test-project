import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

print("Generating synthetic data...")

# Generate user data
n_users = 8000
user_ids = range(1000, 1000 + n_users)

# Generate registration dates between Nov 1 and Nov 21, 2023
start_date = datetime(2023, 11, 1)
end_date = datetime(2023, 11, 21)
registration_dates = [start_date + timedelta(days=np.random.randint(0, (end_date - start_date).days)) for _ in range(n_users)]

# Randomly assign users to groups A and B
groups = np.random.choice(['A', 'B'], size=n_users, p=[0.5, 0.5])

# Simulate user characteristics
ages = np.random.normal(35, 10, n_users).astype(int)
initial_balances = np.random.exponential(1000, n_users)

# Simulate likelihood of making a deposit (70% of users make a deposit)
made_first_deposit = np.random.binomial(1, 0.7, n_users)

# Generate first deposit dates for those who made a deposit
first_deposit_dates = []
for i, deposited in enumerate(made_first_deposit):
    if deposited:
        # Deposit within 0-5 days after registration
        deposit_date = registration_dates[i] + timedelta(days=np.random.randint(0, 6))
        first_deposit_dates.append(deposit_date)
    else:
        first_deposit_dates.append(None)

# Create users dataframe
users_df = pd.DataFrame({
    'user_id': user_ids,
    'registration_date': registration_dates,
    'group_name': groups,
    'age': ages,
    'initial_balance_usd': initial_balances,
    'first_deposit_date': first_deposit_dates
})

# Generate subscriptions data
subscriptions_data = []
subscription_id_counter = 1

for _, user in users_df.iterrows():
    # Group A: Immediate paywall with 2% conversion
    if user['group_name'] == 'A':
        converted = np.random.binomial(1, 0.02)  # 2% conversion
        if converted:
            sub_date = user['registration_date'] + timedelta(days=np.random.randint(1, 8))
            # Simulate monthly payments for up to 6 months with increasing churn
            for month in range(6):
                if np.random.binomial(1, 0.9 - (month * 0.05)):  # Churn increases each month
                    payment_date = sub_date + timedelta(days=30*month)
                    subscriptions_data.append({
                        'user_id': user['user_id'],
                        'subscription_id': subscription_id_counter,
                        'payment_date': payment_date,
                        'payment_status': 'success'
                    })
                    subscription_id_counter += 1
                else:
                    break
    
    # Group B: Free trial with 5% sign-up and 60% conversion after trial
    else:
        converted_trial = np.random.binomial(1, 0.05)  # 5% sign up for trial
        if converted_trial:
            trial_start = user['registration_date'] + timedelta(days=np.random.randint(1, 5))
            # After trial, 60% convert to paying
            converts_to_paying = np.random.binomial(1, 0.6)
            if converts_to_paying:
                for month in range(1, 6):  # Start paying from month 2
                    if np.random.binomial(1, 0.85 - (month * 0.05)):
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

# Create subscriptions dataframe
subscriptions_df = pd.DataFrame(subscriptions_data)

# Generate trades data
trades_data = []
for user_id in users_df['user_id']:
    # Check if user made a deposit
    user_row = users_df[users_df['user_id'] == user_id].iloc[0]
    if user_row['first_deposit_date'] is not None:
        # Active traders make more trades
        n_trades = np.random.poisson(15)
        for i in range(n_trades):
            # Trades spread over 6 months
            trade_date = user_row['registration_date'] + timedelta(days=np.random.randint(1, 180))
            commission = np.random.exponential(5)  # Average $5 commission
            trades_data.append({
                'user_id': user_id,
                'trade_date': trade_date,
                'commission_usd': commission
            })

trades_df = pd.DataFrame(trades_data)

# Save to CSV
users_df.to_csv('data/users.csv', index=False)
subscriptions_df.to_csv('data/subscriptions.csv', index=False)
trades_df.to_csv('data/trades.csv', index=False)

print("Data generation complete!")
print(f"Generated {len(users_df)} users, {len(subscriptions_df)} subscriptions, and {len(trades_df)} trades.")
