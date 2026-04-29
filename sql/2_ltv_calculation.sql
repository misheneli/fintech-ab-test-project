-- Calculate 6-month LTV and other key metrics for the cohorts
WITH user_revenues AS (
    SELECT 
        u.user_id,
        u.group_name,
        -- Calculate subscription revenue (10 per successful payment)
        SUM(CASE WHEN s.payment_status = 'success' THEN 10 ELSE 0 END) AS subscription_revenue,
        -- Calculate trading commission revenue
        SUM(t.commission_usd) AS commission_revenue,
        -- Total revenue for the user
        (SUM(CASE WHEN s.payment_status = 'success' THEN 10 ELSE 0 END) + COALESCE(SUM(t.commission_usd), 0)) AS total_revenue,
        -- Check if user ever converted
        MAX(CASE WHEN s.subscription_id IS NOT NULL THEN 1 ELSE 0 END) AS converted
    FROM users u
    LEFT JOIN subscriptions s ON u.user_id = s.user_id 
        AND s.payment_date BETWEEN u.registration_date AND DATE_ADD(u.registration_date, INTERVAL 6 MONTH)
    LEFT JOIN trades t ON u.user_id = t.user_id 
        AND t.trade_date BETWEEN u.registration_date AND DATE_ADD(u.registration_date, INTERVAL 6 MONTH)
    WHERE u.registration_date BETWEEN '2023-11-01' AND '2023-11-21'
    GROUP BY u.user_id, u.group_name
)
SELECT
    group_name,
    COUNT(user_id) AS total_users,
    AVG(converted) AS conversion_rate,
    AVG(total_revenue) AS avg_ltv,
    SUM(total_revenue) / COUNT(user_id) AS arpu,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_revenue) AS median_ltv
FROM user_revenues
GROUP BY group_name;
