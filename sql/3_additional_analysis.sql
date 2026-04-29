-- Additional analysis: Check behavior of users who made a deposit during the trial (for group B)
WITH user_deposit_during_trial AS (
    SELECT 
        u.user_id,
        u.group_name,
        -- Check if user made a deposit during the first 30 days
        CASE WHEN MAX(CASE WHEN t.trade_date BETWEEN u.registration_date AND DATE_ADD(u.registration_date, INTERVAL 30 DAY) THEN 1 ELSE 0 END) = 1 THEN 1 ELSE 0 END AS deposited_during_trial
    FROM users u
    LEFT JOIN trades t ON u.user_id = t.user_id
    WHERE u.group_name = 'B'
    GROUP BY u.user_id, u.group_name
)
SELECT
    deposited_during_trial,
    COUNT(user_id) AS users,
    AVG(converted) AS conversion_rate,
    AVG(total_revenue) AS avg_ltv
FROM user_deposit_during_trial ud
JOIN user_revenues ur ON ud.user_id = ur.user_id
GROUP BY deposited_during_trial;
