-- Check for group balance (A/A test) before the experiment impact
SELECT 
    group_name,
    COUNT(user_id) AS number_of_users,
    AVG(age) AS average_age,
    AVG(initial_balance_usd) AS average_initial_balance,
    COUNT(CASE WHEN first_deposit_date IS NOT NULL THEN user_id END) * 1.0 / COUNT(user_id) AS deposit_rate
FROM users
WHERE registration_date BETWEEN '2023-11-01' AND '2023-11-21'
GROUP BY group_name;
